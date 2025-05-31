from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Optional

# Assuming get_text is available for localizing button labels.
# This creates a dependency on utils.localization.
# If get_text is async, these keyboard functions might need to be async as well,
# or text needs to be pre-fetched. The document's examples for handlers
# call get_text for button text before creating keyboards, which is a good pattern.
# For simplicity here, we'll assume button texts are passed in or use non-localized keys
# that get_text in handlers will resolve.

# For get_language_keyboard, the text is hardcoded in the handler, so no get_text needed here.
def get_language_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton(text="🇵🇱 Polski", callback_data="lang_pl")
    )
    return builder.as_markup()

# For get_main_menu_keyboard, texts should be fetched using get_text in the handler
# and then passed to this function, or this function needs to be async and call get_text.
# The provided example handler (start.py) calls get_main_menu_keyboard(user["language_code"]),
# implying this function might need to fetch texts itself or receive them.
# Let's assume texts are passed for now, or use keys that will be localized later.
# The document shows `get_main_menu_keyboard(user["language_code"])` being called, and the
# handler fetches `welcome_text` using `get_text`. It doesn't explicitly show passing all
# button texts.
# Let's define it to take pre-fetched texts for buttons for clarity and testability.

async def get_main_menu_keyboard(
    language_code: str, # To potentially fetch texts if not passed
    button_texts: Optional[dict] = None # Pre-fetched texts
) -> InlineKeyboardMarkup:
    from utils.localization import get_text # Local import

    # If button_texts are not provided, fetch them.
    # This makes the keyboard function async.
    if button_texts is None:
        button_texts = {
            "catalog": await get_text("catalog_button", language_code),
            "cart": await get_text("cart_button", language_code, default="🛒 Cart ({count})").format(count=0), # Placeholder count
            "orders": await get_text("orders_button", language_code),
            "settings": await get_text("settings_button", language_code),
            "help": await get_text("help_button", language_code),
        }

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=button_texts["catalog"], callback_data="catalog"))
    builder.row(InlineKeyboardButton(text=button_texts["cart"], callback_data="view_cart")) # Assuming 'view_cart' callback
    builder.row(InlineKeyboardButton(text=button_texts["orders"], callback_data="my_orders"))
    builder.row(
        InlineKeyboardButton(text=button_texts["settings"], callback_data="settings"),
        InlineKeyboardButton(text=button_texts["help"], callback_data="help")
    )
    return builder.as_markup()

# Placeholder for get_categories_keyboard from catalog.py example
# This will also need to be async if it fetches category names or text from DB/localization
async def get_categories_keyboard(
    categories: List[dict], # Expects list of dicts with 'id' and 'name' (or localized name)
    language_code: str
    # button_texts: Optional[dict] = None # For back button, etc.
) -> InlineKeyboardMarkup:
    from utils.localization import get_text # Local import
    builder = InlineKeyboardBuilder()
    for category in categories:
        # Assuming category dict has 'id' and a 'name' field that is already localized or is a key
        # If category['name'] is a key, it should be: await get_text(category['name'], language_code)
        builder.row(InlineKeyboardButton(text=str(category.get('name', 'Unnamed Category')), callback_data=f"category_{category['id']}_0")) # page 0

    # Add a back button to main menu or previous menu
    back_button_text = await get_text("back_button", language_code, default="⬅️ Back")
    # Example: back to main menu; might need specific callback like "main_menu"
    builder.row(InlineKeyboardButton(text=back_button_text, callback_data="main_menu"))
    return builder.as_markup()


# Placeholder for get_products_keyboard from catalog.py example
async def get_products_keyboard(
    products: List[dict], # List of product dicts
    category_id: int,
    current_page: int,
    total_items: int,
    language_code: str,
    items_per_page: int = 5
) -> InlineKeyboardMarkup:
    from utils.localization import get_text # Local import
    builder = InlineKeyboardBuilder()

    for product in products:
        # product_localization.name should be used as per Supabase query
        display_name = product.get('name', 'Unnamed Product')
        if product.get('product_localization') and product['product_localization'].get('name'):
            display_name = product['product_localization']['name']
        builder.row(InlineKeyboardButton(text=display_name, callback_data=f"product_{product['id']}"))

    # Pagination
    total_pages = (total_items + items_per_page - 1) // items_per_page
    if total_pages > 1:
        pagination_buttons = []
        if current_page > 0:
            prev_text = await get_text("prev_page_button", language_code, default="⬅️ Prev")
            pagination_buttons.append(
                InlineKeyboardButton(text=prev_text, callback_data=f"category_{category_id}_{current_page - 1}")
            )
        if current_page < total_pages - 1:
            next_text = await get_text("next_page_button", language_code, default="➡️ Next")
            pagination_buttons.append(
                InlineKeyboardButton(text=next_text, callback_data=f"category_{category_id}_{current_page + 1}")
            )
        if pagination_buttons:
            builder.row(*pagination_buttons)

    back_button_text = await get_text("back_button", language_code, default="⬅️ Back")
    # Example: back to categories list; might need specific callback like "catalog" or "categories_menu"
    builder.row(InlineKeyboardButton(text=back_button_text, callback_data="catalog")) # Or specific "show_categories"
    return builder.as_markup()

# Placeholder for get_product_keyboard from catalog.py example
async def get_product_keyboard(
    product_id: int,
    stock_info: list, # To potentially offer choice of location for adding to cart
    language_code: str
) -> InlineKeyboardMarkup:
    from utils.localization import get_text # Local import
    builder = InlineKeyboardBuilder()

    # Add to cart button - might need to select location if multiple stock locations
    # For simplicity, let's assume a general add to cart. Specific location selection could be another step.
    add_to_cart_text = await get_text("add_to_cart_button", language_code, default="➕ Add to Cart")
    builder.row(InlineKeyboardButton(text=add_to_cart_text, callback_data=f"addtocart_{product_id}")) # Needs location?

    # If multiple locations, you might list them or ask user to choose one before adding to cart.
    # Example: if stock_info has multiple locations with quantity > 0
    # for stock_item in stock_info:
    #    if stock_item.get('quantity', 0) > 0:
    #        loc_name = stock_item.get('locations', {}).get('name', 'Unknown Location')
    #        loc_id = stock_item.get('locations', {}).get('id')
    #        add_to_cart_loc_text = await get_text("add_to_cart_location_button", language_code, default="Add from {location_name}")
    #        builder.row(InlineKeyboardButton(
    #            text=add_to_cart_loc_text.format(location_name=loc_name),
    #            callback_data=f"addtocart_{product_id}_{loc_id}"
    #        ))

    back_button_text = await get_text("back_button", language_code, default="⬅️ Back")
    # Example: back to product list of its category. This requires category_id.
    # This information (like category_id) might need to be passed to this function or be part of product_details.
    # For now, a generic "back_to_catalog" or rely on state/previous message context.
    builder.row(InlineKeyboardButton(text=back_button_text, callback_data="catalog")) # Needs to know where to go back
    return builder.as_markup()
