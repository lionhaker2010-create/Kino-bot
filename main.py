import os
import time
import asyncio
import threading
from auto_messager import AutoMessager 
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

# Database va Admin import
from database import Database
from admin import AdminManager, AdvertisementState
from admin import DeleteContentState

# Keep alive import
from keep_alive import keep_alive, start_pinging

# Botni uyg'otish
keep_alive()
print("✅ Keep-alive server started!")

# Ping ni background da ishlatish
ping_thread = threading.Thread(target=start_pinging, daemon=True)
ping_thread.start()
print("✅ Auto-ping started!")

load_dotenv()

# ==============================================================================
# -*-*- GLOBAL O'ZGARUVCHILAR -*-*-
# ==============================================================================
last_movie_processing_time = 0
last_payment_processing_time = 0

# ==============================================================================
# -*-*- BOT KONFIGURATSIYASI -*-*-
# ==============================================================================
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ==============================================================================
# -*-*- DATABASE VA ADMIN MANAGER -*-*-
# ==============================================================================
db = Database()
admin_manager = AdminManager(db)

# ==============================================================================
# -*-*- YANGI ASOSIY MENYU KLAVIATURASI -*-*-
# ==============================================================================
def main_menu_keyboard(user_id=None, username=None):
    keyboard = [
        [KeyboardButton(text="🎬 Barcha Kontentlar")],
        [KeyboardButton(text="🔍 Qidiruv")],
    ]
    
    # Admin panel faqat adminlar uchun
    if user_id and admin_manager.is_admin(user_id, username):
        keyboard.append([KeyboardButton(text="👑 Admin Panel")])
    
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

# ==============================================================================
# -*-*- YANGI START HANDLERI -*-*-
# ==============================================================================
@dp.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    # Blok tekshiruvi
    if db.is_user_blocked(message.from_user.id):
        block_info = db.get_blocked_user_info(message.from_user.id)
        if block_info:
            reason, duration, until, blocked_at, blocked_by = block_info
            duration_display = {
                "24_soat": "24 soat",
                "7_kun": "7 kun", 
                "Noma'lum": "Noma'lum muddat"
            }.get(duration, duration)
            
            block_message = (
                f"🚫 **KIRISH TA'QICHLANGAN!**\n\n"
                f"Hurmatli foydalanuvchi, platforma qoidalariga amal qilinmaganligi "
                f"sababli hisobingiz faoliyati vaqtincha bloklandi.\n\n"
                f"📋 **Sabab:** {reason}\n"
                f"⏰ **Muddati:** {duration_display}\n\n"
                f"⚠️ **Ogohlantirishlar:**\n"
                f"• Blokni chetlab o'tishga urinish — muddatni uzaytiradi\n"
                f"• Administrator bilan hurmat bilan muloqot qiling\n"
                f"• Yolg'on ma'lumot taqdim qilinishi blokni bekor qilmaydi\n\n"
                f"Agar bu qaror bo'yicha e'tirozingiz bo'lsa, quyidagi manzil orqali administratorga yozing:\n\n"
                f"📞 **Administrator:** @Operator_1985\n"
                f"📝 Arizangiz ko'rib chiqiladi."
            )
            await message.answer(block_message)
            return
    
    # Yangi animatsiya
    msg1 = await message.answer("🚀 **Kino Olamiga Xush Kelibsiz!**")
    await asyncio.sleep(1)
    
    msg2 = await message.answer("⏳ **Yuklanmoqda...**")
    await asyncio.sleep(1)
    
    await msg1.delete()
    await msg2.delete()
    
    # Foydalanuvchi ma'lumotlarini saqlash (soddalashtirilgan)
    user = db.get_user(message.from_user.id)
    if not user:
        db.add_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name or "Foydalanuvchi",
            phone_number="",
            language="uz"
        )
    
    await message.answer(
        "🎬 **Kino Botga Xush Kelibsiz!**\n\n"
        "Bu yerda siz:\n"
        "• 🎬 Barcha kinolarni ko'rishingiz mumkin\n" 
        "• 🔍 Qidiruv orqali kerakli kinoni topishingiz mumkin\n\n"
        "Kerakli bo'limni tanlang:",
        reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
    )
    await state.clear()

