from telegram import Update
from telegram.ext import CallbackContext
from database import save_group_message, save_private_message, load_private_messages, init_db
from api_client import call_api  # 使用统一的 API 调用函数
from crawler import get_top_10_links, fetch_page_content
import logging
import requests
from config import ENABLE_SEARCH  # 导入开关配置
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 从环境变量获取搜索服务的 URL
QUERY_URL = os.getenv('QUERY_URL')

# 配置日志
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    """处理 /start 命令"""
    await update.message.reply_text('Hi, I‘m Big Dog。 你好，我是大狗。')

async def enable_search_command(update: Update, context: CallbackContext) -> None:
    """启用搜索功能"""
    global ENABLE_SEARCH
    ENABLE_SEARCH = True
    await update.message.reply_text("搜索功能已启用。")

async def disable_search_command(update: Update, context: CallbackContext) -> None:
    """禁用搜索功能"""
    global ENABLE_SEARCH
    ENABLE_SEARCH = False
    await update.message.reply_text("搜索功能已禁用。")

async def handle_message(update: Update, context: CallbackContext) -> None:
    """处理用户消息"""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    content = update.message.text

    # 如果用户输入为空，直接返回
    if not content:
        await update.message.reply_text("请输入有效的内容。")
        return

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

    # 如果启用搜索功能，执行搜索逻辑
    if ENABLE_SEARCH:
        # 提示用户正在查询
        await update.message.reply_text("等下，我去查查...")
        # 从环境变量获取查询 URL 并格式化
        query_url = QUERY_URL.format(requests.utils.quote(content))
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
            prompt = f"根据以下信息回答问题：{combined_content}\n\n问题：{content}"
            messages.append({"role": "user", "content": prompt})

    # 调用大模型 API 并处理响应
    try:
        # 直接要求用中文回答
        messages.insert(0, {"role": "user", "content": "请用中文直接回答以下问题，不要输出思考过程。"})
        
        # 过滤掉 content 为 None 或空字符串的消息
        messages = [msg for msg in messages if msg.get("content")]
        
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

