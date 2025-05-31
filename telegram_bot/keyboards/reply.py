from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

# This file is for reply keyboards (buttons appearing below the text input field).
# The document doesn't show explicit use of reply keyboards in the examples,
# but they can be useful for persistent actions.

# Example: A main menu reply keyboard (less common if inline is preferred for navigation)
async def get_main_reply_keyboard(language_code: str) -> ReplyKeyboardMarkup:
    from utils.localization import get_text # Local import

    # Texts should be fetched using get_text, similar to inline keyboards
    catalog_text = await get_text("catalog_button", language_code, "🛍️ Catalog")
    cart_text = await get_text("cart_button", language_code, "🛒 Cart").format(count=0) # Example
    orders_text = await get_text("orders_button", language_code, "📋 My Orders")

    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=catalog_text))
    builder.row(KeyboardButton(text=cart_text), KeyboardButton(text=orders_text))

    return builder.as_markup(resize_keyboard=True)

# Add other reply keyboard generators here if needed.
# For example, a keyboard to request user's phone number or location for order processing.