# ==============================================================================
# -*-*- BARCHA KONTENTLAR HANDLERI -*-*-
# ==============================================================================
@dp.message(F.text == "🎬 Barcha Kontentlar")
async def all_content_fixed(message: types.Message):
    """Barcha kontentlarni ko'rsatish"""
    # Blok tekshiruvi
    if await check_and_block(message):
        return
    
    try:
        # Barcha kinolarni olish
        movies = db.get_all_movies_sorted()
        
        if not movies:
            await message.answer(
                "❌ Hozircha hech qanday kontent mavjud emas.",
                reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
            )
            return
        
        # Kontentlarni to'g'ri guruhlash
        free_movies = []
        paid_movies = []
        
        for movie in movies:
            try:
                movie_id, title, description, category, file_id, price, is_premium, actor_name, banner_file_id, created_at, added_by = movie
                
                if price == 0:
                    free_movies.append(movie)
                else:
                    paid_movies.append(movie)
                    
            except Exception as e:
                print(f"Kino ma'lumotlarini olishda xatolik: {e}")
                continue
        
        # Klaviatura yaratish
        keyboard = []
        
        # Bepul kinolar
        for movie in free_movies:
            try:
                movie_id, title, description, category, file_id, price, is_premium, actor_name, banner_file_id, created_at, added_by = movie
                button_text = f"🎬 {title}"
                if actor_name:
                    button_text += f" - {actor_name}"
                keyboard.append([KeyboardButton(text=button_text)])
            except Exception as e:
                print(f"Bepul kino qo'shishda xatolik: {e}")
        
        # Pullik kinolar
        for movie in paid_movies:
            try:
                movie_id, title, description, category, file_id, price, is_premium, actor_name, banner_file_id, created_at, added_by = movie
                button_text = f"💵 {title}"
                if actor_name:
                    button_text += f" - {actor_name}"
                keyboard.append([KeyboardButton(text=button_text)])
            except Exception as e:
                print(f"Pullik kino qo'shishda xatolik: {e}")
        
        keyboard.append([KeyboardButton(text="🔙 Asosiy Menyu")])
        
        # Xabar matni
        response_text = (
            f"🎬 **Barcha Kontentlar**\n\n"
            f"🆓 **Bepul kinolar:** {len(free_movies)} ta\n"
            f"💵 **Pullik kinolar:** {len(paid_movies)} ta\n"
            f"📊 **Jami:** {len(movies)} ta kino\n\n"
        )
        
        # Agar kontentlar ko'p bo'lsa, qo'shimcha ma'lumot
        if len(free_movies) > 0:
            response_text += f"🆓 **Bepul kinolar:**\n"
            for movie in free_movies[:3]:
                movie_id, title, description, category, file_id, price, is_premium, actor_name, banner_file_id, created_at, added_by = movie
                response_text += f"• {title}\n"
            if len(free_movies) > 3:
                response_text += f"• ... va yana {len(free_movies) - 3} ta\n"
        
        if len(paid_movies) > 0:
            response_text += f"\n💵 **Pullik kinolar:**\n"
            for movie in paid_movies[:3]:
                movie_id, title, description, category, file_id, price, is_premium, actor_name, banner_file_id, created_at, added_by = movie
                response_text += f"• {title} - {price:,} so'm\n"
            if len(paid_movies) > 3:
                response_text += f"• ... va yana {len(paid_movies) - 3} ta\n"
        
        response_text += f"\nKerakli kinoni tanlang:"
        
        await message.answer(
            response_text,
            reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Kontentlarni yuklashda xatolik: {e}\n\n"
            f"Iltimos, keyinroq urinib ko'ring.",
            reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
        )

# ==============================================================================
# -*-*- QIDIRUV HANDLERLARI -*-*-
# ==============================================================================
@dp.message(F.text == "🔍 Qidiruv")
async def search_handler(message: types.Message, state: FSMContext):
    """Qidiruvni boshlash"""
    # Blok tekshiruvi
    if await check_and_block(message):
        return
    
    await message.answer(
        "🔍 **Qidiruv**\n\n"
        "Kino, serial yoki multfilm nomini yozing:\n"
        "Yoki aktyor nomini yozing:\n\n"
        "💡 **Masalan:**\n"
        "• Terminator\n"
        "• Arnold\n"
        "• Komediya\n"
        "• Bolalar",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🔙 Asosiy Menyu")]
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(SearchState.waiting_search_query)

# ==============================================================================
# -*-*- NAVIGATSIYA -*-*-
# ==============================================================================
@dp.message(F.text == "🔙 Asosiy Menyu")
async def back_to_main(message: types.Message):
    await message.answer(
        "Asosiy menyuga qaytingiz:",
        reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
    )

# ==============================================================================
# -*-*- BLOK TEKSHIRUV FUNKSIYASI -*-*-
# ==============================================================================
async def check_and_block(message: types.Message):
    """Foydalanuvchi bloklanganligini tekshirish va xabar yuborish"""
    if db.is_user_blocked(message.from_user.id):
        block_info = db.get_blocked_user_info(message.from_user.id)
        if block_info:
            reason, duration, until, blocked_at, blocked_by = block_info
            
            duration_display = {
                "24_soat": "24 soat",
                "7_kun": "7 kun", 
                "Noma'lum": "Noma'lum muddat"
            }.get(duration, duration)
            
            block_message = (
                f"🚫 **KIRISH TA'QICHLANGAN!**\n\n"
                f"Hurmatli foydalanuvchi, platforma qoidalariga amal qilinmaganligi "
                f"sababli hisobingiz faoliyati vaqtincha bloklandi.\n\n"
                f"📋 **Sabab:** {reason}\n"
                f"⏰ **Muddati:** {duration_display}\n\n"
                f"⚠️ **Ogohlantirishlar:**\n"
                f"• Blokni chetlab o'tishga urinish — muddatni uzaytiradi\n"
                f"• Administrator bilan hurmat bilan muloqot qiling\n"
                f"• Yolg'on ma'lumot taqdim qilinishi blokni bekor qilmaydi\n\n"
                f"Agar bu qaror bo'yicha e'tirozingiz bo'lsa, quyidagi manzil orqali administratorga yozing:\n\n"
                f"📞 **Administrator:** @Operator_1985\n"
                f"📝 Arizangiz ko'rib chiqiladi."
            )
            await message.answer(block_message)
            return True
    return False

# ==============================================================================
# -*-*- HOLATLAR -*-*-
# ==============================================================================
class SearchState(StatesGroup):
    waiting_search_query = State()

# ==============================================================================
# -*-*- BOSHQA XABARLAR -*-*-
# ==============================================================================
@dp.message()
async def handle_other_messages(message: types.Message):
    if message.text:
        await message.answer(
            "Iltimos, menyudan kerakli bo'limni tanlang 👇", 
            reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
        )

# ==============================================================================
# -*-*- BOTNI ISHGA TUSHIRISH -*-*-
# ==============================================================================
async def main():
    print("🤖 Bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())