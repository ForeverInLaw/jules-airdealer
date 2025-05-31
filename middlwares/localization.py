from typing import Callable, Dict, Any, Awaitable, Optional
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

# Assuming supabase_client is initialized and accessible for fetching user language.
# Import it carefully to avoid circular dependencies if it's also initialized elsewhere.
try:
    from database.supabase_client import supabase_client
except ImportError:
    # Fallback or error if supabase_client is critical here
    # For this middleware, it's quite critical.
    print("CRITICAL: Supabase client could not be imported in LocalizationMiddleware.")
    supabase_client = None 

class LocalizationMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject, # More specific types like Message or CallbackQuery could be used if middleware is type-specific
        data: Dict[str, Any]
    ) -> Any:
        user: Optional[User] = data.get("event_from_user")
        
        language_code = "en" # Default language

        if user and supabase_client:
            try:
                db_user = await supabase_client.get_user(user.id)
                if db_user and db_user.get("language_code"):
                    language_code = db_user["language_code"]
                # If db_user is None (new user not yet in DB), they might not have a language_code set.
                # The start handler usually handles creating the user and setting initial language.
                # So, for a very first interaction, language might default to 'en' here,
                # which is fine as language selection is typically the first step.
            except Exception as e:
                print(f"Error fetching user language in LocalizationMiddleware: {e}")
                # Keep default language_code if error occurs
        
        data["language"] = language_code
        # print(f"[LocalizationMiddleware] User {user.id if user else 'Unknown'}, Language: {language_code}") # For debugging
        
        return await handler(event, data)

# Note: The original document uses `data["language"] = language`
# but it's more conventional to use `language_code` for the variable name
# if it stores codes like "en", "ru". I've used `language_code` internally
# and set `data["language"]` as per the document's example usage in other files.
# For consistency, let's stick to `data["language"] = language_code`.
# The handlers will then access it via `data['language']`.
