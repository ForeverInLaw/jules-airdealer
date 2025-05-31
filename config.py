import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Admin settings
ADMIN_IDS_RAW = os.getenv("ADMIN_IDS")
ADMIN_IDS = [int(admin_id.strip()) for admin_id in ADMIN_IDS_RAW.split(',')] if ADMIN_IDS_RAW else []

# Optional
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
DEBUG_RAW = os.getenv("DEBUG", "False") # Default to "False" if not set
DEBUG = DEBUG_RAW.lower() in ('true', '1', 't')

# Basic validation (optional, but good practice)
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set.")
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is not set.")
if not SUPABASE_KEY:
    raise ValueError("SUPABASE_KEY environment variable is not set.")
# SUPABASE_SERVICE_KEY is not strictly required for all operations, so its check might be conditional
# if not SUPABASE_SERVICE_KEY:
#     raise ValueError("SUPABASE_SERVICE_KEY environment variable is not set.")

# You can add more sophisticated validation or logging here if needed
print("Configuration loaded.")
if DEBUG:
    print("DEBUG mode is ON.")
    print(f"BOT_TOKEN: {'*' * 5}{BOT_TOKEN[-5:] if BOT_TOKEN else 'Not Set'}") # Avoid logging the full token
    print(f"SUPABASE_URL: {SUPABASE_URL}")
    print(f"SUPABASE_KEY: {'*' * 5}{SUPABASE_KEY[-5:] if SUPABASE_KEY else 'Not Set'}")
    print(f"SUPABASE_SERVICE_KEY: {'*' * 5}{SUPABASE_SERVICE_KEY[-5:] if SUPABASE_SERVICE_KEY else 'Not Set'}")
    print(f"ADMIN_IDS: {ADMIN_IDS}")
    print(f"WEBHOOK_URL: {WEBHOOK_URL if WEBHOOK_URL else 'Not Set'}")
else:
    print("DEBUG mode is OFF.")
