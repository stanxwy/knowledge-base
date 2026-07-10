## upgrade pip
```bash
(py311) D:\>pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple
Looking in indexes: https://mirrors.aliyun.com/pypi/simple, https://mirrors.aliyun.com/pypi/simple, https://pypi.mirrors.ustc.edu.cn/simple
Requirement already satisfied: pip in D:\dev\miniconda3\envs\py311\Lib\site-packages (26.1.2)
```

## install uv
```bash
(py311) D:\>pip install uv -i https://mirrors.aliyun.com/pypi/simple
Looking in indexes: https://mirrors.aliyun.com/pypi/simple, https://mirrors.aliyun.com/pypi/simple, https://pypi.mirrors.ustc.edu.cn/simple
Collecting uv
  Downloading uv-0.11.28-py3-none-win_amd64.whl (27.6 MB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 27.6/27.6 MB 2.0 MB/s  0:00:13
Installing collected packages: uv
Successfully installed uv-0.11.28
```

## install mineru
```bash
(py311) D:\>uv pip install -U "mineru[all]" -i https://mirrors.aliyun.com/pypi/simple
Using Python 3.11.15 environment at: D:\dev\miniconda3\envs\py311
Resolved 148 packages in 10.12s
      Built pylatexenc==2.10
Prepared 148 packages in 4m 32s
Uninstalled 2 packages in 132ms
░░░░░░░░░░░░░░░░░░░░ [0/148] Installing wheels...
warning: Failed to hardlink files; falling back to full copy. This may lead to degraded performance.
         If the cache and target directories are on different filesystems, hardlinking may not be supported.
         If this is intentional, set `export UV_LINK_MODE=copy` or use `--link-mode=copy` to suppress this warning.
███████████████████░ [143/148] botocore==1.43.45                                                                        
███████████████████░ [146/148] transformers==4.57.6                                      Installed 148 packages in 39.03s
 + accelerate==1.14.0
 + addict==2.4.0
 + aiofiles==24.1.0
 + aiohappyeyeballs==2.7.1
 + aiohttp==3.14.1
 + aiosignal==1.4.0
 + annotated-doc==0.0.4
 + annotated-types==0.7.0
 + anyio==4.14.1
 + apache-tvm-ffi==0.1.12
 + attrs==26.1.0
 + av==18.0.0
 + beautifulsoup4==4.15.0
 + boto3==1.43.45
 + botocore==1.43.45
 + brotli==1.2.0
 + certifi==2026.6.17
 + charset-normalizer==3.4.9
 + click==8.4.2
 + cloudpickle==3.1.2
 + cobble==0.1.4
 + colorama==0.4.6
 + colorlog==6.10.1
 + distro==1.9.0
 + einops==0.8.2
 + et-xmlfile==2.0.0
 + fast-langdetect==0.2.5
 + fastapi==0.139.0
 + fasttext-predict==0.9.2.4
 + ffmpy==1.0.0
 + filelock==3.29.7
 + fire==0.7.1
 + flatbuffers==25.12.19
 + frozenlist==1.8.0
 + fsspec==2026.6.0
 + ftfy==6.3.1
 + gradio==6.8.0
 + gradio-client==2.2.0
 + gradio-pdf==0.0.24
 + groovy==0.1.2
 + h11==0.16.0
 + httpcore==1.0.9
 + httpx==0.28.1
 + httpx-retries==0.6.0
 + huggingface-hub==0.36.2
 + idna==3.18
 + jinja2==3.1.6
 + jiter==0.16.0
 + jmespath==1.1.0
 + json-repair==0.61.2
 + jsonschema==4.26.0
 + jsonschema-specifications==2025.9.1
 + lmdeploy==0.11.1
 + loguru==0.7.3
 + lxml==6.1.1
 + magika==1.0.3
 + mammoth==1.12.0
 + markdown-it-py==4.2.0
 + markupsafe==3.0.3
 + mdurl==0.1.2
 + mineru==3.4.3
 + mineru-vl-utils==1.0.5
 + mmengine-lite==0.10.7
 + modelscope==1.38.1
 + modelscope-hub==0.1.7
 + mpmath==1.3.0
 + msgpack==1.2.1
 + multidict==6.7.1
 + networkx==3.6.1
 + numpy==2.4.6
 + onnxruntime==1.27.0
 + openai==2.45.0
 + openai-harmony==0.0.8
 + opencv-python==5.0.0.93
 + openpyxl==3.1.5
 + orjson==3.11.9
 - packaging==26.0
 + packaging==26.2
 + pandas==3.0.3
 + partial-json-parser==0.2.1.1.post7
 + pdftext==0.7.1
 + peft==0.14.0
 + pillow==12.3.0
 + platformdirs==4.10.0
 + prometheus-client==0.25.0
 + propcache==0.5.2
 + protobuf==7.35.1
 + psutil==7.2.2
 + pybase64==1.4.3
 + pyclipper==1.4.0
 + pydantic==2.13.4
 + pydantic-core==2.46.4
 + pydantic-settings==2.14.2
 + pydub==0.25.1
 + pygments==2.20.0
 + pylatexenc==2.10
 + pypdf==6.14.2
 + pypdfium2==5.10.1
 + pypptx-with-oxml==1.0.3
 + python-dateutil==2.9.0.post0
 + python-docx==1.2.0
 + python-dotenv==1.2.2
 + python-multipart==0.0.32
 + pytz==2026.2
 + pyyaml==6.0.3
 + pyzmq==27.1.0
 + qwen-vl-utils==0.0.14
 + ray==2.56.0
 + referencing==0.37.0
 + regex==2026.6.28
 + reportlab==5.0.0
 + requests==2.34.2
 + rich==15.0.0
 + robust-downloader==0.0.2
 + rpds-py==2026.6.3
 + s3transfer==0.19.0
 + safehttpx==0.1.7
 + safetensors==0.8.0
 + semantic-version==2.10.0
 + sentencepiece==0.2.1
 - setuptools==82.0.1
 + setuptools==83.0.0
 + shapely==2.1.2
 + shellingham==1.5.4
 + shortuuid==1.0.13
 + six==1.17.0
 + sniffio==1.3.1
 + soupsieve==2.8.4
 + starlette==0.52.1
 + sympy==1.14.0
 + termcolor==3.3.0
 + tiktoken==0.13.0
 + tokenizers==0.22.2
 + tomlkit==0.13.3
 + torch==2.8.0
 + torchvision==0.23.0
 + tqdm==4.68.4
 + transformers==4.57.6
 + typer==0.26.8
 + typing-extensions==4.16.0
 + typing-inspection==0.4.2
 + tzdata==2026.2
 + urllib3==2.7.0
 + uvicorn==0.51.0
 + wcwidth==0.8.2
 + win32-setctime==1.2.0
 + xgrammar==0.2.3
 + xlsxwriter==3.2.9
 + yapf==0.43.0
 + yarl==1.24.2

(py311) D:\>mineru --version
mineru, version 3.4.3

```

