
from app.config.mineru_config import load_mineru_config

mineru_config = load_mineru_config()
url = mineru_config.base_url
token = mineru_config.api_token

print(url)
print(token)