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

def call_api(client, messages):
    """
    调用大模型 API
    :param client: 模型客户端
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

def handle_message(client, message):
    """
    处理用户消息，先进行网络搜索，再根据搜索结果总结回答
    :param client: 模型客户端
    :param message: 用户消息
    :return: 回答内容
    """
    # 调用 SearXNG 搜索引擎获取相关内容
    query_url = f"http://198.135.50.173:56880/search?q={requests.utils.quote(message)}&format=json"
    search_result = get_search_results(query_url)
    if search_result:
        top_10_links = get_top_10_links(search_result)
        page_contents = []
        for link in top_10_links:
            logger.info(f"正在获取 {link} 的内容...")
            page_content = fetch_page_content(link)
            if page_content:
                page_contents.append(page_content)
        # 将页面内容拼接成一个字符串
        combined_content = "\n\n".join(page_contents)
        # 将用户问题和页面内容结合
        messages = [
            {"role": "user", "content": message},
            {"role": "user", "content": f"相关页面内容：{combined_content}"}
        ]
        return call_api(client, messages)
    else:
        return "未找到相关结果。"
