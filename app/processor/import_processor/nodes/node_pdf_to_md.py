import json
import logging
import shutil
import time
import zipfile
from pathlib import Path

import requests

from app.config.mineru_config import mineru_config
from app.processor.import_processor.base import BaseNode, setup_logging
from app.processor.import_processor.exceptions import StateFieldError, FileProcessingError, ConfigurationError, \
    PdfConversionError
from app.processor.import_processor.state import ImportGraphState


class NodePDFToMD(BaseNode):
    """
    PDF 转 Markdown 节点：PDF结构化解析
    """

    name = "node_pdf_to_md"
    
    def _step_1_validate_paths(self, state: ImportGraphState) -> tuple[Path, Path]:
        """
        步骤1：校验PDF文件路径和输出目录
        核心职责：参数非空校验 | 路径转换 | PDF文件有效性校验 | 输出目录自动创建
        返回：合法的PDF文件Path对象、输出目录Path对象
        异常：StateFieldError(参数缺失)、FileProcessingError(文件无效)
        """
        
        # 1、参数非空校验
        pdf_path = state.get("pdf_path")
        if not pdf_path:
            raise StateFieldError(field_name='pdf_path', expected_type=str)

        output_file_dir = state.get("output_file_dir")
        if not output_file_dir:
            raise StateFieldError(field_name='output_file_dir', expected_type=str)

        # 2、转换为Path对象统一处理路径
        pdf_path_obj = Path(pdf_path)
        output_dir_obj = Path(output_file_dir)

        # 3、PDF文件有效性校验
        if not pdf_path_obj.exists():
            raise FileProcessingError(message=f"PDF文件{pdf_path_obj.name}不存在")

        # 4、确保输出目录存在，不存在则递归创建
        if not output_dir_obj.exists():
            self.logger.info(f"输出目录不存在，自动创建：{output_dir_obj.absolute()}")
            output_dir_obj.mkdir(parents=True, exist_ok=True)

        return pdf_path_obj, output_dir_obj

    def _step_2_upload_and_poll(self, pdf_path_obj: Path) -> str:
        """
        步骤2：上传PDF至MinerU并轮询解析任务状态
        核心流程：获取上传链接 → 文件上传 → 任务轮询（直至完成/失败/超时）
        参数：pdf_path_obj-已校验的PDF Path对象
        返回：解析结果ZIP包下载链接full_zip_url
        异常：ConfigurationError(配置缺失)、PdfConversionError(请求/上传失败)、TimeoutError(任务超时)
        """

        # 1. 从MinerU服务器获取上传链接
        token = mineru_config.api_token
        url = f"{mineru_config.base_url}/file-urls/batch"
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        data = {
            "files": [
                {"name": pdf_path_obj.name}
            ],
            "model_version": "vlm"
        }

        # 获取上传url和任务的batch_id
        response = requests.post(url, headers=header, json=data)

        # 对响应结果进行校验
        # 先校验http状态
        if response.status_code != 200:
            raise PdfConversionError(message=f"获取上传链接响应失败：状态码：{response.status_code}，响应结果：{response}")

        # 校验业务码
        result = response.json()
        if result.get("code") != 0:
            raise PdfConversionError(f"获取上传链接失败：返回数据：{result}")

        # 获取响应结果
        signed_url = result["data"]["file_urls"][0]
        batch_id = result["data"]["batch_id"]
        self.logger.info(f"获取上传链接成功！batch_id：{batch_id}，signed_url：{signed_url}")

        # 2. 文件上传
        with open(pdf_path_obj, "rb") as f:
            res_upload = requests.put(signed_url, data=f)
            if res_upload.status_code != 200:
                raise PdfConversionError(f"文件上传失败：状态码：{res_upload.status_code}，响应结果：{res_upload}")
            self.logger.info("文件上传成功！")

        # 3. 批量获取任务结果
        poll_url = f"{mineru_config.base_url}/extract-results/batch/{batch_id}"

        start_time = time.time()  # 记录开始时间
        timeout_seconds = 600  # 最大超时时间
        poll_interval = 3  # 轮询间隔时间
        self.logger.info(f"【任务轮询】最大超时：{timeout_seconds}s，batch_id：{batch_id}")

        # 4. 根据batch_id轮询任务状态直到成功"done"
        while True:
            # 已消耗时间
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout_seconds:
                raise TimeoutError(f"【任务轮询】超时！任务处理超{timeout_seconds}秒，batch_id：{batch_id}")

            # 发起轮询请求，短超时10秒，异常则重试
            try:
                res_poll = requests.get(url=poll_url, headers=header, timeout=10)
            except Exception as e:
                self.logger.warning(f"【任务轮询】网络请求异常，{poll_interval}秒后重试：{str(e)}，batch_id：{batch_id}")
                time.sleep(poll_interval)
                continue

            # 处理HTTP响应错误
            if res_poll.status_code != 200:
                raise PdfConversionError(f"【任务轮询】HTTP请求失败，状态码：{res_poll.status_code}，响应内容：{res_poll}")

            # 解析轮询结果，校验业务状态
            poll_data = res_poll.json()
            self.logger.info(f"【任务轮询】轮询结果：{poll_data}")

            if poll_data["code"] != 0:
                raise PdfConversionError(f"【任务轮询】业务错误，返回数据：{poll_data}")

            extract_results = poll_data["data"]["extract_result"]

            # 获取结果
            result_item = extract_results[0]
            data_state = result_item["state"]

            # 状态为 done
            if data_state == "done":
                self.logger.info(f"【任务轮询】解析任务完成！总耗时{int(elapsed_time)}s，batch_id：{batch_id}")

                full_zip_url = result_item["full_zip_url"]
                self.logger.info(f"【任务轮询】返回ZIP包下载链接：{full_zip_url}，batch_id：{batch_id}")

                return full_zip_url

            elif data_state == "failed":
                err_msg = result_item.get("err_msg", "未知错误，无具体信息")
                raise PdfConversionError(f"【任务轮询】解析任务失败！batch_id：{batch_id}，错误信息：{err_msg}")

            else:
                self.logger.info(f"【任务轮询】处理中... 已耗时{int(elapsed_time)}s，状态：{data_state}， batch_id：{batch_id}")
                time.sleep(poll_interval)

    def _step_3_download_and_extract(self, zip_url: str, output_dir_obj: Path, pdf_stem: str) -> str:
        """
       步骤3：下载MinerU解析结果ZIP包并解压，提取目标MD文件
       核心流程：下载ZIP → 清理旧目录并解压 → 查找MD文件 → 重命名统一为PDF同名
       参数：zip_url-ZIP包下载链接；output_dir_obj-输出目录Path；pdf_stem-PDF无后缀纯名称
       返回：最终MD文件的字符串格式绝对路径
       异常：RuntimeError(下载失败)
       """

        # 1、下载ZIP包
        self.logger.info(f"【ZIP下载】开始下载ZIP包：{zip_url} ...")
        response = requests.get(zip_url)

        # 对响应结果进行校验
        if response.status_code != 200:
            raise RuntimeError(f"【ZIP下载】ZIP包下载失败：状态码：{response.status_code}，响应结果：{response}")

        # 拼接ZIP包保存路径并保存
        zip_save_path = output_dir_obj / f"{pdf_stem}_result.zip"
        with open(zip_save_path, "wb") as f:
            f.write(response.content)
        self.logger.info(f"【ZIP下载】ZIP包下载成功：保存路径：{zip_save_path}")


        # 2. 如果目标文件夹已存在，先删除（确保环境干净）
        extract_target_dir = output_dir_obj / pdf_stem
        if extract_target_dir.exists():
            shutil.rmtree(extract_target_dir)
        self.logger.info(f"【ZIP解压】已清空旧的解压目录：{extract_target_dir}")

        # 3、创建解压目录
        extract_target_dir.mkdir(parents=True, exist_ok=True)

        # 4、解压
        self.logger.info(f"【ZIP解压】开始解压ZIP包：{output_dir_obj} ...")
        with zipfile.ZipFile(zip_save_path, "r") as zip_file_obj:
            zip_file_obj.extractall(extract_target_dir)
        self.logger.info(f"【ZIP解压】ZIP解压完成，解压目录：{extract_target_dir}")

        # 5、重命名
        self.logger.info(f"【MD重命名】找到MinerU生成的full.md文件")
        target_md_file = extract_target_dir / "full.md"
        self.logger.info(f"【MD重命名】开始将full.md文件进行重命名")
        new_md_path = target_md_file.with_name(f"{pdf_stem}.md")
        target_md_file.rename(new_md_path)
        self.logger.info(f"【MD重命名】重命名成功，文件名：{pdf_stem}.md")

        return str(new_md_path.absolute())

    def process(self, state: ImportGraphState):
        """
        :param state: `pdf_path`、`file_dir`
        :return: `md_path`、`md_content`
        """

        update_state = {}
        # 步骤1：校验PDF路径和输出目录
        pdf_path_obj, output_dir_obj = self._step_1_validate_paths(state)

        # 步骤2：上传PDF至MinerU并轮询解析结果
        zip_url = self._step_2_upload_and_poll(pdf_path_obj)

        # 步骤3：下载ZIP包并提取MD文件
        md_path = self._step_3_download_and_extract(zip_url, output_dir_obj, pdf_path_obj.stem)

        # 步骤4：读取md的内容
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        # 步骤5：更新state状态
        update_state["md_path"] = md_path
        update_state["md_content"] = md_content

        return update_state

    
