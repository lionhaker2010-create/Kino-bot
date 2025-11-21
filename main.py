import os
import time
import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

from database import Database
from admin import AdminManager, AdvertisementState
from admin import DeleteContentState

load_dotenv()

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

print(f"🔄 Bot ishga tushmoqda...")
print(f"🔑 Admin ID: {ADMIN_ID}")
print(f"🤖 Bot token: {BOT_TOKEN[:10]}...")

# ==============================================================================
# -*-*- ASOSIY FUNKSIYA -*-*-
# ==============================================================================

async def main():
    print("Bot ishga tushdi...")
    
    # Faqat Webhook rejimi (Render uchun)
    print("🌐 Webhook rejimi ishga tushmoqda...")
    
    # Webhook ni o'chirish (avvalgi webhook ni tozalash)
    await bot.delete_webhook(drop_pending_updates=True)
    
    WEBHOOK_PATH = f"/webhook"
    WEBHOOK_URL = f"https://kino-bot-l3nw.onrender.com{WEBHOOK_PATH}"
    
    await bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook sozlandi: {WEBHOOK_URL}")
    
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Server {port}-portda ishga tushmoqda...")
    
    return await web._run_app(app, host="0.0.0.0", port=port)
    
# -*-*- BAZA YARATISH -*-*-
@dp.startup()
async def on_startup():
    db.init_db()  # Barcha jadvallarni yaratadi
    print("✅ Barcha jadvallar yaratildi/yangilandi")    

if __name__ == "__main__":
    asyncio.run(main())

# ==============================================================================
# -*-*- RO'YXATDAN O'TISH HOLATLARI -*-*-
# ==============================================================================
class Registration(StatesGroup):
    language = State()
    name = State()
    phone = State()

# ==============================================================================
# -*-*- QIDIRUV HOLATI -*-*-
# ==============================================================================
class SearchState(StatesGroup):
    waiting_search_query = State()

# ==============================================================================
# -*-*- PREMIUM BOSHQARUV HOLATLARI -*-*-
# ==============================================================================
class PremiumManagementState(StatesGroup):
    waiting_user_id = State()
    waiting_action = State()
    waiting_duration = State()
    waiting_confirmation = State()
    
# ==============================================================================
# -*-*- KONTENT BOSHQARUV HOLATLARI -*-*-
# ==============================================================================
class ContentManagementState(StatesGroup):
    waiting_content_type = State()
    waiting_movie_title = State()
    waiting_movie_description = State()
    waiting_main_category = State()
    waiting_sub_category = State()
    waiting_movie_price = State()  
    waiting_movie_banner = State()
    waiting_movie_file = State()
    
# ==============================================================================
# -*-*- BLOKLASH HOLATLARI -*-*-
# ==============================================================================
class BlockUserState(StatesGroup):
    waiting_user_id = State()
    waiting_reason = State()
    waiting_duration = State()
    waiting_confirmation = State()

class UnblockUserState(StatesGroup):
    waiting_user_id = State()   

# ==============================================================================
# -*-*- TO'LOV HOLATLARI -*-*-
# ==============================================================================
class PaymentState(StatesGroup):
    waiting_payment_method = State()
    waiting_payment_confirmation = State()
    waiting_payment_receipt = State()

# ... (qolgan barcha handlerlar va funksiyalar o'zgarmasdan qoladi)   
    
# ==============================================================================
# -*-*- YAGONA BO'LIM KLAVIATURASI -*-*-
# ==============================================================================
import os
import time
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from dotenv import load_dotenv

from database import Database
from admin import AdminManager, AdvertisementState
from admin import DeleteContentState
from keep_alive import keep_alive

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

async def auto_restart():
    """Auto restart every 6 hours to prevent freezing"""
    while True:
        await asyncio.sleep(6 * 60 * 60)  # 6 hours
        print(f"🔄 Auto-restart at {time.strftime('%Y-%m-%d %H:%M:%S')}")

print(f"🔄 Bot ishga tushmoqda...")
print(f"🔑 Admin ID: {ADMIN_ID}")
print(f"🤖 Bot token: {BOT_TOKEN[:10]}...")

# ==============================================================================
# -*-*- ASOSIY FUNKSIYA -*-*-
# ==============================================================================

async def main():
    print("Bot ishga tushdi...")
    
    # Start auto-restart in background
    asyncio.create_task(auto_restart())
    
    keep_alive()
    
    # Webhook sozlamalari (Render uchun)
    if os.getenv('RENDER'):
        print("🌐 Webhook rejimi ishga tushmoqda...")
        
        # Webhook mode - Render uchun
        WEBHOOK_PATH = f"/webhook"
        WEBHOOK_URL = f"https://kino-bot-l3nw.onrender.com{WEBHOOK_PATH}"
        
        # Set webhook
        await bot.set_webhook(WEBHOOK_URL)
        print(f"✅ Webhook sozlandi: {WEBHOOK_URL}")
        
        # Webhook server
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        # Portni environment'dan olish
        port = int(os.environ.get("PORT", 8080))
        print(f"🚀 Server {port}-portda ishga tushmoqda...")
        
        return await web._run_app(app, host="0.0.0.0", port=port)
    else:
        # Polling mode - local uchun
        print("📡 Polling rejimi ishga tushmoqda...")
        await dp.start_polling(bot)

# -*-*- BAZA YARATISH -*-*-
@dp.startup()
async def on_startup():
    db.init_db()  # Barcha jadvallarni yaratadi
    print("✅ Barcha jadvallar yaratildi/yangilandi")

if __name__ == "__main__":
    asyncio.run(main())

# ==============================================================================
# -*-*- RO'YXATDAN O'TISH HOLATLARI -*-*-
# ==============================================================================
class Registration(StatesGroup):
    language = State()
    name = State()
    phone = State()

# ==============================================================================
# -*-*- QIDIRUV HOLATI -*-*-
# ==============================================================================
class SearchState(StatesGroup):
    waiting_search_query = State()

# ==============================================================================
# -*-*- KLAVIATURALAR -*-*-
# ==============================================================================

# ==============================================================================
# -*-*- PREMIUM BOSHQARUV HOLATLARI -*-*-
# ==============================================================================
class PremiumManagementState(StatesGroup):
    waiting_user_id = State()
    waiting_action = State()
    waiting_duration = State()
    waiting_confirmation = State()
    
# ==============================================================================
# -*-*- KONTENT BOSHQARUV HOLATLARI -*-*-
# ==============================================================================
class ContentManagementState(StatesGroup):
    waiting_content_type = State()
    waiting_movie_title = State()
    waiting_movie_description = State()
    waiting_main_category = State()
    waiting_sub_category = State()
    waiting_movie_price = State()  
    waiting_movie_banner = State()  # <- YANGI: banner rasm
    waiting_movie_file = State()
    
# ==============================================================================
# -*-*- BLOKLASH HOLATLARI -*-*-
# ==============================================================================
class BlockUserState(StatesGroup):
    waiting_user_id = State()
    waiting_reason = State()
    waiting_duration = State()
    waiting_confirmation = State()

class UnblockUserState(StatesGroup):
    waiting_user_id = State()   

# ==============================================================================
# -*-*- TO'LOV HOLATLARI -*-*-
# ==============================================================================
class PaymentState(StatesGroup):
    waiting_payment_method = State()
    waiting_payment_confirmation = State()
    waiting_payment_receipt = State()    

# ... (qolgan kodlar o'zgarmaydi, faqat yuqoridagi qismlar yangilandi)

# ==============================================================================
# -*-*- START VA RO'YXATDAN O'TISH HANDLERLARI -*-*-
# ==============================================================================

@dp.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    # Bloklanganligini tekshirish
    if db.is_user_blocked(message.from_user.id):
        block_info = db.get_blocked_user_info(message.from_user.id)
        if block_info:
            reason, duration, until, blocked_at, blocked_by = block_info
            
            # Muddatni o'qiladigan formatga o'tkazish
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
    
    user = db.get_user(message.from_user.id)
    
    if user:
        await message.answer(
            "🤗 Assalomu Aleykum! Dunyo Kinosi Olamiga xush kelibsiz! 🎬\n"
            "Bu Bot Siz izlagan barcha Kontentlarni o'z ichiga olgan. 🔍\n"
            "Sevimli Kino va Seriallaringizni va Multfilmlarni\n"
            "Musiqa Konsert Dasturlarini To'liq Nomi Yozib\n"
            "Qidiruv Bo'limi Orqali topshingiz ham mumkin!",
            reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
        )
    else:
        await message.answer(
            "🤗 Assalomu Aleykum Dunyo Kinosi Olamiga xush kelibsiz! 🎬\n"
            "Bu Bot Siz izlagan barcha Kontentlarni o'z ichiga olgan. 🔍\n"
            "Sevimli Kino va Seriallaringizni va Multfilmlarni\n"
            "Musiqa Konsert Dasturlarini To'liq Nomi Yozib\n"
            "Qidiruv Bo'limi Orqali topshingiz ham mumkin!\n\n"
            "👇 Kerakli Tilni Tanlang",
            reply_markup=language_keyboard()
        )
        await state.set_state(Registration.language)

# ... (qolgan barcha handlerlar va funksiyalar o'zgarmaydi)

# ==============================================================================
# -*-*- KLAVIATURA FUNKSIYALARI -*-*-
# ==============================================================================

def get_category_keyboard(category_type, category_name=None):
    """Barcha bo'limlar uchun yagona klaviatura"""
    db = Database()  # Database obyektini yaratish
    all_categories = db.get_all_categories()  # <- db orqali chaqirish
    
    if category_type == "main":
        categories = all_categories["main_categories"]
        
        keyboard = []
        row = []
        
        for i, category in enumerate(categories):
            row.append(KeyboardButton(text=category))
            if len(row) == 2 or i == len(categories) - 1:
                keyboard.append(row)
                row = []
        
        keyboard.append([KeyboardButton(text="🔙 Asosiy Menyu")])
        
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    else:
        # ICHKI KATEGORIYALAR UCHUN SODDA KLAVIATURA
        # Faqat "O'tkazib yuborish" va "Orqaga" tugmalari
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="⏭️ O'tkazib yuborish")],
                [KeyboardButton(text="🔙 Orqaga")]
            ],
            resize_keyboard=True
        )

def main_menu_keyboard(user_id=None, username=None):
    keyboard = [
        [KeyboardButton(text="🎬 Barcha Kontentlar"), KeyboardButton(text="📁 Bo'limlar")],
        [KeyboardButton(text="💵 Pullik Hizmatlar"), KeyboardButton(text="🔍 Qidiruv")],
    ]
    
    # Premium taklif tugmasi
    if user_id and not db.check_premium_status(user_id):
        keyboard.append([KeyboardButton(text="💎 Premiumga O'tish"), KeyboardButton(text="🎁 Aksiya")])
    
    # Admin panel
    if user_id and admin_manager.is_admin(user_id, username):
        keyboard.append([KeyboardButton(text="👑 Admin Panel")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

def language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbek"), KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🏴 English")],
        ],
        resize_keyboard=True
    )



# ... (qolgan barcha klaviatura funksiyalari o'zgarmaydi)
    
# ==============================================================================
# -*-*- ASOSIY KATEGORIYALAR KLAVIATURASI -*-*-
# ==============================================================================
def main_categories_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎭 Hollywood"), KeyboardButton(text="🎬 Hind")],
            [KeyboardButton(text="🎥 Rus"), KeyboardButton(text="🎞️ O'zbek")],
            [KeyboardButton(text="🕌 Islomiy"), KeyboardButton(text="🇹🇷 Turk")],
            [KeyboardButton(text="👶 Bolalar"), KeyboardButton(text="🇰🇷 Koreys")],
            [KeyboardButton(text="🔙 Orqaga")],
        ],
        resize_keyboard=True
    )   

# ==============================================================================
# -*-*- ICHKI KATEGORIYALAR KLAVIATURASI -*-*-
# ==============================================================================
def get_sub_categories_keyboard(main_category):
    if main_category == "🎭 Hollywood":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🎬 Mel Gibson"), KeyboardButton(text="💪 Arnold Schwarzenegger")],
                [KeyboardButton(text="🥊 Sylvester Stallone"), KeyboardButton(text="🚗 Jason Statham")],
                [KeyboardButton(text="🐲 Jeki Chan"), KeyboardButton(text="🥋 Skod Adkins")],
                [KeyboardButton(text="📽️ Barcha Hollywood"), KeyboardButton(text="🔙 Orqaga")],
            ],
            resize_keyboard=True
        )
    elif main_category == "🎬 Hind":
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🤴 Shakruhkhan"), KeyboardButton(text="🎬 Amirkhan")],
                [KeyboardButton(text="💪 Akshay Kumar"), KeyboardButton(text="👑 Salmonkhan")],
                [KeyboardButton(text="📀 Barcha Hind"), KeyboardButton(text="🔙 Orqaga")],
            ],
            resize_keyboard=True
        )
    # ... boshqa kategoriyalar uchun ham shunday    

# -*-*- TIL TANLASH KLAVIATURASI -*-*-
def language_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇺🇿 O'zbek"), KeyboardButton(text="🇷🇺 Русский"), KeyboardButton(text="🏴 English")],
        ],
        resize_keyboard=True
    )

# -*-*- TELEFON RAQAM KLAVIATURASI -*-*-
def phone_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

# -*-*- ASOSIY MENYU KLAVIATURASI -*-*-
def main_menu_keyboard(user_id=None, username=None):
    keyboard = [
        [KeyboardButton(text="🎬 Barcha Kontentlar"), KeyboardButton(text="📁 Bo'limlar")],
        [KeyboardButton(text="💵 Pullik Hizmatlar"), KeyboardButton(text="🔍 Qidiruv")],
    ]
    
    # Premium taklif tugmasi
    if user_id and not db.check_premium_status(user_id):
        keyboard.append([KeyboardButton(text="💎 Premiumga O'tish"), KeyboardButton(text="🎁 Aksiya")])
    
    # Admin panel
    if user_id and admin_manager.is_admin(user_id, username):
        keyboard.append([KeyboardButton(text="👑 Admin Panel")])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )

# -*-*- BO'LIMLAR KLAVIATURASI -*-*-
def sections_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎭 Hollywood Kinolari"), KeyboardButton(text="🎬 Hind Filmlari")],
            [KeyboardButton(text="📺 Hind Seriallari"), KeyboardButton(text="🎥 Rus Kinolari")],
            [KeyboardButton(text="📟 Rus Seriallari"), KeyboardButton(text="🎞️ O'zbek Kinolari")],
            [KeyboardButton(text="📱 O'zbek Seriallari"), KeyboardButton(text="🕌 Islomiy Kinolar")],
            [KeyboardButton(text="📖 Islomiy Seriallar"), KeyboardButton(text="🇹🇷 Turk Kinolari")],
            [KeyboardButton(text="📺 Turk Seriallari"), KeyboardButton(text="👶 Bolalar Kinolari")],
            [KeyboardButton(text="🐰 Bolalar Multfilmlari"), KeyboardButton(text="🇰🇷 Koreys Kinolari")],
            [KeyboardButton(text="📡 Koreys Seriallari"), KeyboardButton(text="🎯 Qisqa Filmlar")],
            [KeyboardButton(text="🎤 Konsert Dasturlari"), KeyboardButton(text="🔙 Asosiy Menyu")],
        ],
        resize_keyboard=True
    )

# ==============================================================================
# -*-*- ADMIN KLAVIATURALARI -*-*-
# ==============================================================================

# Oddiy admin klaviaturasi
def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Foydalanuvchilar soni"), KeyboardButton(text="💰 Pullik Hizmatlar Statistika")],
            [KeyboardButton(text="💰 To'lovlarni ko'rish"), KeyboardButton(text="📢 Reklama yuborish")],
            [KeyboardButton(text="👑 Premium Boshqaruv"), KeyboardButton(text="🎬 Kontent Qo'shish")],
            [KeyboardButton(text="📁 Kontentlar Boshqaruvi"), KeyboardButton(text="📋 Kinolar ro'yxati")],
            [KeyboardButton(text="🔄 Holatni tozalash"), KeyboardButton(text="🔙 Asosiy Menyu")],
        ],
        resize_keyboard=True
    )

