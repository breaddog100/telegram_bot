from dotenv import load_dotenv
import os
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ARK_API_KEY = os.getenv('ARK_API_KEY')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("请设置环境变量 TELEGRAM_BOT_TOKEN")
if not ARK_API_KEY:
    raise ValueError("请设置环境变量 ARK_API_KEY")