## install mineru models
```bash
PS D:\> conda activate py311
(py311) PS D:\> $env:MODELSCOPE_CACHE="D:\ai_models\modelscope_cache"

(py311) PS D:\> mineru-models-download
Please select the model download source:  (auto, huggingface, modelscope) [auto]: modelscope
Please select the model type to download:  (pipeline, vlm, all) [all]: all
2026-07-10 19:14:18.610 | INFO     | mineru.cli.models_download:download_models:137 - Downloading all model from modelscope...
2026-07-10 19:14:18.611 | INFO     | mineru.cli.models_download:download_pipeline_models:49 - Downloading model: models/Layout/PP-DocLayoutV2
2026-07-10 19:14:19,334 | INFO    | modelscope_hub.download | Downloading 3 files from OpenDataLab/PDF-Extract-Kit-1.0@master
Downloading: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 3/3 [01:45<00:00, 35.10s/file]
2026-07-10 19:16:05.357 | INFO     | mineru.cli.models_download:download_pipeline_models:49 - Downloading model: models/MFR/unimernet_hf_small_2503
2026-07-10 19:16:06,032 | INFO    | modelscope_hub.download | Downloading 7 files from OpenDataLab/PDF-Extract-Kit-1.0@master
Downloading:  71%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████▊                                             | 5/7 [00:00<00:00,  7.23file/s]2026-07-10 19:16:42,547 | WARNING | modelscope_hub.download | Download failed for models/MFR/unimernet_hf_small_2503/tokenizer.json: ('Connection broken: IncompleteRead(512000 bytes read, 3069950 more expected)', IncompleteRead(512000 bytes read, 3069950 more expected)), will retry                                                                                                    | 74.4M/810M [00:35<05:58, 2.05MB/s]
2026-07-10 19:17:45,461 | WARNING | modelscope_hub.download | Download failed for models/MFR/unimernet_hf_small_2503/tokenizer.json: ('Connection broken: IncompleteRead(134910 bytes read, 3447040 more expected)', IncompleteRead(134910 bytes read, 3447040 more expected)), will retry                                                                                                     | 202M/810M [01:38<04:56, 2.05MB/s]
2026-07-10 19:18:54,466 | WARNING | modelscope_hub.download | Download failed for models/MFR/unimernet_hf_small_2503/tokenizer.json: HTTPSConnectionPool(host='modelscope.cn', port=443): Read timed out., will retryel.safetensors:  42%|███████████████████████████████████████████████████████████████▎                                                                                     | 344M/810M [02:47<03:46, 2.06MB/s]
2026-07-10 19:20:02,824 | WARNING | modelscope_hub.download | Download failed for models/MFR/unimernet_hf_small_2503/tokenizer.json: ('Connection broken: IncompleteRead(143102 bytes read, 3438848 more expected)', IncompleteRead(143102 bytes read, 3438848 more expected)), will retry█████████████████████████████████████████                                                            | 484M/810M [03:55<02:38, 2.06MB/s]
Downloading: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 7/7 [06:38<00:00, 56.97s/file]
2026-07-10 19:22:44.861 | INFO     | mineru.cli.models_download:download_pipeline_models:49 - Downloading model: models/OCR/paddleocr_torch
2026-07-10 19:22:45,623 | INFO    | modelscope_hub.download | Downloading 25 files from OpenDataLab/PDF-Extract-Kit-1.0@master
Downloading: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 25/25 [07:31<00:00, 18.08s/file]
2026-07-10 19:30:17.578 | INFO     | mineru.cli.models_download:download_pipeline_models:49 - Downloading model: models/TabRec/SlanetPlus/slanet-plus.onnx
2026-07-10 19:30:18,240 | INFO    | modelscope_hub.download | Downloading 1 files from OpenDataLab/PDF-Extract-Kit-1.0@master
Downloading: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:03<00:00,  3.47s/file]
2026-07-10 19:30:21.711 | INFO     | mineru.cli.models_download:download_pipeline_models:49 - Downloading model: models/TabRec/UnetStructure/unet.onnx
2026-07-10 19:30:22,348 | INFO    | modelscope_hub.download | Downloading 1 files from OpenDataLab/PDF-Extract-Kit-1.0@master
Downloading: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:03<00:00,  3.80s/file]
2026-07-10 19:30:26.157 | INFO     | mineru.cli.models_download:download_pipeline_models:49 - Downloading model: models/TabCls/paddle_table_cls/PP-LCNet_x1_0_table_cls.onnx
2026-07-10 19:30:26,857 | INFO    | modelscope_hub.download | Downloading 1 files from OpenDataLab/PDF-Extract-Kit-1.0@master
Downloading: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1/1 [00:02<00:00,  2.96s/file]
2026-07-10 19:30:29.821 | INFO     | mineru.cli.models_download:download_pipeline_models:49 - Downloading model: models/MFR/pp_formulanet_plus_m
2026-07-10 19:30:30,507 | INFO    | modelscope_hub.download | Downloading 2 files from OpenDataLab/PDF-Extract-Kit-1.0@master
Downloading:  50%|███████████████████████████████████████████████████████████████████████████████                                                                               | 1/2 [00:02<00:02,  2.74s/file]2026-07-10 19:33:58,692 | WARNING | modelscope_hub.download | Download failed for models/MFR/pp_formulanet_plus_m/PP-FormulaNet_plus-M.pth: ('Connection broken: IncompleteRead(421346066 bytes read, 195992868 more expected)', IncompleteRead(421346066 bytes read, 195992868 more expected)), will retry
Downloading: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 2/2 [05:07<00:00, 153.77s/file]
2026-07-10 19:35:38.053 | INFO     | mineru.cli.models_download:download_pipeline_models:51 - Pipeline models downloaded successfully to: D:\ai_models\modelscope_cache\models\OpenDataLab--PDF-Extract-Kit-1.0\snapshots\master
2026-07-10 19:35:38.055 | INFO     | mineru.cli.models_download:configure_model:33 - The configuration file has been successfully configured, the path is: C:\Users\stan\mineru.json
2026-07-10 19:35:38,795 | INFO    | modelscope_hub.download | Downloading 14 files from OpenDataLab/MinerU2.5-Pro-2605-1.2B@master
Downloading: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 14/14 [18:59<00:00, 81.36s/file]
2026-07-10 19:54:37.908 | INFO     | mineru.cli.models_download:download_vlm_models:58 - VLM models downloaded successfully to: D:\ai_models\modelscope_cache\models\OpenDataLab--MinerU2.5-Pro-2605-1.2B\snapshots\master
2026-07-10 19:54:37.931 | INFO     | mineru.cli.models_download:configure_model:33 - The configuration file has been successfully configured, the path is: C:\Users\stan\mineru.json
(py311) PS D:\>
```

