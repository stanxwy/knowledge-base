from typing import TypedDict

class Config(TypedDict):
    api_key: str
    base_url: str

config = Config(api_key="123", base_url="http://example.com")
print(config)

update = {"api_key": "456", "base_url": "https://example.com"}
config.update(**update)
print(config)