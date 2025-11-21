# -*-*- ADMIN FUNKSIYALARI -*-*-
# -*-*- Bot administratori uchun maxsus funksiyalar -*-*-

import os
from aiogram import Bot
from aiogram.fsm.state import State, StatesGroup
from dotenv import load_dotenv

load_dotenv()

ADMIN_ID = int(os.getenv('ADMIN_ID'))
ADMIN_USERNAME = "Operator_Kino_1985"

# ==============================================================================
# -*-*- REKLAMA HOLATLARI -*-*-
# ==============================================================================
class AdvertisementState(StatesGroup):
    waiting_ad_text = State()
    waiting_ad_confirmation = State()

# ==============================================================================
# -*-*- KONTENT O'CHIRISH HOLATLARI -*-*-
# ==============================================================================
class DeleteContentState(StatesGroup):
    waiting_category = State()
    waiting_movie_selection = State()
    waiting_confirmation = State()

# ==============================================================================
# -*-*- ADMIN MANAGER KLASSI -*-*-
# ==============================================================================
class AdminManager:
    def __init__(self, database):
        self.db = database
    
    # ==========================================================================
    # -*-*- FOYDALANUVCHI ADMIN EKANLIGINI TEKSHIRISH -*-*-
    # ==========================================================================
    def is_admin(self, user_id: int, username: str = None) -> bool:
        # ID orqali tekshirish
        if user_id == ADMIN_ID:
            return True
        # Username orqali tekshirish
        if username and username.lower() == ADMIN_USERNAME.lower():
            return True
        return False
    
    # ==========================================================================
    # -*-*- ADMINGA BILDIRISHNOMA YUBORISH -*-*-
    # ==========================================================================
    async def send_admin_notification(self, bot: Bot, message: str, reply_markup=None):
        try:
            await bot.send_message(ADMIN_ID, message, reply_markup=reply_markup)
            print(f"✅ Admin ga xabar yuborildi (ID: {ADMIN_ID})")
        except Exception as e:
            print(f"❌ Admin ga xabar yuborishda xatolik: {e}")
    
    async def send_admin_notification_with_photo(self, bot: Bot, photo_file_id: str, caption: str = ""):
        """Admin ga rasm bilan xabar yuborish"""
        try:
            await bot.send_photo(ADMIN_ID, photo=photo_file_id, caption=caption)
            print(f"✅ Admin ga rasm yuborildi (ID: {ADMIN_ID})")
        except Exception as e:
            print(f"❌ Admin ga rasm yuborishda xatolik: {e}")
    
    # ==========================================================================
    # -*-*- REKLAMA YUBORISH TO'LIQ FUNKSIYASI -*-*-
    # ==========================================================================
    async def send_advertisement_to_all(self, bot: Bot, ad_text: str):
        users = self.db.get_all_users()
        success_count = 0
        fail_count = 0
        
        for user in users:
            try:
                await bot.send_message(user[0], ad_text)
                success_count += 1
            except Exception as e:
                fail_count += 1
                print(f"Xabar yuborishda xatolik user_id {user[0]}: {e}")
        
        return success_count, fail_count