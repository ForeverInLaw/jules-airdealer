from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

# This is a placeholder for a database middleware.
# It could be used to inject a database session or client into handlers,
# manage database connections per request, or handle transactions.

# Assuming supabase_client is globally available from database.supabase_client
try:
    from database.supabase_client import supabase_client
except ImportError:
    supabase_client = None # Or handle error

class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        # Example: Injecting the supabase_client instance into handler data
        if supabase_client:
            data["supabase_client"] = supabase_client
        else:
            # Handle case where supabase_client is not available, maybe raise an error
            # or skip injecting if it's optional for some handlers.
            print("Warning: Supabase client not available in DatabaseMiddleware.")
            data["supabase_client"] = None 

        # You could also manage session lifecycle here if using something like SQLAlchemy
        # async with db_session_context() as session:
        # data["db_session"] = session
        # result = await handler(event, data)
        # return result
        
        return await handler(event, data)
