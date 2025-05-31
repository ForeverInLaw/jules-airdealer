from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message # Added Message for potential text command triggers
from aiogram.fsm.context import FSMContext # For potential future use with states

try:
    from database.supabase_client import supabase_client
except ImportError:
    print("CRITICAL: Supabase client could not be imported in handlers.catalog.")
    supabase_client = None

from keyboards.inline import (
    get_categories_keyboard,
    get_products_keyboard,
    get_product_keyboard,
    get_main_menu_keyboard # For a potential back to main menu from catalog top
)
from utils.localization import get_text
from utils.helpers import paginate_items, format_product_details # format_price is used within format_product_details

router = Router()
# Assuming middlewares (Localization, Database) are applied at the dispatcher level.

ITEMS_PER_PAGE = 5 # Define items per page for pagination, can be moved to config.py

@router.callback_query(F.data == "catalog")
async def show_catalog_menu_callback_handler(callback: CallbackQuery, language: str, state: FSMContext):
    """
    Handles the 'catalog' callback (e.g., from main menu).
    Displays the catalog menu, typically options to browse by categories, manufacturers, or search.
    The document example shows direct navigation to categories.
    """
    if not supabase_client:
        await callback.message.answer(await get_text("error_db_connection", language, "DB error."))
        await callback.answer()
        return

    try:
        # The document's catalog structure:
        # 🛍️ Каталог товаров
        # │   ├── 📂 По категориям
        # │   ├── 🏭 По производителям
        # │   └── 🔍 Поиск
        # For now, let's implement "По категориям" as the primary way, following the example.
        # We'll fetch and display categories.

        # Fetch categories from Supabase
        # The example in SupabaseClient uses an RPC "get_categories_with_product_count"
        # Let's assume this RPC exists and returns categories with a 'name' field (localized or key) and 'id'.
        categories = await supabase_client.get_categories_with_count(language) # Pass language for RPC

        if not categories:
            no_categories_text = await get_text("no_categories_found", language, "No categories available at the moment.")
            await callback.message.edit_text(no_categories_text) # Or send as new if edit is complex
            await callback.answer()
            return

        catalog_intro_text = await get_text("catalog_menu", language) # "🛍️ Product Catalog
Choose how you'd like to browse:"
                                                                 # This text might be for a menu before listing categories.
                                                                 # If directly showing categories, a text like "choose_category" might be better.

        # For now, using "catalog_menu" as intro then showing categories keyboard
        # A more structured approach might have a catalog menu keyboard first.
        # Example: "catalog_menu" text with buttons "By Category", "By Manufacturer", "Search"
        # Then "categories_list_prompt" text before the actual categories keyboard.

        categories_list_prompt = await get_text("categories_list_prompt", language, "Please select a category:")
        text_to_send = f"{catalog_intro_text}\n\n{categories_list_prompt}"

        # The get_categories_keyboard in keyboards/inline.py expects a list of dicts with 'id' and 'name'
        # Ensure the RPC call or direct query returns this structure.
        # Example category dict: {'id': 1, 'name': 'Electronics'} (name already localized or a key)
        categories_kb = await get_categories_keyboard(categories, language)

        await callback.message.edit_text(text_to_send, reply_markup=categories_kb)
        await callback.answer()

    except Exception as e:
        print(f"Error in show_catalog_menu_callback_handler: {e}")
        error_msg = await get_text("error_generic", language, "Error displaying catalog.")
        await callback.message.answer(error_msg) # Send as new message
        await callback.answer()


@router.callback_query(F.data.startswith("category_"))
async def show_category_products_callback_handler(callback: CallbackQuery, language: str, state: FSMContext):
    """
    Handles callbacks like "category_<category_id>_<page>".
    Displays paginated products for the selected category.
    """
    if not supabase_client:
        await callback.message.answer(await get_text("error_db_connection", language, "DB error."))
        await callback.answer()
        return

    try:
        parts = callback.data.split("_")
        category_id = int(parts[1])
        page = int(parts[2]) if len(parts) > 2 else 0

        # Fetch products for the category
        # get_products_by_category(category_id, language) is defined in SupabaseClient
        all_products = await supabase_client.get_products_by_category(category_id, language)

        if not all_products:
            no_products_text = await get_text("no_products_in_category", language)
            # It's better to edit the message to inform no products, rather than just an alert.
            # Let's provide a keyboard to go back.
            back_to_catalog_kb = await get_categories_keyboard([], language) # Empty categories, just shows back button
            await callback.message.edit_text(no_products_text, reply_markup=back_to_catalog_kb)
            await callback.answer()
            return

        # Paginate products
        paginated_products = paginate_items(all_products, page, ITEMS_PER_PAGE)

        if not paginated_products and page > 0: # page > 0 means they tried to go to a non-existent page
            page_error_text = await get_text("error_invalid_page", language, "Invalid page number.")
            await callback.answer(page_error_text, show_alert=True)
            return
        # This case should be covered by `if not all_products` or `if not paginated_products and page > 0`
        # elif not paginated_products and page == 0:
        #      no_products_text = await get_text("no_products_in_category", language)
        #      await callback.answer(no_products_text, show_alert=True)
        #      return


        # Category name might be useful to display.
        # For this, we might need to fetch category details or pass category name.
        # Assuming for now the context is clear or products themselves show category.
        # For a better UX, the title could be "Products in [Category Name]"
        # This would require fetching category details:
        # category_details = await supabase_client.get_category_details(category_id, language) # (method needs to be created)
        # category_name = category_details.get('name', '') if category_details else ''
        # products_list_title = await get_text("products_in_category_titled", language, "Products in {category_name}:")
        # text = products_list_title.format(category_name=category_name)

        text = await get_text("products_in_category", language) # "Products in this category:"

        products_kb = await get_products_keyboard(
            products=paginated_products,
            category_id=category_id,
            current_page=page,
            total_items=len(all_products),
            language_code=language,
            items_per_page=ITEMS_PER_PAGE
        )

        # Using edit_text, assuming the previous message was the category list or catalog menu.
        await callback.message.edit_text(text, reply_markup=products_kb)
        await callback.answer()

    except Exception as e:
        print(f"Error in show_category_products_callback_handler: {e}")
        error_msg = await get_text("error_generic", language, "Error displaying products.")
        # await callback.message.answer(error_msg) # Avoid replacing if possible
        await callback.answer(error_msg, show_alert=True)