# Kengaytirilgan admin klaviaturasi
def admin_advanced_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Foydalanuvchilar soni"), KeyboardButton(text="💰 Pullik Hizmatlar Statistika")],
            [KeyboardButton(text="💰 To'lovlarni ko'rish"), KeyboardButton(text="📢 Reklama yuborish")],
            [KeyboardButton(text="👑 Premium Boshqaruv"), KeyboardButton(text="🎬 Kontent Qo'shish")],
            [KeyboardButton(text="📁 Kontentlar Boshqaruvi"), KeyboardButton(text="📋 Kinolar ro'yxati")],
            [KeyboardButton(text="🚫 Bloklash"), KeyboardButton(text="✅ Blokdan ochish")],
            [KeyboardButton(text="🔄 Holatni tozalash"), KeyboardButton(text="🔙 Asosiy Menyu")],
        ],
        resize_keyboard=True
    )
    
# ==============================================================================
# -*-*- HOLATNI TOZALASH -*-*-
# ==============================================================================
@dp.message(F.text == "🔄 Holatni tozalash")
async def clear_state(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("✅ Holat tozalandi. Qaytadan boshlang.", reply_markup=admin_keyboard())    
    
# -*-*- PREMIUM BOSHQARUV KLAVIATURASI -*-*-
def premium_management_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Yangi Obuna"), KeyboardButton(text="⏱️ Obunani Uzaytirish")],
            [KeyboardButton(text="❌ Obunani Bekor Qilish"), KeyboardButton(text="📊 Obuna Statistika")],
            [KeyboardButton(text="🔙 Admin Panel")],
        ],
        resize_keyboard=True
    )     
    
# -*-*- BLOKLASH KLAVIATURALARI -*-*-
def block_duration_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="24 soat"), KeyboardButton(text="7 kun")],
            [KeyboardButton(text="Noma'lum muddat"), KeyboardButton(text="🔙 Orqaga")],
        ],
        resize_keyboard=True
    )

def block_confirmation_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Bloklash"), KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True
    )

def unblock_confirmation_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Blokdan ochish"), KeyboardButton(text="❌ Bekor qilish")],
        ],
        resize_keyboard=True
    )    

# -*-*- KONTENT BOSHQARUV KLAVIATURASI -*-*-
def content_management_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎬 Kino Qo'shish"), KeyboardButton(text="📺 Serial Qo'shish")],
            [KeyboardButton(text="📁 Kontentlar Ro'yxati"), KeyboardButton(text="❌ Kontent O'chirish")],
            [KeyboardButton(text="🔙 Admin Panel")],
        ],
        resize_keyboard=True
    )

# -*-*- KINO KATEGORIYALARI KLAVIATURASI -*-*-
def movie_categories_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎭 Hollywood"), KeyboardButton(text="🎬 Hind")],
            [KeyboardButton(text="🎥 Rus"), KeyboardButton(text="🎞️ O'zbek")],
            [KeyboardButton(text="🕌 Islomiy"), KeyboardButton(text="🇹🇷 Turk")],
            [KeyboardButton(text="👶 Bolalar"), KeyboardButton(text="🇰🇷 Koreys")],
            [KeyboardButton(text="🔙 Orqaga")],
        ],
        resize_keyboard=True
    )    
    
# -*-*- PREMIUM BOSHQARUV -*-*-
@dp.message(F.text == "👑 Premium Boshqaruv")
async def premium_management(message: types.Message, state: FSMContext):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        await message.answer(
            "👑 **Premium Boshqaruv Paneliga xush kelibsiz!**\n\n"
            "Quyidagi amallarni bajarishingiz mumkin:\n"
            "• ➕ Yangi obuna qo'shish\n"
            "• ⏱️ Obunani uzaytirish\n"
            "• ❌ Obunani bekor qilish\n"
            "• 📊 Statistikalarni ko'rish\n\n"
            "Foydalanuvchi ID sini yuboring:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(PremiumManagementState.waiting_user_id)
    else:
        await message.answer("Sizga ruxsat yo'q!")
        
# ==============================================================================
# -*-*- BLOK TEKSHIRUV FUNKSIYASI -*-*-
# ==============================================================================

async def check_and_block(message: types.Message):
    """Foydalanuvchi bloklanganligini tekshirish va xabar yuborish"""
    if db.is_user_blocked(message.from_user.id):
        block_info = db.get_blocked_user_info(message.from_user.id)
        if block_info:
            reason, duration, until, blocked_at, blocked_by = block_info
            
            # Muddatni o'qiladigan formatga o'tkazish
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
# -*-*- BLOKLASH HANDLERLARI -*-*-
# ==============================================================================

@dp.message(F.text == "🚫 Bloklash")
async def start_block_user(message: types.Message, state: FSMContext):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        await message.answer(
            "🚫 **Foydalanuvchini Bloklash**\n\n"
            "Bloklamoqchi bo'lgan foydalanuvchi ID sini kiriting:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(BlockUserState.waiting_user_id)
    else:
        await message.answer("Sizga ruxsat yo'q!")

@dp.message(BlockUserState.waiting_user_id)
async def process_block_user_id(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        user_info = db.get_user(user_id)
        
        if user_info:
            await state.update_data(user_id=user_id)
            
            # Foydalanuvchi bloklanganligini tekshirish
            if db.is_user_blocked(user_id):
                block_info = db.get_blocked_user_info(user_id)
                if block_info:
                    reason, duration, until, blocked_at, blocked_by = block_info
                    await message.answer(
                        f"⚠️ **Foydalanuvchi allaqachon bloklangan!**\n\n"
                        f"👤 Foydalanuvchi: {user_info[2]}\n"
                        f"🆔 ID: {user_id}\n"
                        f"📋 Sabab: {reason}\n"
                        f"⏰ Muddat: {duration}\n"
                        f"📅 Bloklangan: {blocked_at}\n"
                        f"👮 Bloklovchi: {blocked_by}",
                        reply_markup=admin_advanced_keyboard()
                    )
                await state.clear()
                return
            
            await state.update_data(user_name=user_info[2])
            await message.answer(
                f"👤 **Foydalanuvchi:** {user_info[2]}\n"
                f"🆔 **ID:** {user_id}\n\n"
                f"Bloklash sababini kiriting:",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.set_state(BlockUserState.waiting_reason)
        else:
            await message.answer("❌ Foydalanuvchi topilmadi!")
            await state.clear()
            
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting:")
        await state.clear()

@dp.message(BlockUserState.waiting_reason)
async def process_block_reason(message: types.Message, state: FSMContext):
    reason = message.text
    await state.update_data(reason=reason)
    
    await message.answer(
        "⏰ **Bloklash muddatini tanlang:**",
        reply_markup=block_duration_keyboard()
    )
    await state.set_state(BlockUserState.waiting_duration)

@dp.message(BlockUserState.waiting_duration)
async def process_block_duration(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Bloklash sababini kiriting:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(BlockUserState.waiting_reason)
        return
        
    duration_map = {
        "24 soat": "24_soat",
        "7 kun": "7_kun", 
        "Noma'lum muddat": "Noma'lum"
    }
    
    duration_key = duration_map.get(message.text)
    if duration_key:
        await state.update_data(block_duration=duration_key, duration_display=message.text)
        
        data = await state.get_data()
        user_id = data['user_id']
        user_name = data['user_name']
        reason = data['reason']
        
        await message.answer(
            f"⚠️ **BLOKLASHNI TASDIQLANG** ⚠️\n\n"
            f"👤 **Foydalanuvchi:** {user_name}\n"
            f"🆔 **ID:** {user_id}\n"
            f"📋 **Sabab:** {reason}\n"
            f"⏰ **Muddat:** {message.text}\n\n"
            f"**Bu foydalanuvchi botdan butunlay bloklanadi!**",
            reply_markup=block_confirmation_keyboard()
        )
        await state.set_state(BlockUserState.waiting_confirmation)
    else:
        await message.answer("❌ Noto'g'ri muddat! Quyidagilardan birini tanlang:")

@dp.message(BlockUserState.waiting_confirmation)
async def process_block_confirmation(message: types.Message, state: FSMContext):
    if message.text == "✅ Bloklash":
        data = await state.get_data()
        user_id = data['user_id']
        user_name = data['user_name']
        reason = data['reason']
        block_duration = data['block_duration']
        duration_display = data['duration_display']
        
        # Foydalanuvchini bloklash
        success = db.block_user(user_id, reason, block_duration, message.from_user.id)
        
        if success:
            # Foydalanuvchiga xabar yuborish
            try:
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
                await bot.send_message(user_id, block_message)
            except Exception as e:
                print(f"Bloklangan foydalanuvchiga xabar yuborishda xatolik: {e}")
            
            await message.answer(
                f"✅ **Foydalanuvchi muvaffaqiyatli bloklandi!**\n\n"
                f"👤 Foydalanuvchi: {user_name}\n"
                f"🆔 ID: {user_id}\n"
                f"📋 Sabab: {reason}\n"
                f"⏰ Muddat: {duration_display}\n\n"
                f"Foydalanuvchiga blok haqida xabar yuborildi.",
                reply_markup=admin_advanced_keyboard()
            )
        else:
            await message.answer(
                "❌ Bloklashda xatolik yuz berdi!",
                reply_markup=admin_advanced_keyboard()
            )
    else:
        await message.answer(
            "❌ Bloklash bekor qilindi.",
            reply_markup=admin_advanced_keyboard()
        )
    
    await state.clear()

# ==============================================================================
# -*-*- BLOKDAN OCHISH HANDLERLARI -*-*-
# ==============================================================================

@dp.message(F.text == "✅ Blokdan ochish")
async def start_unblock_user(message: types.Message, state: FSMContext):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        await message.answer(
            "✅ **Foydalanuvchini Blokdan Ochish**\n\n"
            "Blokdan ochmoqchi bo'lgan foydalanuvchi ID sini kiriting:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(UnblockUserState.waiting_user_id)
    else:
        await message.answer("Sizga ruxsat yo'q!")

@dp.message(UnblockUserState.waiting_user_id)
async def process_unblock_user_id(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        user_info = db.get_user(user_id)
        
        if not user_info:
            await message.answer("❌ Foydalanuvchi topilmadi!", reply_markup=admin_advanced_keyboard())
            await state.clear()
            return
            
        # Foydalanuvchi bloklanganligini tekshirish
        if not db.is_user_blocked(user_id):
            await message.answer(
                f"ℹ️ **Foydalanuvchi bloklanmagan!**\n\n"
                f"👤 Foydalanuvchi: {user_info[2]}\n"
                f"🆔 ID: {user_id}",
                reply_markup=admin_advanced_keyboard()
            )
            await state.clear()
            return
        
        # Foydalanuvchini blokdan ochish
        success = db.unblock_user(user_id)
        
        if success:
            # Foydalanuvchiga xabar yuborish
            try:
                unblock_message = (
                    f"🟢🔓 **Hisobingiz blokdan ochildi!**\n\n"
                    f"Hurmatli foydalanuvchi, sizning profilingiz tekshiruvdan muvaffaqiyatli o'tdi "
                    f"va barcha cheklovlar bekor qilindi.\n"
                    f"Endi xizmatlardan bemalol va to'liq foydalanishingiz mumkin. ✅\n\n"
                    f"⚠️ **Ogohlantirishlar**\n\n"
                    f"Quyidagi qoidalarga rioya qilishingizni so'raymiz:\n\n"
                    f"🚫 Qoidabuzarliklar takrorlansa, hisobingiz yana bloklanishi mumkin\n"
                    f"🛡️ Xizmatdan tartibli va odobli foydalaning\n"
                    f"📛 Spam, haqorat yoki reklama — qat'iyan taqiqlanadi\n"
                    f"📌 Profilingiz xavfsizligi uchun shaxsiy ma'lumotlarni tarqatmang\n\n"
                    f"❓ **Qo'shimcha savollar bo'lsa:**\n\n"
                    f"📩 **Admin:** @Operator_1985"
                )
                await bot.send_message(user_id, unblock_message)
            except Exception as e:
                print(f"Xabar yuborishda xatolik: {e}")
            
            await message.answer(
                f"✅ **Foydalanuvchi blokdan ochildi!**\n\n"
                f"👤 Foydalanuvchi: {user_info[2]}\n"
                f"🆔 ID: {user_id}\n\n"
                f"Foydalanuvchiga blokdan ochilgani haqida xabar yuborildi.",
                reply_markup=admin_advanced_keyboard()
            )
        else:
            await message.answer("❌ Blokdan ochishda xatolik!", reply_markup=admin_advanced_keyboard())
            
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting:", reply_markup=admin_advanced_keyboard())
    
    await state.clear()    
    
# ==============================================================================
# -*-*- YUKLAB OLISH HANDLERLARI -*-*-
# ==============================================================================

@dp.message(F.text == "📥 Yuklab olish")
async def download_movie_handler(message: types.Message, state: FSMContext):
    """Kino yuklab olish"""
    # Blok tekshiruvi
    if await check_and_block(message):
        return
    
    # State dan kino ma'lumotlarini olish
    data = await state.get_data()
    movie_id = data.get('movie_id')
    movie_title = data.get('movie_title', "Noma'lum")
    
    if not movie_id:
        await message.answer("❌ Kino ma'lumotlari topilmadi. Qaytadan urinib ko'ring.")
        return
    
    # Kino ma'lumotlarini olish
    movie = db.get_movie_by_id(movie_id)
    if not movie:
        await message.answer("❌ Kino topilmadi.")
        return
    
    movie_price = movie[5]  # price
    
    # FAQAT PULLIK KINOLARNI YUKLAB OLISH MUMKIN
    if movie_price == 0:
        await message.answer(
            "❌ **Bepul kinolarni yuklab olish mumkin emas!**\n\n"
            "Faqat sotib olingan pullik kinolarni yuklab olishingiz mumkin.\n\n"
            "💡 **Maslahat:** Pullik kinoni sotib oling yoki Premium obunaga o'ting.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="💳 Kino sotib olish"), KeyboardButton(text="💎 Premium obuna")],
                    [KeyboardButton(text="🔙 Orqaga")]
                ],
                resize_keyboard=True
            )
        )
        return
    
    # Foydalanuvchi yuklab olish huquqiga ega ekanligini tekshirish
    can_download = db.can_user_download(message.from_user.id, movie_id)
    
    if not can_download:
        await message.answer(
            "❌ **Yuklab olish huquqi yo'q!**\n\n"
            "Yuklab olish uchun quyidagi shartlardan biri bajarilishi kerak:\n"
            "• Kino sotib olingan bo'lishi\n"
            "• Premium obuna faol bo'lishi\n\n"
            "💡 **Maslahat:** Kino sotib oling yoki Premium obunaga o'ting.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="💳 Kino sotib olish"), KeyboardButton(text="💎 Premium obuna")],
                    [KeyboardButton(text="🔙 Orqaga")]
                ],
                resize_keyboard=True
            )
        )
        return
    
    movie_file_id = movie[4]  # file_id
    
    # Yuklab olish xabari
    await message.answer(
        f"📥 **Yuklab olish boshlandi...**\n\n"
        f"🎬 **Kino:** {movie_title}\n"
        f"💵 **Narxi:** {movie_price:,} so'm\n"
        f"📊 **Hajmi:** ~500MB\n"
        f"⏰ **Vaqt:** 1-2 daqiqa\n\n"
        f"Video yuklanmoqda...",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Video yuborish (yuklab olish)
    try:
        await message.answer_video(
            video=movie_file_id,
            caption=f"📥 **{movie_title}** - Yuklab olindi!\n\n"
                   f"💵 **Narxi:** {movie_price:,} so'm\n"
                   f"✅ **Holati:** Sotib olingan\n\n"
                   f"Video saqlandi. Endi oflayn rejimda tomosha qilishingiz mumkin.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="🎬 Boshqa kinolar"), KeyboardButton(text="🔙 Asosiy Menyu")]
                ],
                resize_keyboard=True
            )
        )
        
        # Yuklab olishni log qilish
        db.log_download(
            user_id=message.from_user.id,
            content_id=movie_id,
            content_name=movie_title,
            price=movie_price,
            download_type="paid_download"
        )
        
    except Exception as e:
        await message.answer(
            f"❌ **Yuklab olishda xatolik!**\n\n"
            f"Xatolik: {e}\n\n"
            f"Iltimos, keyinroq urinib ko'ring.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="🔙 Orqaga")]
                ],
                resize_keyboard=True
            )
        )

