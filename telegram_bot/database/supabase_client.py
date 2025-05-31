import os
from supabase import create_client, Client
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

try:
    from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY
except ImportError:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

class SupabaseClient:
    def __init__(self):
        self.url = SUPABASE_URL
        self.key = SUPABASE_KEY
        self.service_key = SUPABASE_SERVICE_KEY

        if not self.url or not self.key:
            raise ValueError("Supabase URL and Key must be provided.")

        self.client: Client = create_client(self.url, self.key)

        if self.service_key:
            self.admin_client: Client = create_client(self.url, self.service_key)
        else:
            self.admin_client: Optional[Client] = None

    async def get_user(self, telegram_id: int) -> Optional[dict]:
        response = self.client.table("users").select("*").eq("telegram_id", telegram_id).execute()
        return response.data[0] if response.data else None

    async def create_user(self, telegram_id: int, language_code: str = "en") -> dict:
        user_data = {
            "telegram_id": telegram_id,
            "language_code": language_code,
            "is_blocked": False
        }
        response = self.client.table("users").insert(user_data).execute()
        return response.data[0]

    async def get_products_by_category(self, category_id: int, language: str = "en") -> list:
        response = self.client.table("products").select(
            "id, name, price, image_url, variation, manufacturers(name), product_localization!inner(name, description)"
        ).eq("category_id", category_id).eq("product_localization.language_code", language).execute()
        return response.data

    async def get_product_stock(self, product_id: int, location_id: int) -> int:
        response = self.client.table("product_stock").select("quantity").eq(
            "product_id", product_id
        ).eq("location_id", location_id).execute()
        return response.data[0]["quantity"] if response.data else 0

    async def add_to_cart(self, user_id: int, product_id: int, location_id: int, quantity: int):
        existing_response = self.client.table("user_cart").select("*").eq(
            "user_id", user_id
        ).eq("product_id", product_id).eq("location_id", location_id).execute()

        existing_data = existing_response.data

        if existing_data:
            new_quantity = existing_data[0]["quantity"] + quantity
            response = self.client.table("user_cart").update({
                "quantity": new_quantity
            }).eq("user_id", user_id).eq("product_id", product_id).eq("location_id", location_id).execute()
        else:
            cart_data = {
                "user_id": user_id,
                "product_id": product_id,
                "location_id": location_id,
                "quantity": quantity
            }
            response = self.client.table("user_cart").insert(cart_data).execute()
        return response.data

    async def get_user_cart(self, user_id: int, language: str = "en") -> list:
        response = self.client.table("user_cart").select(
            "user_id, product_id, location_id, quantity, "
            "products!inner(id, name, price, image_url, category_id, manufacturer_id, "
            "product_localization!inner(language_code, name, description)), "
            "locations!inner(id, name, address)"
        ).eq("user_id", user_id).eq("products.product_localization.language_code", language).execute()
        return response.data

    async def create_order(self, user_id: int, payment_method: str, language: str = "en") -> dict:
        cart_items = await self.get_user_cart(user_id, language)

        if not cart_items:
            raise ValueError("Cart is empty")

        total_amount = sum(item["quantity"] * float(item["products"]["price"]) for item in cart_items)

        order_data = {
            "user_id": user_id,
            "status": "pending_admin_approval",
            "payment_method": payment_method,
            "total_amount": total_amount
        }

        order_response = self.client.table("orders").insert(order_data).execute()
        order_id = order_response.data[0]["id"]

        order_items_to_insert = []
        for item in cart_items:
            order_item = {
                "order_id": order_id,
                "product_id": item["products"]["id"],
                "location_id": item["location_id"],
                "quantity": item["quantity"],
                "price_at_order": float(item["products"]["price"]),
                "reserved_quantity": 0
            }
            order_items_to_insert.append(order_item)

        if order_items_to_insert:
            self.client.table("order_items").insert(order_items_to_insert).execute()

        self.client.table("user_cart").delete().eq("user_id", user_id).execute()

        return order_response.data[0]

    async def get_user_orders(self, user_id: int, language: str = "en") -> list:
        response = self.client.table("orders").select(
            "id, status, total_amount, created_at, payment_method, "
            "order_items!inner(quantity, price_at_order, products!inner(name))"
        ).eq("user_id", user_id).order("created_at", desc=True).execute()
        return response.data

    async def get_interface_text(self, key: str, language: str = "en") -> str:
        lang_column = f"text_{language}"
        response = self.client.table("interface_text").select(lang_column).eq("key", key).execute()
        if response.data and response.data[0].get(lang_column):
            return response.data[0][lang_column]
        return key

    async def get_product_details(self, product_id: int, language: str = "en") -> Optional[dict]:
        response = self.client.table("products").select(
            "id, name, price, image_url, variation, manufacturers(id, name), categories(id, name), "
            "product_localization!inner(name, description)"
        ).eq("id", product_id).eq("product_localization.language_code", language).single().execute()
        return response.data if response.data else None

    async def get_product_stock_all_locations(self, product_id: int) -> list:
        response = self.client.table("product_stock").select(
            "quantity, locations(id, name)"
        ).eq("product_id", product_id).execute()
        return response.data

    async def get_products_with_filters(self, category_id: int = None, manufacturer_id: int = None,
                                      search_query: str = None, language: str = "en"):
        query = self.client.table("products").select(
            "id, name, price, image_url, variation, manufacturers(id, name), categories(id, name), "
            "product_localization!inner(name, description)"
        ).eq("product_localization.language_code", language)

        if category_id:
            query = query.eq("category_id", category_id)
        if manufacturer_id:
            query = query.eq("manufacturer_id", manufacturer_id)
        if search_query:
            query = query.ilike("product_localization.name", f"%{search_query}%")

        response = query.execute()
        return response.data

    async def get_categories_with_count(self, language: str = "en"):
        response = self.client.rpc("get_categories_with_product_count", {"lang": language}).execute()
        return response.data

    async def update_order_status(self, order_id: int, new_status: str, admin_notes: str = None):
        if not self.admin_client:
            raise ConnectionError("Admin client not initialized. SUPABASE_SERVICE_KEY might be missing.")

        update_data = {"status": new_status}
        if admin_notes:
            update_data["admin_notes"] = admin_notes

        response = self.admin_client.table("orders").update(update_data).eq("id", order_id).execute()
        return response.data[0] if response.data else None

try:
    supabase_client = SupabaseClient()
except ValueError as e:
    print(f"Error initializing SupabaseClient: {e}")
    supabase_client = None
except Exception as e:
    print(f"An unexpected error occurred during SupabaseClient initialization: {e}")
    supabase_client = None
