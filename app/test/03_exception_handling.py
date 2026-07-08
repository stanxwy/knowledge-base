from app.processor.import_processor.exceptions import ValidationError

try:
    # 可能失败的操作
    raise ValidationError("数据类型不匹配")
except Exception as e:
    raise ValidationError(
        message="向量写入失败",
        node_name="import_milvus",
        cause=e
    )

# python -m app.test.03_exception_handling                                                                         
# Traceback (most recent call last):                                                                                                                          
#   File "\knowledge-base\app\test\03_exception_handling.py", line 5, in <module>
#     raise ValidationError("数据类型不匹配")
# app.processor.import_processor.exceptions.ValidationError: 数据类型不匹配

# During handling of the above exception, another exception occurred:

# Traceback (most recent call last):
#   File "<frozen runpy>", line 198, in _run_module_as_main
#   File "<frozen runpy>", line 88, in _run_code
#   File "\knowledge-base\app\test\03_exception_handling.py", line 7, in <module>
#     raise ValidationError(
# app.processor.import_processor.exceptions.ValidationError: [import_milvus] 向量写入失败 (原因: 数据类型不匹配)