@dp.message(F.text == "💳 Kino sotib olish")
async def buy_for_download(message: types.Message, state: FSMContext):
    """Yuklab olish uchun kino sotib olish"""
    await start_payment(message, state)

@dp.message(F.text == "💎 Premium obuna")
async def premium_for_download(message: types.Message):
    """Yuklab olish uchun premium obuna"""
    await premium_subscription(message)
        
# ==============================================================================
# -*-*- KONTENT BOSHQARUV HANDLERLARI -*-*-
# ==============================================================================

# -*-*- KONTENT QO'SHISH -*-*-
@dp.message(F.text == "🎬 Kontent Qo'shish")
async def content_management(message: types.Message):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        await message.answer(
            "🎬 **Kontent Boshqaruv Paneliga xush kelibsiz!**\n\n"
            "Quyidagi amallarni bajarishingiz mumkin:\n"
            "• 🎬 Kino qo'shish\n"
            "• 📺 Serial qo'shish\n"
            "• 📁 Kontentlar ro'yxati\n"
            "• ❌ Kontent o'chirish\n\n"
            "Amalni tanlang:",
            reply_markup=content_management_keyboard()
        )
    else:
        await message.answer("Sizga ruxsat yo'q!")        

# -*-*- KINO QO'SHISH BOSHLASH -*-*-
@dp.message(F.text == "🎬 Kino Qo'shish")
async def start_add_movie(message: types.Message, state: FSMContext):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        await message.answer(
            "🎬 **Yangi Kino Qo'shish**\n\n"
            "Kino nomini kiriting:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(ContentManagementState.waiting_movie_title)
    else:
        await message.answer("Sizga ruxsat yo'q!")

# -*-*- KINO NOMI QABUL QILISH -*-*-
@dp.message(ContentManagementState.waiting_movie_title)
async def process_movie_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("📝 Kino tavsifini kiriting:")
    await state.set_state(ContentManagementState.waiting_movie_description)

# -*-*- KINO TAVSIFI QABUL QILISH -*-*-
@dp.message(ContentManagementState.waiting_movie_description)
async def process_movie_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        "📁 Asosiy kategoriyani tanlang:",
        reply_markup=get_category_keyboard("main")
    )
    await state.set_state(ContentManagementState.waiting_main_category)

# -*-*- ASOSIY KATEGORIYA TANLASH -*-*-
@dp.message(ContentManagementState.waiting_main_category)
async def process_main_category(message: types.Message, state: FSMContext):
    if message.text == "🔙 Asosiy Menyu":
        await message.answer("Amalni tanlang:", reply_markup=content_management_keyboard())
        await state.clear()
        return
        
    # ASOSIY KATEGORIYANI SAQLAYMIZ
    await state.update_data(main_category=message.text)
    
    # FAQAT HOLLYWOOD BO'LIMI UCHUN ICHKI KATEGORIYA (AKTYOR) SO'RAYMIZ
    if message.text == "🎭 Hollywood Kinolari":
        await message.answer(
            f"📁 **{message.text}** bo'limi uchun ichki kategoriyani tanlang:",
            reply_markup=get_category_keyboard("sub", message.text)
        )
        await state.set_state(ContentManagementState.waiting_sub_category)
    else:
        # BOSHQA BO'LIMLAR UCHUN ICHKI KATEGORIYANI O'TKAZIB YUBORAMIZ
        await state.update_data(
            sub_category=message.text,  # Asosiy kategoriyani ichki kategoriya sifatida saqlaymiz
            actor=""  # Aktyor nomi bo'sh
        )
        
        await message.answer(
            "💵 Kino narxini kiriting (so'mda):\n0 - Bepul\n30000 - Yuklab olish uchun",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(ContentManagementState.waiting_movie_price)

# -*-*- ICHKI KATEGORIYA TANLASH -*-*-
@dp.message(ContentManagementState.waiting_main_category)
async def process_main_category(message: types.Message, state: FSMContext):
    if message.text == "🔙 Asosiy Menyu":
        await message.answer("Amalni tanlang:", reply_markup=content_management_keyboard())
        await state.clear()
        return
        
    # ASOSIY KATEGORIYANI SAQLAYMIZ VA ICHKI KATEGORIYANI O'TKAZIB YUBORAMIZ
    await state.update_data(
        main_category=message.text, 
        sub_category=message.text,  # Asosiy kategoriyani ichki kategoriya sifatida saqlaymiz
        actor=""  # Aktyor nomi bo'sh
    )
    
    # ICHKI KATEGORIYANI SO'RAMAYMIZ, TO'GRIDAN-TO'G'RI NARX SO'RAYMIZ
    await message.answer(
        "💵 Kino narxini kiriting (so'mda):\n0 - Bepul\n30000 - Yuklab olish uchun",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(ContentManagementState.waiting_movie_price)
    
# -*-*- KINO NARXI QABUL QILISH -*-*-
@dp.message(ContentManagementState.waiting_movie_price)
async def process_movie_price(message: types.Message, state: FSMContext):
    print(f"DEBUG: Narx kiritildi: '{message.text}'")
    
    try:
        price = int(message.text)
        await state.update_data(price=price)
        print(f"DEBUG: Narx saqlandi: {price}")
        
        # BU QATOR BANNER SO'RASH KERAK
        await message.answer("🖼️ **Kino bannerini yuboring (rasm):**\n\nPoster yoki reklama rasmni yuboring:")
        await state.set_state(ContentManagementState.waiting_movie_banner)  # <- BU HOLATGA O'TISH KERAK
        
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting:")
        
# ==============================================================================
# -*-*- BLOKLASH HANDLERLARI -*-*-
# ==============================================================================

@dp.message(F.text == "🚫 Bloklash")
async def start_block_user(message: types.Message, state: FSMContext):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        await message.answer(
            "🚫 **Foydalanuvchini Bloklash**\n\n"
            "Bloklamoqchi bo'lgan foydalanuvchi ID sini kiriting:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(BlockUserState.waiting_user_id)
    else:
        await message.answer("Sizga ruxsat yo'q!")

@dp.message(BlockUserState.waiting_user_id)
async def process_block_user_id(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        user_info = db.get_user(user_id)
        
        if user_info:
            await state.update_data(user_id=user_id)
            
            # Foydalanuvchi bloklanganligini tekshirish
            if db.is_user_blocked(user_id):
                block_info = db.get_blocked_user_info(user_id)
                if block_info:
                    reason, duration, until, blocked_at, blocked_by = block_info
                    await message.answer(
                        f"⚠️ **Foydalanuvchi allaqachon bloklangan!**\n\n"
                        f"👤 Foydalanuvchi: {user_info[2]}\n"
                        f"🆔 ID: {user_id}\n"
                        f"📋 Sabab: {reason}\n"
                        f"⏰ Muddat: {duration}\n"
                        f"📅 Bloklangan: {blocked_at}\n"
                        f"👮 Bloklovchi: {blocked_by}",
                        reply_markup=admin_advanced_keyboard()
                    )
                await state.clear()
                return
            
            await state.update_data(user_name=user_info[2])
            await message.answer(
                f"👤 **Foydalanuvchi:** {user_info[2]}\n"
                f"🆔 **ID:** {user_id}\n\n"
                f"Bloklash sababini kiriting:",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.set_state(BlockUserState.waiting_reason)
        else:
            await message.answer("❌ Foydalanuvchi topilmadi!")
            await state.clear()
            
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting:")
        await state.clear()

@dp.message(BlockUserState.waiting_reason)
async def process_block_reason(message: types.Message, state: FSMContext):
    reason = message.text
    await state.update_data(reason=reason)
    
    await message.answer(
        "⏰ **Bloklash muddatini tanlang:**",
        reply_markup=block_duration_keyboard()
    )
    await state.set_state(BlockUserState.waiting_duration)

@dp.message(BlockUserState.waiting_duration)
async def process_block_duration(message: types.Message, state: FSMContext):
    if message.text == "🔙 Orqaga":
        await message.answer("Bloklash sababini kiriting:", reply_markup=ReplyKeyboardRemove())
        await state.set_state(BlockUserState.waiting_reason)
        return
        
    duration_map = {
        "24 soat": "24_soat",
        "7 kun": "7_kun", 
        "Noma'lum muddat": "Noma'lum"
    }
    
    duration_key = duration_map.get(message.text)
    if duration_key:
        await state.update_data(block_duration=duration_key, duration_display=message.text)
        
        data = await state.get_data()
        user_id = data['user_id']
        user_name = data['user_name']
        reason = data['reason']
        
        await message.answer(
            f"⚠️ **BLOKLASHNI TASDIQLANG** ⚠️\n\n"
            f"👤 **Foydalanuvchi:** {user_name}\n"
            f"🆔 **ID:** {user_id}\n"
            f"📋 **Sabab:** {reason}\n"
            f"⏰ **Muddat:** {message.text}\n\n"
            f"**Bu foydalanuvchi botdan butunlay bloklanadi!**",
            reply_markup=block_confirmation_keyboard()
        )
        await state.set_state(BlockUserState.waiting_confirmation)
    else:
        await message.answer("❌ Noto'g'ri muddat! Quyidagilardan birini tanlang:")

@dp.message(BlockUserState.waiting_confirmation)
async def process_block_confirmation(message: types.Message, state: FSMContext):
    if message.text == "✅ Bloklash":
        data = await state.get_data()
        user_id = data['user_id']
        user_name = data['user_name']
        reason = data['reason']
        block_duration = data['block_duration']
        duration_display = data['duration_display']
        
        # Foydalanuvchini bloklash
        success = db.block_user(user_id, reason, block_duration, message.from_user.id)
        
        if success:
            # Foydalanuvchiga xabar yuborish
            try:
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
                await bot.send_message(user_id, block_message)
            except Exception as e:
                print(f"Bloklangan foydalanuvchiga xabar yuborishda xatolik: {e}")
            
            await message.answer(
                f"✅ **Foydalanuvchi muvaffaqiyatli bloklandi!**\n\n"
                f"👤 Foydalanuvchi: {user_name}\n"
                f"🆔 ID: {user_id}\n"
                f"📋 Sabab: {reason}\n"
                f"⏰ Muddat: {duration_display}\n\n"
                f"Foydalanuvchiga blok haqida xabar yuborildi.",
                reply_markup=admin_advanced_keyboard()
            )
        else:
            await message.answer(
                "❌ Bloklashda xatolik yuz berdi!",
                reply_markup=admin_advanced_keyboard()
            )
    else:
        await message.answer(
            "❌ Bloklash bekor qilindi.",
            reply_markup=admin_advanced_keyboard()
        )
    
    await state.clear()

# ==============================================================================
# -*-*- BLOKDAN OCHISH HANDLERLARI -*-*-
# ==============================================================================

@dp.message(F.text == "✅ Blokdan ochish")
async def start_unblock_user(message: types.Message, state: FSMContext):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        await message.answer(
            "✅ **Foydalanuvchini Blokdan Ochish**\n\n"
            "Blokdan ochmoqchi bo'lgan foydalanuvchi ID sini kiriting:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(UnblockUserState.waiting_user_id)
    else:
        await message.answer("Sizga ruxsat yo'q!")

@dp.message(UnblockUserState.waiting_user_id)
async def process_unblock_user_id(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        user_info = db.get_user(user_id)
        
        if not user_info:
            await message.answer("❌ Foydalanuvchi topilmadi!", reply_markup=admin_advanced_keyboard())
            await state.clear()
            return
            
        # Foydalanuvchi bloklanganligini tekshirish
        if not db.is_user_blocked(user_id):
            await message.answer(
                f"ℹ️ **Foydalanuvchi bloklanmagan!**\n\n"
                f"👤 Foydalanuvchi: {user_info[2]}\n"
                f"🆔 ID: {user_id}",
                reply_markup=admin_advanced_keyboard()
            )
            await state.clear()
            return
        
        # Foydalanuvchini blokdan ochish
        success = db.unblock_user(user_id)
        
        if success:
            # Foydalanuvchiga xabar yuborish
            try:
                unblock_message = (
                    f"🟢🔓 **Hisobingiz blokdan ochildi!**\n\n"
                    f"Hurmatli foydalanuvchi, sizning profilingiz tekshiruvdan muvaffaqiyatli o'tdi "
                    f"va barcha cheklovlar bekor qilindi.\n"
                    f"Endi xizmatlardan bemalol va to'liq foydalanishingiz mumkin.\n\n"
                    f"📞 **Admin:** @Operator_1985"
                )
                await bot.send_message(user_id, unblock_message)
            except Exception as e:
                print(f"Xabar yuborishda xatolik: {e}")
            
            await message.answer(
                f"✅ **Foydalanuvchi blokdan ochildi!**\n\n"
                f"👤 Foydalanuvchi: {user_info[2]}\n"
                f"🆔 ID: {user_id}",
                reply_markup=admin_advanced_keyboard()
            )
        else:
            await message.answer("❌ Blokdan ochishda xatolik!", reply_markup=admin_advanced_keyboard())
            
    except ValueError:
        await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting:", reply_markup=admin_advanced_keyboard())
    
    await state.clear()

@dp.message(F.text.in_(["✅ HA, blokdan ochish", "❌ BEKOR QILISH"]))
async def process_unblock_confirmation(message: types.Message, state: FSMContext):
    # Faqat state da ma'lumot bo'lsa ishlaydi
    data = await state.get_data()
    if not data:
        await message.answer("Sessiya muddati o'tgan. Qaytadan boshlang.", reply_markup=admin_advanced_keyboard())
        await state.clear()
        return
        
    if message.text == "✅ HA, blokdan ochish":
        user_id = data['user_id']
        user_name = data['user_name']
        
        print(f"DEBUG: Blokdan ochish - User: {user_id}")  # DEBUG
        
        # Foydalanuvchini blokdan ochish
        success = db.unblock_user(user_id)
        
        if success:
            # Foydalanuvchiga xabar yuborish - YANGILANGAN XABAR
            try:
                unblock_message = (
                    f"🟢🔓 **Hisobingiz blokdan ochildi!**\n\n"
                    f"Hurmatli foydalanuvchi, sizning profilingiz tekshiruvdan muvaffaqiyatli o'tdi "
                    f"va barcha cheklovlar bekor qilindi.\n"
                    f"Endi xizmatlardan bemalol va to'liq foydalanishingiz mumkin. ✅\n\n"
                    f"⚠️ **Ogohlantirishlar**\n\n"
                    f"Quyidagi qoidalarga rioya qilishingizni so'raymiz:\n\n"
                    f"🚫 Qoidabuzarliklar takrorlansa, hisobingiz yana bloklanishi mumkin\n"
                    f"🛡️ Xizmatdan tartibli va odobli foydalaning\n"
                    f"📛 Spam, haqorat yoki reklama — qat'iyan taqiqlanadi\n"
                    f"📌 Profilingiz xavfsizligi uchun shaxsiy ma'lumotlarni tarqatmang\n\n"
                    f"❓ **Qo'shimcha savollar bo'lsa:**\n\n"
                    f"📩 **Admin:** @Operator_1985"
                )
                await bot.send_message(user_id, unblock_message)
            except Exception as e:
                print(f"Xabar yuborishda xatolik: {e}")
            
            await message.answer(
                f"✅ **Foydalanuvchi blokdan ochildi!**\n\n"
                f"👤 Foydalanuvchi: {user_name}\n"
                f"🆔 ID: {user_id}\n\n"
                f"Foydalanuvchiga blokdan ochilgani haqida xabar yuborildi.",
                reply_markup=admin_advanced_keyboard()
            )
        else:
            await message.answer("❌ Blokdan ochishda xatolik!", reply_markup=admin_advanced_keyboard())
    else:
        await message.answer("❌ Blokdan ochish bekor qilindi.", reply_markup=admin_advanced_keyboard())
    
    await state.clear()  

# ==============================================================================
# -*-*- BARCHA KONTENTLAR HANDLERI -*-*-
# ==============================================================================

@dp.message(F.text == "🎬 Barcha Kontentlar")
async def all_content(message: types.Message):
    """Barcha kontentlarni ko'rsatish"""
    # Blok tekshiruvi
    if await check_and_block(message):
        return
    
    # Barcha kinolarni olish (bepullar birinchi)
    movies = db.get_all_movies_sorted()
    
    if not movies:
        await message.answer(
            "❌ Hozircha hech qanday kontent mavjud emas.",
            reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
        )
        return
    
    # Kontentlarni guruhlash
    free_movies = [m for m in movies if m[5] == 0]  # price = 0
    paid_movies = [m for m in movies if m[5] > 0]   # price > 0
    
    # Klaviatura yaratish
    keyboard = []
    
    # Bepul kinolar
    for movie in free_movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, banner_file_id, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Asosiy Menyu")])
    
    await message.answer(
        f"🎬 **Barcha Kontentlar**\n\n"
        f"🆓 **Bepul kinolar:** {len(free_movies)} ta\n"
        f"💵 **Pullik kinolar:** {len(paid_movies)} ta\n"
        f"📊 **Jami:** {len(movies)} ta kino\n\n"
        f"Kerakli kinoni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
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

@dp.message(SearchState.waiting_search_query)
async def process_search(message: types.Message, state: FSMContext):
    """Qidiruv natijalarini ko'rsatish"""
    # Blok tekshiruvi
    if await check_and_block(message):
        await state.clear()
        return
    
    search_query = message.text.strip()
    
    # Agar "Asosiy Menyu" bosilsa
    if search_query == "🔙 Asosiy Menyu":
        await message.answer(
            "Asosiy menyuga qaytingiz:",
            reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
        )
        await state.clear()
        return
    
    # Qidiruv so'rovi qisqa bo'lsa
    if len(search_query) < 2:
        await message.answer(
            "❌ Qidiruv so'rovi juda qisqa! Kamida 2 ta belgi kiriting.",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="🔙 Asosiy Menyu")]
                ],
                resize_keyboard=True
            )
        )
        return
    
    # Loading xabari
    search_msg = await message.answer("🔍 **Qidirilmoqda...**")
    
    # Kinolarni qidirish
    movies = db.search_movies(search_query)
    
    await search_msg.delete()
    
    if not movies:
        await message.answer(
            f"❌ **'{search_query}' bo'yicha hech narsa topilmadi**\n\n"
            f"Qidiruv bo'yicha maslahatlar:\n"
            f"• Kino nomini to'g'ri yozganingizni tekshiring\n"
            f"• Qisqaroq so'z yozib ko'ring\n"
            f"• Boshqa tilarda yozib ko'ring\n"
            f"• Aktyor nomini yozing",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="🔍 Qayta qidirish"), KeyboardButton(text="🔙 Asosiy Menyu")]
                ],
                resize_keyboard=True
            )
        )
        return
    
    # Kontentlarni guruhlash
    free_movies = [m for m in movies if m[5] == 0]  # price = 0
    paid_movies = [m for m in movies if m[5] > 0]   # price > 0
    
    # Klaviatura yaratish
    keyboard = []
    
    # Bepul kinolar
    for movie in free_movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, banner_file_id, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    # Pullik kinolar
    for movie in paid_movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, banner_file_id, created_at, added_by = movie
        button_text = f"💵 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔍 Qayta qidirish"), KeyboardButton(text="🔙 Asosiy Menyu")])
    
    await message.answer(
        f"🔍 **Qidiruv natijalari: '{search_query}'**\n\n"
        f"🆓 **Bepul kinolar:** {len(free_movies)} ta\n"
        f"💵 **Pullik kinolar:** {len(paid_movies)} ta\n"
        f"📊 **Jami topilgan:** {len(movies)} ta\n\n"
        f"Kerakli kinoni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )
    
    await state.clear()

@dp.message(F.text == "🔍 Qayta qidirish")
async def search_again(message: types.Message, state: FSMContext):
    """Qayta qidirish"""
    await search_handler(message, state)    
        
# ==============================================================================
# -*-*- KONTENT BANNERI YUBORISH (EMERGENCY FIX) -*-*-
# ==============================================================================
async def send_content_banner(message: types.Message, movie, user_id):
    """Kontent bannerini yuborish"""
    try:
        # 11 TA USTUNNI OLISH
        movie_id, title, description, category, file_id, price, is_premium, actor_name, banner_file_id, created_at, added_by = movie
        
        print(f"🚨 EMERGENCY DEBUG: Kino: {title}, Narx: {price}, User: {user_id}")
        
        # Foydalanuvchi holatini TEKSHRISH
        user_has_purchased = db.check_user_purchase(user_id, movie_id)
        is_premium_user = db.check_premium_status(user_id)
        can_download = db.can_user_download(user_id, movie_id)  # <- YANGI
        
        print(f"🚨 EMERGENCY DEBUG: Sotib olgan: {user_has_purchased}, Premium: {is_premium_user}, Yuklab olish: {can_download}")
        
        # Banner matni
        caption = (
            f"🎬 **{title}**\n\n"
            f"📝 {description}\n\n"
            f"🎭 **Aktyor:** {actor_name}\n"
            f"📁 **Kategoriya:** {category}\n"
            f"💵 **Narxi:** {price:,} so'm\n"
            f"📊 **Sifat:** HD 1080p\n\n"
        )
        
        # HOLATNI ANIQLASH
        can_watch = False
        download_button = None
        
        if price == 0:
            caption += "🆓 **Bepul kontent** - Darrov ko'rashingiz mumkin!"
            can_watch = True
            # Bepul kinolar uchun YUKLAB OLISH TUGMASI YO'Q
        elif user_has_purchased:
            caption += "✅ **Sotib olingan** - Darrov ko'rashingiz mumkin!"
            can_watch = True
            download_button = KeyboardButton(text="📥 Yuklab olish")  # Sotib olingan uchun yuklab olish
        elif is_premium_user:
            caption += "👑 **Premium** - Darrov ko'rashingiz mumkin!"
            can_watch = True
            download_button = KeyboardButton(text="📥 Yuklab olish")  # Premium uchun yuklab olish
        else:
            caption += "🔒 **Pullik kontent** - Yuklab olish uchun to'lov qiling"
            can_watch = False
            download_button = KeyboardButton(text="💳 Yuklab olish uchun to'lash")
        
        print(f"🚨 EMERGENCY DEBUG: Ko'rish ruxsati: {can_watch}, Yuklab olish: {can_download}")
        
        # 1. ALOHIDA BANNER RASMI YUBORISH
        if banner_file_id:
            await message.answer_photo(
                photo=banner_file_id,
                caption=caption
            )
        
        # 2. VIDEO YUBORISH - FAQAT CAN_WATCH = TRUE BO'LSA
        if can_watch:
            print(f"🚨 EMERGENCY DEBUG: TO'LIQ VIDEO YUBORILMOQDA")
            
            # Klaviatura yaratish
            keyboard_buttons = []
            
            # FAQAT PULLIK KINOLAR UCHUN YUKLAB OLISH TUGMASI
            if price > 0 and download_button:
                keyboard_buttons.append([download_button])
            
            keyboard_buttons.append([KeyboardButton(text="🔙 Orqaga")])
            
            # Video yuborish
            await message.answer_video(
                video=file_id,
                caption="🎬 **Video** - Play tugmasini bosing va tomosha qiling!",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=keyboard_buttons,
                    resize_keyboard=True
                )
            )
        else:
            print(f"🚨 EMERGENCY DEBUG: FAQAT PREVIEW YUBORILMOQDA")
            # Pullik kontent - FAQAT XABAR, VIDEO EMAS!
            await message.answer(
                "🔒 **PULLIK KONTENT**\n\n"
                "Bu kino pullik! To'liq ko'rish uchun quyidagi tugma orqali to'lov qiling:",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text="💳 Yuklab olish uchun to'lash")],
                        [KeyboardButton(text="🔙 Orqaga")],
                    ],
                    resize_keyboard=True
                )
            )
        
        print(f"🚨 EMERGENCY DEBUG: Jarayon tugadi")
        
    except Exception as e:
        print(f"🚨 EMERGENCY DEBUG: Xatolik: {e}")
        await message.answer(f"❌ Xatolik: {e}")
        
