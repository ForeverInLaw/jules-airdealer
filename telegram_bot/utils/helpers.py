from typing import List, Any

def paginate_items(items: List[Any], page: int, items_per_page: int) -> List[Any]:
    """
    Helper function to paginate a list of items.
    `page` is 0-indexed.
    """
    if page < 0:
        page = 0
    start_index = page * items_per_page
    end_index = start_index + items_per_page
    return items[start_index:end_index]

async def format_price(price: float, currency: str = "USD", language: str = "en") -> str:
    """
    Formats a price with currency symbol.
    (This is a placeholder - actual formatting might depend on language/locale)
    """
    # In a real app, you'd use locale-specific formatting
    if currency == "USD":
        return f"${price:.2f}"
    elif currency == "EUR":
        return f"€{price:.2f}"
    elif currency == "PLN":
        return f"{price:.2f} zł"
    elif currency == "RUB": # Assuming RUB for Russian
        return f"{price:.2f} ₽"
    return f"{price:.2f} {currency}"

async def format_product_details(product: dict, stock_info: list, language: str) -> str:
    """
    Formats product details for display.
    (Placeholder - needs actual implementation based on product structure and desired output)
    """
    from .localization import get_text # Local import to avoid circular dependency at module level

    name = product.get('name', 'N/A')
    if product.get('product_localization'):
        name = product['product_localization'].get('name', name)

    description = ""
    if product.get('product_localization'):
        description = product['product_localization'].get('description', '')

    price_str = await format_price(float(product.get('price', 0)), language=language) # Assuming price needs currency based on lang

    details_text = await get_text("product_details_template", language,
                                default="{name}\n\n{description}\n\nPrice: {price}\n\nStock:\n{stock_list}")

    stock_lines = []
    if stock_info:
        for stock_item in stock_info:
            loc_name = stock_item.get('locations', {}).get('name', 'Unknown Location')
            qty = stock_item.get('quantity', 0)
            stock_line = await get_text("product_stock_line", language, default="{location_name}: {quantity} units")
            stock_lines.append(stock_line.format(location_name=loc_name, quantity=qty))
    else:
        stock_lines.append(await get_text("stock_unavailable", language, default="Stock information unavailable"))

    return details_text.format(
        name=name,
        description=description,
        price=price_str,
        stock_list="\n".join(stock_lines)
    )

# Add any other helper functions that might be needed across the application.
# For example, functions for validating input, generating complex keyboard layouts dynamically, etc.
