import logging
import requests
from dotenv import load_dotenv
import os
from config import MODEL_PROVIDER, DEEPSEEK_API_URL, ARK_API_KEY, DEEPSEEK_MODEL, GROQ_API_KEY, GROQ_MODEL

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

# 从环境变量中获取 Google Custom Search API 配置
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CX = os.getenv('GOOGLE_CX')

def search_google(query):
    """
    使用 Google Custom Search API 进行搜索
    :param query: 搜索查询字符串
    :return: 搜索结果的文本摘要
    """
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CX}&q={query}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json()
        if 'items' in results:
            return ' '.join([item['snippet'] for item in results['items']])
        else:
            return "未找到相关结果。"
    except requests.RequestException as e:
        logger.error(f"搜索时出错: {e}")
        return "搜索时出错，请稍后再试。"

def call_api(client, message):
    """
    调用大模型 API
    :param client: 模型客户端
    :param message: 用户消息
    :return: 模型生成的回答
    """
    messages = [
        {
            "role": "user",
            "content": message
        }
    ]
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

def handle_message(client, message):
    """
    处理用户消息，先进行网络搜索，再根据搜索结果总结回答
    :param client: 模型客户端
    :param message: 用户消息
    :return: 回答内容
    """
    search_result = search_google(message)
    # 将搜索结果作为上下文，让模型总结回答
    summary_query = f"请总结以下搜索结果来回答问题 '{message}': {search_result}"
    return call_api(client, summary_query)
