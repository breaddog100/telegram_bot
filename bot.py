import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers import start, handle_message
from config import TELEGRAM_BOT_TOKEN
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
async def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await application.run_polling()
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
