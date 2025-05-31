import asyncio
import logging
import sys # Import sys for sys.exit

from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Import Bot, Dispatcher, and configurations
try:
    from config import BOT_TOKEN, WEBHOOK_URL, DEBUG, SUPABASE_URL # Added SUPABASE_URL
    # Assuming main.py initializes bot and dp, or we do it here.
    # The document example for webhook.py implies bot and dp are imported from main.
    # This can create a circular dependency if main.py also tries to run webhook logic.
    # A cleaner way is for webhook.py to be the main entry point if webhook mode is chosen,
    # or for main.py to call a setup function from webhook.py.

    # For this implementation, let's assume main.py is the primary entry point for polling,
    # and webhook.py is an alternative entry point if webhooks are used.
    # Thus, webhook.py will need to initialize its own Bot and Dispatcher,
    # and register all handlers and middlewares, similar to main.py.

    from aiogram import Bot, Dispatcher
    from aiogram.enums import ParseMode

    # Import middlewares
    from middlewares.localization import LocalizationMiddleware
    from middlewares.database import DatabaseMiddleware

    # Import routers
    from handlers import start, catalog, cart, orders, settings

    # Import Supabase client for checks (optional here, but good for consistency)
    from database.supabase_client import supabase_client # Removed SUPABASE_URL from here as it's in config

except ImportError as e:
    print(f"CRITICAL: Error importing necessary modules in webhook.py: {e}. "
          "Ensure config.py and all handlers/middlewares are correctly placed and importable.")
    sys.exit(1)


logger = logging.getLogger(__name__)

# This path should match the one used in `bot.set_webhook` and registered in `app`.
WEBHOOK_PATH = "/webhook" # Example, can be made configurable

async def on_startup(bot: Bot, webhook_base_url: str):
    """Sets the webhook when the application starts."""
    webhook_full_url = f"{webhook_base_url.rstrip('/')}{WEBHOOK_PATH}"
    try:
        await bot.set_webhook(webhook_full_url)
        logger.info(f"Webhook set successfully to: {webhook_full_url}")
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        # Depending on severity, you might want to exit or raise
        raise

async def on_shutdown(bot: Bot):
    """Removes the webhook when the application shuts down."""
    try:
        await bot.delete_webhook()
        logger.info("Webhook deleted successfully.")
    except Exception as e:
        logger.error(f"Failed to delete webhook: {e}")


def setup_bot_and_dispatcher():
    if not BOT_TOKEN:
        logger.critical("BOT_TOKEN is not configured. Webhook cannot start.")
        sys.exit(1) # Or raise an exception

    if not SUPABASE_URL and not supabase_client:
        logger.warning("SUPABASE_URL is not configured. Database features will be unavailable.")
    elif SUPABASE_URL and not supabase_client:
        logger.error("SUPABASE_URL is configured, but Supabase client failed to initialize.")
        # sys.exit(1) # Decide if critical

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()

    # Register middlewares
    dp.update.middleware(DatabaseMiddleware())
    dp.update.middleware(LocalizationMiddleware())

    # Register routers
    dp.include_router(start.router)
    dp.include_router(catalog.router)
    dp.include_router(cart.router)
    dp.include_router(orders.router)
    dp.include_router(settings.router)

    logger.info("Bot and Dispatcher initialized for webhook.")
    return bot, dp


def run_webhook_server():
    """
    Initializes and runs the aiohttp web server for the webhook.
    This function is intended to be called if webhook mode is active.
    """
    if not WEBHOOK_URL:
        logger.info("WEBHOOK_URL not set. Webhook server will not start. Use polling (main.py).")
        return

    logging.basicConfig(level=logging.INFO if not DEBUG else logging.DEBUG,
                        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    bot, dp = setup_bot_and_dispatcher()

    app = web.Application()

    # Register startup and shutdown actions
    app.on_startup.append(lambda _: on_startup(bot, WEBHOOK_URL))
    app.on_shutdown.append(lambda _: on_shutdown(bot))

    # Create SimpleRequestHandler instance
    webhook_request_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    # Register webhook handler on application
    webhook_request_handler.register(app, path=WEBHOOK_PATH)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    # setup_application will run dp.emit_startup() and dp.emit_shutdown()
    setup_application(app, dp, bot=bot)

    # Get host and port from WEBHOOK_URL or use defaults
    # Example: WEBHOOK_URL = "https://your-domain.com" implies port 443 (HTTPS)
    # For local testing, WEBHOOK_URL might be "http://localhost:8080"
    # aiohttp's run_app typically uses host '0.0.0.0' and a specified port.
    # The port needs to be consistent with what Telegram sends requests to.
    # If WEBHOOK_URL is "https://your-domain.com/somepath", the actual listening port
    # is determined by your reverse proxy (e.g., nginx) forwarding to this app's port.
    # For simplicity, let's assume a common local setup or that the environment handles port mapping.
    # The document example uses port 8000.

    host = "0.0.0.0"
    port = 8000 # Default port, make configurable if needed e.g. from .env

    logger.info(f"Starting aiohttp server for webhook on {host}:{port}{WEBHOOK_PATH}")
    web.run_app(app, host=host, port=port)


if __name__ == "__main__":
    # This allows running webhook.py directly if desired.
    # Ensure that main.py's polling logic is not started if webhook.py is the entry point.
    # Typically, you'd have one entry point that decides mode, or run one script explicitly.
    logger.info("Attempting to start webhook server directly from webhook.py...")
    run_webhook_server()
