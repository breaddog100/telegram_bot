from telegram import Update
from telegram.ext import CallbackContext
from database import save_group_message, save_private_message, load_private_messages, init_db
from api_client import call_api  # 使用统一的 API 调用函数
import logging
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
    # 调用大模型 API 并处理响应
    try:
        response = call_api(messages)  # 使用统一的 API 调用函数
        if update.message.chat.type == "private":
            save_private_message(user_id, username, "assistant", response)
        else:
            save_group_message(chat_id, user_id, username, "assistant", response)
        # 分段发送长消息
        max_length = 4096
        for i in range(0, len(response), max_length):
            chunk = response[i:i + max_length]
            await update.message.reply_text(chunk)
    except Exception as e:
        logger.error(f"调用大模型 API 时发生错误: {e}")
        await update.message.reply_text('请求失败，请稍后再试。')
