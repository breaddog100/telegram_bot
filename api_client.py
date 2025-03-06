from volcenginesdkarkruntime import Ark
from config import ARK_API_KEY
client = Ark(
    api_key=ARK_API_KEY,
    timeout=1800,  # 设置超时时间为 30 分钟
)
def call_deepseek_api(messages):
    try:
        # 打印对话历史（用于调试）
        logger.info(f"上下文: {messages}")
        # 发送请求，传递上下文
        response = client.chat.completions.create(
            model="deepseek-r1-250120",  # 替换为你的模型 ID
            messages=messages
        )
        # 返回模型生成的回答
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"调用Deepseek API失败: {e}")
        return '请求失败，请稍后再试。'
