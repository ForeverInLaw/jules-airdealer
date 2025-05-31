# Corrected content for telegram_bot/handlers/settings.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder # Added import

try:
    from database.supabase_client import supabase_client
except ImportError:
    supabase_client = None

from utils.localization import get_text
from keyboards.inline import get_language_keyboard

router = Router()

@router.callback_query(F.data == "settings")
async def settings_callback_handler(callback: CallbackQuery, language: str, state: FSMContext):
    if not supabase_client: # Though settings might not always need DB
        # await callback.message.answer(await get_text("error_db_connection", language, "DB error."))
        # await callback.answer()
        # return
        pass # Allow basic settings even if DB is down for some

    try:
        settings_text = await get_text("settings_menu_title", language, "⚙️ Settings")
        change_lang_text = await get_text("change_language_button", language, "🌐 Change Language")
        # Assuming "main_menu" callback is handled by start.py or a general handler
        back_to_main_text = await get_text("main_menu_button", language, "🏠 Main Menu")


        builder = InlineKeyboardBuilder()
        builder.row(InlineKeyboardButton(text=change_lang_text, callback_data="settings_change_language"))
        builder.row(InlineKeyboardButton(text=back_to_main_text, callback_data="main_menu"))


        await callback.message.edit_text(settings_text, reply_markup=builder.as_markup())
        await callback.answer()

    except Exception as e:
        print(f"Error in settings_callback_handler: {e}")
        error_msg = await get_text("error_generic", language, "Error displaying settings.")
        await callback.message.answer(error_msg) # Send as new message
        await callback.answer()

@router.callback_query(F.data == "settings_change_language")
async def settings_change_language_prompt_handler(callback: CallbackQuery, language: str, state: FSMContext):
    """Presents the language selection keyboard again."""
    try:
        prompt_text = await get_text("choose_language_prompt_settings", language,
                                     "Please select your new preferred language:")
        lang_keyboard = get_language_keyboard() # This is a synchronous function

        await callback.message.edit_text(prompt_text, reply_markup=lang_keyboard)
        await callback.answer()
    except Exception as e:
        print(f"Error in settings_change_language_prompt_handler: {e}")
        error_msg = await get_text("error_generic", language, "Error preparing language change.")
        # await callback.message.answer(error_msg) # Avoid if possible
        await callback.answer(error_msg, show_alert=True)

# Note: The actual language change logic would be handled by the "lang_<selected_lang>" callback query,
# which is already defined in handlers/start.py. After selecting a new language here,
# that existing handler will update the user's language in the DB and show the main menu.

# Placeholder for other settings functionalities:
# - Selecting default location/warehouse (settings_select_location -> shows locations -> saves to user profile)
# - Managing notification preferences
