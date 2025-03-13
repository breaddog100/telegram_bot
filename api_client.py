import logging
import requests
from dotenv import load_dotenv
import os
from config import MODEL_PROVIDER, DEEPSEEK_API_URL, ARK_API_KEY, DEEPSEEK_MODEL, GROQ_API_KEY, GROQ_MODEL
from crawler import get_search_results, get_top_10_links, fetch_page_content

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 根据配置选择大模型
if MODEL_PROVIDER == "deepseek":
    from volcenginesdkarkruntime import Ark
    client = Ark(api_key=ARK_API_KEY, timeout=1800)
elif MODEL_PROVIDER == "groq":
    import groq
    client = groq.Client(api_key=GROQ_API_KEY)
else:
    raise ValueError(f"不支持的模型提供商: {MODEL_PROVIDER}")

def call_api(messages):
    """
    调用大模型 API
    :param messages: 消息列表，包含用户问题和搜索引擎结果
    :return: 模型生成的回答
    """
    logger.info(f"请求上下文: {messages}")
    try:
        # 根据配置调用不同的 API
        if MODEL_PROVIDER == "deepseek":
            response = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=messages
            )
        elif MODEL_PROVIDER == "groq":
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages
            )
        logger.info(f"响应数据: {response}")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"调用{MODEL_PROVIDER} API失败: {e}", exc_info=True)
        return '请求失败，请稍后再试。'