# -*-*- KINO BANNERI QABUL QILISH -*-*-
@dp.message(ContentManagementState.waiting_movie_banner, F.photo)
async def process_movie_banner(message: types.Message, state: FSMContext):
    banner_file_id = message.photo[-1].file_id
    await state.update_data(banner_file_id=banner_file_id)
    await message.answer("📁 **Kino faylini yuboring (video):**")
    await state.set_state(ContentManagementState.waiting_movie_file)        
        
# -*-*- KINO FAYLI QABUL QILISH -*-*-
@dp.message(ContentManagementState.waiting_movie_file, F.video)
async def process_movie_file(message: types.Message, state: FSMContext):
    global last_movie_processing_time
    
    current_time = time.time()
    if current_time - last_movie_processing_time < 5:
        return
    last_movie_processing_time = current_time
    
    print(f"🎬 DEBUG: Video qabul qilindi - {message.video.file_id}")
    
    data = await state.get_data()
    print(f"🎬 DEBUG: State data: {data}")
    
    if not data:
        await message.answer("❌ Ma'lumotlar topilmadi.", reply_markup=admin_advanced_keyboard())
        return
    
    required_fields = ['title', 'description', 'main_category', 'sub_category', 'actor', 'price', 'banner_file_id']
    for field in required_fields:
        if field not in data:
            await message.answer(f"❌ {field} maydoni topilmadi.", reply_markup=admin_advanced_keyboard())
            await state.clear()
            return
    
    full_category = f"{data['main_category']} - {data['sub_category']}"
    
    print(f"🎬 DEBUG: Kino qo'shilmoqda - {data['title']}, {full_category}")
    
    # Kino qo'shish (banner bilan)
    movie_id = db.add_movie(
        title=data['title'],
        description=data['description'],
        category=full_category,
        file_id=message.video.file_id,
        price=data['price'],
        is_premium=(data['price'] > 0),
        added_by=message.from_user.id,
        actor_name=data['actor'],
        banner_file_id=data['banner_file_id']
    )
    
    print(f"🎬 DEBUG: Kino qo'shildi - ID: {movie_id}")
    
    await state.clear()
    
    await message.answer(
        f"✅ **Kino Muvaffaqiyatli Qo'shildi!**\n\n"
        f"🎬 Nomi: {data['title']}\n"
        f"🎭 Aktyor: {data['actor']}\n"
        f"📁 Kategoriya: {full_category}\n"
        f"💵 Narxi: {data['price']} so'm\n"
        f"🖼️ Banner: ✅\n"
        f"🔓 Holati: {'Pullik' if data['price'] > 0 else 'Bepul'}\n"
        f"🆔 ID: {movie_id}",
        reply_markup=admin_advanced_keyboard()
    )

# -*-*- KONTENTLAR RO'YXATI -*-*-
@dp.message(F.text == "📁 Kontentlar Boshqaruvi")
async def content_list_management(message: types.Message):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        await message.answer(
            "📁 **Kontentlar Boshqaruvi**\n\n"
            "Bu yerda barcha kontentlarni ko'rishingiz va boshqarishingiz mumkin:",
            reply_markup=content_management_keyboard()
        )
    else:
        await message.answer("Sizga ruxsat yo'q!")        

# -*-*- FOYDALANUVCHI ID QABUL QILISH -*-*-
@dp.message(PremiumManagementState.waiting_user_id)
async def process_user_id(message: types.Message, state: FSMContext):
    try:
        user_id = int(message.text)
        user_info = db.get_user(user_id)
        
        if user_info:
            await state.update_data(user_id=user_id)
            
            # Foydalanuvchi ma'lumotlari
            user_name = user_info[2] if user_info[2] else "Noma'lum"
            is_premium = db.check_premium_status(user_id)
            
            premium_status = "✅ Faol" if is_premium else "❌ Faol emas"
            
            await message.answer(
                f"👤 **Foydalanuvchi Ma'lumotlari:**\n"
                f"🆔 ID: {user_id}\n"
                f"📛 Ism: {user_name}\n"
                f"💎 Premium: {premium_status}\n\n"
                f"Quyidagi amallardan birini tanlang:",
                reply_markup=premium_management_keyboard()
            )
            await state.set_state(PremiumManagementState.waiting_action)
        else:
            await message.answer(
                "❌ Foydalanuvchi topilmadi! ID ni tekshirib qayta kiriting:",
                reply_markup=admin_keyboard()
            )
            await state.clear()
            
    except ValueError:
        await message.answer(
            "❌ Noto'g'ri format! Faqat raqam kiriting:",
            reply_markup=admin_keyboard()
        )
        await state.clear()

# -*-*- AMAL TANLASH -*-*-
@dp.message(PremiumManagementState.waiting_action)
async def process_action(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    
    if message.text == "➕ Yangi Obuna":
        await message.answer(
            "Obuna muddatini kiriting (kunlarda):\n"
            "Masalan: 30 (1 oy)",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(PremiumManagementState.waiting_duration)
        
    elif message.text == "⏱️ Obunani Uzaytirish":
        if db.check_premium_status(user_id):
            await message.answer(
                "Qancha kun uzaytirmoqchisiz?",
                reply_markup=ReplyKeyboardRemove()
            )
            await state.set_state(PremiumManagementState.waiting_duration)
        else:
            await message.answer(
                "❌ Bu foydalanuvchida premium obuna mavjud emas!",
                reply_markup=premium_management_keyboard()
            )
            
    elif message.text == "❌ Obunani Bekor Qilish":
        if db.check_premium_status(user_id):
            await message.answer(
                "⚠️ **Obunani bekor qilish**\n\n"
                "Haqiqatan ham bu foydalanuvchining premium obunasini bekor qilmoqchimisiz?\n\n"
                "✅ Ha - obuna bekor qilinadi\n"
                "❌ Yo'q - bekor qilish",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(text="✅ Ha"), KeyboardButton(text="❌ Yo'q")]
                    ],
                    resize_keyboard=True
                )
            )
            await state.set_state(PremiumManagementState.waiting_confirmation)
        else:
            await message.answer(
                "❌ Bu foydalanuvchida premium obuna mavjud emas!",
                reply_markup=premium_management_keyboard()
            )
            
    elif message.text == "📊 Obuna Statistika":
        stats = db.get_premium_stats()
        user_info = db.get_user(user_id)
        user_name = user_info[2] if user_info[2] else "Noma'lum"
        
        await message.answer(
            f"📊 **Obuna Statistika:**\n\n"
            f"👤 Foydalanuvchi: {user_name}\n"
            f"🆔 ID: {user_id}\n"
            f"💎 Status: {'Premium' if db.check_premium_status(user_id) else 'Oddiy'}\n\n"
            f"📈 Umumiy statistika:\n"
            f"• Premium a'zolar: {stats['premium_users']} ta\n"
            f"• Oylik daromad: {stats['monthly_income']:,} so'm",
            reply_markup=premium_management_keyboard()
        )
        
    elif message.text == "🔙 Admin Panel":
        await message.answer(
            "Admin panelga qaytingiz:",
            reply_markup=admin_keyboard()
        )
        await state.clear()

# -*-*- OBUNA MUDDATI QABUL QILISH -*-*-
@dp.message(PremiumManagementState.waiting_duration)
async def process_duration(message: types.Message, state: FSMContext):
    try:
        duration = int(message.text)
        data = await state.get_data()
        user_id = data['user_id']
        user_info = db.get_user(user_id)
        user_name = user_info[2] if user_info[2] else "Noma'lum"
        
        # Premium obunani qo'shish
        db.add_premium_subscription(user_id, duration)
        
        await message.answer(
            f"✅ **Premium Obuna Muvaffaqiyatli Qo'shildi!**\n\n"
            f"👤 Foydalanuvchi: {user_name}\n"
            f"🆔 ID: {user_id}\n"
            f"⏱️ Muddat: {duration} kun\n"
            f"📅 Tugash sanasi: {duration} kundan keyin\n\n"
            f"Foydalanuvchiga xabar yuborildi.",
            reply_markup=admin_keyboard()
        )
        
        # Foydalanuvchiga bildirishnoma yuborish
        try:
            await bot.send_message(
                user_id,
                f"🎉 **Tabriklaymiz!**\n\n"
                f"Sizga premium obuna berildi!\n"
                f"⏱️ Muddat: {duration} kun\n"
                f"💎 Endi barcha kontentlardan foydalanishingiz mumkin!"
            )
        except:
            print(f"Foydalanuvchi {user_id} ga xabar yuborishda xatolik")
            
        await state.clear()
        
    except ValueError:
        await message.answer(
            "❌ Noto'g'ri format! Faqat raqam kiriting:"
        )

