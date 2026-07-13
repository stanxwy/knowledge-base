from pathlib import Path
import os
import shutil

# 创建 Path 对象
path = Path("./docs/Docker镜像加速.md")

# 常用属性
print(path.name)    # "万用表的使用.pdf" - 完整文件名
print(path.stem)       # "万用表的使用" - 不含扩展名的文件名
print(path.suffix)     # ".pdf" - 扩展名
print(path.parent)     # Path("D:/doc") - 父目录

# 常用方法
print(path.exists())  # True/False - 文件是否存在
print(path.is_file())  # True/False - 是否为文件
print(path.is_dir())   # True/False - 是否为目录

# 路径拼接（使用 / 运算符）
output_path = path.parent / "output" / "result.md"
print(output_path)

new_dir = path.parent / "a" / "b" / "c"
print("type(new_dir)", type(new_dir))
print(new_dir) # relative path
print(new_dir.absolute()) # absolute path
new_dir.mkdir(parents=True, exist_ok=True)
print(new_dir.exists())

# 删除目录
shutil.rmtree((path.parent / "a"))
print(new_dir.exists())


for file in os.listdir(Path(".")):
    print(file)