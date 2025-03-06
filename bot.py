import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import start, handle_message
from config import TELEGRAM_BOT_TOKEN
from database import init_db
# 配置日志
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
async def main() -> None:
    # 初始化数据库
    init_db()
    logger.info("数据库初始化完成！")
    # 创建 Application 实例
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    # 添加命令处理器
    application.add_handler(CommandHandler("start", start))
    # 添加消息处理器
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # 启动 Bot
    await application.run_polling()
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