@router.callback_query(F.data.startswith("product_"))
async def show_product_details_callback_handler(callback: CallbackQuery, language: str, state: FSMContext):
    """
    Handles callbacks like "product_<product_id>".
    Displays detailed information about the selected product.
    """
    if not supabase_client:
        await callback.message.answer(await get_text("error_db_connection", language, "DB error."))
        await callback.answer()
        return

    try:
        product_id = int(callback.data.split("_")[1])

        # Fetch product details
        # get_product_details(product_id, language) defined in SupabaseClient
        product = await supabase_client.get_product_details(product_id, language)

        if not product:
            not_found_text = await get_text("product_not_found", language, "Product not found.")
            await callback.answer(not_found_text, show_alert=True)
            return

        # Fetch stock information
        # get_product_stock_all_locations(product_id) defined in SupabaseClient
        stock_info = await supabase_client.get_product_stock_all_locations(product_id)

        # Format product details using helper
        # format_product_details(product, stock_info, language) is an async helper
        formatted_text = await format_product_details(product, stock_info, language)

        # The get_product_keyboard needs category_id for the back button to work correctly.
        # Product details from Supabase should ideally include category_id.
        # Assuming product dict contains 'categories': {'id': category_id, 'name': 'Category Name'}
        # or a direct 'category_id' field.
        # Let's assume product['categories']['id'] or product['category_id'] is available.
        # The current get_product_keyboard in inline.py has a generic "catalog" back button.
        # To make it go back to the specific category product list, it needs category_id.
        # For now, this detail is omitted as per current keyboard structure, but important for UX.
        # Example: product_kb = await get_product_keyboard(product_id, product.get('category_id'), stock_info, language)

        product_kb = await get_product_keyboard(product_id, stock_info, language)

        image_url = product.get("image_url")

        if image_url:
            # If current message has a photo, edit media. Otherwise, delete and send new, or send new directly.
            if callback.message.photo:
                 media = InputMediaPhoto(media=image_url, caption=formatted_text)
                 await callback.message.edit_media(media, reply_markup=product_kb)
            else:
                # If previous message was text (e.g. product list), delete it and send a new photo message.
                # This is a common pattern.
                try:
                    await callback.message.delete()
                except Exception as e_del:
                    print(f"Could not delete previous message: {e_del}") # Log and continue

                await callback.message.answer_photo(
                    photo=image_url,
                    caption=formatted_text,
                    reply_markup=product_kb
                )
        else:
            # No image, just edit the text
            await callback.message.edit_text(formatted_text, reply_markup=product_kb)

        await callback.answer()

    except Exception as e:
        print(f"Error in show_product_details_callback_handler: {e}")
        error_msg = await get_text("error_generic", language, "Error displaying product details.")
        # await callback.message.answer(error_msg)
        await callback.answer(error_msg, show_alert=True)

# TODO:
# - Handlers for "By Manufacturers" and "Search" if those are top-level catalog options.
# - If "catalog_menu" text implies a keyboard with [Categories, Manufacturers, Search],
#   then "catalog" callback should show that keyboard first.
#   Then, a new callback like "show_categories" would call the categories listing logic.
#   The current implementation directly lists categories under "catalog" callback.
#   This matches the `handlers/catalog.py` example's directness for `show_catalog`.
# - Refine back button logic in get_product_keyboard to return to the correct category page.
#   This means product_details should probably include category_id, and this should be passed
#   to get_product_keyboard, which then constructs a callback like `category_<cat_id>_<last_page_of_product>`.
#   This is a more advanced state/context management.
#   For now, `get_product_keyboard` has a generic "back to catalog (categories list)" button.

```