## test run mineru
```bash
(py311) PS D:\> mineru -p H3C.pdf -o output --backend pipeline
2026-07-10 20:05:50.436 | INFO     | mineru.cli.client:run_orchestrated_cli:953 - Started local mineru-api at http://127.0.0.1:36320
2026-07-10 20:05:58.041 | INFO     | __main__:create_app:236 - Request concurrency limited to 3
Start MinerU FastAPI Service: http://127.0.0.1:36320
API documentation: http://127.0.0.1:36320/docs
INFO:     Started server process [12528]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:36320 (Press CTRL+C to quit)
2026-07-10 20:05:59.674 | INFO     | mineru.cli.client:run_planned_task:832 - Submitting batch 1/1 | 1 document, 6 pages in this batch | 6 pages total | task#1 [H3C]
2026-07-10 20:06:59.772 | INFO     | mineru.backend.pipeline.pipeline_analyze:doc_analyze_streaming:209 - Pipeline processing-window multi-file run. doc_count=1, total_pages=6, window_size=64, total_batches=1
2026-07-10 20:07:05.548 | INFO     | mineru.backend.pipeline.pipeline_analyze:doc_analyze_streaming:264 - Pipeline processing window batch 1/1: 6/6 pages, batch_pages=6, doc_slices=doc0:1-6
2026-07-10 20:07:05.571 | INFO     | mineru.backend.pipeline.pipeline_analyze:batch_image_analyze:364 - GPU Memory: 1 GB, Batch Ratio: 1.
2026-07-10 20:07:05.571 | INFO     | mineru.backend.pipeline.model_init:__init__:239 - DocAnalysis init, this may take some times......
2026-07-10 20:07:09.018 | INFO     | mineru.backend.pipeline.model_init:__init__:291 - DocAnalysis init done!
2026-07-10 20:07:09.031 | INFO     | mineru.backend.pipeline.pipeline_analyze:custom_model_init:83 - model init cost: 3.46052885055542
Layout Predict: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 6/6 [00:09<00:00,  1.66s/it]
Table orientation: : 0it [00:00, ?it/s]
Table-wireless Predict: 0it [00:00, ?it/s]
OCR-det ch: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 38/38 [00:10<00:00,  3.52it/s]
Seal Predict: 0it [00:00, ?it/s]
OCR-rec Predict: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 5/5 [00:00<00:00, 16.18it/s]
Processing pages: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 6/6 [00:01<00:00,  4.19it/s]
2026-07-10 20:07:33.509 | INFO     | mineru.cli.client:run_planned_task:883 - Completed batch 1/1 | Processed 6/6 pages | 1 of 1 batch finished | task#1 [H3C]
(py311) PS D:\>
```