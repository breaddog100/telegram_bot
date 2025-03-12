import logging
from config import MODEL_PROVIDER, DEEPSEEK_API_URL, ARK_API_KEY, DEEPSEEK_MODEL, GROQ_API_KEY, GROQ_MODEL
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
def call_api(client):
    messages = [
        {
            "role": "user",
            "content": get_user_message()  # 假设这是获取用户消息的函数
        }
    ]
    print(f"调用API时的messages参数: {messages}")  # 调试输出
    try:
        response = client.chat.completions.create(
            model="your_model_name",  # 替换为实际的模型名称
            messages=messages
        )
        return response
    except Exception as e:
        print(f"调用API时出错: {e}")
        return None
    """调用大模型 API"""
    try:
        # 打印请求的上下文（用于调试）
        logger.info(f"请求上下文: {messages}")
        
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
        
        # 打印响应数据（用于调试）
        logger.info(f"响应数据: {response}")
        
        # 返回模型生成的回答
        return response.choices[0].message.content
    except Exception as e:
        # 打印详细的错误信息（用于调试）
        logger.error(f"调用{MODEL_PROVIDER} API失败: {e}", exc_info=True)
        return '请求失败，请稍后再试。'
