import json
from typing import Optional
# Assuming supabase_client is initialized in database.supabase_client
# and can be imported.
# If supabase_client is None due to initialization error, this will also fail.
# Proper error handling or dependency injection might be needed in a larger app.
try:
    from database.supabase_client import supabase_client
except ImportError:
    # This is a fallback or could indicate a circular dependency or init issue.
    # For now, we'll allow it to be None and handle it in get_text.
    supabase_client = None 

# Fallback local cache for texts if DB fails or for overrides
# This part is not in the original document but can be useful.
# For now, we'll stick to the document's direct DB approach.
# loaded_texts = {}

# def load_texts_from_json(language_code: str):
#     global loaded_texts
#     try:
#         with open(f"locales/{language_code}.json", "r", encoding="utf-8") as f:
#             loaded_texts[language_code] = json.load(f)
#     except FileNotFoundError:
#         loaded_texts[language_code] = {}
#         print(f"Warning: Locale file for {language_code}.json not found.")

async def get_text(key: str, language_code: str = "en", default: Optional[str] = None) -> str:
    """
    Fetches a localized text string from Supabase based on its key and language.
    Falls back to the key itself or a provided default if not found.
    """
    if supabase_client:
        try:
            # The get_interface_text method in SupabaseClient already handles fallback to key
            text = await supabase_client.get_interface_text(key, language_code)
            # If text is the key itself (meaning not found in DB), and a default is provided, use default.
            if text == key and default is not None:
                return default
            return text
        except Exception as e:
            print(f"Error fetching text '{key}' for lang '{language_code}' from Supabase: {e}")
            # Fallback to key or default if Supabase call fails
            return default if default is not None else key
    else:
        # Supabase client not available, fallback to key or default
        print(f"Warning: Supabase client not available for get_text (key: {key}, lang: {language_code}).")
        # Optionally, could try loading from local JSON files here as a further fallback.
        # if not loaded_texts.get(language_code):
        #     load_texts_from_json(language_code)
        # return loaded_texts.get(language_code, {}).get(key, default if default is not None else key)
        return default if default is not None else key

# Example of how you might add more localization utility functions:
# async def get_formatted_date(date_obj, language_code: str = "en"):
#     # ... logic to format date based on language ...
#     return str(date_obj)
