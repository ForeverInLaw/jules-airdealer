import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
# from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application # For webhook
# from aiohttp import web # For webhook

# Import configurations
try:
    from config import BOT_TOKEN, DEBUG, WEBHOOK_URL, SUPABASE_URL # Check if SUPABASE_URL is needed here directly
except ImportError:
    print("CRITICAL: config.py not found or essential variables are missing.")
    sys.exit(1)

# Import middlewares
from middlewares.localization import LocalizationMiddleware
from middlewares.database import DatabaseMiddleware

# Import routers from handlers
from handlers import start, catalog, cart, orders, settings # __init__.py in handlers should make these importable

# Import Supabase client instance to check availability (optional, for early exit)
try:
    from database.supabase_client import supabase_client
    if not supabase_client and SUPABASE_URL: # Only critical if SUPABASE_URL was set (meaning DB is intended)
        print("CRITICAL: Supabase client failed to initialize. Check SUPABASE_URL, SUPABASE_KEY, and database connectivity.")
        # sys.exit(1) # Decide if bot should run without DB, depends on functionality
except ImportError:
    if SUPABASE_URL: # If Supabase is configured but client can't be imported
        print("CRITICAL: Supabase client module not found, but SUPABASE_URL is set.")
        # sys.exit(1)
    supabase_client = None # Ensure it's defined for checks

# Configure logging
logging.basicConfig(level=logging.INFO if not DEBUG else logging.DEBUG,
                    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    if not BOT_TOKEN:
        logger.critical("BOT_TOKEN is not configured in .env file. Bot cannot start.")
        return

    if not SUPABASE_URL and not supabase_client:
        logger.warning("SUPABASE_URL is not configured. Database features will be unavailable.")
    elif SUPABASE_URL and not supabase_client:
        logger.error("SUPABASE_URL is configured, but Supabase client failed to initialize. Check credentials and connectivity.")
        # Depending on how critical DB is, you might exit:
        # return

    # Initialize Bot instance with default parse mode which will be passed to all API calls
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)

    # Initialize Dispatcher
    dp = Dispatcher()

    # Register middlewares
    # Order matters: DatabaseMiddleware might be needed by LocalizationMiddleware if it stores lang pref there
    # However, our LocalizationMiddleware fetches user from DB itself.
    # So, DatabaseMiddleware providing client to data, then LocalizationMiddleware using it, is one way.
    # Or LocalizationMiddleware imports global supabase_client.
    # Current setup: both import global supabase_client.
    # Let's ensure they are registered.
    dp.update.middleware(DatabaseMiddleware()) # To pass supabase_client via data if needed by handlers
    dp.update.middleware(LocalizationMiddleware()) # To pass language_code via data

    # Register routers
    logger.info("Registering routers...")
    dp.include_router(start.router)
    logger.info("Included start router.")
    dp.include_router(catalog.router)
    logger.info("Included catalog router.")
    dp.include_router(cart.router)
    logger.info("Included cart router.")
    dp.include_router(orders.router)
    logger.info("Included orders router.")
    dp.include_router(settings.router)
    logger.info("Included settings router.")
    logger.info("All routers registered.")

    # Decide polling or webhook based on WEBHOOK_URL in config
    if WEBHOOK_URL:
        logger.info(f"Starting bot in webhook mode. URL: {WEBHOOK_URL}")
        # # The webhook setup from the document:
        # # Make sure to create webhook.py as in the document if using this.
        # # For now, this part is commented out as webhook.py is not yet in the plan.
        # # It would require aiohttp and modifications to this main() or a separate webhook.py script.
        # await bot.set_webhook(f"{WEBHOOK_URL}/webhook") # Path as defined in webhook.py
        # # Create aiohttp.web.Application instance
        # app = web.Application()
        # # Create an instance of request handler
        # webhook_requests_handler = SimpleRequestHandler(
        #     dispatcher=dp,
        #     bot=bot,
        # )
        # # Register webhook handler on application
        # webhook_requests_handler.register(app, path="/webhook") # Path as defined
        # # Mount dispatcher startup and shutdown hooks to aiohttp application
        # setup_application(app, dp, bot=bot)
        # # And finally start webserver
        # web.run_app(app, host="0.0.0.0", port=8000) # Or other host/port
        logger.warning("Webhook mode is configured but not fully implemented in main.py yet. Please use webhook.py or implement here.")
        logger.info("Falling back to polling mode for now as webhook logic is commented out.")
        await bot.delete_webhook(drop_pending_updates=True) # Ensure polling mode if webhook is not fully set up
        await dp.start_polling(bot)


    else:
        logger.info("Starting bot in polling mode.")
        # Remove any existing webhook to ensure polling works
        await bot.delete_webhook(drop_pending_updates=True)
        # Start polling
        await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}", exc_info=True)
    finally:
        logger.info("Bot shutdown.")
