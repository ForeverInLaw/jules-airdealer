from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

# Assuming supabase_client and language are available via middleware or context
try:
    from database.supabase_client import supabase_client
except ImportError:
    supabase_client = None

from utils.localization import get_text
# from keyboards.inline import get_cart_keyboard # Example, will need to be created

router = Router()

# TODO: Define ITEMS_PER_PAGE for cart pagination if needed, or get from config

# Example: Handler to view the cart
@router.callback_query(F.data == "view_cart")
async def view_cart_callback_handler(callback: CallbackQuery, language: str, state: FSMContext):
    if not supabase_client:
        await callback.message.answer(await get_text("error_db_connection", language, "DB error."))
        await callback.answer()
        return

    user_id = callback.from_user.id
    try:
        cart_items = await supabase_client.get_user_cart(user_id, language)

        if not cart_items:
            empty_cart_text = await get_text("cart_is_empty", language, "Your cart is currently empty.")
            # Consider providing a keyboard to go back to catalog or main menu
            # from keyboards.inline import get_main_menu_keyboard # Dynamically import if needed
            # main_menu_kb = await get_main_menu_keyboard(language) # Example
            await callback.message.edit_text(empty_cart_text) #, reply_markup=main_menu_kb)
            await callback.answer()
            return

        # Format cart items for display
        # This will require a helper function, e.g., format_cart_details(cart_items, language)
        # For now, a simple representation:
        cart_summary_lines = [f"Cart for {callback.from_user.full_name}:"]
        total_amount = 0.0

        for item in cart_items:
            product_name = item.get("products", {}).get("product_localization", {}).get("name", "Unknown Product")
            quantity = item.get("quantity", 0)
            price = float(item.get("products", {}).get("price", 0.0))
            item_total = quantity * price
            total_amount += item_total
            price_str = f"{price:.2f}" # Simplified, use format_price helper
            item_total_str = f"{item_total:.2f}" # Simplified
            cart_summary_lines.append(
                f"- {product_name} (x{quantity}) @ {price_str} each = {item_total_str}"
            )

        total_amount_str = f"{total_amount:.2f}" # Simplified
        cart_summary_lines.append(f"\nTotal: {total_amount_str}") # Add currency symbol

        # from keyboards.inline import get_cart_keyboard # Dynamically import if needed
        # cart_keyboard = await get_cart_keyboard(cart_items, language) # Keyboard for checkout, clear cart, modify items

        await callback.message.edit_text(
            text="\n".join(cart_summary_lines),
            # reply_markup=cart_keyboard
        )
        await callback.answer()

    except Exception as e:
        print(f"Error in view_cart_callback_handler: {e}")
        error_msg = await get_text("error_generic", language, "Error displaying cart.")
        await callback.message.answer(error_msg)
        await callback.answer()

# Example: Handler to add item to cart (called from product details)
@router.callback_query(F.data.startswith("addtocart_"))
async def add_to_cart_callback_handler(callback: CallbackQuery, language: str, state: FSMContext):
    if not supabase_client:
        await callback.message.answer(await get_text("error_db_connection", language, "DB error."))
        await callback.answer()
        return

    user_id = callback.from_user.id
    try:
        parts = callback.data.split("_")
        product_id = int(parts[1])
        # Location ID might be part of callback_data if multiple locations exist for a product
        # e.g., "addtocart_<product_id>_<location_id>"
        # For now, assume a default location or that location is handled elsewhere (e.g., user settings)

        # For this example, let's assume location_id=1 is a default or only location.
        # In a real scenario, user must have a selected location or choose one.
        # This needs to be determined based on the `user_cart` table structure `(user_id, product_id, location_id, quantity)`
        # The document implies location_id is necessary for user_cart.
        # Let's assume user has a default location or we need to ask.
        # For now, this will fail if location_id is not determined.
        # A placeholder:
        # user_settings = await supabase_client.get_user(user_id) # to get default location_id if stored there
        # location_id = user_settings.get("default_location_id")
        # if not location_id:
        #    await callback.answer(await get_text("error_no_location_selected", language, "Please select a location first."), show_alert=True)
        #    return

        # Hardcoding location_id for now, this needs proper implementation
        location_id = 1 # Placeholder - THIS IS A MAJOR GAP TO BE ADDRESSED
        quantity = 1 # Default quantity to add

        await supabase_client.add_to_cart(user_id, product_id, location_id, quantity)

        added_to_cart_text = await get_text("item_added_to_cart", language, "Item added to your cart!")
        await callback.answer(added_to_cart_text, show_alert=True)

        # Optionally, update the product message or cart button text
        # For example, refresh the product details message to show updated cart info or disable "add to cart"
        # This could involve re-fetching product details and re-rendering the message + keyboard.

    except ValueError as ve: # E.g. if location_id is not found and logic raises ValueError
        print(f"ValueError in add_to_cart_callback_handler: {ve}")
        await callback.answer(str(ve), show_alert=True)
    except Exception as e:
        print(f"Error in add_to_cart_callback_handler: {e}")
        error_msg = await get_text("error_generic", language, "Error adding item to cart.")
        await callback.answer(error_msg, show_alert=True)


# Placeholder for other cart functionalities:
# - Update quantity
# - Remove item
# - Clear cart
# - Proceed to checkout
