from telegram import Update
from telegram.ext import CallbackContext
from database import save_group_message, save_private_message, load_private_messages, init_db
from api_client import call_api  # 使用统一的 API 调用函数
from crawler import get_top_10_links, fetch_page_content
import logging
import requests

# 配置日志
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    """处理 /start 命令"""
    await update.message.reply_text('Hi, I‘m Big Dog。 你好，我是大狗。')

async def handle_message(update: Update, context: CallbackContext) -> None:
    """处理用户消息"""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    content = update.message.text

    # 根据聊天类型处理消息
    if update.message.chat.type == "private":
        # 保存私聊消息
        save_private_message(user_id, username, "user", content)
        # 加载历史消息
        MAX_HISTORY_ROUNDS = 5
        messages = load_private_messages(user_id, MAX_HISTORY_ROUNDS)
        messages.append({"role": "user", "content": content})
    else:
        # 保存群聊消息
        save_group_message(chat_id, user_id, username, "user", content)
        # 处理提及机器人的消息
        if update.message.text and '@' + context.bot.username in update.message.text:
            question = update.message.text.replace('@' + context.bot.username, '').strip()
            if update.message.reply_to_message:
                if update.message.reply_to_message.from_user.id == context.bot.id:
                    referenced_content = update.message.reply_to_message.text
                    messages = [
                        {"role": "assistant", "content": referenced_content},
                        {"role": "user", "content": question}
                    ]
                else:
                    referenced_content = update.message.reply_to_message.text
                    messages = [
                        {"role": "user", "content": referenced_content},
                        {"role": "user", "content": question}
                    ]
            else:
                messages = [{"role": "user", "content": question}]
        elif update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id:
            question = update.message.text.strip()
            if question:
                referenced_content = update.message.reply_to_message.text
                messages = [
                    {"role": "assistant", "content": referenced_content},
                    {"role": "user", "content": question}
                ]
        else:
            # 如果没有 @bot 或引用 bot 的发言，直接返回
            return

    # 第一步：让大模型判断是否需要搜索
    try:
        # 构造判断是否需要搜索的提示
        prompt = f"""
        用户问题：{content}

        请根据以下规则判断是否需要联网搜索：
        1. 如果问题简单、常见或无需额外信息即可回答，请回答 '否'。
        2. 如果问题复杂、需要最新信息或需要具体数据支持，请回答 '是'。

        请回答 '是' 或 '否'。
        """
        need_search_response = call_api([{"role": "user", "content": prompt}])

        # 解析大模型的回答
        if "否" in need_search_response:
            # 不需要搜索，直接生成回答
            final_response = call_api(messages)
            if update.message.chat.type == "private":
                save_private_message(user_id, username, "assistant", final_response)
            else:
                save_group_message(chat_id, user_id, username, "assistant", final_response)
            await update.message.reply_text(final_response)
            return
    except Exception as e:
        logger.error(f"调用大模型 API 时发生错误: {e}")
        await update.message.reply_text('请求失败，请稍后再试。')
        return

    # 第二步：需要搜索，执行搜索逻辑
    try:
        # 调用自定义的searxng搜索服务获取相关内容
        query_url = f"http://198.135.50.173:56880/search?q={requests.utils.quote(content)}&format=json"
        search_result = requests.get(query_url).json()
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
            prompt = f"用户问题：{content}\n\n相关页面内容：{combined_content}"
            messages.append({"role": "user", "content": prompt})

            # 调用大模型生成最终回答
            final_response = call_api(messages)
            if update.message.chat.type == "private":
                save_private_message(user_id, username, "assistant", final_response)
            else:
                save_group_message(chat_id, user_id, username, "assistant", final_response)
            # 分段发送长消息
            max_length = 4096
            for i in range(0, len(final_response), max_length):
                chunk = final_response[i:i + max_length]
                await update.message.reply_text(chunk)
        else:
            await update.message.reply_text("未找到相关结果。")
    except Exception as e:
        logger.error(f"调用大模型 API 或搜索引擎时发生错误: {e}")
        await update.message.reply_text('请求失败，请稍后再试。')