if __name__ == "__main__":
    setup_logging()

    init_state = {
        "pdf_path": "./kb/H3C LA2608室内无线网关 用户手册-6W100-整本手册.pdf",
        "output_file_dir": "./output"
    }
    node_pdf_to_md = NodePDFToMD()
    result = node_pdf_to_md(init_state)
    logging.getLogger().info(json.dumps(result, ensure_ascii=False, indent=4))

"""
python -m app.processor.import_processor.nodes.node_pdf_to_md
config loaded True...
ImportConfig instance not found...
creating ImportConfig instance...
2026-07-09 00:18:02 - import.node_pdf_to_md - INFO - --- node_pdf_to_md 开始 ---
2026-07-09 00:18:03 - import.node_pdf_to_md - INFO - 获取上传链接成功！batch_id：c3bc4c31-5e7b-4ae7-800d-da1cd28a69f6，signed_url：https://mineru.oss-cn-shanghai.aliyuncs.com/api-upload/extract/2026-07-09/c3bc4c31-5e7b-4ae7-800d-da1cd28a69f6/a1d92bec-7546-445f-8450-9d291bdee105.pdf?Expires=1783613883&OSSAccessKeyId=LTAI5t8fSGMgiRhQn4mpp926&Signature=Mkd52v39hudYmr6uulN5FAFjrAQ%3D
2026-07-09 00:18:04 - import.node_pdf_to_md - INFO - 文件上传成功！
2026-07-09 00:18:04 - import.node_pdf_to_md - INFO - 【任务轮询】最大超时：600s，batch_id：c3bc4c31-5e7b-4ae7-800d-da1cd28a69f6
2026-07-09 00:18:04 - import.node_pdf_to_md - INFO - 【任务轮询】轮询结果：{'code': 0, 'msg': 'ok', 'trace_id': '0fcecdeb86c9ece83f9184229c01d7df', 'data': {'batch_id': 'c3bc4c31-5e7b-4ae7-800d-da1cd28a69f6', 'extract_result': [{'file_name': 'H3C LA2608室内无线网关 用户手册-6W100-整本手册.pdf', 'state': 'pending', 'err_msg': ''}]}}
2026-07-09 00:18:04 - import.node_pdf_to_md - INFO - 【任务轮询】处理中... 已耗时0s，状态：pending， batch_id：c3bc4c31-5e7b-4ae7-800d-da1cd28a69f6
2026-07-09 00:18:07 - import.node_pdf_to_md - INFO - 【任务轮询】轮询结果：{'code': 0, 'msg': 'ok', 'trace_id': 'fc03764febc139dde4628ac00055bfda', 'data': {'batch_id': 'c3bc4c31-5e7b-4ae7-800d-da1cd28a69f6', 'extract_result': [{'file_name': 'H3C LA2608室内无线网关 用户手册-6W100-整本手册.pdf', 'state': 'done', 'err_msg': '', 'full_zip_url': 'https://cdn-mineru.openxlab.org.cn/pdf/2026-06-22/61bd4b2e-b9f1-4782-b162-5c480189fb91.zip'}]}}
2026-07-09 00:18:07 - import.node_pdf_to_md - INFO - 【任务轮询】解析任务完成！总耗时3s，batch_id：c3bc4c31-5e7b-4ae7-800d-da1cd28a69f6
2026-07-09 00:18:07 - import.node_pdf_to_md - INFO - 【任务轮询】返回ZIP包下载链接：https://cdn-mineru.openxlab.org.cn/pdf/2026-06-22/61bd4b2e-b9f1-4782-b162-5c480189fb91.zip，batch_id：c3bc4c31-5e7b-4ae7-800d-da1cd28a69f6
2026-07-09 00:18:07 - import.node_pdf_to_md - INFO - 【ZIP下载】开始下载ZIP包：https://cdn-mineru.openxlab.org.cn/pdf/2026-06-22/61bd4b2e-b9f1-4782-b162-5c480189fb91.zip ...
2026-07-09 00:18:08 - import.node_pdf_to_md - INFO - 【ZIP下载】ZIP包下载成功：保存路径：output\H3C LA2608室内无线网关 用户手册-6W100-整本手册_result.zip
2026-07-09 00:18:08 - import.node_pdf_to_md - INFO - 【ZIP解压】已清空旧的解压目录：output\H3C LA2608室内无线网关 用户手册-6W100-整本手册
2026-07-09 00:18:08 - import.node_pdf_to_md - INFO - 【ZIP解压】开始解压ZIP包：output ...
2026-07-09 00:18:08 - import.node_pdf_to_md - INFO - 【ZIP解压】ZIP解压完成，解压目录：output\H3C LA2608室内无线网关 用户手册-6W100-整本手册
2026-07-09 00:18:08 - import.node_pdf_to_md - INFO - 【MD重命名】找到MinerU生成的full.md文件
2026-07-09 00:18:08 - import.node_pdf_to_md - INFO - 【MD重命名】开始将full.md文件进行重命名
2026-07-09 00:18:08 - import.node_pdf_to_md - INFO - 【MD重命名】重命名成功，文件名：H3C LA2608室内无线网关 用户手册-6W100-整本手册.md
2026-07-09 00:18:08 - import.node_pdf_to_md - INFO - --- node_pdf_to_md 完成 ---
2026-07-09 00:18:08 - root - INFO - {
    "md_path": "D:\\code\\atguigu\\knowledge-base\\output\\H3C LA2608室内无线网关 用户手册-6W100-整本手册\\H3C LA2608室内无线网关 用户手册-6W100-整本手册.md",
    "md_content": "# H3C LA2608 室内无线网关\n\n用户手册\n\nCopyright © 2014 杭州华三通信技术有限公司及其许可者 版权所有，保留一切权利。\n\n未经本公司书面许可，任何单位和个人不得擅自摘抄、复制本书内容的部分或全部，并不得以任何形式传播。\n\nH3C、 、Aolynk、 Aolynk 、H<sup>3</sup>Care、 Heare TOP G, TOPG IRF、NetPilot、Neocean、NeoVTL、SecPro、SecPoint、SecEngine、SecPath、Comware、Secware、Storware、NQA、VVG、V<sup>2</sup>G、V<sup>n</sup>G、PSPT、XGbus、N-Bus、TiGem、InnoVision、HUASAN、华三均为杭州华三通信技术有限公司的商标。对于本手册中出现的其它公司的商标、产品标识及商品名称，由各自权利人拥有。\n\n由于产品版本升级或其他原因，本手册内容有可能变更。H3C保留在没有任何通知或者提示的情况下对本手册的内容进行修改的权利。本手册仅作为使用指导，H3C尽全力在本手册中提供准确的信息，但是 H3C 并不确保手册内容完全没有错误，本手册中的所有陈述、信息和建议也不构成任何明示或暗示的担保。\n\n## 目 录\n\n1 H3C LA2608 室内无线网关用户手册 …… 1\n1.1 概述 …… 1\n1.2 配置LA2608与无线控制器互通 …… 1\n1.2.1 配置LA2608 …… 1\n1.2.2 配置运营商无线控制器 …… 2\n1.2.3 验证LA2608与无线控制器是否连通 …… 3\n\n## 1 H3C LA2608 室内无线网关用户手册\n\n## 1.1 概述\n\nH3C LA2608-GM/GU 室内无线网关（以下简称 LA2608）可以为用户提供无线服务，为了实现对设备的管理，LA2608需要通过 3G/4G网络连接到运营商无线控制器。\n\n![](images/16288d553bf867b279adb856534213ef37a0d17bdec59c9c4abf824878cd7e56.jpg)\n\n说明\n\n目前，LA2608只支持与 H3C公司的无线控制器互通。\n\n## 1.2 配置LA2608与无线控制器互通\n\n如 图 1 所示，LA2608 安装了SIM卡，通过 3G/4G网络连接到运营商无线控制器，并向用户提供无线服务。关于LA2608的安装方法，请参见“H3C LA2608室内无线网关 快速安装指南”。\n\n图1 配置 LA2608与无线控制器互通\n\n![](images/2436b496658837dfc940d48d8565fa9a9135932ebf6e2c2a25e9fff4f674dd39.jpg)\n\n## 1.2.1 配置LA2608\n\n(1) 配置拨号访问组的拨号控制列表\n\n```txt\n<LA2608>system-view\n[LA2608]dialer-rule 1 ip permit\n(2) 配置 DCC 拨号\n```\n\n![](images/06474f326a73aa174281952c2d7a262f50b5a813a0a0523744c4cc52374ef0fd.jpg)\n\ndialer number命令用来配置发起呼叫的拨号串，不同运营商的拨号串不同，请用户在配置前向网络运营商获取发起呼叫的拨号串。\n\n```powershell\n[LA2608]interface Cellular-Ethernet2/0\n[LA2608-Cellular-Ethernet2/0]ip address cellular-allocated\n[LA2608-Cellular-Ethernet2/0]dialer enable-circular\n[LA2608-Cellular-Ethernet2/0]dialer-group 1\n[LA2608-Cellular-Ethernet2/0]dialer timer idle 0\n```\n\n```txt\n[LA2608-Cellular-Ethernet2/0]dialer timer autodial 5\n[LA2608-Cellular-Ethernet2/0]dialer number *99# autodial\n[LA2608-Cellular-Ethernet2/0]nat outbound\n[LA2608-Cellular-Ethernet2/0]quit\n\n(3) 配置 DNS 解析功能\n[LA2608]dns resolve\n\n(4) 配置静态路由\n[LA2608]ip route-static 0.0.0.0 0.0.0.0 Cellular-Ethernet2/0\n\n(5) 指定运营商无线控制器的 IP 地址\n[LA2608] wlan ac ip 60.191.99.143\n```\n\n## 1.2.2 配置运营商无线控制器\n\n![](images/08e8c1c7f9c7f47a615d8449dea68240baed840efe2f63d2a292dceb249bef98.jpg)\n\n## 说明\n\n如下配置仅供参考，运营商可根据实际情况进行调整。\n\n## (1) 创建业务 VLAN\n\n```txt\n(1) 创建业务 VLAN\n<AC>system-view\n[AC]vlan 2\n[AC-vlan2] quit\n(2) 创建 WLAN-ESS 接口并加入业务 VLAN\n[AC]interface WLAN-ESS 1\n[AC-WLAN-ESS1]port access vlan 2\n[AC-WLAN-ESS1]quit\n(3) 配置明文方式的服务模板\n[AC]wlan service-template 1 clear\n[AC-wlan-st-1]ssid ssidh3c\n[AC-wlan-st-1]bind WLAN-ESS 1\n[AC-wlan-st-1]service-template enable\nPlease wait... Done.\n[AC-wlan-st-1]quit\n(4) 开启自动 AP 功能\n[AC]wlan auto-ap enable\n[AC]wlan ap 2608 model LA2608 id 1\n[AC-wlan-ap-2608]serial-id auto\n[AC-wlan-ap-2608]radio 1\n[AC-wlan-ap-2608-radio-1]service-template 1\n[AC-wlan-ap-2608-radio-1]radio enable\n[AC-wlan-ap-2608-radio-1]quit\n[AC-wlan-ap-2608]quit\n(5) 配置 VLAN 接口 IP 地址\n[AC]interface Vlan-interface 1\n[AC-Vlan-interface1]ip address 60.191.99.143 255.255.0.0\n[AC-Vlan-interface1]quit\n[AC]interface Vlan-interface 2\n[AC-Vlan-interface2]ip address 10.249.136.1 255.255.252.0\n[AC-Vlan-interface2]quit\n(6) 使能 DHCP 服务，配置 DHCP 地址池\n```\n\n```txt\n[AC]dhcp enable\n[AC]dhcp server ip-pool vlan2\n[AC-dhcp-pool-vlan1]network 10.249.136.0 22\n[AC-dhcp-pool-vlan1]gateway-list 10.249.136.1\n[AC-dhcp-pool-vlan1]dns-list 218.201.96.130\n[AC-dhcp-pool-vlan1]quit\n```\n\n## 1.2.3 验证LA2608 与无线控制器是否连通\n\n在无线控制器上执行 display wlan ap 命令，state 字段显示为“R/M”，表示 LA2608 与无线控制器之间已经建立连接。\n\n```txt\n<Sysname> display wlan ap all\nTotal Number of APs configured : 1\nTotal Number of configured APs connected : 1\nTotal Number of auto APs connected : 0\nAP Profiles\nState : I = Idle, J = Join, JA = JoinAck, IL = ImageLoad\nC = Config, R = Run, KU = KeyUpdate, KC = KeyCfm\nM = Master, B = Backup\n```\n\n```csv\nAP Name State Model Serial-ID\nap1 R/M LA2608 036286A054000033\n```"
}
"""