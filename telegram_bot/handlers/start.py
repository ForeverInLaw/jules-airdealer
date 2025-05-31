from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext # For potential future use with states

# Assuming supabase_client is initialized in database.supabase_client
# and LocalizationMiddleware provides 'language' in data.
# DatabaseMiddleware might provide 'supabase_client' in data.
try:
    from database.supabase_client import supabase_client
except ImportError:
    # This handler heavily relies on supabase_client.
    # If it's not available, it should ideally not register or handle errors gracefully.
    print("CRITICAL: Supabase client could not be imported in handlers.start.")
    supabase_client = None

from keyboards.inline import get_language_keyboard, get_main_menu_keyboard
from utils.localization import get_text

router = Router()

# Apply middlewares if they are not applied globally in main.py
# Example: router.message.middleware(DatabaseMiddleware())
# router.message.middleware(LocalizationMiddleware())
# router.callback_query.middleware(DatabaseMiddleware())
# router.callback_query.middleware(LocalizationMiddleware())
# For now, assuming middlewares are registered at the Dispatcher level in main.py

@router.message(CommandStart())
async def start_command_handler(message: Message, state: FSMContext, language: str): # Added language from middleware
    """
    Handles the /start command.
    Checks if the user exists. If new, prompts for language. If existing, shows main menu.
    The 'language' parameter is expected to be injected by LocalizationMiddleware.
    """
    if not supabase_client:
        await message.answer("Error: Bot database connection is not configured. Please contact admin.")
        return

    user_telegram_id = message.from_user.id
    user_first_name = message.from_user.first_name

    try:
        user = await supabase_client.get_user(user_telegram_id)

        if not user:
            # New user - offer language choice
            # The text "🌐 Please choose your language / Выберите язык / Wybierz język:"
            # is multi-language itself, so it's hardcoded here as per the document.
            # Alternatively, one could fetch a key like "select_language_prompt" using the default 'en'
            # or try to guess from message.from_user.language_code (though this might not be reliable for initial setup)
            await message.answer(
                text="🌐 Please choose your language / Выберите язык / Wybierz język:",
                reply_markup=get_language_keyboard()
            )
        else:
            # Existing user
            # Use the language already set for the user (available via LocalizationMiddleware)
            user_lang = user.get("language_code", language) # Fallback to middleware language if DB is weird

            welcome_text = await get_text("welcome_back", user_lang)
            main_menu_keyboard = await get_main_menu_keyboard(user_lang) # Fetches texts internally

            await message.answer(
                text=welcome_text.format(name=user_first_name),
                reply_markup=main_menu_keyboard
            )
    except Exception as e:
        print(f"Error in /start command: {e}")
        # Generic error message, could be localized too
        error_msg = await get_text("error_generic", language, default="An unexpected error occurred. Please try again later.")
        await message.answer(error_msg)

@router.callback_query(F.data.startswith("lang_"))
async def set_language_callback_handler(callback: CallbackQuery, state: FSMContext, language: str): # Added language from middleware
    """
    Handles language selection from the inline keyboard.
    Creates or updates the user with the selected language.
    """
    if not supabase_client:
        await callback.message.answer("Error: Bot database connection is not configured. Please contact admin.")
        await callback.answer()
        return

    selected_language = callback.data.split("_")[1]
    user_telegram_id = callback.from_user.id
    user_first_name = callback.from_user.first_name

    try:
        user = await supabase_client.get_user(user_telegram_id)
        if not user:
            await supabase_client.create_user(user_telegram_id, selected_language)
        else:
            # User exists, update their language preference
            # Direct update using supabase_client.client as per document example
            await supabase_client.client.table("users").update({
                "language_code": selected_language
            }).eq("telegram_id", user_telegram_id).execute()

        # Update the language in the current context for immediate effect if needed by subsequent code
        # data['language'] = selected_language # If we could modify middleware data; not standard.
        # For now, rely on next request to get updated language via middleware.

        welcome_text_key = "welcome_new_user" # Or "language_selection_confirmed"
        welcome_text = await get_text(welcome_text_key, selected_language)
        main_menu_keyboard = await get_main_menu_keyboard(selected_language) # Pass selected_language

        # Edit the message that had the language buttons
        await callback.message.edit_text(
            text=welcome_text.format(name=user_first_name),
            reply_markup=main_menu_keyboard
        )
        await callback.answer() # Acknowledge the callback

    except Exception as e:
        print(f"Error in set_language_callback_handler: {e}")
        # Use the 'language' from middleware for this error message, as selected_language might not be set if error is early
        error_msg = await get_text("error_generic", language, default="An error occurred while setting language.")
        await callback.message.answer(error_msg) # Send as new message if edit fails or is complex
        await callback.answer(await get_text("error_generic_short", language, default="Error"), show_alert=True)
