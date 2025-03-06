import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import start, handle_message
from config import TELEGRAM_BOT_TOKEN
from database import init_db
import asyncio
# 配置日志
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为 INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
    handlers=[
        logging.FileHandler("bot.log"),  # 将日志输出到 bot.log 文件
        logging.StreamHandler()  # 同时将日志输出到控制台
    ]
)
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
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    # 保持程序运行
    while True:
        await asyncio.sleep(1)
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断。")
    except Exception as e:
        logger.error(f"程序发生异常: {e}", exc_info=True)
    finally:
        if 'application' in locals():
            loop.run_until_complete(application.stop())
        loop.close()
        logger.info("程序已停止。")