# -*-*- TASDIQLASH -*-*-
@dp.message(PremiumManagementState.waiting_confirmation)
async def process_confirmation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    user_info = db.get_user(user_id)
    user_name = user_info[2] if user_info[2] else "Noma'lum"
    
    if message.text == "✅ Ha":
        # Premium obunani bekor qilish
        # Bu yerda database funksiyasi kerak
        await message.answer(
            f"✅ **Premium Obuna Bekor Qilindi!**\n\n"
            f"👤 Foydalanuvchi: {user_name}\n"
            f"🆔 ID: {user_id}\n"
            f"💎 Status: Oddiy foydalanuvchi\n\n"
            f"Foydalanuvchiga xabar yuborildi.",
            reply_markup=admin_keyboard()
        )
        
        # Foydalanuvchiga bildirishnoma yuborish
        try:
            await bot.send_message(
                user_id,
                f"ℹ️ **Ogohlik!**\n\n"
                f"Sizning premium obunangiz bekor qilindi.\n"
                f"Premium xizmatlardan foydalana olmaysiz."
            )
        except:
            print(f"Foydalanuvchi {user_id} ga xabar yuborishda xatolik")
            
    else:
        await message.answer(
            "❌ Amal bekor qilindi.",
            reply_markup=premium_management_keyboard()
        )
        await state.set_state(PremiumManagementState.waiting_action)
    
    await state.clear()    

# -*-*- PULLIK HIZMATLAR KLAVIATURASI -*-*-
def premium_services_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💎 Premium Obuna"), KeyboardButton(text="🎯 Maxsus Kontentlar")],
            [KeyboardButton(text="📥 Yuklab Olish"), KeyboardButton(text="🔧 Shaxsiy Qo'llab-quvvatlash")],
            [KeyboardButton(text="💳 To'lov qilish"), KeyboardButton(text="📋 To'lov Qo'llanmasi")],
            [KeyboardButton(text="🔍 Obunani tekshirish"), KeyboardButton(text="📞 Admin bilan bog'lanish")],
            [KeyboardButton(text="🔙 Asosiy Menyu")],
        ],
        resize_keyboard=True
    )

# -*-*- TO'LOV KLAVIATURASI -*-*-
def payment_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💳 Karta orqali to'lash"), KeyboardButton(text="📱 Click orqali to'lash")],
            [KeyboardButton(text="🔙 Pullik Hizmatlarga qaytish")],
        ],
        resize_keyboard=True
    )

# ==============================================================================
# -*-*- START VA RO'YXATDAN O'TISH HANDLERLARI -*-*-
# ==============================================================================

@dp.message(CommandStart())
async def start_command(message: types.Message, state: FSMContext):
    # Bloklanganligini tekshirish
    if db.is_user_blocked(message.from_user.id):
        block_info = db.get_blocked_user_info(message.from_user.id)
        if block_info:
            reason, duration, until, blocked_at, blocked_by = block_info
            
            # Muddatni o'qiladigan formatga o'tkazish
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
    
    user = db.get_user(message.from_user.id)
    
    if user:
        await message.answer(
            "🤗 Assalomu Aleykum! Dunyo Kinosi Olamiga xush kelibsiz! 🎬\n"
            "Bu Bot Siz izlagan barcha Kontentlarni o'z ichiga olgan. 🔍\n"
            "Sevimli Kino va Seriallaringizni va Multfilmlarni\n"
            "Musiqa Konsert Dasturlarini To'liq Nomi Yozib\n"
            "Qidiruv Bo'limi Orqali topshingiz ham mumkin!",
            reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
        )
    else:
        await message.answer(
            "🤗 Assalomu Aleykum Dunyo Kinosi Olamiga xush kelibsiz! 🎬\n"
            "Bu Bot Siz izlagan barcha Kontentlarni o'z ichiga olgan. 🔍\n"
            "Sevimli Kino va Seriallaringizni va Multfilmlarni\n"
            "Musiqa Konsert Dasturlarini To'liq Nomi Yozib\n"
            "Qidiruv Bo'limi Orqali topshingiz ham mumkin!\n\n"
            "👇 Kerakli Tilni Tanlang",
            reply_markup=language_keyboard()
        )
        await state.set_state(Registration.language)


