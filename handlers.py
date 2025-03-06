from telegram import Update
from telegram.ext import CallbackContext
from database import save_group_message, save_private_message, load_private_messages
from api_client import call_deepseek_api

async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Hi, I‘m Big Dog。 你好，我是大狗。')
async def handle_message(update: Update, context: CallbackContext) -> None:
    init_db()
    
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    content = update.message.text
    
    if update.message.chat.type == "private":
        save_private_message(user_id, username, "user", content)
        MAX_HISTORY_ROUNDS = 5
        messages = load_private_messages(user_id, MAX_HISTORY_ROUNDS)
        messages.append({"role": "user", "content": content})
    else:
        save_group_message(chat_id, user_id, username, "user", content)
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
            return
    
    try:
        response = call_deepseek_api(messages)
        if update.message.chat.type == "private":
            save_private_message(user_id, username, "assistant", response)
        else:
            save_group_message(chat_id, user_id, username, "assistant", response)
        max_length = 4096
        for i in range(0, len(response), max_length):
            chunk = response[i:i + max_length]
            await update.message.reply_text(chunk)
    except Exception as e:
        logger.error(f"调用Deepseek API时发生错误: {e}")
        await update.message.reply_text('请求失败，请稍后再试。')
