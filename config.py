import os
from dotenv import load_dotenv

load_dotenv()

FEISHU_APP_ID = os.getenv("FEISHU_APP_ID")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET")
DEFAULT_APP_TOKEN = os.getenv("DEFAULT_APP_TOKEN")
DEFAULT_TABLE_ID = os.getenv("DEFAULT_TABLE_ID")

ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
ZHIPU_API_URL = os.getenv("ZHIPU_API_URL", "https://open.bigmodel.cn/api/paas/v4/chat/completions")

FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "80"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def validate_config():
    required_configs = {
        "FEISHU_APP_ID": FEISHU_APP_ID,
        "FEISHU_APP_SECRET": FEISHU_APP_SECRET,
        "DEFAULT_APP_TOKEN": DEFAULT_APP_TOKEN,
        "DEFAULT_TABLE_ID": DEFAULT_TABLE_ID,
        "ZHIPU_API_KEY": ZHIPU_API_KEY,
    }
    
    missing = [key for key, value in required_configs.items() if not value]
    
    if missing:
        raise ValueError(f"缺少必要配置项: {', '.join(missing)}，请检查.env文件")
