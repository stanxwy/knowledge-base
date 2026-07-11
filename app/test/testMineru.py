"""
执行 MinerU 命令
import_file_path: 解析的文件路径
file_dir_path: 解析后的文件目录
"""
import os
import subprocess
import time

# 1. 设置环境变量
env = os.environ.copy()
# 使用本地模型
env["MINERU_MODEL_SOURCE"] = "local"

# 1. 构建命令行
cmd = "mineru -p ./kb/B3-211H.pdf -o ./output --backend pipeline"

process_start_time = time.time()

# 2. 执行命令行(子进程执行命令行)
proc = subprocess.Popen(
    args=cmd,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    errors="replace",       # 遇到乱码时替换
    text=True,              # 输出的内容是字符串 不是字节
    encoding="utf-8",       # 用指定的中文字符集进行编解码
    bufsize=1               # 按行缓冲，只要缓冲区一行满了就输出
)

# 3. 获取日志信息
for line in proc.stdout:
    print(f"执行MinerU产生的日志：{line}")

# 4. 等待子进程做完
processed_code = proc.wait()

process_end_time = time.time()
if processed_code == 0:
    print(f"MinerU成功解析PDF文件，耗时:{process_end_time - process_start_time:.2f}s")
else:
    print("MinerU解析PDF文件失败")

