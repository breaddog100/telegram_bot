from volcenginesdkarkruntime import Ark
from config import ARK_API_KEY
import logging
# 配置日志
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
# 初始化 Ark 客户端
client = Ark(
    api_key=ARK_API_KEY,
    timeout=1800,  # 设置超时时间为 30 分钟
)
def call_deepseek_api(messages):
    """调用 Deepseek API"""
    try:
        # 打印请求的上下文（用于调试）
        logger.info(f"请求上下文: {messages}")
        # 发送请求，传递上下文
        response = client.chat.completions.create(
            model="deepseek-r1-250120",  # 替换为你的模型 ID
            messages=messages
        )
        # 打印响应数据（用于调试）
        logger.info(f"响应数据: {response}")
        # 返回模型生成的回答
        return response.choices[0].message.content
    except Exception as e:
        # 打印详细的错误信息（用于调试）
        logger.error(f"调用Deepseek API失败: {e}", exc_info=True)
        return '请求失败，请稍后再试。'
