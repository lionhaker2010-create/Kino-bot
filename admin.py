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
        
    # -*-*- TO'LOV BILDIRISHNOMASI -*-*-
    async def send_payment_notification_to_admin(self, bot: Bot, payment_data, receipt_file_id=None):
        """Admin ga to'lov haqida bildirishnoma yuborish"""
        
        message_text = (
            f"💰 **YANGI TO'LOV SO'ROVI!**\n\n"
            f"👤 **Foydalanuvchi:** {payment_data['user_name']}\n"
            f"🆔 **User ID:** {payment_data['user_id']}\n"
            f"🎯 **Xizmat turi:** {payment_data['service_name']}\n"
            f"💵 **Summa:** {payment_data['amount']:,} so'm\n"
            f"📝 **Tavsif:** {payment_data['description']}\n"
            f"🆔 **To'lov ID:** {payment_data['payment_id']}\n\n"
            f"**Tasdiqlash uchun quyidagi tugmalardan birini bosing:**"
        )
        
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        
        keyboard = [
            [KeyboardButton(text=f"✅ Tasdiqlash #{payment_data['payment_id']}")],
            [KeyboardButton(text=f"❌ Rad etish #{payment_data['payment_id']}")],
            [KeyboardButton(text="📋 To'lovlar ro'yxati")]
        ]
        
        try:
            if receipt_file_id:
                # Chek suratini yuborish
                await bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=receipt_file_id,
                    caption=message_text,
                    reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
                )
            else:
                await bot.send_message(
                    chat_id=ADMIN_ID,
                    text=message_text,
                    reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
                )
            return True
        except Exception as e:
            print(f"❌ Admin ga xabar yuborishda xatolik: {e}")
            return False    