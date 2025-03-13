import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN
from database import init_db
import asyncio

# 关键修复点：确保正确导入
from handlers import start, handle_message

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main() -> None:
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
        await asyncio.sleep(3600)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用户中断。")
    except Exception as e:
        logger.error(f"程序发生异常: {e}", exc_info=True)
    finally:
        logger.info("程序已停止。")
