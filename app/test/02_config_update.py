from typing import TypedDict

class Config(TypedDict):
    api_key: str
    base_url: str

test = Config(api_key="123", base_url="http://example.com")
print(test)

update = {"api_key": "456", "base_url": "https://example.com"}
test.update(**update)
print(test)