@dp.message(Registration.language)
async def process_language(message: types.Message, state: FSMContext):
    language_text = message.text
    
    language_map = {
        "🇺🇿 O'zbek": "uz",
        "🇷🇺 Русский": "ru", 
        "🏴 English": "en"
    }
    
    language = language_map.get(language_text, "uz")
    await state.update_data(language=language)
    
    await message.answer(
        "Ismingizni kiriting:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(Registration.name)

@dp.message(Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    
    await message.answer(
        "Telefon raqamingizni yuboring:",
        reply_markup=phone_keyboard()
    )
    await state.set_state(Registration.phone)

@dp.message(Registration.phone, F.contact)
async def process_phone(message: types.Message, state: FSMContext):
    phone_number = message.contact.phone_number
    data = await state.get_data()
    
    # -*-*- YUKLASH ANIMATSIYASI -*-*-
    processing_msg = await message.answer("Ma'lumotlaringiz Tekshirilmoqda...")
    
    for i in range(3):
        await asyncio.sleep(1)
        dots = "." * (i + 1)
        await processing_msg.edit_text(f"Ma'lumotlaringiz Tekshirilmoqda{dots}")
    
    # -*-*- BAZAGA FOYDALANUVCHI QO'SHISH -*-*-
    db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=data['name'],
        phone_number=phone_number,
        language=data['language']
    )
    
    await processing_msg.delete()
    
    # -*-*- TASDIQLASH XABARI -*-*-
    await message.answer(
        "✅ Sizning Ro'yxatdan O'tish Ma'lumotlaringiz Tasdiqlandi!",
        reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
    )
    
    # -*-*- ADMINGA BILDIRISHNOMA -*-*-
    await admin_manager.send_admin_notification(
        bot, 
        f"📊 Yangi foydalanuvchi ro'yxatdan o'tdi!\n"
        f"👤 Ism: {data['name']}\n"
        f"📞 Tel: {phone_number}\n"
        f"🌐 Til: {data['language']}\n"
        f"🆔 ID: {message.from_user.id}"
    )
    
    await state.clear()

# ==============================================================================
# -*-*- ASOSIY MENYU HANDLERLARI -*-*-
# ==============================================================================

@dp.message(F.text == "🎬 Barcha Kontentlar")
async def all_content(message: types.Message):
    await message.answer("🎬 Barcha Kontentlar bo'limi. Bu yerda barcha mavjud kontentlarni ko'rishingiz mumkin.")

@dp.message(F.text == "📁 Bo'limlar")
async def sections(message: types.Message):
    await message.answer(
        "📁 Kerakli bo'limni tanlang:",
        reply_markup=sections_keyboard()
    )

@dp.message(F.text == "💵 Pullik Hizmatlar")
async def premium_services(message: types.Message):
    await message.answer(
        "💵 **Pullik xizmatlarimiz:**\n\n"
        "💎 **Premium Obuna** - 130,000 so'm/oy\n"
        "📥 **Yuklab Olish** - 30,000 so'm/film\n"
        "🎯 **Maxsus Kontentlar** - 50,000-200,000 so'm\n"
        "🔧 **Shaxsiy Qo'llab-quvvatlash** - 20,000 so'm/soat\n\n"
        "💳 Batafsil ma'lumot va to'lov uchun:\n"
        "📞 @Operator_Kino_1985",
        reply_markup=premium_services_keyboard()
    )

@dp.message(F.text == "🔍 Qidiruv")
async def search_handler(message: types.Message, state: FSMContext):
    await message.answer(
        "🔍 Qidiruv: Kino, serial yoki multfilm nomini yozing:",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(SearchState.waiting_search_query)

# ==============================================================================
# -*-*- BO'LIMLAR HANDLERLARI -*-*-
# ==============================================================================
        
# ==============================================================================
# -*-*- YAGONA BO'LIM HANDLERLARI -*-*-
# ==============================================================================

@dp.message(F.text == "📁 Bo'limlar")
async def sections(message: types.Message):
    await message.answer(
        "📁 Kerakli bo'limni tanlang:",
        reply_markup=get_category_keyboard("main")
    )

# ==============================================================================
# -*-*- KONTENT O'CHIRISH HANDLERLARI -*-*-
# ==============================================================================

# -*-*- KONTENT O'CHIRISH BOSHLASH -*-*-
@dp.message(F.text == "❌ Kontent O'chirish")
async def start_delete_content(message: types.Message, state: FSMContext):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        await message.answer(
            "🗑️ **Kontent O'chirish**\n\n"
            "Qaysi kategoriyadagi kontentni o'chirmoqchisiz?\n"
            "Kategoriyani tanlang:",
            reply_markup=get_category_keyboard("main")
        )
        await state.set_state(DeleteContentState.waiting_category)
    else:
        await message.answer("Sizga ruxsat yo'q!")

# -*-*- KATEGORIYA TANLASH -*-*-
@dp.message(DeleteContentState.waiting_category)
async def process_delete_category(message: types.Message, state: FSMContext):
    print(f"DEBUG: Foydalanuvchi matni: '{message.text}'")
    
    if message.text == "🔙 Asosiy Menyu":
        await message.answer("Amalni tanlang:", reply_markup=content_management_keyboard())
        await state.clear()
        return
    
    # Har qanday kategoriyani qabul qilish
    category = message.text
    await state.update_data(category=category)
    print(f"DEBUG: Kategoriya saqlandi: '{category}'")
    
    # Kategoriyadagi kinolarni olish
    movies = db.get_movies_by_category_for_admin(category)
    print(f"DEBUG: '{category}' dagi kinolar soni: {len(movies)}")
    
    if not movies:
        await message.answer(
            f"❌ **{category}** kategoriyasida hech qanday kino topilmadi.\n\n"
            f"Boshqa kategoriyani tanlang:",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    # Kinolar ro'yxatini tayyorlash
    keyboard = []
    for movie in movies:
        movie_id, title, actor, price, created_at = movie
        button_text = f"🎬 {title}"
        keyboard.append([KeyboardButton(text=button_text)])
        print(f"DEBUG: Kino qo'shildi: {title}")
    
    keyboard.append([KeyboardButton(text="🔙 Boshqa kategoriya")])
    keyboard.append([KeyboardButton(text="🔙 Admin Panel")])
    
    await message.answer(
        f"🗑️ **{category}** kategoriyasidagi kinolar:\n\n"
        f"O'chirmoqchi bo'lgan kinoni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )
    await state.set_state(DeleteContentState.waiting_movie_selection)
    print("DEBUG: Holat o'zgartirildi: waiting_movie_selection")
    
# -*-*- KINO TANLASH -*-*-
@dp.message(DeleteContentState.waiting_movie_selection)
async def process_movie_selection(message: types.Message, state: FSMContext):
    print(f"DEBUG: Tanlangan kino: '{message.text}'")
    
    if message.text == "🔙 Boshqa kategoriya":
        await message.answer(
            "Boshqa kategoriyani tanlang:",
            reply_markup=get_category_keyboard("main")
        )
        await state.set_state(DeleteContentState.waiting_category)
        return
        
    if message.text == "🔙 Admin Panel":
        await message.answer(
            "Admin panelga qaytingiz:",
            reply_markup=admin_keyboard()
        )
        await state.clear()
        return
    
    # Kino nomini olish (🎬 belgisini olib tashlash)
    movie_title = message.text.replace("🎬 ", "").strip()
    print(f"DEBUG: Kino nomi: '{movie_title}'")
    
    # Kino ma'lumotlarini olish
    data = await state.get_data()
    category = data.get('category')
    print(f"DEBUG: Kategoriya: '{category}'")
    
    # Kategoriyadagi barcha kinolarni olish
    movies = db.get_movies_by_category_for_admin(category)
    print(f"DEBUG: Kategoriyadagi kinolar soni: {len(movies)}")
    
    # DEBUG: Barcha kinolarni ko'rsatish
    print("DEBUG: Barcha kinolar ro'yxati:")
    for i, movie in enumerate(movies):
        movie_id, title, actor, price, created_at = movie
        print(f"DEBUG: {i+1}. ID: {movie_id}, Nomi: '{title}'")
    
    selected_movie = None
    for movie in movies:
        movie_id, title, actor, price, created_at = movie
        print(f"DEBUG: Tekshirilayotgan kino: '{title}'")
        if title.strip() == movie_title.strip():
            selected_movie = movie
            print(f"DEBUG: Kino topildi: {title}")
            break
    
    if not selected_movie:
        print(f"DEBUG: Kino topilmadi: '{movie_title}'")
        await message.answer("❌ Kino topilmadi! Iltimos, qayta urinib ko'ring.")
        return
    
    movie_id, title, actor, price, created_at = selected_movie
    
    await state.update_data(movie_id=movie_id, movie_title=title)
    
    await message.answer(
        f"⚠️ **KINO O'CHIRISH** ⚠️\n\n"
        f"🎬 **Nomi:** {title}\n"
        f"🎭 **Aktyor:** {actor}\n"
        f"📁 **Kategoriya:** {category}\n"
        f"💵 **Narxi:** {price} so'm\n"
        f"📅 **Qo'shilgan sana:** {created_at}\n"
        f"🆔 **ID:** {movie_id}\n\n"
        f"**HAQIQATDAN HAM BU KINONI O'CHIRMOQCHIMISIZ?**\n\n"
        f"Bu amalni ortga qaytarib bo'lmaydi!",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ HA, O'CHIRISH"), KeyboardButton(text="❌ BEKOR QILISH")]
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(DeleteContentState.waiting_confirmation)

# -*-*- TASDIQLASH -*-*-
@dp.message(DeleteContentState.waiting_confirmation)
async def process_delete_confirmation(message: types.Message, state: FSMContext):
    data = await state.get_data()
    movie_id = data.get('movie_id')
    movie_title = data.get('movie_title')
    category = data.get('category')
    
    if message.text == "✅ HA, O'CHIRISH":
        # Kino o'chirish
        success = db.delete_movie(movie_id)
        
        if success:
            await message.answer(
                f"✅ **KINO O'CHIRILDI!**\n\n"
                f"🎬 **Nomi:** {movie_title}\n"
                f"🆔 **ID:** {movie_id}\n"
                f"📁 **Kategoriya:** {category}\n\n"
                f"Kino bazadan muvaffaqiyatli o'chirildi.",
                reply_markup=admin_advanced_keyboard()  # <- O'ZGARDI
            )
            
            # Admin log
            await admin_manager.send_admin_notification(
                bot,
                f"🗑️ **Kino o'chirildi**\n\n"
                f"👤 **Admin:** {message.from_user.first_name}\n"
                f"🎬 **Kino:** {movie_title}\n"
                f"🆔 **ID:** {movie_id}\n"
                f"📁 **Kategoriya:** {category}"
            )
        else:
            await message.answer(
                f"❌ **XATOLIK!**\n\n"
                f"Kino o'chirishda xatolik yuz berdi.\n"
                f"Iltimos, qayta urinib ko'ring.",
                reply_markup=admin_advanced_keyboard()  # <- O'ZGARDI
            )
    else:
        await message.answer(
            "❌ Kino o'chirish bekor qilindi.",
            reply_markup=admin_advanced_keyboard()  # <- O'ZGARDI
        )
    
    await state.clear()

# ==============================================================================
# -*-*- KINO TANLANGANDA VIDEO YUBORISH (YANGILANGAN) -*-*-
# ==============================================================================
@dp.message(F.text.startswith("🎬"))
async def show_movie_details(message: types.Message, state: FSMContext):
    """Kino tanlanganda banner yuborish"""
    full_text = message.text[2:].strip()  # "🎬 " ni olib tashlaymiz
    user_id = message.from_user.id
    
    print(f"DEBUG: Kino tanlandi: '{full_text}'")
    
    # Faqat kino nomini olish (aktyor nomini olib tashlash)
    movie_title = full_text
    if " - " in full_text:
        movie_title = full_text.split(" - ")[0].strip()
    
    print(f"DEBUG: Qidirilayotgan kino nomi: '{movie_title}'")
    
    # Barcha kinolardan qidirish
    all_movies = db.get_all_movies_sorted()
    selected_movie = None
    
    for movie in all_movies:
        movie_id, db_title, description, category, file_id, price, is_premium, db_actor, banner_file_id, created_at, added_by = movie
        
        # Faqat kino nomini solishtiramiz
        if movie_title.lower() == db_title.lower():
            selected_movie = movie
            print(f"DEBUG: Kino topildi: {db_title}")
            break
    
    if selected_movie:
        # KINO MA'LUMOTLARINI STATE GA SAQLASH
        await state.update_data(
            movie_id=selected_movie[0],
            movie_title=selected_movie[1],
            movie_price=selected_movie[5]
        )
        
        print(f"DEBUG: Banner yuborilmoqda...")
        # BANNER YUBORISH
        await send_content_banner(message, selected_movie, user_id)
    else:
        print(f"DEBUG: Kino topilmadi")
        await message.answer("❌ Kino topilmadi. Iltimos, qayta urinib ko'ring.")
        
# ==============================================================================
# -*-*- TO'LOV HANDLERLARI -*-*-
# ==============================================================================

@dp.message(F.text == "💳 Yuklab olish uchun to'lash")
async def start_payment(message: types.Message, state: FSMContext):
    """To'lov boshlash"""
    # State dan kino ma'lumotlarini olish
    data = await state.get_data()
    movie_id = data.get('movie_id')
    movie_title = data.get('movie_title', "Noma'lum")
    movie_price = data.get('movie_price', 30000)
    
    if not movie_id:
        await message.answer("❌ Kino ma'lumotlari topilmadi. Qaytadan urinib ko'ring.")
        return
    
    await message.answer(
        f"💳 **To'lov ma'lumotlari:**\n\n"
        f"🎬 Kino: {movie_title}\n"
        f"💵 Summa: {movie_price:,} so'm\n\n"
        f"🏦 **Karta orqali:** 9860 3501 4890 3205 (HUMO)\n"
        f"📱 **Click orqali:** +998888882505\n\n"
        f"📸 **To'lov chekini yuboring:**\n"
        "(screenshot yoki rasm)",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(PaymentState.waiting_payment_receipt)
    
# Global o'zgaruvchi
last_payment_processing_time = 0

@dp.message(F.text.startswith("✅ Tasdiqlash #"))
async def confirm_payment(message: types.Message):
    """To'lovni tasdiqlash"""
    global last_payment_processing_time
    
    # 3 soniya ichida qayta ishlamaslik
    current_time = time.time()
    if current_time - last_payment_processing_time < 3:
        return
    last_payment_processing_time = current_time
    
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        try:
            payment_id = int(message.text.split("#")[1])
            
            # To'lov ma'lumotlarini olish
            pending_payments = db.get_pending_payments()
            payment_info = None
            for payment in pending_payments:
                if payment[0] == payment_id:
                    payment_info = payment
                    break
            
            if payment_info:
                user_id = payment_info[1]
                movie_id = payment_info[4]
                
                # KINO NOMINI TO'G'RI OLISH
                movie = db.get_movie_by_id(movie_id)
                if movie:
                    movie_title = movie[1]  # Kino nomi
                    file_id = movie[4]      # Video file_id
                else:
                    movie_title = "Noma'lum"
                    file_id = None
                
                # Foydalanuvchiga kinoni ochish huquqini berish
                db.add_user_purchase(user_id, movie_id)
                db.update_payment_status(payment_id, "completed")
                
                # Foydalanuvchiga xabar
                await bot.send_message(
                    user_id,
                    f"🎉 **To'lov tasdiqlandi!**\n\n"
                    f"✅ **{movie_title}** kinosi ochildi!\n"
                    f"Siz endi bu kinoni istalgan vaqt tomosha qilishingiz mumkin.\n\n"
                    f"📁 Bo'limlar orqali kinoni topib ko'rishingiz mumkin."
                )
                
                await message.answer(
                    f"✅ To'lov #{payment_id} tasdiqlandi!\n"
                    f"👤 Foydalanuvchi: {user_id}\n"
                    f"🎬 Kino: {movie_title}",
                    reply_markup=admin_advanced_keyboard()
                )
            else:
                await message.answer("❌ To'lov topilmadi")
                
        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}")

@dp.message(PaymentState.waiting_payment_receipt, F.photo)
async def process_payment_receipt(message: types.Message, state: FSMContext):
    receipt_file_id = message.photo[-1].file_id
    
    # State dan TO'LIQ MA'LUMOTLARNI OLISH
    data = await state.get_data()
    movie_id = data.get('movie_id')
    movie_title = data.get('movie_title', "Noma'lum")
    movie_price = data.get('movie_price', 30000)
    
    if not movie_id:
        await message.answer("❌ Kino ma'lumotlari topilmadi. Qaytadan boshlang.")
        await state.clear()
        return
    
    # To'lovni bazaga yozish
    payment_id = db.add_payment(
        user_id=message.from_user.id,
        amount=movie_price,
        content_id=movie_id,
        content_type="movie",
        receipt_file_id=receipt_file_id
    )
    
    # POYEZD ANIMATSIYASI
    train_animations = [
        "🚂▱▱▱▱▱▱▱▱▱ **To'lov tekshirilmoqda...**",
        "🚂▰▱▱▱▱▱▱▱▱ **Keling...**",
        "🚂▰▰▱▱▱▱▱▱▱ **Tekshirilmoqda...**",
        "🚂▰▰▰▱▱▱▱▱▱ **Ma'lumotlar...**",
        "🚂▰▰▰▰▱▱▱▱▱ **To'lov...**",
        "🚂▰▰▰▰▰▱▱▱▱ **Tasdiqlanmoqda...**",
        "🚂▰▰▰▰▰▰▱▱▱ **Tez orada...**",
        "🚂▰▰▰▰▰▰▰▱▱ **Natija bilan...**",
        "🚂▰▰▰▰▰▰▰▰▱ **Ko'rishamiz!**",
        "🚂▰▰▰▰▰▰▰▰▰✅ **Tayyor!**"
    ]

    # Loading xabarini yuborish
    loading_msg = await message.answer("🚂 **To'lov tekshirilmoqda...**")

    # Poyezd animatsiyasi - reply_markup O'CHIRILDI
    for animation in train_animations:
        await loading_msg.edit_text(
            f"{animation}\n\n"
            f"🎬 **Kino:** {movie_title}\n"
            f"💵 **Summa:** {movie_price:,} so'm\n"
            f"🆔 **To'lov ID:** {payment_id}"
        )
        await asyncio.sleep(0.7)

    # Yakuniy xabar
    await loading_msg.edit_text(
        "✅ **To'lov cheki qabul qilindi!**\n\n"
        f"🎬 **Kino:** {movie_title}\n"
        f"💵 **Summa:** {movie_price:,} so'm\n"
        f"🆔 **To'lov ID:** {payment_id}\n\n"
        f"⏳ **Admin tomonidan tekshirilmoqda...**\n"
        f"📞 **Agar 1 soat ichida javob bo'lmasa, @Operator_Kino_1985 ga murojaat qiling.**"
    )
    
    # Foydalanuvchiga asosiy menyuni qaytarish
    await message.answer(
        "Asosiy menyuga qaytingiz:",
        reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
    )
    
    # Admin ga CHEK SURATINI YUBORISH
    try:
        await bot.send_photo(
            chat_id=ADMIN_ID,
            photo=receipt_file_id,
            caption=f"📸 To'lov cheki - ID: {payment_id}"
        )
    except Exception as e:
        print(f"❌ Chek suratini yuborishda xatolik: {e}")
    
    # Admin ga to'lov ma'lumotlari
    admin_message = (
        f"💰 **Yangi to'lov so'rovi!**\n\n"
        f"👤 **Foydalanuvchi:** {message.from_user.first_name}\n"
        f"🆔 **User ID:** {message.from_user.id}\n"
        f"🎬 **Kino:** {movie_title}\n"
        f"🆔 **Kino ID:** {movie_id}\n"
        f"💵 **Summa:** {movie_price:,} so'm\n"
        f"🆔 **To'lov ID:** {payment_id}\n\n"
        f"📸 **Chek surati yuqorida yuborildi**\n\n"
        f"**Quyidagi tugmalardan birini bosing:**"
    )
    
    await bot.send_message(
        chat_id=ADMIN_ID,
        text=admin_message,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=f"✅ Tasdiqlash #{payment_id}")],
                [KeyboardButton(text=f"❌ Rad etish #{payment_id}")],
                [KeyboardButton(text="💰 To'lovlarni ko'rish")]
            ],
            resize_keyboard=True
        )
    )
    
    await state.clear()
    
@dp.message(F.text.startswith("❌ Rad etish #"))
async def reject_payment(message: types.Message):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        try:
            payment_id = int(message.text.split("#")[1])
            
            # To'lov ma'lumotlarini olish
            pending_payments = db.get_pending_payments()
            payment_info = None
            for payment in pending_payments:
                if payment[0] == payment_id:
                    payment_info = payment
                    break
            
            if payment_info:
                user_id = payment_info[1]
                movie_title = payment_info[9] if payment_info[9] else "Noma'lum"
                
                # To'lovni rad etish
                db.update_payment_status(payment_id, "rejected")
                
                # Foydalanuvchiga xabar
                await bot.send_message(
                    user_id,
                    f"❌ **To'lov rad etildi!**\n\n"
                    f"**{movie_title}** kinosi uchun to'lov chekingiz tasdiqlanmadi.\n"
                    f"📞 Sababini bilish uchun @Operator_Kino_1985 ga murojaat qiling."
                )
                
                await message.answer(
                    f"❌ To'lov #{payment_id} rad etildi!\n"
                    f"👤 Foydalanuvchi: {user_id} ga xabar yuborildi.",
                    reply_markup=admin_keyboard()
                )
            else:
                await message.answer("❌ To'lov topilmadi")
                
        except Exception as e:
            await message.answer(f"❌ Xatolik: {e}")
    
# ==============================================================================
# -*-*- CHEK YUBORISH SO'ROVI -*-*-
# ==============================================================================
@dp.message(F.text == "📸 Chek yuborish")
async def request_receipt(message: types.Message, state: FSMContext):
    await message.answer(
        "📸 **To'lov chekini yuboring:**\n\n"
        "• Ekran screenshotini oling\n" 
        "• To'liq summa va vaqt ko'rinsin\n"
        "• Yorqin va o'qiladigan bo'lsin",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(PaymentState.waiting_payment_receipt)    
    
# ==============================================================================
# -*-*- YUKLAB OLISH HANDLERI -*-*-
# ==============================================================================

@dp.message(F.text == "📥 Yuklab olish")
async def download_movie(message: types.Message):
    user_id = message.from_user.id
    
    # Premium statusni tekshirish
    if db.check_premium_status(user_id):
        await message.answer(
            "🎬 **Yuklab olish**\n\n"
            "Sizda premium obuna faol! Har qanday kinoni yuklab olishingiz mumkin.\n\n"
            "📁 Bo'limlar orqali kerakli kinoni toping va yuklab oling."
        )
    else:
        await message.answer(
            "📥 **Yuklab Olish Xizmati**\n\n"
            "Kinolarni telefon yoki kompyuteringizga yuklab oling:\n\n"
            "💰 **Narxlar:**\n"
            "• Kino: 30,000 so'm\n"
            "• Serial (1 qism): 15,000 so'm\n\n"
            "💳 **To'lov qiling:**\n"
            "Karta: 9860 3501 4890 3205\n"
            "Click: +998888882505\n\n"
            "To'lov qilgach, chekni @Operator_Kino_1985 ga yuboring.",
            reply_markup=premium_services_keyboard()
        )    

@dp.message(PaymentState.waiting_payment_receipt, F.text == "🔙 Orqaga")
async def back_from_payment(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "To'lov bekor qilindi.",
        reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
    ) 

    
# ==============================================================================
# -*-*- HOLLYWOOD KINOLARINI KO'RSATISH -*-*-
# ==============================================================================
@dp.message(F.text == "🎭 Hollywood Kinolari")
async def show_hollywood_movies(message: types.Message):
    """Hollywood kinolarini ko'rsatish"""
    movies = db.get_movies_by_category("🎭 Hollywood")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda kinolar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        # 11 TA USTUNNI OLISH
        movie_id, title, description, category, file_id, price, is_premium, actor_name, banner_file_id, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"🎭 **Hollywood Kinolari**\n\n"
        f"Jami: {len(movies)} ta kino\n\n"
        f"Kerakli kinoni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    ) 
    
        
# ==============================================================================
# -*-*- BARCHA BO'LIMLAR UCHUN KINO KO'RSATISH -*-*-
# ==============================================================================

@dp.message(F.text == "🎬 Hind Filmlari")
async def show_indian_movies(message: types.Message):
    """Hind filmlarini ko'rsatish"""
    movies = db.get_movies_by_category("🎬 Hind")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda kinolar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        # 11 TA USTUN
        movie_id, title, description, category, file_id, price, is_premium, actor_name, banner_file_id, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"🎬 **Hind Filmlari**\n\n"
        f"Jami: {len(movies)} ta kino\n\n"
        f"Kerakli kinoni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "📺 Hind Seriallari")
async def show_indian_series(message: types.Message):
    """Hind seriallarini ko'rsatish"""
    movies = db.get_movies_by_category("📺 Hind")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda kontentlar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"📺 **Hind Seriallari**\n\n"
        f"Jami: {len(movies)} ta kontent\n\n"
        f"Kerakli serialni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "🎥 Rus Kinolari")
async def show_russian_movies(message: types.Message):
    """Rus kinolarini ko'rsatish"""
    movies = db.get_movies_by_category("🎥 Rus")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda kinolar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"🎥 **Rus Kinolari**\n\n"
        f"Jami: {len(movies)} ta kino\n\n"
        f"Kerakli kinoni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "📟 Rus Seriallari")
async def show_russian_series(message: types.Message):
    """Rus seriallarini ko'rsatish"""
    movies = db.get_movies_by_category("📟 Rus")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda kontentlar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"📟 **Rus Seriallari**\n\n"
        f"Jami: {len(movies)} ta kontent\n\n"
        f"Kerakli serialni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "🎞️ O'zbek Kinolari")
async def show_uzbek_movies(message: types.Message):
    """O'zbek kinolarini ko'rsatish"""
    movies = db.get_movies_by_category("🎞️ O'zbek")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda kinolar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"🎞️ **O'zbek Kinolari**\n\n"
        f"Jami: {len(movies)} ta kino\n\n"
        f"Kerakli kinoni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "📱 O'zbek Seriallari")
async def show_uzbek_series(message: types.Message):
    """O'zbek seriallarini ko'rsatish"""
    movies = db.get_movies_by_category("📱 O'zbek")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda kontentlar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"📱 **O'zbek Seriallari**\n\n"
        f"Jami: {len(movies)} ta kontent\n\n"
        f"Kerakli serialni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "🕌 Islomiy Kinolar")
async def show_islamic_movies(message: types.Message):
    """Islomiy kinolarni ko'rsatish"""
    movies = db.get_movies_by_category("🕌 Islomiy")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda kinolar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"🕌 **Islomiy Kinolar**\n\n"
        f"Jami: {len(movies)} ta kino\n\n"
        f"Kerakli kinoni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "📖 Islomiy Seriallar")
async def show_islamic_series(message: types.Message):
    """Islomiy seriallarni ko'rsatish"""
    movies = db.get_movies_by_category("📖 Islomiy")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda kontentlar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"📖 **Islomiy Seriallar**\n\n"
        f"Jami: {len(movies)} ta kontent\n\n"
        f"Kerakli serialni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "🇹🇷 Turk Kinolari")
async def show_turkish_movies(message: types.Message):
    """Turk kinolarini ko'rsatish"""
    movies = db.get_movies_by_category("🇹🇷 Turk")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda kinolar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"🇹🇷 **Turk Kinolari**\n\n"
        f"Jami: {len(movies)} ta kino\n\n"
        f"Kerakli kinoni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "📺 Turk Seriallari")
async def show_turkish_series(message: types.Message):
    """Turk seriallarini ko'rsatish"""
    movies = db.get_movies_by_category("📺 Turk")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda kontentlar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"📺 **Turk Seriallari**\n\n"
        f"Jami: {len(movies)} ta kontent\n\n"
        f"Kerakli serialni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "👶 Bolalar Kinolari")
async def show_kids_movies(message: types.Message):
    """Bolalar kinolarini ko'rsatish"""
    movies = db.get_movies_by_category("👶 Bolalar")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda kinolar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"👶 **Bolalar Kinolari**\n\n"
        f"Jami: {len(movies)} ta kino\n\n"
        f"Kerakli kinoni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "🐰 Bolalar Multfilmlari")
async def show_kids_cartoons(message: types.Message):
    """Bolalar multfilmlarini ko'rsatish"""
    movies = db.get_movies_by_category("🐰 Bolalar")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda multfilmlar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"🐰 **Bolalar Multfilmlari**\n\n"
        f"Jami: {len(movies)} ta multfilm\n\n"
        f"Kerakli multfilmni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "🇰🇷 Koreys Kinolari")
async def show_korean_movies(message: types.Message):
    """Koreys kinolarini ko'rsatish"""
    movies = db.get_movies_by_category("🇰🇷 Koreys")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda kinolar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"🇰🇷 **Koreys Kinolari**\n\n"
        f"Jami: {len(movies)} ta kino\n\n"
        f"Kerakli kinoni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "📡 Koreys Seriallari")
async def show_korean_series(message: types.Message):
    """Koreys seriallarini ko'rsatish"""
    movies = db.get_movies_by_category("📡 Koreys")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda kontentlar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"📡 **Koreys Seriallari**\n\n"
        f"Jami: {len(movies)} ta kontent\n\n"
        f"Kerakli serialni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "🎯 Qisqa Filmlar")
async def show_short_films(message: types.Message):
    """Qisqa filmlarni ko'rsatish"""
    movies = db.get_movies_by_category("🎯 Qisqa")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda filmlar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"🎯 **Qisqa Filmlar**\n\n"
        f"Jami: {len(movies)} ta film\n\n"
        f"Kerakli filmni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )

@dp.message(F.text == "🎤 Konsert Dasturlari")
async def show_concert_programs(message: types.Message):
    """Konsert dasturlarini ko'rsatish"""
    movies = db.get_movies_by_category("🎤 Konsert")
    
    if not movies:
        await message.answer(
            "❌ Hozircha bu bo'limda konsertlar mavjud emas.",
            reply_markup=get_category_keyboard("main")
        )
        return
    
    keyboard = []
    for movie in movies:
        movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
        button_text = f"🎬 {title}"
        if actor_name:
            button_text += f" - {actor_name}"
        keyboard.append([KeyboardButton(text=button_text)])
    
    keyboard.append([KeyboardButton(text="🔙 Bo'limlarga qaytish")])
    
    await message.answer(
        f"🎤 **Konsert Dasturlari**\n\n"
        f"Jami: {len(movies)} ta konsert\n\n"
        f"Kerakli konsertni tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    )   

# ==============================================================================
# -*-*- BO'LIMLAR ICHIDAGI KLAVIATURALAR -*-*-
# ==============================================================================

def hollywood_movies_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎬 Mel Gibson Kinolari"), KeyboardButton(text="💪 Arnold Schwarzenegger Kinolari")],
            [KeyboardButton(text="🥊 Sylvester Stallone Kinolari"), KeyboardButton(text="🚗 Jason Statham Kinolari")],
            [KeyboardButton(text="🐲 Jeki Chan Kinolari"), KeyboardButton(text="🥋 Skod Adkins Kinolari")],
            [KeyboardButton(text="🎭 Denzil Washington Kinolari"), KeyboardButton(text="💥 Jan Clod Van Dam Kinolari")],
            [KeyboardButton(text="👊 Brus lee Kinolari"), KeyboardButton(text="😂 Jim Cerry Kinolari")],
            [KeyboardButton(text="🏴‍☠️ Jonni Depp Kinolari"), KeyboardButton(text="🥋 Jet Lee Kinolari")],
            [KeyboardButton(text="👊 Mark Dacascos Kinolari"), KeyboardButton(text="🎬 Bred Pitt Kinolari")],
            [KeyboardButton(text="🎭 Leonardo Dicaprio Kinolari"), KeyboardButton(text="📽️ Barcha Hollywood Kinolari")],
            [KeyboardButton(text="🔙 Bo'limlarga qaytish")],
        ],
        resize_keyboard=True
    )

def indian_movies_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🤴 Shakruhkhan Kinolari"), KeyboardButton(text="🎬 Amirkhan Kinolari")],
            [KeyboardButton(text="💪 Akshay Kumar Kinolari"), KeyboardButton(text="👑 Salmonkhan Kinolari")],
            [KeyboardButton(text="🌟 SayfAlihon Kinolari"), KeyboardButton(text="🎭 Amitahbachchan Kinolari")],
            [KeyboardButton(text="🔥 MethunChakraborty Kinolari"), KeyboardButton(text="🎥 Dharmendra Kinolari")],
            [KeyboardButton(text="🎞️ Raj Kapur Kinolari"), KeyboardButton(text="🚗 Tezlik 1/2/3 Qismlar")],
            [KeyboardButton(text="📀 Boshqa Hind Kinolari"), KeyboardButton(text="🔙 Bo'limlarga qaytish")],
        ],
        resize_keyboard=True
    )