"""
(py311) PS D:\knowledge-base> python -m app.test.testMineru
执行MinerU产生的日志：2026-07-11 09:36:38.075 | INFO     | mineru.cli.client:run_orchestrated_cli:953 - Started local mineru-api at http://127.0.0.1:19794

执行MinerU产生的日志：2026-07-11 09:36:42.675 | INFO     | __main__:create_app:236 - Request concurrency limited to 3

执行MinerU产生的日志：INFO:     Started server process [13800]

执行MinerU产生的日志：INFO:     Waiting for application startup.

执行MinerU产生的日志：INFO:     Application startup complete.

执行MinerU产生的日志：INFO:     Uvicorn running on http://127.0.0.1:19794 (Press CTRL+C to quit)

执行MinerU产生的日志：2026-07-11 09:36:43.172 | INFO     | mineru.cli.client:run_planned_task:832 - Submitting batch 1/1 | 1 document, 17 pages in this batch | 17 pages total | task#1 [B3-211H]

执行MinerU产生的日志：2026-07-11 09:37:18.740 | INFO     | mineru.backend.pipeline.pipeline_analyze:doc_analyze_streaming:209 - Pipeline processing-window multi-file run. doc_count=1, total_pages=17, window_size=64, total_batches=1

执行MinerU产生的日志：2026-07-11 09:37:24.435 | INFO     | mineru.backend.pipeline.pipeline_analyze:doc_analyze_streaming:264 - Pipeline processing window batch 1/1: 17/17 pages, batch_pages=17, doc_slices=doc0:1-17

执行MinerU产生的日志：2026-07-11 09:37:24.439 | INFO     | mineru.backend.pipeline.pipeline_analyze:batch_image_analyze:364 - GPU Memory: 1 GB, Batch Ratio: 1.

执行MinerU产生的日志：2026-07-11 09:37:24.439 | INFO     | mineru.backend.pipeline.model_init:__init__:239 - DocAnalysis init, this may take some times......

执行MinerU产生的日志：2026-07-11 09:37:26.916 | INFO     | mineru.backend.pipeline.model_init:__init__:291 - DocAnalysis init done!

执行MinerU产生的日志：2026-07-11 09:37:26.917 | INFO     | mineru.backend.pipeline.pipeline_analyze:custom_model_init:83 - model init cost: 2.478496789932251

执行MinerU产生的日志：Start MinerU FastAPI Service: http://127.0.0.1:19794

执行MinerU产生的日志：API documentation: http://127.0.0.1:19794/docs

执行MinerU产生的日志：

执行MinerU产生的日志：Layout Predict:   0%|          | 0/17 [00:00<?, ?it/s]

执行MinerU产生的日志：Layout Predict:   6%|▌         | 1/17 [00:01<00:24,  1.52s/it]

执行MinerU产生的日志：Layout Predict:  12%|█▏        | 2/17 [00:02<00:19,  1.33s/it]

执行MinerU产生的日志：Layout Predict:  18%|█▊        | 3/17 [00:03<00:18,  1.30s/it]

执行MinerU产生的日志：Layout Predict:  24%|██▎       | 4/17 [00:05<00:16,  1.28s/it]

执行MinerU产生的日志：Layout Predict:  29%|██▉       | 5/17 [00:06<00:15,  1.31s/it]

执行MinerU产生的日志：Layout Predict:  35%|███▌      | 6/17 [00:07<00:14,  1.33s/it]

执行MinerU产生的日志：Layout Predict:  41%|████      | 7/17 [00:09<00:13,  1.35s/it]

执行MinerU产生的日志：Layout Predict:  47%|████▋     | 8/17 [00:10<00:11,  1.33s/it]

执行MinerU产生的日志：Layout Predict:  53%|█████▎    | 9/17 [00:11<00:09,  1.24s/it]

执行MinerU产生的日志：Layout Predict:  59%|█████▉    | 10/17 [00:12<00:08,  1.24s/it]

执行MinerU产生的日志：Layout Predict:  65%|██████▍   | 11/17 [00:14<00:07,  1.26s/it]

执行MinerU产生的日志：Layout Predict:  71%|███████   | 12/17 [00:15<00:06,  1.25s/it]

执行MinerU产生的日志：Layout Predict:  76%|███████▋  | 13/17 [00:16<00:05,  1.29s/it]

执行MinerU产生的日志：Layout Predict:  82%|████████▏ | 14/17 [00:18<00:03,  1.31s/it]

执行MinerU产生的日志：Layout Predict:  88%|████████▊ | 15/17 [00:19<00:02,  1.31s/it]

执行MinerU产生的日志：Layout Predict:  94%|█████████▍| 16/17 [00:20<00:01,  1.30s/it]

执行MinerU产生的日志：Layout Predict: 100%|██████████| 17/17 [00:22<00:00,  1.28s/it]

执行MinerU产生的日志：Layout Predict: 100%|██████████| 17/17 [00:22<00:00,  1.30s/it]

执行MinerU产生的日志：

执行MinerU产生的日志：Table orientation det:   0%|          | 0/6 [00:00<?, ?it/s]

执行MinerU产生的日志：Table orientation det:  17%|█▋        | 1/6 [00:01<00:05,  1.07s/it]

执行MinerU产生的日志：Table orientation det:  33%|███▎      | 2/6 [00:01<00:03,  1.20it/s]

执行MinerU产生的日志：Table orientation det:  50%|█████     | 3/6 [00:02<00:02,  1.10it/s]

执行MinerU产生的日志：Table orientation det:  67%|██████▋   | 4/6 [00:03<00:01,  1.11it/s]

执行MinerU产生的日志：Table orientation det:  83%|████████▎ | 5/6 [00:04<00:00,  1.01it/s]

执行MinerU产生的日志：Table orientation det: 100%|██████████| 6/6 [00:05<00:00,  1.05it/s]

执行MinerU产生的日志：Table orientation score: 100%|██████████| 6/6 [00:05<00:00,  1.05it/s]

执行MinerU产生的日志：Table orientation score: 100%|██████████| 6/6 [00:05<00:00,  1.05it/s]

执行MinerU产生的日志：Table orientation: 100%|██████████| 6/6 [00:05<00:00,  1.05it/s]

执行MinerU产生的日志：Table orientation: 100%|██████████| 6/6 [00:05<00:00,  1.05it/s]

执行MinerU产生的日志：Table orientation: 100%|██████████| 6/6 [00:05<00:00,  1.06it/s]

执行MinerU产生的日志：

执行MinerU产生的日志：Table-ocr det:   0%|          | 0/6 [00:00<?, ?it/s]

执行MinerU产生的日志：Table-ocr det:  17%|█▋        | 1/6 [00:01<00:06,  1.29s/it]

执行MinerU产生的日志：Table-ocr det:  33%|███▎      | 2/6 [00:02<00:03,  1.04it/s]

执行MinerU产生的日志：Table-ocr det:  50%|█████     | 3/6 [00:02<00:02,  1.04it/s]

执行MinerU产生的日志：Table-ocr det:  67%|██████▋   | 4/6 [00:03<00:01,  1.08it/s]

执行MinerU产生的日志：Table-ocr det:  83%|████████▎ | 5/6 [00:04<00:00,  1.03it/s]

执行MinerU产生的日志：Table-ocr det: 100%|██████████| 6/6 [00:05<00:00,  1.09it/s]

执行MinerU产生的日志：Table-ocr det: 100%|██████████| 6/6 [00:05<00:00,  1.05it/s]

执行MinerU产生的日志：

执行MinerU产生的日志：Table-ocr rec ch:   0%|          | 0/314 [00:00<?, ?it/s]

执行MinerU产生的日志：Table-ocr rec ch:   2%|▏         | 6/314 [00:00<00:08, 34.61it/s]

执行MinerU产生的日志：Table-ocr rec ch:   4%|▍         | 12/314 [00:00<00:08, 36.00it/s]

执行MinerU产生的日志：Table-ocr rec ch:   6%|▌         | 18/314 [00:00<00:07, 39.84it/s]

执行MinerU产生的日志：Table-ocr rec ch:   8%|▊         | 24/314 [00:00<00:07, 39.47it/s]

执行MinerU产生的日志：Table-ocr rec ch:  10%|▉         | 30/314 [00:00<00:07, 39.40it/s]

执行MinerU产生的日志：Table-ocr rec ch:  11%|█▏        | 36/314 [00:00<00:07, 39.68it/s]

执行MinerU产生的日志：Table-ocr rec ch:  13%|█▎        | 42/314 [00:01<00:06, 41.06it/s]

执行MinerU产生的日志：Table-ocr rec ch:  15%|█▌        | 48/314 [00:01<00:06, 40.97it/s]

执行MinerU产生的日志：Table-ocr rec ch:  17%|█▋        | 54/314 [00:01<00:06, 40.55it/s]

执行MinerU产生的日志：Table-ocr rec ch:  19%|█▉        | 60/314 [00:01<00:06, 41.50it/s]

执行MinerU产生的日志：Table-ocr rec ch:  21%|██        | 66/314 [00:01<00:06, 41.10it/s]

执行MinerU产生的日志：Table-ocr rec ch:  23%|██▎       | 72/314 [00:01<00:05, 40.96it/s]

执行MinerU产生的日志：Table-ocr rec ch:  25%|██▍       | 78/314 [00:01<00:05, 39.95it/s]

执行MinerU产生的日志：Table-ocr rec ch:  27%|██▋       | 84/314 [00:02<00:05, 39.87it/s]

执行MinerU产生的日志：Table-ocr rec ch:  29%|██▊       | 90/314 [00:02<00:05, 41.34it/s]

执行MinerU产生的日志：Table-ocr rec ch:  31%|███       | 96/314 [00:02<00:05, 40.73it/s]

执行MinerU产生的日志：Table-ocr rec ch:  32%|███▏      | 102/314 [00:02<00:05, 40.99it/s]

执行MinerU产生的日志：Table-ocr rec ch:  34%|███▍      | 108/314 [00:02<00:05, 40.31it/s]

执行MinerU产生的日志：Table-ocr rec ch:  36%|███▋      | 114/314 [00:02<00:04, 40.36it/s]

执行MinerU产生的日志：Table-ocr rec ch:  38%|███▊      | 120/314 [00:02<00:04, 40.53it/s]

执行MinerU产生的日志：Table-ocr rec ch:  40%|████      | 126/314 [00:03<00:04, 40.49it/s]

执行MinerU产生的日志：Table-ocr rec ch:  42%|████▏     | 132/314 [00:03<00:04, 41.45it/s]

执行MinerU产生的日志：Table-ocr rec ch:  44%|████▍     | 138/314 [00:03<00:04, 39.31it/s]

执行MinerU产生的日志：Table-ocr rec ch:  46%|████▌     | 144/314 [00:03<00:04, 40.82it/s]

执行MinerU产生的日志：Table-ocr rec ch:  48%|████▊     | 150/314 [00:03<00:04, 40.50it/s]

执行MinerU产生的日志：Table-ocr rec ch:  50%|████▉     | 156/314 [00:03<00:03, 40.13it/s]

执行MinerU产生的日志：Table-ocr rec ch:  52%|█████▏    | 162/314 [00:04<00:03, 40.27it/s]

执行MinerU产生的日志：Table-ocr rec ch:  54%|█████▎    | 168/314 [00:04<00:03, 40.10it/s]

执行MinerU产生的日志：Table-ocr rec ch:  55%|█████▌    | 174/314 [00:04<00:03, 40.44it/s]

执行MinerU产生的日志：Table-ocr rec ch:  57%|█████▋    | 180/314 [00:04<00:03, 39.61it/s]

执行MinerU产生的日志：Table-ocr rec ch:  59%|█████▉    | 186/314 [00:04<00:03, 39.53it/s]

执行MinerU产生的日志：Table-ocr rec ch:  61%|██████    | 192/314 [00:04<00:03, 39.85it/s]

执行MinerU产生的日志：Table-ocr rec ch:  63%|██████▎   | 198/314 [00:04<00:02, 39.64it/s]

执行MinerU产生的日志：Table-ocr rec ch:  65%|██████▍   | 204/314 [00:05<00:02, 40.91it/s]

执行MinerU产生的日志：Table-ocr rec ch:  67%|██████▋   | 210/314 [00:05<00:02, 40.13it/s]

执行MinerU产生的日志：Table-ocr rec ch:  69%|██████▉   | 216/314 [00:05<00:02, 40.25it/s]

执行MinerU产生的日志：Table-ocr rec ch:  71%|███████   | 222/314 [00:05<00:02, 40.39it/s]

执行MinerU产生的日志：Table-ocr rec ch:  73%|███████▎  | 228/314 [00:05<00:02, 39.50it/s]

执行MinerU产生的日志：Table-ocr rec ch:  75%|███████▍  | 234/314 [00:05<00:02, 39.95it/s]

执行MinerU产生的日志：Table-ocr rec ch:  76%|███████▋  | 240/314 [00:05<00:01, 39.22it/s]

执行MinerU产生的日志：Table-ocr rec ch:  78%|███████▊  | 246/314 [00:06<00:01, 39.52it/s]

执行MinerU产生的日志：Table-ocr rec ch:  80%|████████  | 252/314 [00:06<00:01, 34.80it/s]

执行MinerU产生的日志：Table-ocr rec ch:  82%|████████▏ | 258/314 [00:06<00:01, 32.01it/s]

执行MinerU产生的日志：Table-ocr rec ch:  84%|████████▍ | 264/314 [00:06<00:01, 30.29it/s]

执行MinerU产生的日志：Table-ocr rec ch:  86%|████████▌ | 270/314 [00:07<00:01, 27.46it/s]

执行MinerU产生的日志：Table-ocr rec ch:  88%|████████▊ | 276/314 [00:07<00:01, 25.25it/s]

执行MinerU产生的日志：Table-ocr rec ch:  90%|████████▉ | 282/314 [00:07<00:01, 22.39it/s]

执行MinerU产生的日志：Table-ocr rec ch:  92%|█████████▏| 288/314 [00:08<00:01, 19.28it/s]

执行MinerU产生的日志：Table-ocr rec ch:  94%|█████████▎| 294/314 [00:08<00:01, 17.24it/s]

执行MinerU产生的日志：Table-ocr rec ch:  96%|█████████▌| 300/314 [00:08<00:00, 16.04it/s]

执行MinerU产生的日志：Table-ocr rec ch:  97%|█████████▋| 306/314 [00:09<00:00, 14.61it/s]

执行MinerU产生的日志：Table-ocr rec ch:  99%|█████████▉| 312/314 [00:10<00:00, 12.40it/s]

执行MinerU产生的日志：Table-ocr rec ch: 100%|██████████| 314/314 [00:10<00:00, 11.35it/s]

执行MinerU产生的日志：Table-ocr rec ch: 100%|██████████| 314/314 [00:10<00:00, 30.20it/s]

执行MinerU产生的日志：

执行MinerU产生的日志：Table-wireless Predict:   0%|          | 0/6 [00:00<?, ?it/s]

执行MinerU产生的日志：Table-wireless Predict:  67%|██████▋   | 4/6 [00:00<00:00,  4.36it/s]

执行MinerU产生的日志：Table-wireless Predict: 100%|██████████| 6/6 [00:02<00:00,  1.82it/s]

执行MinerU产生的日志：Table-wireless Predict: 100%|██████████| 6/6 [00:02<00:00,  2.06it/s]

执行MinerU产生的日志：

执行MinerU产生的日志：Table-wired Predict:   0%|          | 0/5 [00:00<?, ?it/s]

执行MinerU产生的日志：Table-wired Predict:  20%|██        | 1/5 [00:02<00:08,  2.11s/it]

执行MinerU产生的日志：Table-wired Predict:  40%|████      | 2/5 [00:02<00:04,  1.35s/it]

执行MinerU产生的日志：Table-wired Predict:  60%|██████    | 3/5 [00:05<00:04,  2.05s/it]

执行MinerU产生的日志：Table-wired Predict:  80%|████████  | 4/5 [00:07<00:01,  1.89s/it]

执行MinerU产生的日志：Table-wired Predict: 100%|██████████| 5/5 [00:08<00:00,  1.63s/it]

执行MinerU产生的日志：Table-wired Predict: 100%|██████████| 5/5 [00:08<00:00,  1.73s/it]

执行MinerU产生的日志：

执行MinerU产生的日志：OCR-det ch:   0%|          | 0/150 [00:00<?, ?it/s]

执行MinerU产生的日志：OCR-det ch:   1%|          | 1/150 [00:00<01:23,  1.79it/s]

执行MinerU产生的日志：OCR-det ch:   1%|▏         | 2/150 [00:00<00:49,  3.00it/s]

执行MinerU产生的日志：OCR-det ch:   2%|▏         | 3/150 [00:00<00:37,  3.97it/s]

执行MinerU产生的日志：OCR-det ch:   3%|▎         | 4/150 [00:01<01:13,  1.99it/s]

执行MinerU产生的日志：OCR-det ch:   8%|▊         | 12/150 [00:02<00:16,  8.27it/s]

执行MinerU产生的日志：OCR-det ch:  13%|█▎        | 20/150 [00:02<00:09, 13.77it/s]

执行MinerU产生的日志：OCR-det ch:  15%|█▌        | 23/150 [00:02<00:12, 10.56it/s]

执行MinerU产生的日志：OCR-det ch:  21%|██        | 31/150 [00:04<00:17,  6.69it/s]

执行MinerU产生的日志：OCR-det ch:  22%|██▏       | 33/150 [00:05<00:20,  5.82it/s]

执行MinerU产生的日志：OCR-det ch:  23%|██▎       | 34/150 [00:05<00:19,  5.98it/s]

执行MinerU产生的日志：OCR-det ch:  28%|██▊       | 42/150 [00:06<00:17,  6.15it/s]

执行MinerU产生的日志：OCR-det ch:  33%|███▎      | 50/150 [00:07<00:16,  6.20it/s]

执行MinerU产生的日志：OCR-det ch:  38%|███▊      | 57/150 [00:09<00:15,  6.09it/s]

执行MinerU产生的日志：OCR-det ch:  39%|███▉      | 59/150 [00:09<00:14,  6.08it/s]

执行MinerU产生的日志：OCR-det ch:  45%|████▍     | 67/150 [00:10<00:14,  5.76it/s]

执行MinerU产生的日志：OCR-det ch:  50%|█████     | 75/150 [00:12<00:13,  5.73it/s]

执行MinerU产生的日志：OCR-det ch:  55%|█████▌    | 83/150 [00:13<00:11,  5.74it/s]

执行MinerU产生的日志：OCR-det ch:  61%|██████    | 91/150 [00:15<00:10,  5.54it/s]

执行MinerU产生的日志：OCR-det ch:  65%|██████▌   | 98/150 [00:16<00:10,  5.20it/s]

执行MinerU产生的日志：OCR-det ch:  67%|██████▋   | 100/150 [00:16<00:09,  5.43it/s]

执行MinerU产生的日志：OCR-det ch:  69%|██████▊   | 103/150 [00:17<00:07,  5.90it/s]

执行MinerU产生的日志：OCR-det ch:  71%|███████   | 106/150 [00:18<00:08,  5.33it/s]

执行MinerU产生的日志：OCR-det ch:  73%|███████▎  | 109/150 [00:18<00:07,  5.82it/s]

执行MinerU产生的日志：OCR-det ch:  74%|███████▍  | 111/150 [00:18<00:06,  5.78it/s]

执行MinerU产生的日志：OCR-det ch:  76%|███████▌  | 114/150 [00:19<00:05,  6.57it/s]

执行MinerU产生的日志：OCR-det ch:  79%|███████▊  | 118/150 [00:19<00:04,  7.66it/s]

执行MinerU产生的日志：OCR-det ch:  81%|████████▏ | 122/150 [00:19<00:03,  7.56it/s]

执行MinerU产生的日志：OCR-det ch:  83%|████████▎ | 125/150 [00:20<00:03,  7.67it/s]

执行MinerU产生的日志：OCR-det ch:  87%|████████▋ | 130/150 [00:20<00:02,  9.59it/s]

执行MinerU产生的日志：OCR-det ch:  88%|████████▊ | 132/150 [00:20<00:02,  8.53it/s]

执行MinerU产生的日志：OCR-det ch:  89%|████████▉ | 134/150 [00:21<00:02,  7.99it/s]

执行MinerU产生的日志：OCR-det ch:  91%|█████████ | 136/150 [00:21<00:01,  7.29it/s]

执行MinerU产生的日志：OCR-det ch:  91%|█████████▏| 137/150 [00:21<00:02,  6.31it/s]

执行MinerU产生的日志：OCR-det ch:  92%|█████████▏| 138/150 [00:22<00:02,  5.95it/s]

执行MinerU产生的日志：OCR-det ch:  95%|█████████▌| 143/150 [00:22<00:00,  8.82it/s]

执行MinerU产生的日志：OCR-det ch:  97%|█████████▋| 146/150 [00:22<00:00,  9.75it/s]

执行MinerU产生的日志：OCR-det ch:  98%|█████████▊| 147/150 [00:23<00:00,  7.50it/s]

执行MinerU产生的日志：OCR-det ch:  99%|█████████▊| 148/150 [00:23<00:00,  5.75it/s]

执行MinerU产生的日志：OCR-det ch:  99%|█████████▉| 149/150 [00:23<00:00,  5.08it/s]

执行MinerU产生的日志：OCR-det ch: 100%|██████████| 150/150 [00:24<00:00,  4.67it/s]

执行MinerU产生的日志：OCR-det ch: 100%|██████████| 150/150 [00:24<00:00,  6.24it/s]

执行MinerU产生的日志：

执行MinerU产生的日志：OCR-rec Predict:   0%|          | 0/200 [00:00<?, ?it/s]

执行MinerU产生的日志：OCR-rec Predict:   3%|▎         | 6/200 [00:00<00:03, 52.46it/s]

执行MinerU产生的日志：OCR-rec Predict:   6%|▌         | 12/200 [00:00<00:03, 50.47it/s]

执行MinerU产生的日志：OCR-rec Predict:   9%|▉         | 18/200 [00:00<00:03, 45.71it/s]

执行MinerU产生的日志：OCR-rec Predict:  12%|█▏        | 24/200 [00:00<00:03, 46.29it/s]

执行MinerU产生的日志：OCR-rec Predict:  15%|█▌        | 30/200 [00:00<00:04, 40.82it/s]

执行MinerU产生的日志：OCR-rec Predict:  18%|█▊        | 36/200 [00:00<00:04, 36.14it/s]

执行MinerU产生的日志：OCR-rec Predict:  21%|██        | 42/200 [00:01<00:04, 34.65it/s]

执行MinerU产生的日志：OCR-rec Predict:  24%|██▍       | 48/200 [00:01<00:04, 33.69it/s]

执行MinerU产生的日志：OCR-rec Predict:  27%|██▋       | 54/200 [00:01<00:04, 33.19it/s]

执行MinerU产生的日志：OCR-rec Predict:  30%|███       | 60/200 [00:01<00:04, 31.82it/s]

执行MinerU产生的日志：OCR-rec Predict:  33%|███▎      | 66/200 [00:01<00:04, 31.02it/s]

执行MinerU产生的日志：OCR-rec Predict:  36%|███▌      | 72/200 [00:02<00:04, 31.47it/s]

执行MinerU产生的日志：OCR-rec Predict:  39%|███▉      | 78/200 [00:02<00:04, 29.98it/s]

执行MinerU产生的日志：OCR-rec Predict:  42%|████▏     | 84/200 [00:02<00:04, 26.79it/s]

执行MinerU产生的日志：OCR-rec Predict:  45%|████▌     | 90/200 [00:02<00:04, 25.24it/s]

执行MinerU产生的日志：OCR-rec Predict:  48%|████▊     | 96/200 [00:03<00:05, 20.42it/s]

执行MinerU产生的日志：OCR-rec Predict:  51%|█████     | 102/200 [00:03<00:05, 18.30it/s]

执行MinerU产生的日志：OCR-rec Predict:  54%|█████▍    | 108/200 [00:04<00:06, 15.01it/s]

执行MinerU产生的日志：OCR-rec Predict:  57%|█████▋    | 114/200 [00:04<00:06, 13.12it/s]

执行MinerU产生的日志：OCR-rec Predict:  60%|██████    | 120/200 [00:05<00:06, 11.79it/s]

执行MinerU产生的日志：OCR-rec Predict:  63%|██████▎   | 126/200 [00:06<00:07, 10.53it/s]

执行MinerU产生的日志：OCR-rec Predict:  66%|██████▌   | 132/200 [00:06<00:07,  9.50it/s]

执行MinerU产生的日志：OCR-rec Predict:  69%|██████▉   | 138/200 [00:07<00:06,  8.91it/s]

执行MinerU产生的日志：OCR-rec Predict:  72%|███████▏  | 144/200 [00:08<00:06,  8.64it/s]

执行MinerU产生的日志：OCR-rec Predict:  75%|███████▌  | 150/200 [00:09<00:06,  8.14it/s]

执行MinerU产生的日志：OCR-rec Predict:  78%|███████▊  | 156/200 [00:10<00:05,  7.51it/s]

执行MinerU产生的日志：OCR-rec Predict:  81%|████████  | 162/200 [00:10<00:04,  7.69it/s]

执行MinerU产生的日志：OCR-rec Predict:  84%|████████▍ | 168/200 [00:11<00:04,  7.18it/s]

执行MinerU产生的日志：OCR-rec Predict:  87%|████████▋ | 174/200 [00:12<00:03,  7.19it/s]

执行MinerU产生的日志：OCR-rec Predict:  90%|█████████ | 180/200 [00:13<00:02,  6.94it/s]

执行MinerU产生的日志：OCR-rec Predict:  93%|█████████▎| 186/200 [00:14<00:02,  6.49it/s]

执行MinerU产生的日志：OCR-rec Predict:  96%|█████████▌| 192/200 [00:15<00:01,  6.37it/s]

执行MinerU产生的日志：OCR-rec Predict:  99%|█████████▉| 198/200 [00:16<00:00,  6.00it/s]

执行MinerU产生的日志：OCR-rec Predict: 100%|██████████| 200/200 [00:17<00:00,  5.64it/s]

执行MinerU产生的日志：OCR-rec Predict: 100%|██████████| 200/200 [00:17<00:00, 11.51it/s]

执行MinerU产生的日志：

执行MinerU产生的日志：Seal Predict: 0it [00:00, ?it/s]

执行MinerU产生的日志：Seal Predict: 0it [00:00, ?it/s]

执行MinerU产生的日志：

执行MinerU产生的日志：Processing pages:   0%|          | 0/17 [00:00<?, ?it/s]

执行MinerU产生的日志：Processing pages:  18%|█▊        | 3/17 [00:00<00:00, 29.65it/s]

执行MinerU产生的日志：Processing pages:  35%|███▌      | 6/17 [00:00<00:00, 24.51it/s]

执行MinerU产生的日志：Processing pages:  53%|█████▎    | 9/17 [00:00<00:00, 26.22it/s]

执行MinerU产生的日志：Processing pages:  76%|███████▋  | 13/17 [00:00<00:00, 30.55it/s]

执行MinerU产生的日志：Processing pages: 100%|██████████| 17/17 [00:00<00:00, 32.03it/s]

执行MinerU产生的日志：Processing pages: 100%|██████████| 17/17 [00:00<00:00, 26.20it/s]

执行MinerU产生的日志：2026-07-11 09:39:07.374 | INFO     | mineru.cli.client:run_planned_task:883 - Completed batch 1/1 | Processed 17/17 pages | 1 of 1 batch finished | task#1 [B3-211H]

MinerU成功解析PDF文件，耗时:165.38s
"""