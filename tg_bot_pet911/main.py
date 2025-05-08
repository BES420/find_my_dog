import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage

from tg_bot_pet911.config.config import BOT_TOKEN, REDIS_DSN
from tg_bot_pet911.bot.handlers import start, gender, photo, location, comment, confirm, cancel
from tg_bot_pet911.tests.test_all_handlers import router as test_router


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Get logger
logger = logging.getLogger(__name__)


async def main():
    """Main function to start the bot."""
    logger.info("Starting bot...")
    
    # Check if we have a token
    if not BOT_TOKEN:
        logger.error("No token provided. Set the BOT_TOKEN environment variable.")
        return
    
    # Create bot and dispatcher instances
    bot = Bot(token=BOT_TOKEN)
    
    # Use MemoryStorage by default, only try Redis if specifically requested
    USE_REDIS = False  # Set to True to use Redis
    
    if USE_REDIS and REDIS_DSN:
        try:
            # Try to use Redis storage
            storage = RedisStorage.from_url(REDIS_DSN)
            logger.info("Using Redis storage for FSM.")
        except Exception as e:
            # Fallback to memory storage if Redis is not available
            logger.warning(f"Redis connection failed ({e}), using in-memory storage.")
            storage = MemoryStorage()
    else:
        # Use memory storage
        storage = MemoryStorage()
        logger.info("Using in-memory storage for FSM.")
    
    dp = Dispatcher(storage=storage)
    
    # Register the cancel handler first to make it available globally
    dp.include_router(cancel.router)
    
    # Register other routers
    dp.include_router(start.router)
    dp.include_router(gender.router)
    dp.include_router(photo.router)
    dp.include_router(location.router)
    dp.include_router(comment.router)
    dp.include_router(confirm.router)
    
    # Register test router
    dp.include_router(test_router)
    
    # Start polling
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started successfully!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main()) 