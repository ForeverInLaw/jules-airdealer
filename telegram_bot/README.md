# Telegram Ordering System Bot

This project is a Telegram bot designed for managing an ordering system, built with Python using the Aiogram 3.x library and integrated with Supabase for database backend.

## 🌟 Features

*   User registration and language selection (English, Russian, Polish).
*   Product catalog browsing by categories (manufacturers and search to be implemented).
*   Paginated product lists and detailed product views with images.
*   Shopping cart functionality (view cart, add items - location selection for adding to cart needs refinement).
*   Order creation and viewing user's order history (placeholder).
*   Basic settings management (language change).
*   Supabase integration for all data persistence.
*   Localization support for UI elements.
*   Admin functions (defined in database structure, bot-side implementation pending).
*   Supports both polling and webhook modes for receiving Telegram updates.

## 🛠️ Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd telegram-bot
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment variables:**
    *   Copy the `.env.example` file to `.env`:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file and fill in your actual credentials and settings:
        *   `BOT_TOKEN`: Your Telegram bot token.
        *   `SUPABASE_URL`: Your Supabase project URL.
        *   `SUPABASE_KEY`: Your Supabase public anon key.
        *   `SUPABASE_SERVICE_KEY`: Your Supabase service role key (for admin operations).
        *   `ADMIN_IDS`: Comma-separated Telegram user IDs for bot administrators.
        *   `WEBHOOK_URL` (Optional): If you plan to use webhooks.
        *   `DEBUG` (Optional): Set to `True` for debug logging.

5.  **Set up Supabase Database:**
    *   Ensure your Supabase project is created.
    *   Import the necessary database schema. The required tables include:
        `users`, `locations`, `manufacturers`, `categories`, `products`, `product_localization`, `product_stock`, `orders`, `order_items`, `user_cart`, `interface_text`, `admins`.
    *   Configure Row Level Security (RLS) policies as needed. (Refer to the detailed requirements document for examples).
    *   Ensure the `get_categories_with_product_count` RPC function is created in Supabase if you are using the catalog feature as implemented.

## 🚀 Running the Bot

*   **Polling Mode (default):**
    ```bash
    python main.py
    ```

*   **Webhook Mode:**
    Ensure `WEBHOOK_URL` is correctly set in your `.env` file. You will also need a reverse proxy (like Nginx) to forward requests from your public `WEBHOOK_URL` to the bot application.
    ```bash
    python webhook.py
    ```

## 📖 Detailed Documentation

For a comprehensive overview of the database structure, advanced configuration, specific Supabase queries, detailed functional requirements, and original code examples, please refer to the main requirements document provided with this project. (If this code was generated based on an issue, that issue description serves as the detailed document).

## 📝 To-Do / Further Development

*   Implement "Browse by Manufacturers" and "Search" in the catalog.
*   Refine location selection logic, especially for adding items to the cart and during checkout.
*   Complete implementation of cart modification (update quantity, remove item).
*   Full checkout process leading to order creation.
*   Detailed order view for users.
*   Admin panel functionalities (e.g., order management, product management).
*   More robust error handling and user feedback.
*   Comprehensive testing.

## 🤝 Contributing

Contributions are welcome! Please refer to the project's contribution guidelines (if available).
