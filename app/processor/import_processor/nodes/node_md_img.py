import os
import re
from collections import deque
from pathlib import Path
from typing import Tuple, List, Dict

from app.processor.import_processor.base import BaseNode
from app.processor.import_processor.exceptions import StateFieldError, FileProcessingError
from app.processor.import_processor.state import ImportGraphState
from app.services.object_store_service import ObjectStoreService, get_object_store_service
from app.utils.api_throttle import apply_api_rate_limit
from app.services.llm_service import generate_image_caption


MAX_QUEUE_SIZE = 10
API_WINDOW_SIZE = 60

class NodeMDImg(BaseNode):

    name: str = "node_md_img"

    def __init__(self, object_store: ObjectStoreService = get_object_store_service()):
        super().__init__()
        self._object_store = object_store

    def _validate_input_state(self, state: ImportGraphState) -> Tuple[str, Path, Path]:

        md_path = state.get("md_path")
        if not md_path:
            raise StateFieldError(field_name='md_path', expected_type=str)

        md_path_obj = Path(md_path)
        if not md_path_obj.exists():
            raise FileProcessingError(message=f"MD file {md_path_obj.name} does not exist")

        md_content = state["md_content"]

        images_dir = md_path_obj.parent / "images"

        return md_content, md_path_obj, images_dir

    def _collect_ref_images(self, md_content: str, images_dir: Path) -> List[Tuple[str, str, Tuple[str, str]]]:
        referenced_images = []
        for image_file in os.listdir(images_dir):
            self.logger.debug(f"Checking image file: {image_file}")

            file_ext = os.path.splitext(image_file)[1].lower()
            if file_ext not in self.config.image_extensions:
                self.logger.warning(f"Extension not supported, skip：{image_file}")
                continue

            img_path = str(images_dir / image_file)
            context = self._extract_image_context(md_content, image_file)

            if not context:
                self.logger.warning(f"Image not referenced in MD, skip: {image_file}")
                continue

            referenced_images.append((image_file, img_path, context))

        self.logger.info(f"Images to be processed: {len(referenced_images)}")
        return referenced_images
    
    def _extract_image_context(self, md_content: str, image_file: str, context_len: int = 100) -> Tuple[str, str]:
        # ![alt text](images/file.extension)
        pattern = re.compile(r"!\[.*?\]\(.*?" + re.escape(image_file) + r".*?\)")

        match = pattern.search(md_content)
        if not match:
            self.logger.debug(f"Image not referenced in MD, skip: {image_file}")
            return None

        start, end = match.span()
        self.logger.debug(f"Image {image_file} position: {start}-{end}")
        pre_text = md_content[max(0, start - context_len):start]
        post_text = md_content[end:min(len(md_content), end + context_len)]
        return pre_text, post_text

    def _generate_image_captions(self, doc_stem: str, target_images: List[Tuple[str, str, Tuple[str, str]]]) -> Dict[str, str]:
        captions = {}
        request_deque = deque()

        for img_file_name, image_file_path, context in target_images:
            apply_api_rate_limit(request_deque, max_requests=MAX_QUEUE_SIZE, window_seconds=API_WINDOW_SIZE)
            captions[img_file_name] = generate_image_caption(image_file_path, doc_stem, context)
        return captions
    
    def _upload_and_replace(self, doc_stem: str, target_images: List[Tuple[str, str, Tuple[str, str]]], summaries: Dict[str, str], md_content: str) -> str:
        # idempotent operation
        upload_dir = doc_stem.replace(" ", "")
        self._object_store.clean_img_dir(upload_dir)

        urls = self._upload_images_batch(upload_dir, target_images)

        # ({ image_file: summary }, { image_file: url }) -> { image_file: (summary, url) }
        image_info = self._build_image_info(summaries, urls)

        return self._replace_img_alt_and_url(md_content, image_info)

    def _upload_images_batch(self, upload_dir: str, target_images: List[Tuple]) -> Dict[str, str]:
        urls = {}
        for img_file, local_img_path, _ in target_images:
            urls[img_file] = self._object_store.upload_img(local_img_path, f"{upload_dir}/{img_file}")
            self.logger.debug(f"Image {img_file} uploaded to {urls[img_file]}")
        self.logger.info(f"{len(target_images)} images uploaded to Object Store")
        return urls

    def _build_image_info(self, summaries: Dict[str, str], urls: Dict[str, str]) -> Dict[str, Tuple[str, str]]:
        image_info = {}
        for image_file, summary in summaries.items():
            if url := urls.get(image_file):
                image_info[image_file] = (summary, url)
        return image_info

    def _replace_img_alt_and_url(self, md_content: str, image_info: Dict[str, Tuple[str, str]]) -> str:

        for image_file, (summary, new_url) in image_info.items():
            pattern = re.compile(r"!\[.*?\]\(.*?" + re.escape(image_file) + r".*?\)")
            md_content = pattern.sub(lambda _: f"![{summary}]({new_url})", md_content)

        self.logger.info(f"Image reference replaced in MD, total replaced: {len(image_info)}")
        return md_content

    def _backup_new_md_file(self, original_md_path: str, md_content: str) -> str:

        new_md_file_name = os.path.splitext(original_md_path)[0] + "_new.md"
        with open(new_md_file_name, "w", encoding="utf-8") as f:
            f.write(md_content)

        self.logger.info(f"processed MD file saved as {new_md_file_name}")
        return new_md_file_name

    def process(self, state: ImportGraphState) -> ImportGraphState:

        md_content, md_path_obj, images_dir = self._validate_input_state(state)
        if not images_dir.exists():
            self.logger.info("Directory images/ not found, skip image processing")
            return {}

        referenced_images = self._collect_ref_images(md_content, images_dir)
        if not referenced_images:
            self.logger.info("No referenced images found, skip image processing")
            return {}

        captions = self._generate_image_captions(md_path_obj.stem, referenced_images)

        new_md_content = self._upload_and_replace(md_path_obj.stem, referenced_images, captions, md_content)

        new_md_file_name = self._backup_new_md_file(md_path_obj, new_md_content)

        return {
            "md_path": new_md_file_name,
            "md_content": new_md_content
        }