def russian_movies_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💼 Ishdagi Ishq"), KeyboardButton(text="🎭 Shurikning Sarguzashtlari")],
            [KeyboardButton(text="👑 Ivan Vasilivich"), KeyboardButton(text="🔥 Gugurtga Ketib")],
            [KeyboardButton(text="🕵️ If Qalqasing Mahbuzi"), KeyboardButton(text="👶 O'nta Neger Bolasi")],
            [KeyboardButton(text="⚔️ Qo'lga Tushmas Qasoskorlar"), KeyboardButton(text="📀 Barcha Rus Kinolari")],
            [KeyboardButton(text="🔙 Bo'limlarga qaytish")],
        ],
        resize_keyboard=True
    )

def russian_series_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🎮 Igra Seriali"), KeyboardButton(text="🚗 Bumer Seriali")],
            [KeyboardButton(text="👥 Birgada Seriali"), KeyboardButton(text="📺 Barcha Rus Seriallari")],
            [KeyboardButton(text="🔙 Bo'limlarga qaytish")],
        ],
        resize_keyboard=True
    )

def kids_movies_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏠 Bola Uyda Yolg'iz 1"), KeyboardButton(text="🏠 Bola Uyda Yolg'iz 2")],
            [KeyboardButton(text="🏠 Bola Uyda Yolg'iz 3"), KeyboardButton(text="✈️ Uchubchi Devid")],
            [KeyboardButton(text="⚡ Garry Poter 1"), KeyboardButton(text="⚡ Garry Poter 2")],
            [KeyboardButton(text="⚡ Garry Poter 3"), KeyboardButton(text="⚡ Garry Poter 4")],
            [KeyboardButton(text="🎬 Barcha Bolalar Kinolari"), KeyboardButton(text="🔙 Bo'limlarga qaytish")],
        ],
        resize_keyboard=True
    )

def kids_cartoons_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❄️ Muzlik Davri 1"), KeyboardButton(text="❄️ Muzlik Davri 2")],
            [KeyboardButton(text="❄️ Muzlik Davri 3"), KeyboardButton(text="🐭 Tom & Jerry")],
            [KeyboardButton(text="🐻 Bori va Quyon"), KeyboardButton(text="🐻 Ayiq va Masha")],
            [KeyboardButton(text="🐼 Kungfu Panda 1"), KeyboardButton(text="🐼 Kungfu Panda 2")],
            [KeyboardButton(text="🐼 Kungfu Panda 3"), KeyboardButton(text="🐼 Kungfu Panda 4")],
            [KeyboardButton(text="🐎 Mustang"), KeyboardButton(text="📀 Barcha Multfilmlar")],
            [KeyboardButton(text="🔙 Bo'limlarga qaytish")],
        ],
        resize_keyboard=True
    )

def islamic_series_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🕌 Uvays Karoniy"), KeyboardButton(text="👑 Umar ibn Hattob")],
            [KeyboardButton(text="🌙 Olamga Nur Soshgan Oy"), KeyboardButton(text="📺 Barcha Islomiy Seriallar")],
            [KeyboardButton(text="🔙 Bo'limlarga qaytish")],
        ],
        resize_keyboard=True
    )

def korean_series_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❄️ Qish Sonatasi 1-20"), KeyboardButton(text="☀️ Yoz Ifori 1-20")],
            [KeyboardButton(text="💖 Qalbim Chechagi 1-17"), KeyboardButton(text="🏦 Va Bank 1-20")],
            [KeyboardButton(text="👑 Jumong 1-20"), KeyboardButton(text="⚓ Dengiz Hukumdori 1-20")],
            [KeyboardButton(text="📺 Barcha Koreys Seriallari"), KeyboardButton(text="🔙 Bo'limlarga qaytish")],
        ],
        resize_keyboard=True
    )

def korean_movies_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🏙️ Jinoyatchilar Shahri 1"), KeyboardButton(text="🏙️ Jinoyatchilar Shahri 2")],
            [KeyboardButton(text="🏙️ Jinoyatchilar Shahri 3"), KeyboardButton(text="🏙️ Jinoyatchilar Shahri 4")],
            [KeyboardButton(text="🎬 Barcha Koreys Kinolari"), KeyboardButton(text="🔙 Bo'limlarga qaytish")],
        ],
        resize_keyboard=True
    )

def turkish_series_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="👑 Sulton Abdulhamidhon"), KeyboardButton(text="🐺 Qashqirlar Makoni")],
            [KeyboardButton(text="📺 Barcha Turk Seriallari"), KeyboardButton(text="🔙 Bo'limlarga qaytish")],
        ],
        resize_keyboard=True
    )

# ==============================================================================
# -*-*- NAVIGATSIYA HANDLERLARI -*-*-
# ==============================================================================

@dp.message(F.text == "🔙 Bo'limlarga qaytish")
async def back_to_sections(message: types.Message):
    await message.answer(
        "📁 Bo'limlar menyusiga qaytingiz:",
        reply_markup=sections_keyboard()
    )

@dp.message(F.text == "🔙 Asosiy Menyu")
async def back_to_main(message: types.Message):
    await message.answer(
        "Asosiy menyuga qaytingiz:",
        reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
    )

@dp.message(F.text == "🔙 Pullik Hizmatlarga qaytish")
async def back_to_premium_services(message: types.Message):
    await message.answer(
        "💵 Pullik xizmatlar menyusiga qaytingiz:",
        reply_markup=premium_services_keyboard()
    )

# ==============================================================================
# -*-*- PULLIK HIZMATLAR HANDLERLARI -*-*-
# ==============================================================================

@dp.message(F.text == "💎 Premium Obuna")
async def premium_subscription(message: types.Message):
    await message.answer(
        "💎 **Premium Obuna - Obuna Bo'lish Tartibi**\n\n"
        
        "📋 **OBUNA BO'LISH UCHUN QILISH KERAK:**\n"
        "1. 💳 **To'lov qiling** - 130,000 so'm\n"
        "   • Karta: 9860 3501 4890 3205 (HUMO)\n"
        "   • Click: +998888882505\n\n"
        
        "2. 📸 **Chekni yuboring**\n"
        "   • To'lov chekini (screenshot)\n"
        "   • @Operator_Kino_1985 ga yuboring\n\n"
        
        "3. ⏳ **Kuting**\n"
        "   • 1 soat ichida obuna faollashtiriladi\n"
        "   • Barcha kontentlar ochiladi\n\n"
        
        "4. 🎬 **Foydalaning**\n"
        "   • Barcha kinolar va seriallar\n"
        "   • HD sifatda tomosha qiling\n"
        "   • Yuklab oling\n\n"
        
        "✅ **OBUNA BO'LGACH:**\n"
        "• Barcha bo'limlar ochiladi\n"
        "• Cheksiz ko'rish imkoniyati\n"
        "• Yuklab olish huquqi\n"
        "• Yangi kontentlar avtomatik qo'shiladi\n\n"
        
        "💰 **Narxi:** 130,000 so'm/oy\n"
        "📞 **Admin:** @Operator_Kino_1985\n"
        "📱 **Tel:** +998888882505"
    )

@dp.message(F.text == "📥 Yuklab Olish")
async def download_service(message: types.Message):
    await message.answer(
        "📥 **Yuklab Olish Xizmati Tafsilotlari:**\n\n"
        "✅ **Kinolarni telefon yoki kompyuteringizga yuklab oling**\n"
        "✅ **Internet bo'lmaganda ko'ring**\n"
        "✅ **Turli formatlar mavjud**\n"
        "✅ **Tez yuklab olish**\n\n"
        "💰 **Narxlar:**\n"
        "• Kino: 30,000 so'm\n"
        "• Serial (1 qism): 15,000 so'm\n"
        "• Konsert: 25,000 so'm\n\n"
        "💳 **Karta raqami:** 9860 3501 4890 3205 (HUMO)\n"
        "📞 **Admin:** @Operator_Kino_1985\n\n"
        "Kerakli kontentni tanlang va to'lov qiling.",
        reply_markup=payment_keyboard()
    )

@dp.message(F.text == "🎯 Maxsus Kontentlar")
async def exclusive_content(message: types.Message):
    await message.answer(
        "🎯 **Maxsus Kontentlar:**\n\n"
        "• Eksklyuziv kinolar\n"
        "• Rejissor versiyalari\n"
        "• Sahna ortidagi lavhalar\n"
        "• Aktyorlar intervyulari\n\n"
        "💰 **Narxi:** 50,000 - 200,000 so'm\n\n"
        "💳 To'lov uchun: @Operator_Kino_1985"
    )

@dp.message(F.text == "🔧 Shaxsiy Qo'llab-quvvatlash")
async def personal_support(message: types.Message):
    await message.answer(
        "🔧 **Shaxsiy Qo'llab-quvvatlash:**\n\n"
        "• Shaxsiy maslahat\n"
        "• Texnik yordam\n"
        "• Maxsus so'rovlar\n"
        "• 24/7 javob\n\n"
        "💰 **Narxi:** 20,000 so'm/soat\n\n"
        "💳 To'lov uchun: @Operator_Kino_1985"
    )

@dp.message(F.text == "💳 To'lov qilish")
async def payment_instructions(message: types.Message):
    await message.answer(
        "💳 **To'lov Qilish Tartibi:**\n\n"
        
        "🏦 **Karta orqali to'lov:**\n"
        "1. **Karta raqami:** 9860 3501 4890 3205\n"
        "2. **Karta turi:** HUMO\n"
        "3. **Summa:** 130,000 so'm\n"
        "4. **Izoh:** Premium Obuna\n\n"
        
        "📱 **Click orqali to'lov:**\n"
        "1. **Raqam:** +998 90 123 45 67\n"
        "2. **Summa:** 130,000 so'm\n"
        "3. **Izoh:** Kino Bot Premium\n\n"
        
        "📸 **Chek olish:**\n"
        "• To'lov muvaffaqiyatli amalga oshgach\n"
        "• Chekni (screenshot) oling\n"
        "• @Operator_Kino_1985 ga yuboring\n\n"
        
        "⏱️ **Eslatma:** To'lovdan keyin 1 soat ichida javob beriladi"
    )

