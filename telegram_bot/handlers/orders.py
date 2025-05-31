from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

# Assuming supabase_client and language are available
try:
    from database.supabase_client import supabase_client
except ImportError:
    supabase_client = None

from utils.localization import get_text
# from keyboards.inline import get_orders_keyboard, get_order_details_keyboard # Examples

router = Router()

@router.callback_query(F.data == "my_orders")
async def my_orders_callback_handler(callback: CallbackQuery, language: str, state: FSMContext):
    if not supabase_client:
        await callback.message.answer(await get_text("error_db_connection", language, "DB error."))
        await callback.answer()
        return

    user_id = callback.from_user.id
    try:
        orders = await supabase_client.get_user_orders(user_id, language) # Pass language if needed for localized product names in orders

        if not orders:
            no_orders_text = await get_text("no_orders_found", language, "You have no orders yet.")
            # Keyboard to go to catalog?
            await callback.message.edit_text(no_orders_text)
            await callback.answer()
            return

        # Format orders for display (similar to cart, needs a helper)
        orders_summary_lines = [f"Your Orders ({callback.from_user.full_name}):"]
        for order in orders:
            order_id = order.get("id")
            status = order.get("status", "N/A")
            total_amount = float(order.get("total_amount", 0.0))
            created_at = order.get("created_at", "N/A") # Format this date

            #簡易的な表示。format_priceや日付フォーマットヘルパーを使うべき
            total_amount_str = f"{total_amount:.2f}"

            orders_summary_lines.append(
                f"Order #{order_id} - Status: {status} - Total: {total_amount_str} - Date: {created_at.split('T')[0] if created_at else 'N/A'}"
            )
            # Add callback button for each order to view details:
            # InlineKeyboardButton(text=f"View Order #{order_id}", callback_data=f"orderdetails_{order_id}")

        # from keyboards.inline import get_orders_keyboard # Dynamically import if needed
        # orders_keyboard = await get_orders_keyboard(orders, language) # For pagination or order-specific actions

        await callback.message.edit_text(
            text="\n".join(orders_summary_lines),
            # reply_markup=orders_keyboard
        )
        await callback.answer()

    except Exception as e:
        print(f"Error in my_orders_callback_handler: {e}")
        error_msg = await get_text("error_generic", language, "Error fetching orders.")
        await callback.message.answer(error_msg)
        await callback.answer()

# Placeholder for other order functionalities:
# - View order details (orderdetails_<order_id>)
# - Cancel order (if status allows)
# - Reorder
# - Create order (from checkout process)
