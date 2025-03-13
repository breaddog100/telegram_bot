from dotenv import load_dotenv
import os
# 加载 .env 文件中的环境变量
load_dotenv()
# Telegram Bot 配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("请设置环境变量 TELEGRAM_BOT_TOKEN")
# 选择使用的大模型（可选：deepseek 或 groq）
MODEL_PROVIDER = os.getenv('MODEL_PROVIDER', 'groq')  # 默认使用 deepseek
# Deepseek API 配置
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL')  # Deepseek API 的 URL
ARK_API_KEY = os.getenv('ARK_API_KEY')  # Deepseek API 的密钥
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-r1-250120')  # 默认模型 ID
# Groq API 配置
GROQ_API_KEY = os.getenv('GROQ_API_KEY')  # Groq API 的密钥
GROQ_MODEL = os.getenv('GROQ_MODEL', 'qwen-2.5-32b')  # 默认模型 ID
# 数据库配置
DATABASE_FILE = os.getenv('DATABASE_FILE', 'bot.db')  # 默认数据库文件路径
# 日志配置
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')  # 默认日志文件路径
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # 默认日志级别
# 其他配置
MAX_HISTORY_ROUNDS = int(os.getenv('MAX_HISTORY_ROUNDS', '5'))  # 默认最大历史对话轮次
# 检查必要的环境变量
if MODEL_PROVIDER == "deepseek":
    if not DEEPSEEK_API_URL:
        raise ValueError("请设置环境变量 DEEPSEEK_API_URL")
    if not ARK_API_KEY:
        raise ValueError("请设置环境变量 ARK_API_KEY")
elif MODEL_PROVIDER == "groq":
    if not GROQ_API_KEY:
        raise ValueError("请设置环境变量 GROQ_API_KEY")
else:
    raise ValueError(f"不支持的模型提供商: {MODEL_PROVIDER}")