@dp.message(F.text == "🔍 Obunani tekshirish")
async def check_subscription(message: types.Message):
    user_id = message.from_user.id
    is_premium = db.check_premium_status(user_id)
    
    if is_premium:
        await message.answer(
            "✅ **Sizda Premium Obuna faol!**\n\n"
            "🎬 Barcha kontentlar ochiq\n"
            "⭐ Premium afzalliklar faol\n"
            "📅 Obuna muddati davom etmoqda\n\n"
            "Muddatingiz tugashiga: 15 kun qoldi"
        )
    else:
        await message.answer(
            "❌ **Sizda Premium Obuna faol emas!**\n\n"
            "💎 Obuna bo'lish uchun:\n"
            "1. To'lov qiling\n"
            "2. Chekni yuboring\n"
            "3. Kutib turing\n\n"
            "📞 Admin: @Operator_Kino_1985"
        )

@dp.message(F.text == "🎁 Aksiya")
async def special_offer(message: types.Message):
    await message.answer(
        "🎁 **MAXSUS AKSIYA - 50% CHEGIRMA!**\n\n"
        
        "🔥 **Faqat birinchi 10 ta buyurtma uchun:**\n"
        "~~130,000 so'm~~ → **65,000 so'm**\n\n"
        
        "⏰ **Muddati:** Bugungina\n"
        "👥 **Qolgan joylar:** 3 ta\n\n"
        
        "🚀 **HOZIR RO'YXATDAN O'TING:**\n"
        "1. 65,000 so'm to'lang\n"
        "2. Chekni @Operator_Kino_1985 ga yuboring\n"
        "3. Premium obunangiz faollashtirilsin!\n\n"
        
        "💳 **Karta:** 9860 3501 4890 3205\n"
        "📞 **Admin:** @Operator_Kino_1985\n\n"
        
        "⚡ **TEZ HARAKAT QILING - Joylar cheklangan!**"
    )

@dp.message(F.text == "📦 Obuna Paketlari")
async def subscription_packages(message: types.Message):
    await message.answer(
        "📦 **OBUNA PAKETLARI - O'zingizga Mosini Tanlang**\n\n"
        
        "💎 **STANDART** - 130,000 so'm/oy\n"
        "• Barcha kinolar va seriallar\n"
        "• HD 720p sifat\n"
        "• Yuklab olish\n\n"
        
        "⭐ **PREMIUM** - 180,000 so'm/oy\n"
        "• Barcha kontentlar\n"
        "• HD 1080p sifat\n"
        "• Cheksiz yuklab olish\n"
        "• Maxsus kontentlar\n\n"
        
        "👑 **VIP** - 250,000 so'm/oy\n"
        "• Premium + barcha afzalliklar\n"
        "• Shaxsiy qo'llab-quvvatlash\n"
        "• Yangi filmlardan 24 soat oldin\n"
        "• Eksklyuziv intervyular\n\n"
        
        "🎯 **HOZIR TANLANG:**\n"
        "💳 Karta: 9860 3501 4890 3205\n"
        "📞 Admin: @Operator_Kino_1985"
    )
    
# ==============================================================================
# -*-*- ADMIN BILAN BOG'LANISH HANDLERLARI -*-*-
# ==============================================================================

@dp.message(F.text == "📞 Admin bilan bog'lanish")
async def contact_admin(message: types.Message):
    await message.answer(
        f"📞 **Admin bilan bog'lanish:**\n\n"
        
        f"👤 **Admin:** @Operator_Kino_1985\n"
        f"📱 **Telefon:** +998888882505\n\n"
        
        f"💬 **Qanday murojaat qilish kerak:**\n"
        f"1. To'lov chekini yuboring\n"
        f"2. Foydalanuvchi ID ni yozing\n"
        f"3. Qaysi xizmat uchun to'lov qilganingizni yozing\n\n"
        
        f"⏱️ **Javob berish vaqti:**\n"
        f"• Odatiy: 1 soat ichida\n"
        f"• Ish vaqtida: 15-30 daqiqa\n"
        f"• Tushlik vaqti: 1-2 soat\n\n"
        
        f"📋 **Kerakli ma'lumotlar:**\n"
        f"• To'lov cheki (screenshot)\n"
        f"• Foydalanuvchi ID: {message.from_user.id}\n"
        f"• Xizmat turi (Premium/Yuklab olish va h.k.)"
    )    
    
@dp.message(F.text == "📋 To'lov Qo'llanmasi")
async def payment_guide(message: types.Message):
    await message.answer(
        "📋 **To'lov Qo'llanmasi:**\n\n"
        
        "📸 **CHEK QANDAY BO'LISHI KERAK:**\n"
        "• To'liq ekran screenshot\n"
        "• Summa va vaqt aniq ko'rinsin\n"
        "• Karta raqami/to'lov raqami ko'rinsin\n"
        "• Yorqin va o'qiladigan bo'lsin\n\n"
        
        "⏰ **ISh VAQTI:**\n"
        "• Dushanba - Juma: 9:00 - 22:00\n"
        "• Shanba - Yakshanba: 10:00 - 20:00\n"
        "• Tushlik: 13:00 - 14:00\n\n"
        
        "📞 **BOG'LANISH:**\n"
        "• Telegram: @Operator_Kino_1985\n"
        "• Telefon: +998888882505\n"
        "• Xabar: \"Premium Obuna uchun to'lov\"\n\n"
        
        "⚠️ **ESLATMA:**\n"
        "• Cheksiz obuna faollashtirilmaydi!\n"
        "• Noto'g'ri chek yuborilsa, obuna berilmaydi!"
    )    

@dp.message(F.text == "💳 Karta orqali to'lash")
async def card_payment(message: types.Message):
    await message.answer(
        "💳 **Karta orqali to'lov:**\n\n"
        "🏦 **Bank:** Kapital Bank\n"
        "💳 **Karta raqami:** 9860 3501 4890 3205\n"
        "📱 **Karta turi:** HUMO\n"
        "👤 **Karta egasi:** [Admin Ismi]\n\n"
        "📋 **To'lov tartibi:**\n"
        "1. Kerakli summani o'tkazing\n"
        "2. To'lov chekini (screenshot) saqlang\n"
        "3. Chekni @Operator_Kino_1985 ga yuboring\n"
        "4. Xizmat faollashtiriladi\n\n"
        "⏱️ **Faollashtirish:** 1 soat ichida"
    )

@dp.message(F.text == "📱 Click orqali to'lash")
async def click_payment(message: types.Message):
    await message.answer(
        "📱 **Click orqali to'lov:**\n\n"
        "🔢 **Telefon raqam:** +998 90 123 45 67\n"
        "👤 **Ism:** [Admin Ismi]\n\n"
        "📋 **To'lov tartibi:**\n"
        "1. Click ilovasini oching\n"
        "2. 'To'lov' bo'limiga o'ting\n"
        "3. Yuqoridagi raqamga to'lov qiling\n"
        "4. To'lov chekini saqlang\n"
        "5. Chekni @Operator_Kino_1985 ga yuboring\n\n"
        "⏱️ **Faollashtirish:** 1 soat ichida"
    )

# ==============================================================================
# -*-*- ADMIN HANDLERLARI -*-*-
# ==============================================================================

@dp.message(F.text == "👑 Admin Panel")
async def admin_panel(message: types.Message):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        users_count = db.get_users_count()
        today_users = db.get_today_users()
        stats = db.get_premium_stats()
        
        await message.answer(
            f"👑 **Admin Panelga xush kelibsiz!**\n\n"
            f"📊 **Statistika:**\n"
            f"• Jami foydalanuvchilar: {users_count} ta\n"
            f"• Bugungi yangi: {today_users} ta\n"
            f"• Premium a'zolar: {stats['premium_users']} ta\n"
            f"• Oylik daromad: {stats['monthly_income']:,} so'm\n\n"
            f"🆔 ID: {message.from_user.id}\n"
            f"👤 Username: @{message.from_user.username}\n\n"
            f"Quyidagi funksiyalardan foydalanishingiz mumkin:",
            reply_markup=admin_advanced_keyboard()  # <- Yangi klaviatura
        )
    else:
        await message.answer("Sizga ruxsat yo'q!")

@dp.message(F.text == "📊 Foydalanuvchilar soni")
async def users_count(message: types.Message):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        users_count = db.get_users_count()
        today_users = db.get_today_users()
        await message.answer(
            f"📊 Statistika:\n\n"
            f"• Jami foydalanuvchilar: {users_count} ta\n"
            f"• Bugun ro'yxatdan o'tganlar: {today_users} ta"
        )
    else:
        await message.answer("Sizga ruxsat yo'q!")
        
# ==============================================================================
# -*-*- TO'LOVLARNI KO'RISH -*-*-
# ==============================================================================
@dp.message(F.text == "💰 To'lovlarni ko'rish")
async def view_payments(message: types.Message):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        pending_payments = db.get_pending_payments()
        
        if pending_payments:
            response = "💰 **Kutilayotgan to'lovlar:**\n\n"
            for payment in pending_payments:
                response += (
                    f"🆔 To'lov ID: {payment[0]}\n"
                    f"👤 Foydalanuvchi: {payment[8]} (ID: {payment[1]})\n"
                    f"🎬 Kino: {payment[9]}\n"
                    f"💵 Summa: {payment[2]:,} so'm\n"
                    f"⏰ Sana: {payment[7]}\n"
                    f"✅ Tasdiqlash: `✅ Tasdiqlash #{payment[0]}`\n"
                    f"❌ Rad etish: `❌ Rad etish #{payment[0]}`\n\n"
                )
        else:
            response = "✅ Kutilayotgan to'lovlar yo'q"
        
        await message.answer(response)

# ==============================================================================
# -*-*- KINOLAR RO'YXATI -*-*-
# ==============================================================================
@dp.message(F.text == "📋 Kinolar ro'yxati")
async def list_all_movies(message: types.Message):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        # Barcha kategoriyalardagi kinolarni olish
        all_categories = db.get_all_categories()
        all_movies = []
        
        for main_category in all_categories["main_categories"]:
            movies = db.get_movies_by_category(main_category)
            all_movies.extend(movies)
        
        if not all_movies:
            await message.answer("📋 Hozircha hech qanday kino mavjud emas.")
            return
        
        response = "📋 **Barcha Kinolar:**\n\n"
        for movie in all_movies:
            movie_id, title, description, category, file_id, price, is_premium, actor_name, created_at, added_by = movie
            response += f"🆔 ID: {movie_id}\n🎬 Nomi: {title}\n📁 Kategoriya: {category}\n"
            if actor_name:
                response += f"🎭 Aktyor: {actor_name}\n"
            response += f"💵 Narxi: {price} so'm\n"
            response += f"🔓 {'Premium' if is_premium else 'Oddiy'}\n"
            response += "─" * 30 + "\n"
        
        # Xabar juda uzun bo'lsa, bo'laklab yuborish
        if len(response) > 4000:
            parts = [response[i:i+4000] for i in range(0, len(response), 4000)]
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(response)
    else:
        await message.answer("Sizga ruxsat yo'q!")     

@dp.message(F.text == "💰 Pullik Hizmatlar Statistika")
async def premium_stats(message: types.Message):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        stats = db.get_premium_stats()
        await message.answer(
            f"💰 **Pullik Hizmatlar Statistika:**\n\n"
            f"👑 **Premium obuna a'zolari:** {stats['premium_users']} ta\n"
            f"💸 **Oylik daromad:** {stats['monthly_income']:,} so'm\n"
            f"📥 **Yuklab olishlar soni:** {stats['downloads_count']} ta\n"
            f"🔧 **Faol support ticketlar:** {stats['active_tickets']} ta\n"
            f"🎬 **Eng ko'p yuklangan:** {stats['most_downloaded']}\n\n"
            f"💳 **Karta raqami:** 9860 3501 4890 3205\n"
            f"📞 **Admin:** @Operator_Kino_1985"
        )
    else:
        await message.answer("Sizga ruxsat yo'q!")

@dp.message(F.text == "📢 Reklama yuborish")
async def send_advertisement(message: types.Message, state: FSMContext):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        await message.answer(
            "📢 Reklama matnini yuboring:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(AdvertisementState.waiting_ad_text)
    else:
        await message.answer("Sizga ruxsat yo'q!")

@dp.message(F.text == "👑 Premium Boshqaruv")
async def premium_management(message: types.Message):
    if admin_manager.is_admin(message.from_user.id, message.from_user.username):
        await message.answer(
            "👑 **Premium Boshqaruv Paneliga xush kelibsiz!**\n\n"
            "Bu yerda premium obunalarni boshqarishingiz mumkin:\n"
            "• Yangi obuna qo'shish\n"
            "• Obunani uzaytirish\n"
            "• Obunani bekor qilish\n"
            "• Statistikalarni ko'rish\n\n"
            "Foydalanuvchi ID sini yuboring:",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer("Sizga ruxsat yo'q!")

# ==============================================================================
# -*-*- QIDIRUV HANDLERI -*-*-
# ==============================================================================

@dp.message(SearchState.waiting_search_query)
async def process_search(message: types.Message, state: FSMContext):
    search_query = message.text
    await message.answer(
        f"🔍 '{search_query}' so'rovi bo'yicha natijalar:\n\n"
        f"1. {search_query} - Kino (2024)\n"
        f"2. {search_query} - Serial (2023)\n"
        f"3. {search_query} - Multfilm (2022)",
        reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
    )
    await state.clear()
    
# ==============================================================================
# -*-*- BLOK TEKSHIRUVI -*-*-
# ==============================================================================

async def check_user_blocked(user_id: int) -> bool:
    """Foydalanuvchi bloklanganligini tekshirish"""
    if db.is_user_blocked(user_id):
        block_info = db.get_blocked_user_info(user_id)
        if block_info:
            reason, duration, until, blocked_at, blocked_by = block_info
            
            # Muddatni o'qiladigan formatga o'tkazish
            duration_display = {
                "24_soat": "24 soat",
                "7_kun": "7 kun", 
                "Noma'lum": "Noma'lum muddat"
            }.get(duration, duration)
            
            return True
    return False

async def send_block_message(user_id: int):
    """Bloklangan foydalanuvchiga xabar yuborish"""
    block_info = db.get_blocked_user_info(user_id)
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
        return block_message
    return None    

# ==============================================================================
# -*-*- BOSHQA XABARLAR HANDLERI -*-*-
# ==============================================================================

@dp.message()
async def handle_other_messages(message: types.Message):
    if message.text:
        await message.answer(
            "Iltimos, menyudan kerakli bo'limni tanlang 👇", 
            reply_markup=main_menu_keyboard(message.from_user.id, message.from_user.username)
        )
       
# ==============================================================================
# -*-*- ASOSIY FUNKSIYA -*-*-
# ==============================================================================

async def main():
    print("Bot ishga tushdi...")
    
    # Webhook sozlamalari (Render uchun)
    if os.getenv('RENDER'):
        print("🌐 Webhook rejimi ishga tushmoqda...")
        
        # Webhook ni o'chirish (avvalgi webhook ni tozalash)
        await bot.delete_webhook(drop_pending_updates=True)
        
        WEBHOOK_PATH = f"/webhook"
        WEBHOOK_URL = f"https://kino-bot-l3nw.onrender.com{WEBHOOK_PATH}"
        
        await bot.set_webhook(WEBHOOK_URL)
        print(f"✅ Webhook sozlandi: {WEBHOOK_URL}")
        
        app = web.Application()
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot,
        )
        webhook_requests_handler.register(app, path=WEBHOOK_PATH)
        setup_application(app, dp, bot=bot)
        
        port = int(os.environ.get("PORT", 8080))
        print(f"🚀 Server {port}-portda ishga tushmoqda...")
        
        return await web._run_app(app, host="0.0.0.0", port=port)
    else:
        # Polling mode - local uchun
        print("📡 Polling rejimi ishga tushmoqda...")
        
        # Localda webhook o'chirish
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Start auto-restart in background
        asyncio.create_task(auto_restart())
        
        # keep_alive ni faqat localda chaqiramiz
        keep_alive()
        
        await dp.start_polling(bot)
    
# -*-*- BAZA YARATISH -*-*-
@dp.startup()
async def on_startup():
    db.init_db()  # Barcha jadvallarni yaratadi
    print("✅ Barcha jadvallar yaratildi/yangilandi")    

if __name__ == "__main__":
    asyncio.run(main())