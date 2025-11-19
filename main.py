# ==================== IMPORT QISM ====================
import os
import logging
from datetime import datetime
import pytz
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, CallbackQueryHandler
)
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database import Database
from admin import AdminPanel, handle_admin_messages, reply_to_user, confirm_payment, admin_start, handle_admin_files
from dotenv import load_dotenv

load_dotenv()

# Database
db = Database()

# Admin panel - faqat instance yaratamiz
admin_panel = AdminPanel()

# ==================== LOGGER SOZLASH ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ==================== KONSTANTALAR ====================
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

db = Database()
admin_panel = AdminPanel()

LANGUAGE, NAME, PHONE = range(3)  # Conversation states

# ==================== AVTOMATIK XABARLAR ====================
AUTOMATIC_MESSAGES = [
    {
        "time": "09:00",
        "message": (
            "🕌 Assalomu Aleykum! Xayrli tong! 🌅\n\n"
            "🌟 Yangi kun yangi imkoniyatlar bilan keldi! \n"
            "🎬 Bugun o'zingizni sevimli kinolar olamiga cho'mdirib yuboring!\n\n"
            "🔍 Qidiruv bo'limi orqali istalgan kinoni toping va kuningizni yorqin qiling! ✨\n"
            "💫 Yaxshi kayfiyat va yorqin tomoshalar tilaymiz! 🍿"
        )
    },
    {
        "time": "14:00",
        "message": (
            "🕌 Assalomu Aleykum! Quyoshli peshin! ☀️\n\n"
            "🍽️ Tushlikdan keyin dam olish vaqtida sevimli seriallaringiz bilan hordiq chiqaring!\n\n"
            "📺 Seriallar bo'limida yangi fasllar sizni kutmoqda!\n"
            "💖 Dam oling, tomosha qiling va rohatlaning! 🎉"
        )
    },
    {
        "time": "20:00",
        "message": (
            "🕌 Assalomu Aleykum! Sokin kechalar! 🌙\n\n"
            "🏡 Kechqurun - oila va do'stlar bilan birga bo'lish va go'zal tomoshalar orttirish vaqti!\n\n"
            "🍿 Lazzatli snacklar tayyorlang va sevimli filmlaringizga sho'ng'ing!\n"
            "💫 Sizga quvonch va dam olish bilan to'la kech tilaymiz! ❤️"
        )
    }
]

# ==================== TIL MATNLARI ====================
TEXTS = {
    'uz': {
        # Asosiy
        'welcome': "🤗 Assalomu Aleykum Dunyo Kinosi Olamiga xush kelibsiz",
        'description': "🎬 Bu Bot Siz izlagan barcha Kino va Seriallarni o'z ichiga olgan",
        'search': "🔍 Sevimli Kino va Seriallaringizni va Multfilmlarni To'liq Nomi Yozib Qidiruv Bo'limi Orqali topshingiz mumkin",
        'register': "✅ Iltimos Botdan To'liq Foydalanish uchun Ro'yxatdan O'ting faqat Bir marta",
        'choose_language': "🌐 Tilni tanlang",
        'enter_name': "👤 Ismingizni kiriting:",
        'enter_phone': "📞 Telefon raqamingizni kiriting:",
        'success_register': "✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!",
        
        # Asosiy menyu
        'main_menu': "🏠 Asosiy menyu",
        'search_movies': "🎬 Kino qidirish",
        'categories': "📋 Kategoriyalar",
        'profile': "👤 Profil",
        'premium_services': "💼 Pullik Hizmatlar",
        'change_language': "🌐 Tilni tanlash",
        
        # Kategoriyalar
        'choose_category': "📋 Kategoriyalar:\nIltimos kerakli kategoriyani tanlang:",
        'hollywood': "🎭 Hollywood Kinolari",
        'hindi': "🇮🇳 Hind Filmlari",
        'russian': "🇷🇺 Rus Kinolari",
        'uzbek': "🇺🇿 O'zbek Kinolari",
        'islamic': "🕌 Islomiy Kinolar",
        'turkish': "📺 Turk Seriallari",
        'kids': "👶 Bolalar Kinolari",
        'cartoons': "🐰 Bolalar Multfilmlari",
        'korean_movies': "🇰🇷 Koreys Kinolari",
        'korean_series': "📺 Koreys Seriallari",
        'music': "🎵 Musiqa",
        
        # Sahifalash
        'page_info': "📄 Sahifa: {page}/{total_pages} | Jami: {total_count} ta",
        'view_content': "⬇️ Quyidagi kontentlarni ko'ring:",
        'content_sent': "✅ {count} ta kontent yuborildi",
        'navigation_help': "⬅️ Oldingi/Keyingi ➡️ tugmalari bilan navigatsiya qiling",
        'no_content': "❌ Hozircha {subject} mavjud emas",
        'content_soon': "⏳ Tez orada qo'shiladi yoki\n💼 Pullik hizmatlar bo'limidan so'rab olishingiz mumkin",
        
        # Profil
        'profile_info': "👤 Profil:\n🆔 ID: {user_id}\n📛 Ism: {name}\n📞 Tel: {phone}",
        'profile_not_found': "❌ Profil topilmadi",
        
        # Qidiruv
        'search_prompt': "🔍 Kino qidirish:\nIltimos kino nomini kiriting:",
        'search_results': "🔍 '{query}' bo'yicha natijalar:",
        'no_results': "❌ '{query}' bo'yicha hech narsa topilmadi",
        
        # Pullik hizmatlar
        'premium_menu': "💼 Pullik Hizmatlar bo'limi\n\nQuyidagi tugmalardan birini tanlang:",
        'paid_movies': "💰 Pullik Kinolar",
        'contact_admin': "📞 Adminga Xabar",
        'view_response': "👀 Javobni Ko'rish",
        'back': "🔙 Orqaga",
        
        # To'lov va ogohlantirish
        'warning': "⚠️ OGOHLANTIRISH! ⚠️",
        'warning_text': """Hurmatli foydalanuvchi!

📝 Mavzulardan chetga chiqmagan holda so'rovlar yuboring
🚫 Nomaqbul va xaqoratlik so'zlar ishlatmang
👁️ Bot to'liq kuzatiladi, o'zingizni asrang
🙏 Tushunganingiz uchun katta rahmat

👨‍💼 Admin ruhsati bilan""",
        
        'payment_info': """💳 Admin karta raqami: 8600 1104 7759 4067

💰 Narxlar:
🎬 Birgina kino narhi - 30,000 so'm
📺 Birgina serial narhi - 10,000 so'm
🐰 Birgina multfilm narhi - 30,000 so'm

📸 To'lov qilib bo'lgach chek surati yuboring
👨‍💼 Adminga yuboring

❓ Sizni qanday kontentlar qiziqtirmoqda?
📝 Shularni batafsil yozing

📞 Agar botimiz javob bermasa: @Operator_1985""",
        
        # Admin kontakt
        'admin_contact_info': """👨‍💼 Adminga xabar yuborish

📝 Sizni qiziqtirgan kontent nomini uz/ru/en tillarida yozishingiz mumkin

✅ Agar bu kontentlar mavjud bo'lsa,
👨‍💼 Operator sizga javob yuboradi

💼 Pullik kontentlarni sotib olish pullik hizmat bo'limi bilan tanishib chiqing

👇 Xabaringizni yozing va yuboring:""",
        
        'payment_instructions': """💳 To'lov va buyurtma tartibi:

1️⃣ Pullik hizmatlar bilan tanishgan bo'lsangiz
2️⃣ Quyidagi ma'lumotlarni yuboring:

📸 To'lov chek surati
📝 Kontent nomi (aniq va xatolarsiz)

💳 To'lov qilish uchun karta raqami:
8600 1104 7759 4067

📞 Qo'shimcha ma'lumot uchun: @Operator_1985""",
        
        # Xabar yuborish
        'message_sent': "✅ Xabaringiz adminga yuborildi!",
        'response_soon': "⏳ Tez orada javob beradi.",
        'view_response_section': "👀 Javobni 'Javobni Ko'rish' bo'limida ko'rashingiz mumkin.",
        
        # Javob ko'rish
        'no_response': "👀 Javobni ko'rish:\n\n📨 Hozircha sizga hech qanday javob kelmagan.\n⏳ Agar admin javob yuborgan bo'lsa, tez orada shu yerda ko'rasiz.\n\n📞 Shoshilgan bo'lsangiz: @Operator_1985",
        
        # Xatoliklar
        'error_loading': "❌ Kontentlarni yuklashda xatolik yuz berdi. Iltimos qayta urinib ko'ring.",
        'error_sending': "❌ Fayl yuborishda xatolik",
        'first_page': "❌ Siz birinchi sahifadasiz",
        'last_page': "❌ Siz oxirgi sahifadasiz",
        'no_page_content': "❌ Bu sahifada kontent yo'q",
        'invalid_page': "❌ Noto'g'ri sahifa formati",
        'no_pagination_data': "❌ Sahifalash ma'lumotlari topilmadi",
    },
    
    'ru': {
        # Asosiy
        'welcome': "🤗 Добро пожаловать в мир мирового кино",
        'description': "🎬 Этот бот содержит все фильмы и сериалы, которые вы искали",
        'search': "🔍 Вы можете найти свои любимые фильмы, сериалы и мультфильмы, написав полное название в разделе поиска",
        'register': "✅ Пожалуйста, зарегистрируйтесь для полного использования бота всего один раз",
        'choose_language': "🌐 Выберите язык",
        'enter_name': "👤 Введите ваше имя:",
        'enter_phone': "📞 Введите ваш номер телефона:",
        'success_register': "✅ Вы успешно зарегистрировались!",
        
        # Asosiy menyu
        'main_menu': "🏠 Главное меню",
        'search_movies': "🎬 Поиск фильмов",
        'categories': "📋 Категории",
        'profile': "👤 Профиль",
        'premium_services': "💼 Платные услуги",
        'change_language': "🌐 Сменить язык",
        
        # Kategoriyalar
        'choose_category': "📋 Категории:\nПожалуйста, выберите нужную категорию:",
        'hollywood': "🎭 Голливудские фильмы",
        'hindi': "🇮🇳 Индийские фильмы",
        'russian': "🇷🇺 Русские фильмы",
        'uzbek': "🇺🇿 Узбекские фильмы",
        'islamic': "🕌 Исламские фильмы",
        'turkish': "📺 Турецкие сериалы",
        'kids': "👶 Детские фильмы",
        'cartoons': "🐰 Детские мультфильмы",
        'korean_movies': "🇰🇷 Корейские фильмы",
        'korean_series': "📺 Корейские сериалы",
        'music': "🎵 Музыка",
        
        # Sahifalash
        'page_info': "📄 Страница: {page}/{total_pages} | Всего: {total_count} шт",
        'view_content': "⬇️ Просмотрите следующий контент:",
        'content_sent': "✅ Отправлено {count} контентов",
        'navigation_help': "⬅️ Навигация с помощью кнопок Предыдущий/Следующий ➡️",
        'no_content': "❌ Пока нет {subject}",
        'content_soon': "⏳ Скоро будет добавлено или\n💼 Вы можете запросить в разделе платных услуг",
        
        # Profil
        'profile_info': "👤 Профиль:\n🆔 ID: {user_id}\n📛 Имя: {name}\n📞 Тел: {phone}",
        'profile_not_found': "❌ Профиль не найден",
        
        # Qidiruv
        'search_prompt': "🔍 Поиск фильмов:\nПожалуйста, введите название фильма:",
        'search_results': "🔍 Результаты по запросу '{query}':",
        'no_results': "❌ По запросу '{query}' ничего не найдено",
        
        # Pullik hizmatlar
        'premium_menu': "💼 Раздел платных услуг\n\nВыберите одну из кнопок ниже:",
        'paid_movies': "💰 Платные фильмы",
        'contact_admin': "📞 Связаться с админом",
        'view_response': "👀 Посмотреть ответ",
        'back': "🔙 Назад",
        
        # To'lov va ogohlantirish
        'warning': "⚠️ ПРЕДУПРЕЖДЕНИЕ! ⚠️",
        'warning_text': """Уважаемый пользователь!

📝 Отправляйте запросы, не отклоняясь от темы
🚫 Не используйте нецензурные и оскорбительные слова
👁️ Бот полностью отслеживается, будьте осторожны
🙏 Большое спасибо за понимание

👨‍💼 С разрешения администратора""",
        
        'payment_info': """💳 Номер карты администратора: 8600 1104 7759 4067

💰 Цены:
🎬 Один фильм - 30,000 сум
📺 Один сериал - 10,000 сум
🐰 Один мультфильм - 30,000 сум

📸 После оплаты отправьте скриншот чека
👨‍💼 Отправьте администратору

❓ Каким контентом вы интересуетесь?
📝 Подробно напишите об этом

📞 Если наш бот не отвечает: @Operator_1985""",
        
        # Admin kontakt
        'admin_contact_info': """👨‍💼 Отправить сообщение администратору

📝 Вы можете написать название контента, который вас интересует, на уз/рус/англ языках

✅ Если этот контент доступен,
👨‍💼 Оператор ответит вам

💼 Ознакомьтесь с разделом платных услуг для покупки платного контента

👇 Напишите и отправьте ваше сообщение:""",
        
        'payment_instructions': """💳 Процедура оплаты и заказа:

1️⃣ Если вы ознакомились с платными услугами
2️⃣ Отправьте следующую информацию:

📸 Скриншот чека об оплате
📝 Название контента (точно и без ошибок)

💳 Номер карты для оплаты:
8600 1104 7759 4067

📞 Для дополнительной информации: @Operator_1985""",
        
        # Xabar yuborish
        'message_sent': "✅ Ваше сообщение отправлено администратору!",
        'response_soon': "⏳ Скоро ответит.",
        'view_response_section': "👀 Вы можете посмотреть ответ в разделе 'Посмотреть ответ'.",
        
        # Javob ko'rish
        'no_response': "👀 Посмотреть ответ:\n\n📨 Пока вам не пришло никаких ответов.\n⏳ Если администратор отправил ответ, вы скоро увидите его здесь.\n\n📞 Если срочно: @Operator_1985",
        
        # Xatoliklar
        'error_loading': "❌ Произошла ошибка при загрузке контента. Пожалуйста, попробуйте еще раз.",
        'error_sending': "❌ Ошибка при отправке файла",
        'first_page': "❌ Вы на первой странице",
        'last_page': "❌ Вы на последней странице",
        'no_page_content': "❌ На этой странице нет контента",
        'invalid_page': "❌ Неправильный формат страницы",
        'no_pagination_data': "❌ Данные пагинации не найдены",
    },
    
    'en': {
        # Asosiy
        'welcome': "🤗 Welcome to the World Cinema Universe",
        'description': "🎬 This Bot contains all the Movies and Series you are looking for",
        'search': "🔍 You can find your favorite Movies, Series and Cartoons by writing the Full Name in the Search section",
        'register': "✅ Please Register to use the Bot Fully only Once",
        'choose_language': "🌐 Choose language",
        'enter_name': "👤 Enter your name:",
        'enter_phone': "📞 Enter your phone number:",
        'success_register': "✅ You have successfully registered!",
        
        # Asosiy menyu
        'main_menu': "🏠 Main menu",
        'search_movies': "🎬 Search movies",
        'categories': "📋 Categories",
        'profile': "👤 Profile",
        'premium_services': "💼 Premium Services",
        'change_language': "🌐 Change language",
        
        # Kategoriyalar
        'choose_category': "📋 Categories:\nPlease select the desired category:",
        'hollywood': "🎭 Hollywood Movies",
        'hindi': "🇮🇳 Hindi Films",
        'russian': "🇷🇺 Russian Movies",
        'uzbek': "🇺🇿 Uzbek Movies",
        'islamic': "🕌 Islamic Movies",
        'turkish': "📺 Turkish Series",
        'kids': "👶 Kids Movies",
        'cartoons': "🐰 Kids Cartoons",
        'korean_movies': "🇰🇷 Korean Movies",
        'korean_series': "📺 Korean Series",
        'music': "🎵 Music",
        
        # Sahifalash
        'page_info': "📄 Page: {page}/{total_pages} | Total: {total_count} items",
        'view_content': "⬇️ View the following content:",
        'content_sent': "✅ {count} content items sent",
        'navigation_help': "⬅️ Navigate with Previous/Next ➡️ buttons",
        'no_content': "❌ No {subject} available yet",
        'content_soon': "⏳ Coming soon or\n💼 You can request in premium services section",
        
        # Profil
        'profile_info': "👤 Profile:\n🆔 ID: {user_id}\n📛 Name: {name}\n📞 Phone: {phone}",
        'profile_not_found': "❌ Profile not found",
        
        # Qidiruv
        'search_prompt': "🔍 Search movies:\nPlease enter the movie name:",
        'search_results': "🔍 Results for '{query}':",
        'no_results': "❌ Nothing found for '{query}'",
        
        # Pullik hizmatlar
        'premium_menu': "💼 Premium Services section\n\nSelect one of the buttons below:",
        'paid_movies': "💰 Paid Movies",
        'contact_admin': "📞 Contact Admin",
        'view_response': "👀 View Response",
        'back': "🔙 Back",
        
        # To'lov va ogohlantirish
        'warning': "⚠️ WARNING! ⚠️",
        'warning_text': """Dear user!

📝 Send requests without deviating from topics
🚫 Do not use inappropriate and offensive words
👁️ The bot is fully monitored, be careful
🙏 Thank you for understanding

👨‍💼 With admin permission""",
        
        'payment_info': """💳 Admin card number: 8600 1104 7759 4067

💰 Prices:
🎬 Single movie - 30,000 soum
📺 Single series - 10,000 soum
🐰 Single cartoon - 30,000 soum

📸 After payment, send screenshot of receipt
👨‍💼 Send to admin

❓ What content are you interested in?
📝 Write about it in detail

📞 If our bot doesn't respond: @Operator_1985""",
        
        # Admin kontakt
        'admin_contact_info': """👨‍💼 Send message to admin

📝 You can write the name of content you're interested in uz/ru/en languages

✅ If this content is available,
👨‍💼 Operator will respond to you

💼 Check premium services section for purchasing paid content

👇 Write and send your message:""",
        
        'payment_instructions': """💳 Payment and order procedure:

1️⃣ If you've familiarized with premium services
2️⃣ Send the following information:

📸 Screenshot of payment receipt
📝 Content name (accurate and error-free)

💳 Card number for payment:
8600 1104 7759 4067

📞 For additional information: @Operator_1985""",
        
        # Xabar yuborish
        'message_sent': "✅ Your message has been sent to admin!",
        'response_soon': "⏳ Will respond soon.",
        'view_response_section': "👀 You can view the response in 'View Response' section.",
        
        # Javob ko'rish
        'no_response': "👀 View Response:\n\n📨 You haven't received any responses yet.\n⏳ If admin sent a response, you'll see it here soon.\n\n📞 If urgent: @Operator_1985",
        
        # Xatoliklar
        'error_loading': "❌ Error loading content. Please try again.",
        'error_sending': "❌ Error sending file",
        'first_page': "❌ You are on the first page",
        'last_page': "❌ You are on the last page",
        'no_page_content': "❌ No content on this page",
        'invalid_page': "❌ Invalid page format",
        'no_pagination_data': "❌ Pagination data not found",
    }
}

# ==================== TIL TANLASH HANDLERLARI ====================
async def handle_uzbek_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """O'zbek tilini tanlash"""
    context.user_data['language'] = 'uz'
    lang = 'uz'
    text = TEXTS[lang]
    
    await update.message.reply_text(
        text['welcome'] + "\n\n" +
        text['description'] + "\n\n" +
        text['search'] + "\n\n" +
        text['register'] + "\n\n" +
        text['enter_name'],
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def handle_russian_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rus tilini tanlash"""
    context.user_data['language'] = 'ru'
    lang = 'ru'
    text = TEXTS[lang]
    
    await update.message.reply_text(
        text['welcome'] + "\n\n" +
        text['description'] + "\n\n" +
        text['search'] + "\n\n" +
        text['register'] + "\n\n" +
        text['enter_name'],
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def handle_english_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ingliz tilini tanlash"""
    context.user_data['language'] = 'en'
    lang = 'en'
    text = TEXTS[lang]
    
    await update.message.reply_text(
        text['welcome'] + "\n\n" +
        text['description'] + "\n\n" +
        text['search'] + "\n\n" +
        text['register'] + "\n\n" +
        text['enter_name'],
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME
    
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tilni tanlash"""
    lang_text = update.message.text
    
    print(f"DEBUG: Til tanlandi: '{lang_text}'")  # Debug uchun
    
    if lang_text == "🇺🇿 O'zbek tili":
        context.user_data['language'] = 'uz'
        lang = 'uz'
    elif lang_text == "🇷🇺 Русский язык":
        context.user_data['language'] = 'ru'
        lang = 'ru'
    elif lang_text == "🇺🇸 English":
        context.user_data['language'] = 'en'
        lang = 'en'
    else:
        lang = 'uz'  # Default
    
    text = TEXTS[lang]
    
    await update.message.reply_text(
        text['welcome'] + "\n\n" +
        text['description'] + "\n\n" +
        text['search'] + "\n\n" +
        text['register'] + "\n\n" +
        text['enter_name'],
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME    

# ==================== ASOSIY MENU FUNKSIYALARI ====================
def get_main_menu(lang='uz'):
    """Tilga qarab asosiy menyu"""
    if lang == 'uz':
        keyboard = [
            ["🎬 Kino qidirish", "📋 Kategoriyalar"],
            ["👤 Profil", "💼 Pullik Hizmatlar"],
            ["🌐 Tilni tanlash"]
        ]
    elif lang == 'ru':
        keyboard = [
            ["🎬 Поиск фильмов", "📋 Категории"],
            ["👤 Профиль", "💼 Платные услуги"],
            ["🌐 Сменить язык"]
        ]
    else:
        keyboard = [
            ["🎬 Search movies", "📋 Categories"],
            ["👤 Profile", "💼 Premium Services"],
            ["🌐 Change language"]
        ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_categories_menu():
    """Kategoriyalar menyusi"""
    keyboard = [
        ["🎭 Hollywood Kinolari"],
        ["🇮🇳 Hind Filmlari"],
        ["🇷🇺 Rus Kinolari"],
        ["🇺🇿 O'zbek Kinolari"],
        ["🕌 Islomiy Kinolar"],
        ["📺 Turk Seriallari"],
        ["👶 Bolalar Kinolari"],
        ["🐰 Bolalar Multfilmlari"],
        ["🇰🇷 Koreys Kinolari"],
        ["📺 Koreys Seriallari"],  # Bu yerda Koreys Seriallari mavjud
        ["🎵 Musiqa"],
        ["🔙 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_language_menu():
    keyboard = [
        ["🇺🇿 O'zbek tili", "🇷🇺 Русский язык"],
        ["🇺🇸 English"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== PULLIK HIZMATLAR MENU FUNKSIYALARI ====================
def get_premium_menu():
    keyboard = [
        ["💰 Pullik Kinolar"],
        ["📞 Adminga Xabar"],
        ["👀 Javobni Ko'rish"],
        ["🔙 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== YANGI: SODDA PULLIK HIZMATLAR MENYUSI ====================
def get_premium_menu_simple():
    """Soddalashtirilgan pullik hizmatlar menyusi"""
    keyboard = [
        ["📦 Barcha Pullik Kontentlar"],
        ["ℹ️ Qo'llanma"],
        ["🔙 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_premium_content_categories():
    """Pullik kontent kategoriyalari"""
    keyboard = [
        ["🎬 Pullik Kinolar", "📺 Pullik Seriallar"],
        ["🐰 Pullik Multfilmlar", "🎵 Pullik Musiqalar"],
        ["🔙 Orqaga"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== YANGI: BARCHA PULLIK KONTENTLARNI KO'RSATISH ====================
async def show_all_premium_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha pullik kontentlarni ko'rsatish"""
    await update.message.reply_text(
        "💰 *Barcha Pullik Kontentlar*\n\n"
        "Qaysi turdagi pullik kontentlarni ko'rmoqchisiz?",
        reply_markup=get_premium_content_categories(),
        parse_mode='Markdown'
    )

# ==================== YANGI: PULLIK KONTENT KATEGORIYASINI KO'RSATISH ====================
async def show_premium_content_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pullik kontent kategoriyasini ko'rsatish"""
    category_map = {
        "🎬 Pullik Kinolar": "premium_movies",
        "📺 Pullik Seriallar": "premium_series",
        "🐰 Pullik Multfilmlar": "premium_cartoons", 
        "🎵 Pullik Musiqalar": "premium_music"
    }
    
    selected_category = update.message.text
    premium_category = category_map.get(selected_category)
    
    if premium_category:
        # Pullik kontentlarni olish
        contents = db.get_premium_content_by_category("premium", premium_category)
        
        if contents:
            content_list = "💰 *Pullik Kontentlar:*\n\n"
            
            for content in contents[:10]:  # Faqat birinchi 10 tasi
                content_list += f"🎬 {content[3]}\n💰 {content[5]:,} so'm\n\n"
            
            if len(contents) > 10:
                content_list += f"... va yana {len(contents) - 10} ta kontent"
            
            await update.message.reply_text(
                content_list + "\n\n⬇️ Kontentni tanlang va to'lov qiling:",
                reply_markup=get_premium_content_selection_menu(contents),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Hozircha {selected_category} mavjud emas.\n\n"
                "⏳ Tez orada qo'shiladi.",
                reply_markup=get_premium_menu_simple()
            )

def get_premium_content_selection_menu(contents):
    """Pullik kontentlarni tanlash menyusi"""
    keyboard = []
    
    for content in contents[:5]:  # Faqat birinchi 5 tasi
        keyboard.append([f"💰 {content[3]}"])
    
    keyboard.append(["🔙 Orqaga", "🏠 Asosiy menyu"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_contact_menu():
    keyboard = [
        ["📝 Kontent so'rovi yuborish"],
        ["💳 To'lov chekini yuborish"],
        ["🔙 Orqaga"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
# ==================== YANGI: SODDA PULLIK HIZMATLAR MENYUSI ====================
def get_premium_menu_simple():
    """Soddalashtirilgan pullik hizmatlar menyusi"""
    keyboard = [
        ["📦 Barcha Pullik Kontentlar"],
        ["ℹ️ Qo'llanma"],
        ["🔙 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_premium_content_categories():
    """Pullik kontent kategoriyalari"""
    keyboard = [
        ["🎬 Pullik Kinolar", "📺 Pullik Seriallar"],
        ["🐰 Pullik Multfilmlar", "🎵 Pullik Musiqalar"],
        ["🔙 Orqaga"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_payment_confirmation_menu():
    """To'lov tasdiqlash menyusi"""
    keyboard = [
        ["💳 To'lov qilish", "📸 Chek yuborish"],
        ["🔙 Orqaga", "🏠 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)    

# ==================== HOLLYWOOD SUB-MENU FUNKSIYALARI ====================
def get_hollywood_menu():
    keyboard = [
        ["🎬 Mel Gibson Kinolari"],
        ["💪 Arnold Schwarzenegger Kinolari"],
        ["🥊 Sylvester Stallone Kinolari"],
        ["🚗 Jason Statham Kinolari"],
        ["🐉 Jeki Chan Kinolari"],
        ["🥋 Skod Adkins Kinolari"],
        ["🎭 Denzil Washington Kinolari"],
        ["💥 Jan Clod Van Dam Kinolari"],
        ["👊 Brus Li Kinolari"],
        ["😂 Jim Cerry Kinolari"],
        ["🎩 Jonni Depp Kinolari"],
        ["🌟 Boshqa Hollywood Kinolari"],
        ["🔙 Kategoriyalar", "🏠 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== HIND SUB-MENU FUNKSIYALARI ====================
def get_hindi_menu():
    keyboard = [
        ["🤴 Shakruhkhan Kinolari"],
        ["🎯 Amirkhan Kinolari"],
        ["🦸 Akshay Kumar Kinolari"],
        ["👑 Salmonkhan Kinolari"],
        ["🌟 SayfAlihon Kinolari"],
        ["🎭 Amitahbachchan Kinolari"],
        ["💃 MethunChakraborty Kinolari"],
        ["👨‍🦳 Dharmendra Kinolari"],
        ["🎬 Raj Kapur Kinolari"],
        ["📀 Boshqa Hind Kinolari"],
        ["🔙 Kategoriyalar", "🏠 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== RUS SUB-MENU FUNKSIYALARI ====================
def get_russian_movies_menu():
    keyboard = [
        ["💘 Ishdagi Ishq"],
        ["🎭 Shurikning Sarguzashtlari"],
        ["🔄 Ivan Vasilivich"],
        ["🔥 Gugurtga Ketib"],
        ["🕵️ If Qalqasing Mahbuzi"],
        ["👶 O'nta Neger Bolasi"],
        ["⚔️ Qo'lga Tushmas Qasoskorlar"],
        ["🎬 Barcha Rus Kinolari"],
        ["🔙 Kategoriyalar", "🏠 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== O'ZBEK SUB-MENU FUNKSIYALARI ====================
def get_uzbek_movies_menu():
    keyboard = [
        ["🏘️ Mahallada Duv-Duv Gap"],
        ["👰 Kelinlar Qo'zg'aloni"],
        ["👨 Abdullajon"],
        ["😊 Suyinchi"],
        ["🌳 Chinor Ositidagi Duel"],
        ["🙏 Yaratganga Shukur"],
        ["💃 Yor-Yor"],
        ["🎉 To'ylar Muborak"],
        ["💣 Bomba"],
        ["😜 Shum Bola"],
        ["⚡ Temir Xotin"],
        ["🎬 Barcha UZ Klassik Kinolari"],
        ["🔙 Kategoriyalar", "🏠 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== ISLOMIY SUB-MENU FUNKSIYALARI ====================
def get_islamic_movies_menu():
    keyboard = [
        ["📿 Umar Ibn Ali Hattob To'liq"],
        ["🌙 Olamga Nur Sochgan Oy To'liq"],
        ["🎬 Barcha Islomiy Kinolar"],
        ["📺 Barcha Islomiy Seriallar"],
        ["🔙 Kategoriyalar", "🏠 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== TURK SUB-MENU FUNKSIYALARI ====================
def get_turkish_series_menu():
    keyboard = [
        ["👑 Sulton Abdulhamidhon"],
        ["🐺 Qashqirlar Makoni"],
        ["📺 Barcha Turk Seriallari"],
        ["🔙 Kategoriyalar", "🏠 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== BOLALAR SUB-MENU FUNKSIYALARI ====================
def get_kids_movies_menu():
    keyboard = [
        ["👦 Bola Uyda Yolg'iz 1-3"],
        ["✈️ Uchuvchi Devid"],
        ["⚡ Garry Poter 1-4"],
        ["🎬 Barcha Bolalar Kinolari"],
        ["🔙 Kategoriyalar", "🏠 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_cartoons_menu():
    keyboard = [
        ["❄️ Muzlik Davri 1-3"],
        ["🐭 Tom & Jerry"],
        ["🐻 Bori va Quyon"],
        ["🍯 Ayiq va Masha"],
        ["🐼 Kungfu Panda 1-4"],
        ["🐎 Mustang"],
        ["🎬 Barcha Multfilmlar"],
        ["🔙 Kategoriyalar", "🏠 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== KOREYS SUB-MENU FUNKSIYALARI ====================
def get_korean_movies_menu():
    keyboard = [
        ["🏙️ Jinoyatchilar Shahri 1-4"],
        ["🎬 Barcha Koreys Kinolari"],
        ["🔙 Kategoriyalar", "🏠 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_korean_series_menu():
    """Koreys Seriallari menyusi - YANGILANGAN"""
    keyboard = [
        ["❄️ Qish Sonatasi 1-20"],
        ["☀️ Yoz Ifori 1-20"],
        ["🏦 Va Bank 1-20"],
        ["👑 Jumong Barcha Qismlar"],
        ["⚓ Dengiz Hukumdori Barcha Qismlar"],
        ["💖 Qalbim Chechagi 1-17"],  # YANGI QO'SHILDI
        ["📺 Barcha Koreys Seriallari"],
        ["🔙 Kategoriyalar", "🏠 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== MUSIQA SUB-MENU FUNKSIYALARI ====================
def get_music_menu():
    keyboard = [
        ["🎵 O'zbek Musiqalari"],
        ["🎶 Rus Musiqalari"],
        ["🎼 Hind Musiqalari"],
        ["🎧 Turk Musiqalari"],
        ["🎤 Koreys Musiqalari"],
        ["🎹 Barcha Musiqalar"],
        ["🔙 Kategoriyalar", "🏠 Asosiy menyu"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== AVTOMATIK XABAR FUNKSIYALARI ====================
async def send_daily_message(app, message_text):
    """Barcha foydalanuvchilarga xabar yuborish"""
    try:
        users = db.get_all_users()
        success_count = 0
        fail_count = 0
        
        for user_id in users:
            try:
                await app.bot.send_message(chat_id=user_id, text=message_text)
                success_count += 1
            except Exception as e:
                logging.error(f"Foydalanuvchi {user_id} ga xabar yuborishda xatolik: {e}")
                fail_count += 1
        
        if ADMIN_ID:
            report_text = (
                f"📊 Kundalik xabar hisoboti:\n"
                f"✅ Muvaffaqiyatli: {success_count}\n"
                f"❌ Xatolik: {fail_count}\n"
                f"👥 Jami: {len(users)}"
            )
            await app.bot.send_message(int(ADMIN_ID), report_text)
            
    except Exception as e:
        logging.error(f"Kundalik xabar yuborishda xatolik: {e}")

def setup_scheduler(app):
    """Kundalik xabarlar uchun scheduler sozlash"""
    scheduler = BackgroundScheduler()
    timezone = pytz.timezone('Asia/Tashkent')
    
    for msg in AUTOMATIC_MESSAGES:
        hour, minute = msg['time'].split(':')
        scheduler.add_job(
            send_daily_message,
            trigger=CronTrigger(hour=int(hour), minute=int(minute), timezone=timezone),
            args=[app, msg['message']],
            id=f"daily_message_{msg['time']}",
            replace_existing=True
        )
    
    scheduler.start()
    return scheduler

# ==================== START VA RO'YXATDAN O'TISH HANDLERLARI ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Admin tekshirish
    admin_panel = AdminPanel()
    if await admin_panel.check_admin(user_id):
        return await admin_start(update, context)
    
    # Oddiy foydalanuvchi uchun
    existing_user = db.get_user(user_id)
    
    if existing_user:
        # Ro'yxatdan o'tgan foydalanuvchi
        lang = existing_user[4] if len(existing_user) > 4 else 'uz'
        text = TEXTS[lang]
        
        await update.message.reply_text(
            text['welcome'] + "\n\n" +
            text['description'] + "\n\n" +
            text['search'] + "\n\n" +
            "👇 " + ("Quyidagi menyudan kerakli bo'limni tanlang:" if lang == 'uz' else 
                    "Выберите нужный раздел из меню ниже:" if lang == 'ru' else 
                    "Select the desired section from the menu below:"),
            reply_markup=get_main_menu(lang)
        )
        return ConversationHandler.END
    else:
        # Yangi foydalanuvchi
        await update.message.reply_text(
            "🤗 Assalomu Aleykum Dunyo Kinosi Olamiga xush kelibsiz\n\n"
            "🎬 Bu Bot Siz izlagan barcha Kino va Seriallarni o'z ichiga olgan\n\n"
            "🔍 Sevimli Kino va Seriallaringizni va Multfilmlarni To'liq Nomi Yozib Qidiruv Bo'limi Orqali topshingiz mumkin\n\n"
            "🌐 Tilni tanlang:",
            reply_markup=get_language_menu()
        )
        return LANGUAGE

# ==================== TILNI O'ZGARTIRISH ====================
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tilni o'zgartirish - ConversationHandlerga qaytish"""
    # Foydalanuvchi ma'lumotlarini olish
    user_id = update.effective_user.id
    user_data = db.get_user(user_id)
    
    if user_data:
        # Agar foydalanuvchi ro'yxatdan o'tgan bo'lsa, tilni yangilash
        current_lang = user_data[4] if len(user_data) > 4 else 'uz'
        
        # Til menyusini joriy tilga qarab ko'rsatish
        if current_lang == 'uz':
            text = "🌐 Tilni tanlang:"
        elif current_lang == 'ru':
            text = "🌐 Выберите язык:"
        else:
            text = "🌐 Choose language:"
        
        await update.message.reply_text(
            text,
            reply_markup=get_language_menu()
        )
        
        # Conversation state ga qaytish
        context.user_data['changing_language'] = True
        return LANGUAGE
    else:
        # Agar foydalanuvchi ro'yxatdan o'tmagan bo'lsa
        lang = context.user_data.get('language', 'uz')
        text = TEXTS[lang]
        
        await update.message.reply_text(
            text['choose_language'],
            reply_markup=get_language_menu()
        )
        return LANGUAGE

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text
    lang = context.user_data.get('language', 'uz')
    text = TEXTS[lang]
    
    contact_button = KeyboardButton("📞 Telefon raqamini yuborish", request_contact=True)
    
    # Tilga qarab kontakt tugma matnini o'zgartirish
    if lang == 'ru':
        contact_button = KeyboardButton("📞 Отправить номер телефона", request_contact=True)
    elif lang == 'en':
        contact_button = KeyboardButton("📞 Send phone number", request_contact=True)
    
    keyboard = [[contact_button]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        text['enter_phone'],
        reply_markup=reply_markup
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text
    
    user = update.effective_user
    name = context.user_data['name']
    lang = context.user_data.get('language', 'uz')
    
    # Foydalanuvchini bazaga qo'shish
    db.add_user(user.id, user.username, name, phone)
    
    text = TEXTS[lang]
    
    # Agar til o'zgartirish jarayonida bo'lsa
    if context.user_data.get('changing_language'):
        await update.message.reply_text(
            "✅ " + ("Til muvaffaqiyatli o'zgartirildi!" if lang == 'uz' else 
                    "Язык успешно изменен!" if lang == 'ru' else 
                    "Language successfully changed!"),
            reply_markup=get_main_menu(lang)
        )
        del context.user_data['changing_language']
    else:
        # Yangi ro'yxatdan o'tish
        await update.message.reply_text(
            text['success_register'] + "\n\n" +
            "🎬 " + ("Endi kinolar olamidan bahramand bo'lishingiz mumkin!" if lang == 'uz' else 
                    "Теперь вы можете наслаждаться миром кино!" if lang == 'ru' else 
                    "Now you can enjoy the world of cinema!"),
            reply_markup=get_main_menu(lang)
        )
    
    if ADMIN_ID:
        try:
            await context.bot.send_message(
                int(ADMIN_ID),
                "🆕 Yangi foydalanuvchi:\n" +
                "👤 Ism: " + name + "\n" +
                "📞 Tel: " + phone + "\n" +
                "🆔 ID: " + str(user.id) +
                "\n🌐 Til: " + lang
            )
        except Exception as e:
            logging.error(f"Adminga xabar yuborishda xatolik: {e}")
    
    return ConversationHandler.END

# ==================== KATEGORIYA HANDLERLARI ====================
async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Kategoriyalar:\nIltimos kerakli kategoriyani tanlang:",
        reply_markup=get_categories_menu()
    )

async def show_hollywood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎭 Hollywood Kinolari:\nIltimos aktyor tanlang:",
        reply_markup=get_hollywood_menu()
    )

async def show_hindi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇮🇳 Hind Filmlari:\nIltimos aktyor tanlang:",
        reply_markup=get_hindi_menu()
    )

async def show_russian_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇷🇺 Rus Kinolari:\nIltimos film tanlang:",
        reply_markup=get_russian_movies_menu()
    )

async def show_uzbek_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇺🇿 O'zbek Kinolari:\nIltimos film tanlang:",
        reply_markup=get_uzbek_movies_menu()
    )

async def show_islamic_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🕌 Islomiy Kinolar:\nIltimos kategoriya tanlang:",
        reply_markup=get_islamic_movies_menu()
    )

async def show_turkish_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📺 Turk Seriallari:\nIltimos serial tanlang:",
        reply_markup=get_turkish_series_menu()
    )

async def show_kids_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👶 Bolalar Kinolari:\nIltimos film tanlang:",
        reply_markup=get_kids_movies_menu()
    )

async def show_cartoons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🐰 Bolalar Multfilmlari:\nIltimos multfilm tanlang:",
        reply_markup=get_cartoons_menu()
    )

async def show_korean_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🇰🇷 Koreys Kinolari:\nIltimos film tanlang:",
        reply_markup=get_korean_movies_menu()
    )

async def show_korean_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📺 Koreys Seriallari:\nIltimos serial tanlang:",
        reply_markup=get_korean_series_menu()
    )

async def show_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 Musiqa:\nIltimos musiqa turini tanlang:",
        reply_markup=get_music_menu()
    )

# ==================== ORQAGA QAYTISH HANDLERLARI ====================
async def back_to_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📋 Kategoriyalar:",
        reply_markup=get_categories_menu()
    )

async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    if await admin_panel.check_admin(user_id):
        await update.message.reply_text(
            "👨‍💻 Admin panelga qaytdingiz:",
            reply_markup=admin_panel.get_admin_main_menu()
        )
    else:
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=get_main_menu())

# ==================== KONTENT KO'RSATISH VA SAHIFALASH FUNKSIYALARI ====================
def get_content_navigation_menu(page, total_pages, subject, category_type="hollywood"):
    """Kontent navigatsiya menyusini yaratish - HAR BIR KONTENT UCHUN ALOHIDA"""
    keyboard = []
    
    # Oldingi/Keyingi tugmalari
    nav_buttons = []
    if page > 1:
        nav_buttons.append("⬅️ Oldingi")
    
    # Sahifa raqamlari (faqat ko'p sahifali bo'lsa)
    if total_pages > 1:
        page_buttons = []
        # Faqat chegarali sonli sahifalarni ko'rsatish
        max_visible_pages = min(5, total_pages)
        start_page = max(1, page - 2)
        end_page = min(total_pages, start_page + max_visible_pages - 1)
        
        # Agar oxiriga yetmasa, start pageni sozlaymiz
        if end_page - start_page + 1 < max_visible_pages:
            start_page = max(1, end_page - max_visible_pages + 1)
        
        for p in range(start_page, end_page + 1):
            if p == page:
                page_buttons.append(f"🔹 {p}")  # Joriy sahifa
            else:
                page_buttons.append(f"{p}")     # Boshqa sahifalar
        
        if page_buttons:
            # Sahifalarni qatorlarga bo'lish
            for i in range(0, len(page_buttons), 3):
                keyboard.append(page_buttons[i:i+3])
    
    if page < total_pages:
        if not nav_buttons:  # Agar oldingi tugmasi yo'q bo'lsa
            nav_buttons.append("Keyingi ➡️")
        else:
            nav_buttons.append("Keyingi ➡️")
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Orqaga qaytish tugmalari
    back_buttons = []
    if category_type == "hollywood":
        back_buttons.extend(["🔙 Hollywood Kinolari", "🏠 Asosiy menyu"])
    elif category_type == "hindi":
        back_buttons.extend(["🔙 Hind Filmlari", "🏠 Asosiy menyu"])
    elif category_type == "russian":
        back_buttons.extend(["🔙 Rus Kinolari", "🏠 Asosiy menyu"])
    elif category_type == "uzbek":
        back_buttons.extend(["🔙 O'zbek Kinolari", "🏠 Asosiy menyu"])
    elif category_type == "islamic":
        back_buttons.extend(["🔙 Islomiy Kinolar", "🏠 Asosiy menyu"])
    elif category_type == "turkish":
        back_buttons.extend(["🔙 Turk Seriallari", "🏠 Asosiy menyu"])
    elif category_type == "kids":
        back_buttons.extend(["🔙 Bolalar Kinolari", "🏠 Asosiy menyu"])
    elif category_type == "cartoons":
        back_buttons.extend(["🔙 Bolalar Multfilmlari", "🏠 Asosiy menyu"])
    elif category_type == "korean_movies":
        back_buttons.extend(["🔙 Koreys Kinolari", "🏠 Asosiy menyu"])
    elif category_type == "korean_series":
        back_buttons.extend(["🔙 Koreys Seriallari", "🏠 Asosiy menyu"])
    elif category_type == "music":
        back_buttons.extend(["🔙 Musiqa", "🏠 Asosiy menyu"])
    else:
        back_buttons.extend(["🔙 Kategoriyalar", "🏠 Asosiy menyu"])
    
    keyboard.append(back_buttons)
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== YANGILANGAN SAHIFALAB KONTENT KO'RSATISH ====================
async def send_paginated_content(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                               category, subject, category_type="hollywood"):
    """Kontentlarni sahifalab ko'rsatish - YANGILANGAN VERSIYA"""
    try:
        # Sahifa raqamini olish
        page = context.user_data.get(f'page_{category}_{subject}', 1)
        
        print(f"DEBUG: Kontent ko'rsatish - Category: {category}, Subject: {subject}, Page: {page}")
        
        # Kontentlarni olish
        contents, total_pages, total_count = db.get_content_by_subject_paginated(
            category, subject, page
        )
        
        print(f"DEBUG: Bazadan qaytgan kontentlar: {len(contents)} ta, Jami sahifalar: {total_pages}")
        
        if contents:
            # Faqat bitta kontentni ko'rsatish
            content = contents[0]  # Birinchi kontentni olish
            title = content[1]
            description = content[2]
            file_id = content[4]
            file_type = content[5]
            
            caption = f"🎬 {title}\n📝 {description}\n\n📄 Sahifa: {page}/{total_pages} | Jami: {total_count} ta"
            
            # Navigatsiya menyusini yaratish
            reply_markup = get_content_navigation_menu(page, total_pages, subject, category_type)
            
            # Kontentni yuborish
            try:
                if file_type == "video":
                    await update.message.reply_video(video=file_id, caption=caption, reply_markup=reply_markup)
                elif file_type == "photo":
                    await update.message.reply_photo(photo=file_id, caption=caption, reply_markup=reply_markup)
                elif file_type == "audio":
                    await update.message.reply_audio(audio=file_id, caption=caption, reply_markup=reply_markup)
                elif file_type == "document":
                    await update.message.reply_document(document=file_id, caption=caption, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(caption, reply_markup=reply_markup)
                
                print(f"DEBUG: Kontent yuborildi: {title}")
                
            except Exception as e:
                logging.error(f"Kontent yuborishda xatolik: {e}")
                await update.message.reply_text(f"❌ Fayl yuborishda xatolik: {caption}", reply_markup=reply_markup)
            
        else:
            await update.message.reply_text(
                f"❌ Hozircha {subject} mavjud emas.\n\n"
                "⏳ Tez orada qo'shiladi yoki\n"
                "💼 Pullik hizmatlar bo'limidan so'rab olishingiz mumkin.",
                reply_markup=get_categories_menu()
            )
            
    except Exception as e:
        logging.error(f"Kontent ko'rsatishda xatolik: {e}")
        await update.message.reply_text(
            "❌ Kontentlarni yuklashda xatolik yuz berdi. Iltimos qayta urinib ko'ring.",
            reply_markup=get_categories_menu()
        )
        
# ==================== SAHIFA RAQAMLARI HANDLERI ====================
async def handle_page_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sahifa raqamini tanlash - YANGILANGAN VERSIYA"""
    message_text = update.message.text
    
    print(f"DEBUG: Sahifa tanlandi: '{message_text}'")
    
    # Sahifa raqamini ajratib olish (🔹 5 -> 5)
    if "🔹" in message_text:
        page_text = message_text.replace("🔹", "").strip()
    else:
        page_text = message_text.strip()
    
    if page_text.isdigit():
        page = int(page_text)
        current_category = context.user_data.get('current_category')
        current_subject = context.user_data.get('current_subject')
        category_type = context.user_data.get('category_type', 'hollywood')
        
        if current_category and current_subject:
            # Kontentlarni tekshirish
            contents, total_pages, total_count = db.get_content_by_subject_paginated(
                current_category, current_subject, page
            )
            if contents:
                context.user_data[f'page_{current_category}_{current_subject}'] = page
                await send_paginated_content(update, context, current_category, current_subject, category_type)
            else:
                await update.message.reply_text("❌ Bu sahifada kontent yo'q")
        else:
            await update.message.reply_text("❌ Sahifalash ma'lumotlari topilmadi")
    else:
        await update.message.reply_text("❌ Noto'g'ri sahifa formati")       

# ==================== NAVIGATSIYA HANDLERLARI ====================
# ==================== OLDINGI SAHIFAGA O'TISH ====================
async def handle_previous_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Oldingi sahifaga o'tish"""
    current_category = context.user_data.get('current_category')
    current_subject = context.user_data.get('current_subject')
    category_type = context.user_data.get('category_type', 'hollywood')
    
    if current_category and current_subject:
        current_page = context.user_data.get(f'page_{current_category}_{current_subject}', 1)
        if current_page > 1:
            context.user_data[f'page_{current_category}_{current_subject}'] = current_page - 1
            await send_paginated_content(update, context, current_category, current_subject, category_type)
        else:
            await update.message.reply_text("❌ Siz birinchi sahifadasiz")
            
# ==================== ASOSIY MENYUGA QAYTISH HANDLERI ====================
async def handle_main_menu_return(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asosiy menyuga qaytish"""
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    # User data ni tozalash
    keys_to_remove = [key for key in context.user_data.keys() if key.startswith('page_') or key.startswith('current_')]
    for key in keys_to_remove:
        del context.user_data[key]
    
    if await admin_panel.check_admin(user_id):
        await update.message.reply_text(
            "👨‍💻 Admin panelga qaytdingiz:",
            reply_markup=admin_panel.get_admin_main_menu()
        )
    else:
        await update.message.reply_text(
            "🏠 Asosiy menyuga qaytingiz:",
            reply_markup=get_main_menu()
        )    

# ==================== ASOSIY MENYU HANDLERI ====================
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Asosiy menyuga qaytish - YANGILANGAN VERSIYA"""
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    # User data ni tozalash
    keys_to_remove = [key for key in context.user_data.keys() if key.startswith('page_') or key.startswith('current_')]
    for key in keys_to_remove:
        del context.user_data[key]
        print(f"DEBUG: User data tozalandi: {key}")
    
    if await admin_panel.check_admin(user_id):
        await update.message.reply_text(
            "👨‍💻 Admin panelga qaytdingiz:",
            reply_markup=admin_panel.get_admin_main_menu()
        )
    else:
        await update.message.reply_text(
            "🏠 Asosiy menyuga qaytingiz:",
            reply_markup=get_main_menu()
        )  

# ==================== UNIVERSAL ASOSIY MENYU HANDLERI ====================
async def universal_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha joylardan asosiy menyuga qaytish"""
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    # Barcha sahifalash ma'lumotlarini tozalash
    for key in list(context.user_data.keys()):
        if key.startswith('page_') or key.startswith('current_') or key.startswith('waiting_'):
            del context.user_data[key]
    
    if await admin_panel.check_admin(user_id):
        await update.message.reply_text(
            "👨‍💻 Admin panelga qaytdingiz:",
            reply_markup=admin_panel.get_admin_main_menu()
        )
    else:
        await update.message.reply_text(
            "🏠 Asosiy menyuga qaytingiz:",
            reply_markup=get_main_menu()
        )      

# ==================== KEYINGI SAHIFAGA O'TISH ====================
async def handle_next_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Keyingi sahifaga o'tish"""
    current_category = context.user_data.get('current_category')
    current_subject = context.user_data.get('current_subject')
    category_type = context.user_data.get('category_type', 'hollywood')
    
    if current_category and current_subject:
        current_page = context.user_data.get(f'page_{current_category}_{current_subject}', 1)
        contents, total_pages, total_count = db.get_content_by_subject_paginated(
            current_category, current_subject, current_page + 1
        )
        if contents:
            context.user_data[f'page_{current_category}_{current_subject}'] = current_page + 1
            await send_paginated_content(update, context, current_category, current_subject, category_type)
        else:
            await update.message.reply_text("❌ Siz oxirgi sahifadasiz")

async def handle_next_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Keyingi sahifaga o'tish"""
    current_category = context.user_data.get('current_category')
    current_subject = context.user_data.get('current_subject')
    category_type = context.user_data.get('category_type', 'hollywood')
    
    if current_category and current_subject:
        current_page = context.user_data.get(f'page_{current_category}_{current_subject}', 1)
        contents, total_pages, total_count = db.get_content_by_subject_paginated(
            current_category, current_subject, current_page + 1
        )
        if contents:
            context.user_data[f'page_{current_category}_{current_subject}'] = current_page + 1
            await send_paginated_content(update, context, current_category, current_subject, category_type)

async def handle_page_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sahifa raqamini qayta ishlash"""
    message_text = update.message.text
    page_text = message_text.replace('🔹 ', '').strip()
    
    if page_text.isdigit():
        page = int(page_text)
        current_category = context.user_data.get('current_category')
        current_subject = context.user_data.get('current_subject')
        category_type = context.user_data.get('category_type', 'hollywood')
        
        if current_category and current_subject:
            contents, total_pages, total_count = db.get_content_by_subject_paginated(
                current_category, current_subject, page
            )
            if contents:
                context.user_data[f'page_{current_category}_{current_subject}'] = page
                await send_paginated_content(update, context, current_category, current_subject, category_type)

# ==================== HOLLYWOOD KONTENTLARINI KO'RSATISH FUNKSIYALARI ====================
async def show_mel_gibson_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hollywood"
    context.user_data['current_subject'] = "🎬 Mel Gibson Kinolari"
    context.user_data['category_type'] = "hollywood"
    context.user_data["page_hollywood_🎬 Mel Gibson Kinolari"] = 1
    await send_paginated_content(update, context, "hollywood", "🎬 Mel Gibson Kinolari", "hollywood")

async def show_arnold_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hollywood"
    context.user_data['current_subject'] = "💪 Arnold Schwarzenegger Kinolari"
    context.user_data['category_type'] = "hollywood"
    context.user_data["page_hollywood_💪 Arnold Schwarzenegger Kinolari"] = 1
    await send_paginated_content(update, context, "hollywood", "💪 Arnold Schwarzenegger Kinolari", "hollywood")

async def show_stallone_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hollywood"
    context.user_data['current_subject'] = "🥊 Sylvester Stallone Kinolari"
    context.user_data['category_type'] = "hollywood"
    context.user_data["page_hollywood_🥊 Sylvester Stallone Kinolari"] = 1
    await send_paginated_content(update, context, "hollywood", "🥊 Sylvester Stallone Kinolari", "hollywood")

async def show_statham_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hollywood"
    context.user_data['current_subject'] = "🚗 Jason Statham Kinolari"
    context.user_data['category_type'] = "hollywood"
    context.user_data["page_hollywood_🚗 Jason Statham Kinolari"] = 1
    await send_paginated_content(update, context, "hollywood", "🚗 Jason Statham Kinolari", "hollywood")

async def show_jackie_chan_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hollywood"
    context.user_data['current_subject'] = "🐉 Jeki Chan Kinolari"
    context.user_data['category_type'] = "hollywood"
    context.user_data["page_hollywood_🐉 Jeki Chan Kinolari"] = 1
    await send_paginated_content(update, context, "hollywood", "🐉 Jeki Chan Kinolari", "hollywood")

async def show_adkins_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hollywood"
    context.user_data['current_subject'] = "🥋 Skod Adkins Kinolari"
    context.user_data['category_type'] = "hollywood"
    context.user_data["page_hollywood_🥋 Skod Adkins Kinolari"] = 1
    await send_paginated_content(update, context, "hollywood", "🥋 Skod Adkins Kinolari", "hollywood")

async def show_denzel_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hollywood"
    context.user_data['current_subject'] = "🎭 Denzil Washington Kinolari"
    context.user_data['category_type'] = "hollywood"
    context.user_data["page_hollywood_🎭 Denzil Washington Kinolari"] = 1
    await send_paginated_content(update, context, "hollywood", "🎭 Denzil Washington Kinolari", "hollywood")

async def show_van_damme_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hollywood"
    context.user_data['current_subject'] = "💥 Jan Clod Van Dam Kinolari"
    context.user_data['category_type'] = "hollywood"
    context.user_data["page_hollywood_💥 Jan Clod Van Dam Kinolari"] = 1
    await send_paginated_content(update, context, "hollywood", "💥 Jan Clod Van Dam Kinolari", "hollywood")

async def show_bruce_lee_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hollywood"
    context.user_data['current_subject'] = "👊 Brus Li Kinolari"
    context.user_data['category_type'] = "hollywood"
    context.user_data["page_hollywood_👊 Brus Li Kinolari"] = 1
    await send_paginated_content(update, context, "hollywood", "👊 Brus Li Kinolari", "hollywood")

async def show_jim_carrey_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hollywood"
    context.user_data['current_subject'] = "😂 Jim Cerry Kinolari"
    context.user_data['category_type'] = "hollywood"
    context.user_data["page_hollywood_😂 Jim Cerry Kinolari"] = 1
    await send_paginated_content(update, context, "hollywood", "😂 Jim Cerry Kinolari", "hollywood")

async def show_johnny_depp_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hollywood"
    context.user_data['current_subject'] = "🎩 Jonni Depp Kinolari"
    context.user_data['category_type'] = "hollywood"
    context.user_data["page_hollywood_🎩 Jonni Depp Kinolari"] = 1
    await send_paginated_content(update, context, "hollywood", "🎩 Jonni Depp Kinolari", "hollywood")

async def show_other_hollywood_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hollywood"
    context.user_data['current_subject'] = "🌟 Boshqa Hollywood Kinolari"
    context.user_data['category_type'] = "hollywood"
    context.user_data["page_hollywood_🌟 Boshqa Hollywood Kinolari"] = 1
    await send_paginated_content(update, context, "hollywood", "🌟 Boshqa Hollywood Kinolari", "hollywood")

# ==================== RUS KONTENTLARINI KO'RSATISH FUNKSIYALARI ====================
async def show_love_in_work(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "russian"
    context.user_data['current_subject'] = "💘 Ishdagi Ishq"
    context.user_data['category_type'] = "russian"
    context.user_data["page_russian_💘 Ishdagi Ishq"] = 1
    await send_paginated_content(update, context, "russian", "💘 Ishdagi Ishq", "russian")

async def show_shurik_adventures(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "russian"
    context.user_data['current_subject'] = "🎭 Shurikning Sarguzashtlari"
    context.user_data['category_type'] = "russian"
    context.user_data["page_russian_🎭 Shurikning Sarguzashtlari"] = 1
    await send_paginated_content(update, context, "russian", "🎭 Shurikning Sarguzashtlari", "russian")

async def show_ivan_vasilivich(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "russian"
    context.user_data['current_subject'] = "🔄 Ivan Vasilivich"
    context.user_data['category_type'] = "russian"
    context.user_data["page_russian_🔄 Ivan Vasilivich"] = 1
    await send_paginated_content(update, context, "russian", "🔄 Ivan Vasilivich", "russian")

async def show_match_going(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "russian"
    context.user_data['current_subject'] = "🔥 Gugurtga Ketib"
    context.user_data['category_type'] = "russian"
    context.user_data["page_russian_🔥 Gugurtga Ketib"] = 1
    await send_paginated_content(update, context, "russian", "🔥 Gugurtga Ketib", "russian")

async def show_diamond_arm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "russian"
    context.user_data['current_subject'] = "🕵️ If Qalqasing Mahbuzi"
    context.user_data['category_type'] = "russian"
    context.user_data["page_russian_🕵️ If Qalqasing Mahbuzi"] = 1
    await send_paginated_content(update, context, "russian", "🕵️ If Qalqasing Mahbuzi", "russian")

async def show_ten_negro_children(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "russian"
    context.user_data['current_subject'] = "👶 O'nta Neger Bolasi"
    context.user_data['category_type'] = "russian"
    context.user_data["page_russian_👶 O'nta Neger Bolasi"] = 1
    await send_paginated_content(update, context, "russian", "👶 O'nta Neger Bolasi", "russian")

async def show_elusive_avengers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "russian"
    context.user_data['current_subject'] = "⚔️ Qo'lga Tushmas Qasoskorlar"
    context.user_data['category_type'] = "russian"
    context.user_data["page_russian_⚔️ Qo'lga Tushmas Qasoskorlar"] = 1
    await send_paginated_content(update, context, "russian", "⚔️ Qo'lga Tushmas Qasoskorlar", "russian")

async def show_all_russian_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "russian"
    context.user_data['current_subject'] = "🎬 Barcha Rus Kinolari"
    context.user_data['category_type'] = "russian"
    context.user_data["page_russian_🎬 Barcha Rus Kinolari"] = 1
    await send_paginated_content(update, context, "russian", "🎬 Barcha Rus Kinolari", "russian")

# ==================== O'ZBEK KINOLARI KONTENTLARINI KO'RSATISH ====================
async def show_mahalla_duv_duv_gap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "uzbek"
    context.user_data['current_subject'] = "🏘️ Mahallada Duv-Duv Gap"
    context.user_data['category_type'] = "uzbek"
    context.user_data["page_uzbek_🏘️ Mahallada Duv-Duv Gap"] = 1
    await send_paginated_content(update, context, "uzbek", "🏘️ Mahallada Duv-Duv Gap", "uzbek")

async def show_kelinlar_qozgaloni(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "uzbek"
    context.user_data['current_subject'] = "👰 Kelinlar Qo'zg'aloni"
    context.user_data['category_type'] = "uzbek"
    context.user_data["page_uzbek_👰 Kelinlar Qo'zg'aloni"] = 1
    await send_paginated_content(update, context, "uzbek", "👰 Kelinlar Qo'zg'aloni", "uzbek")

async def show_abdullajon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "uzbek"
    context.user_data['current_subject'] = "👨 Abdullajon"
    context.user_data['category_type'] = "uzbek"
    context.user_data["page_uzbek_👨 Abdullajon"] = 1
    await send_paginated_content(update, context, "uzbek", "👨 Abdullajon", "uzbek")

async def show_suyinchi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "uzbek"
    context.user_data['current_subject'] = "😊 Suyinchi"
    context.user_data['category_type'] = "uzbek"
    context.user_data["page_uzbek_😊 Suyinchi"] = 1
    await send_paginated_content(update, context, "uzbek", "😊 Suyinchi", "uzbek")

async def show_chinor_duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "uzbek"
    context.user_data['current_subject'] = "🌳 Chinor Ositidagi Duel"
    context.user_data['category_type'] = "uzbek"
    context.user_data["page_uzbek_🌳 Chinor Ositidagi Duel"] = 1
    await send_paginated_content(update, context, "uzbek", "🌳 Chinor Ositidagi Duel", "uzbek")

async def show_yaratganga_shukur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "uzbek"
    context.user_data['current_subject'] = "🙏 Yaratganga Shukur"
    context.user_data['category_type'] = "uzbek"
    context.user_data["page_uzbek_🙏 Yaratganga Shukur"] = 1
    await send_paginated_content(update, context, "uzbek", "🙏 Yaratganga Shukur", "uzbek")

async def show_yor_yor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "uzbek"
    context.user_data['current_subject'] = "💃 Yor-Yor"
    context.user_data['category_type'] = "uzbek"
    context.user_data["page_uzbek_💃 Yor-Yor"] = 1
    await send_paginated_content(update, context, "uzbek", "💃 Yor-Yor", "uzbek")

async def show_tuylar_muborak(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "uzbek"
    context.user_data['current_subject'] = "🎉 To'ylar Muborak"
    context.user_data['category_type'] = "uzbek"
    context.user_data["page_uzbek_🎉 To'ylar Muborak"] = 1
    await send_paginated_content(update, context, "uzbek", "🎉 To'ylar Muborak", "uzbek")

async def show_bomba(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "uzbek"
    context.user_data['current_subject'] = "💣 Bomba"
    context.user_data['category_type'] = "uzbek"
    context.user_data["page_uzbek_💣 Bomba"] = 1
    await send_paginated_content(update, context, "uzbek", "💣 Bomba", "uzbek")

async def show_shum_bola(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "uzbek"
    context.user_data['current_subject'] = "😜 Shum Bola"
    context.user_data['category_type'] = "uzbek"
    context.user_data["page_uzbek_😜 Shum Bola"] = 1
    await send_paginated_content(update, context, "uzbek", "😜 Shum Bola", "uzbek")

async def show_temir_xotin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "uzbek"
    context.user_data['current_subject'] = "⚡ Temir Xotin"
    context.user_data['category_type'] = "uzbek"
    context.user_data["page_uzbek_⚡ Temir Xotin"] = 1
    await send_paginated_content(update, context, "uzbek", "⚡ Temir Xotin", "uzbek")

async def show_all_uzbek_classic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "uzbek"
    context.user_data['current_subject'] = "🎬 Barcha UZ Klassik Kinolari"
    context.user_data['category_type'] = "uzbek"
    context.user_data["page_uzbek_🎬 Barcha UZ Klassik Kinolari"] = 1
    await send_paginated_content(update, context, "uzbek", "🎬 Barcha UZ Klassik Kinolari", "uzbek")

# ==================== ISLOMIY KONTENTLARINI KO'RSATISH ====================
async def show_umar_ibn_hattab(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "islamic"
    context.user_data['current_subject'] = "📿 Umar Ibn Ali Hattob To'liq"
    context.user_data['category_type'] = "islamic"
    context.user_data["page_islamic_📿 Umar Ibn Ali Hattob To'liq"] = 1
    await send_paginated_content(update, context, "islamic", "📿 Umar Ibn Ali Hattob To'liq", "islamic")

async def show_nur_scattering_moon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "islamic"
    context.user_data['current_subject'] = "🌙 Olamga Nur Sochgan Oy To'liq"
    context.user_data['category_type'] = "islamic"
    context.user_data["page_islamic_🌙 Olamga Nur Sochgan Oy To'liq"] = 1
    await send_paginated_content(update, context, "islamic", "🌙 Olamga Nur Sochgan Oy To'liq", "islamic")

async def show_all_islamic_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "islamic"
    context.user_data['current_subject'] = "🎬 Barcha Islomiy Kinolar"
    context.user_data['category_type'] = "islamic"
    context.user_data["page_islamic_🎬 Barcha Islomiy Kinolar"] = 1
    await send_paginated_content(update, context, "islamic", "🎬 Barcha Islomiy Kinolar", "islamic")

async def show_all_islamic_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "islamic"
    context.user_data['current_subject'] = "📺 Barcha Islomiy Seriallar"
    context.user_data['category_type'] = "islamic"
    context.user_data["page_islamic_📺 Barcha Islomiy Seriallar"] = 1
    await send_paginated_content(update, context, "islamic", "📺 Barcha Islomiy Seriallar", "islamic")

# ==================== TURK KONTENTLARINI KO'RSATISH ====================
async def show_sultan_abdulhamid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "turkish"
    context.user_data['current_subject'] = "👑 Sulton Abdulhamidhon"
    context.user_data['category_type'] = "turkish"
    context.user_data["page_turkish_👑 Sulton Abdulhamidhon"] = 1
    await send_paginated_content(update, context, "turkish", "👑 Sulton Abdulhamidhon", "turkish")

async def show_wolves_lair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "turkish"
    context.user_data['current_subject'] = "🐺 Qashqirlar Makoni"
    context.user_data['category_type'] = "turkish"
    context.user_data["page_turkish_🐺 Qashqirlar Makoni"] = 1
    await send_paginated_content(update, context, "turkish", "🐺 Qashqirlar Makoni", "turkish")

async def show_all_turkish_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "turkish"
    context.user_data['current_subject'] = "📺 Barcha Turk Seriallari"
    context.user_data['category_type'] = "turkish"
    context.user_data["page_turkish_📺 Barcha Turk Seriallari"] = 1
    await send_paginated_content(update, context, "turkish", "📺 Barcha Turk Seriallari", "turkish")

# ==================== BOLALAR KONTENTLARINI KO'RSATISH ====================
async def show_home_alone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "kids"
    context.user_data['current_subject'] = "👦 Bola Uyda Yolg'iz 1-3"
    context.user_data['category_type'] = "kids"
    context.user_data["page_kids_👦 Bola Uyda Yolg'iz 1-3"] = 1
    await send_paginated_content(update, context, "kids", "👦 Bola Uyda Yolg'iz 1-3", "kids")

async def show_flying_david(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "kids"
    context.user_data['current_subject'] = "✈️ Uchuvchi Devid"
    context.user_data['category_type'] = "kids"
    context.user_data["page_kids_✈️ Uchuvchi Devid"] = 1
    await send_paginated_content(update, context, "kids", "✈️ Uchuvchi Devid", "kids")

async def show_harry_potter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "kids"
    context.user_data['current_subject'] = "⚡ Garry Poter 1-4"
    context.user_data['category_type'] = "kids"
    context.user_data["page_kids_⚡ Garry Poter 1-4"] = 1
    await send_paginated_content(update, context, "kids", "⚡ Garry Poter 1-4", "kids")

async def show_all_kids_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "kids"
    context.user_data['current_subject'] = "🎬 Barcha Bolalar Kinolari"
    context.user_data['category_type'] = "kids"
    context.user_data["page_kids_🎬 Barcha Bolalar Kinolari"] = 1
    await send_paginated_content(update, context, "kids", "🎬 Barcha Bolalar Kinolari", "kids")

# ==================== MULTFILMLAR KONTENTLARINI KO'RSATISH ====================
async def show_ice_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "cartoons"
    context.user_data['current_subject'] = "❄️ Muzlik Davri 1-3"
    context.user_data['category_type'] = "cartoons"
    context.user_data["page_cartoons_❄️ Muzlik Davri 1-3"] = 1
    await send_paginated_content(update, context, "cartoons", "❄️ Muzlik Davri 1-3", "cartoons")

async def show_tom_jerry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "cartoons"
    context.user_data['current_subject'] = "🐭 Tom & Jerry"
    context.user_data['category_type'] = "cartoons"
    context.user_data["page_cartoons_🐭 Tom & Jerry"] = 1
    await send_paginated_content(update, context, "cartoons", "🐭 Tom & Jerry", "cartoons")

async def show_winnie_pooh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "cartoons"
    context.user_data['current_subject'] = "🐻 Bori va Quyon"
    context.user_data['category_type'] = "cartoons"
    context.user_data["page_cartoons_🐻 Bori va Quyon"] = 1
    await send_paginated_content(update, context, "cartoons", "🐻 Bori va Quyon", "cartoons")

async def show_bear_and_masha(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "cartoons"
    context.user_data['current_subject'] = "🍯 Ayiq va Masha"
    context.user_data['category_type'] = "cartoons"
    context.user_data["page_cartoons_🍯 Ayiq va Masha"] = 1
    await send_paginated_content(update, context, "cartoons", "🍯 Ayiq va Masha", "cartoons")

async def show_kungfu_panda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "cartoons"
    context.user_data['current_subject'] = "🐼 Kungfu Panda 1-4"
    context.user_data['category_type'] = "cartoons"
    context.user_data["page_cartoons_🐼 Kungfu Panda 1-4"] = 1
    await send_paginated_content(update, context, "cartoons", "🐼 Kungfu Panda 1-4", "cartoons")

async def show_mustang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "cartoons"
    context.user_data['current_subject'] = "🐎 Mustang"
    context.user_data['category_type'] = "cartoons"
    context.user_data["page_cartoons_🐎 Mustang"] = 1
    await send_paginated_content(update, context, "cartoons", "🐎 Mustang", "cartoons")

async def show_all_cartoons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "cartoons"
    context.user_data['current_subject'] = "🎬 Barcha Multfilmlar"
    context.user_data['category_type'] = "cartoons"
    context.user_data["page_cartoons_🎬 Barcha Multfilmlar"] = 1
    await send_paginated_content(update, context, "cartoons", "🎬 Barcha Multfilmlar", "cartoons")

# ==================== KOREYS KONTENTLARINI KO'RSATISH ====================
async def show_criminals_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "korean_movies"
    context.user_data['current_subject'] = "🏙️ Jinoyatchilar Shahri 1-4"
    context.user_data['category_type'] = "korean_movies"
    context.user_data["page_korean_movies_🏙️ Jinoyatchilar Shahri 1-4"] = 1
    await send_paginated_content(update, context, "korean_movies", "🏙️ Jinoyatchilar Shahri 1-4", "korean_movies")

async def show_all_korean_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "korean_movies"
    context.user_data['current_subject'] = "🎬 Barcha Koreys Kinolari"
    context.user_data['category_type'] = "korean_movies"
    context.user_data["page_korean_movies_🎬 Barcha Koreys Kinolari"] = 1
    await send_paginated_content(update, context, "korean_movies", "🎬 Barcha Koreys Kinolari", "korean_movies")

async def show_winter_sonata(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "korean_series"
    context.user_data['current_subject'] = "❄️ Qish Sonatasi 1-20"
    context.user_data['category_type'] = "korean_series"
    context.user_data["page_korean_series_❄️ Qish Sonatasi 1-20"] = 1
    await send_paginated_content(update, context, "korean_series", "❄️ Qish Sonatasi 1-20", "korean_series")

async def show_summer_fever(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "korean_series"
    context.user_data['current_subject'] = "☀️ Yoz Ifori 1-20"
    context.user_data['category_type'] = "korean_series"
    context.user_data["page_korean_series_☀️ Yoz Ifori 1-20"] = 1
    await send_paginated_content(update, context, "korean_series", "☀️ Yoz Ifori 1-20", "korean_series")

async def show_and_bank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "korean_series"
    context.user_data['current_subject'] = "🏦 Va Bank 1-20"
    context.user_data['category_type'] = "korean_series"
    context.user_data["page_korean_series_🏦 Va Bank 1-20"] = 1
    await send_paginated_content(update, context, "korean_series", "🏦 Va Bank 1-20", "korean_series")

async def show_jumong(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "korean_series"
    context.user_data['current_subject'] = "👑 Jumong Barcha Qismlar"
    context.user_data['category_type'] = "korean_series"
    context.user_data["page_korean_series_👑 Jumong Barcha Qismlar"] = 1
    await send_paginated_content(update, context, "korean_series", "👑 Jumong Barcha Qismlar", "korean_series")

async def show_sea_ruler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "korean_series"
    context.user_data['current_subject'] = "⚓ Dengiz Hukumdori Barcha Qismlar"
    context.user_data['category_type'] = "korean_series"
    context.user_data["page_korean_series_⚓ Dengiz Hukumdori Barcha Qismlar"] = 1
    await send_paginated_content(update, context, "korean_series", "⚓ Dengiz Hukumdori Barcha Qismlar", "korean_series")

# ==================== QALBIM CHECHAGI HANDLERI ====================
async def show_heartbeat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Qalbim Chechagi serialini ko'rsatish"""
    context.user_data['current_category'] = "korean_series"
    context.user_data['current_subject'] = "💖 Qalbim Chechagi 1-17"
    context.user_data['category_type'] = "korean_series"
    context.user_data["page_korean_series_💖 Qalbim Chechagi 1-17"] = 1
    await send_paginated_content(update, context, "korean_series", "💖 Qalbim Chechagi 1-17", "korean_series")

async def show_all_korean_series(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "korean_series"
    context.user_data['current_subject'] = "📺 Barcha Koreys Seriallari"
    context.user_data['category_type'] = "korean_series"
    context.user_data["page_korean_series_📺 Barcha Koreys Seriallari"] = 1
    await send_paginated_content(update, context, "korean_series", "📺 Barcha Koreys Seriallari", "korean_series")

# ==================== MUSIQA KONTENTLARINI KO'RSATISH ====================
async def show_uzbek_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "music"
    context.user_data['current_subject'] = "🎵 O'zbek Musiqalari"
    context.user_data['category_type'] = "music"
    context.user_data["page_music_🎵 O'zbek Musiqalari"] = 1
    await send_paginated_content(update, context, "music", "🎵 O'zbek Musiqalari", "music")

async def show_russian_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "music"
    context.user_data['current_subject'] = "🎶 Rus Musiqalari"
    context.user_data['category_type'] = "music"
    context.user_data["page_music_🎶 Rus Musiqalari"] = 1
    await send_paginated_content(update, context, "music", "🎶 Rus Musiqalari", "music")

async def show_hindi_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "music"
    context.user_data['current_subject'] = "🎼 Hind Musiqalari"
    context.user_data['category_type'] = "music"
    context.user_data["page_music_🎼 Hind Musiqalari"] = 1
    await send_paginated_content(update, context, "music", "🎼 Hind Musiqalari", "music")

async def show_turkish_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "music"
    context.user_data['current_subject'] = "🎧 Turk Musiqalari"
    context.user_data['category_type'] = "music"
    context.user_data["page_music_🎧 Turk Musiqalari"] = 1
    await send_paginated_content(update, context, "music", "🎧 Turk Musiqalari", "music")

async def show_korean_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "music"
    context.user_data['current_subject'] = "🎤 Koreys Musiqalari"
    context.user_data['category_type'] = "music"
    context.user_data["page_music_🎤 Koreys Musiqalari"] = 1
    await send_paginated_content(update, context, "music", "🎤 Koreys Musiqalari", "music")

async def show_all_music(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "music"
    context.user_data['current_subject'] = "🎹 Barcha Musiqalar"
    context.user_data['category_type'] = "music"
    context.user_data["page_music_🎹 Barcha Musiqalar"] = 1
    await send_paginated_content(update, context, "music", "🎹 Barcha Musiqalar", "music")
    
    # ==================== HIND KONTENTLARINI KO'RSATISH FUNKSIYALARI ====================
async def show_shahrukh_khan_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hindi"
    context.user_data['current_subject'] = "🤴 Shakruhkhan Kinolari"
    context.user_data['category_type'] = "hindi"
    context.user_data["page_hindi_🤴 Shakruhkhan Kinolari"] = 1
    await send_paginated_content(update, context, "hindi", "🤴 Shakruhkhan Kinolari", "hindi")

async def show_amir_khan_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hindi"
    context.user_data['current_subject'] = "🎯 Amirkhan Kinolari"
    context.user_data['category_type'] = "hindi"
    context.user_data["page_hindi_🎯 Amirkhan Kinolari"] = 1
    await send_paginated_content(update, context, "hindi", "🎯 Amirkhan Kinolari", "hindi")

async def show_akshay_kumar_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hindi"
    context.user_data['current_subject'] = "🦸 Akshay Kumar Kinolari"
    context.user_data['category_type'] = "hindi"
    context.user_data["page_hindi_🦸 Akshay Kumar Kinolari"] = 1
    await send_paginated_content(update, context, "hindi", "🦸 Akshay Kumar Kinolari", "hindi")

async def show_salman_khan_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hindi"
    context.user_data['current_subject'] = "👑 Salmonkhan Kinolari"
    context.user_data['category_type'] = "hindi"
    context.user_data["page_hindi_👑 Salmonkhan Kinolari"] = 1
    await send_paginated_content(update, context, "hindi", "👑 Salmonkhan Kinolari", "hindi")

async def show_saif_ali_khan_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hindi"
    context.user_data['current_subject'] = "🌟 SayfAlihon Kinolari"
    context.user_data['category_type'] = "hindi"
    context.user_data["page_hindi_🌟 SayfAlihon Kinolari"] = 1
    await send_paginated_content(update, context, "hindi", "🌟 SayfAlihon Kinolari", "hindi")

async def show_amitabh_bachchan_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hindi"
    context.user_data['current_subject'] = "🎭 Amitahbachchan Kinolari"
    context.user_data['category_type'] = "hindi"
    context.user_data["page_hindi_🎭 Amitahbachchan Kinolari"] = 1
    await send_paginated_content(update, context, "hindi", "🎭 Amitahbachchan Kinolari", "hindi")

async def show_mithun_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hindi"
    context.user_data['current_subject'] = "💃 MethunChakraborty Kinolari"
    context.user_data['category_type'] = "hindi"
    context.user_data["page_hindi_💃 MethunChakraborty Kinolari"] = 1
    await send_paginated_content(update, context, "hindi", "💃 MethunChakraborty Kinolari", "hindi")

async def show_dharmendra_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hindi"
    context.user_data['current_subject'] = "👨‍🦳 Dharmendra Kinolari"
    context.user_data['category_type'] = "hindi"
    context.user_data["page_hindi_👨‍🦳 Dharmendra Kinolari"] = 1
    await send_paginated_content(update, context, "hindi", "👨‍🦳 Dharmendra Kinolari", "hindi")

async def show_raj_kapur_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hindi"
    context.user_data['current_subject'] = "🎬 Raj Kapur Kinolari"
    context.user_data['category_type'] = "hindi"
    context.user_data["page_hindi_🎬 Raj Kapur Kinolari"] = 1
    await send_paginated_content(update, context, "hindi", "🎬 Raj Kapur Kinolari", "hindi")

async def show_other_hindi_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['current_category'] = "hindi"
    context.user_data['current_subject'] = "📀 Boshqa Hind Kinolari"
    context.user_data['category_type'] = "hindi"
    context.user_data["page_hindi_📀 Boshqa Hind Kinolari"] = 1
    await send_paginated_content(update, context, "hindi", "📀 Boshqa Hind Kinolari", "hindi")
    
# ==================== DEBUG COMMAND ====================
async def debug_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kontentlarni debug qilish"""
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    if not await admin_panel.check_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    all_content = db.get_all_content()
    
    if all_content:
        debug_info = f"📊 Database da {len(all_content)} ta kontent:\n\n"
        for content in all_content[:10]:
            debug_info += f"ID: {content[0]}\nNomi: {content[1]}\nKategoriya: {content[3]}\nFayl turi: {content[5]}\n\n"
        
        await update.message.reply_text(debug_info)
    else:
        await update.message.reply_text("❌ Database da hech qanday kontent yo'q")

# ==================== BAZA HOLATINI TEKSHIRISH ====================
async def check_database(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Database holatini tekshirish"""
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    if not await admin_panel.check_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    try:
        users = db.get_all_users()
        all_content = db.get_all_content()
        
        status_text = (
            "📊 Database Holati:\n\n"
            f"👥 Foydalanuvchilar: {len(users)} ta\n"
            f"🎬 Kontentlar: {len(all_content)} ta\n\n"
            f"✅ Database ishlayapti"
        )
        
        await update.message.reply_text(status_text)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Database xatosi: {e}")

# ==================== KONTENTLARNI TEKSHIRISH COMMAND ====================
async def check_uzbek_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """O'zbek kinolarini tekshirish"""
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    if not await admin_panel.check_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    contents = db.get_content_by_subject("uzbek", "🏘️ Mahallada Duv-Duv Gap")
    
    if contents:
        content_info = f"📊 🏘️ Mahallada Duv-Duv Gap kontentlari ({len(contents)} ta):\n\n"
        for content in contents:
            content_info += f"🎬 {content[1]}\n📁 {content[3]}\n📄 {content[5]}\n\n"
        
        await update.message.reply_text(content_info)
    else:
        await update.message.reply_text("❌ Hech qanday kontent topilmadi")

# ==================== QIDIRUV HANDLERLARI ====================
async def search_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 Kino qidirish:\nIltimos kino nomini kiriting:",
        reply_markup=ReplyKeyboardMarkup([["🔙 Asosiy menyu"]], resize_keyboard=True)
    )

async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    if query != "🔙 Asosiy menyu":
        results = db.search_content(query)
        if results:
            for item in results[:3]:
                await update.message.reply_text("🎬 " + item[1] + "\n📝 " + item[2])
        else:
            await update.message.reply_text("❌ '" + query + "' bo'yicha hech narsa topilmadi")
    else:
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=get_main_menu())

# ==================== PULLIK HIZMATLAR HANDLERLARI ====================
async def show_premium_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💼 Pullik Hizmatlar bo'limi\n\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=get_premium_menu()
    ) 
    
# ==================== YANGI: PULLIK KONTENT KATEGORIYASINI KO'RSATISH ====================
async def show_premium_content_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pullik kontent kategoriyasini ko'rsatish"""
    category_map = {
        "🎬 Pullik Kinolar": "premium_movies",
        "📺 Pullik Seriallar": "premium_series",
        "🐰 Pullik Multfilmlar": "premium_cartoons", 
        "🎵 Pullik Musiqalar": "premium_music"
    }
    
    selected_category = update.message.text
    premium_category = category_map.get(selected_category)
    
    if premium_category:
        # Pullik kontentlarni olish
        contents = db.get_premium_content_by_category("premium", premium_category)
        
        if contents:
            content_list = "💰 *Pullik Kontentlar:*\n\n"
            
            for content in contents[:10]:  # Faqat birinchi 10 tasi
                content_list += f"🎬 {content[3]}\n💰 {content[5]:,} so'm\n\n"
            
            if len(contents) > 10:
                content_list += f"... va yana {len(contents) - 10} ta kontent"
            
            await update.message.reply_text(
                content_list + "\n\n⬇️ Kontentni tanlang va to'lov qiling:",
                reply_markup=get_premium_content_selection_menu(contents),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Hozircha {selected_category} mavjud emas.\n\n"
                "⏳ Tez orada qo'shiladi.",
                reply_markup=get_premium_menu_simple()
            )

def get_premium_content_selection_menu(contents):
    """Pullik kontentlarni tanlash menyusi"""
    keyboard = []
    
    for content in contents[:5]:  # Faqat birinchi 5 tasi
        keyboard.append([f"💰 {content[3]}"])
    
    keyboard.append(["🔙 Orqaga", "🏠 Asosiy menyu"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)    
    
# ==================== YANGI: PULLIK KONTENT HANDLERLARI ====================

async def show_paid_movies_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kino sotib olish menyusi"""
    text, reply_markup = get_paid_content_menu("movie")
    await update.message.reply_text(text, reply_markup=reply_markup)
    context.user_data['payment_type'] = 'movie'

async def show_paid_series_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Serial sotib olish menyusi"""
    text, reply_markup = get_paid_content_menu("series")
    await update.message.reply_text(text, reply_markup=reply_markup)
    context.user_data['payment_type'] = 'series'

async def show_paid_cartoons_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Multfilm sotib olish menyusi"""
    text, reply_markup = get_paid_content_menu("cartoon")
    await update.message.reply_text(text, reply_markup=reply_markup)
    context.user_data['payment_type'] = 'cartoon'

async def handle_paid_content_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pullik kontent tanlash"""
    content_name = update.message.text.replace("💰 ", "")
    payment_type = context.user_data.get('payment_type', 'movie')
    
    # Narxlarni belgilash
    prices = {
        'movie': 30000,
        'series': 10000, 
        'cartoon': 30000
    }
    
    price = prices.get(payment_type, 30000)
    
    context.user_data['selected_content'] = content_name
    context.user_data['content_price'] = price
    
    await update.message.reply_text(
        f"💳 *To'lov Ma'lumotlari:*\n\n"
        f"🎬 Kontent: {content_name}\n"
        f"💰 Narx: {price:,} so'm\n"
        f"📋 Turi: {'Kino' if payment_type == 'movie' else 'Serial' if payment_type == 'series' else 'Multfilm'}\n\n"
        f"💳 *To'lov kartasi:* 8600 1104 7759 4067\n\n"
        f"To'lov qilgach, chek suratini yuboring yoki 'To\'lov qilish' tugmasini bosing:",
        reply_markup=get_payment_confirmation_menu(),
        parse_mode='Markdown'
    )

async def handle_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """To'lov tasdiqlash"""
    await update.message.reply_text(
        "📸 Iltimos, to'lov cheki suratini yuboring:\n\n"
        "💡 *Eslatma:* Chekda quyidagilar ko'rinishi kerak:\n"
        "• To'lov summasi\n" 
        "• Karta raqami (oxirgi 4 ta raqam)\n"
        "• Sana va vaqt\n\n"
        "Yoki chek ma'lumotlarini matn shaklida yuboring:",
        reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True),
        parse_mode='Markdown'
    )
    context.user_data['waiting_for_receipt'] = True

# ==================== TO'LOV CHEKINI QAYTA ISHLASH ====================
async def handle_payment_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """To'lov chekini qayta ishlash"""
    
    # Agar admin kontent qo'shish jarayonida bo'lsa, bu xabarni e'tiborsiz qoldirish
    if context.user_data.get('waiting_for_content_title') or context.user_data.get('waiting_for_content_description'):
        # Bu xabarni admin kontent qo'shish jarayonida qayta ishlash
        await handle_admin_messages(update, context)
        return
        
    # Agar foydalanuvchi to'lov cheki yuborayotgan bo'lsa
    if context.user_data.get('waiting_for_receipt'):
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        if update.message.photo:
            # Rasm qabul qilish
            file_id = update.message.photo[-1].file_id
            receipt_type = "photo"
        else:
            # Matn qabul qilish
            receipt_text = update.message.text
            file_id = receipt_text
            receipt_type = "text"
        
        content_name = context.user_data.get('selected_content', 'Nomalum')
        content_type = context.user_data.get('payment_type', 'movie')
        price = context.user_data.get('content_price', 30000)
        
        # To'lovni bazaga qo'shish
        db.add_payment(user_id, content_type, content_name, price, file_id)
        
        # Adminga xabar yuborish
        if ADMIN_ID:
            try:
                # Usernameni alohida o'zgaruvchiga olish
                username = update.effective_user.username or "Nomalum"
                
                admin_message = (
                    f"💳 *Yangi To'lov So'rovi:*\n\n"
                    f"👤 Foydalanuvchi: {user_name}\n"
                    f"🆔 ID: {user_id}\n"
                    f"📛 Username: @{username}\n\n"
                    f"🎬 Kontent: {content_name}\n"
                    f"💰 Narx: {price:,} so'm\n"
                    f"📋 Turi: {content_type}\n\n"
                    f"📸 Chek turi: {recept_type}\n\n"
                    f"✅ Tasdiqlash: /confirm_{user_id}_{content_name.replace(' ', '_')}\n"
                    f"❌ Rad etish: /reject_{user_id}_{content_name.replace(' ', '_')}"
                )
                
                if receipt_type == "photo":
                    await context.bot.send_photo(
                        chat_id=int(ADMIN_ID),
                        photo=file_id,
                        caption=admin_message,
                        parse_mode='Markdown'
                    )
                else:
                    await context.bot.send_message(
                        chat_id=int(ADMIN_ID),
                        text=admin_message + f"\n\n📝 Chek matni: {file_id}",
                        parse_mode='Markdown'
                    )
                    
            except Exception as e:
                logging.error(f"Adminga to'lov xabarini yuborishda xatolik: {e}")
        
        await update.message.reply_text(
            "✅ To'lov ma'lumotlari adminga yuborildi!\n\n"
            "⏳ To'lov tekshirilgach kontent sizga ochiladi.\n"
            "📞 Tezroq javob olish uchun: @Operator_1985",
            reply_markup=get_premium_menu()
        )
        
        context.user_data['waiting_for_receipt'] = False
        context.user_data['selected_content'] = None
        context.user_data['payment_type'] = None 

async def show_paid_movies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    warning_text = (
        "⚠️ OGOHLANTIRISH! ⚠️\n\n"
        "Hurmatli foydalanuvchi!\n\n"
        "📝 Mavzulardan chetga chiqmagan holda so'rovlar yuboring\n"
        "🚫 Nomaqbul va xaqoratlik so'zlar ishlatmang\n"
        "👁️ Bot to'liq kuzatiladi, o'zingizni asrang\n"
        "🙏 Tushunganingiz uchun katta rahmat\n\n"
        "👨‍💼 Admin ruhsati bilan\n\n"
        "💳 Admin karta raqami: 8600 1104 7759 4067\n\n"
        "💰 Narxlar:\n"
        "🎬 Birgina kino narhi - 30,000 so'm\n"
        "📺 Birgina serial narhi - 10,000 so'm\n"
        "🐰 Birgina multfilm narhi - 30,000 so'm\n\n"
        "📸 To'lov qilib bo'lgach chek surati yuboring\n"
        "👨‍💼 Adminga yuboring\n\n"
        "❓ Sizni qanday kontentlar qiziqtirmoqda?\n"
        "📝 Shularni batafsil yozing\n\n"
        "📞 Agar botimiz javob bermasa: @Operator_1985"
    )
    
    await update.message.reply_text(
        warning_text,
        reply_markup=get_paid_movies_menu()
    )

async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    instruction_text = (
        "👨‍💼 Adminga xabar yuborish\n\n"
        "📝 Sizni qiziqtirgan kontent nomini uz/ru/en tillarida yozishingiz mumkin\n\n"
        "✅ Agar bu kontentlar mavjud bo'lsa,\n"
        "👨‍💼 Operator sizga javob yuboradi\n\n"
        "💼 Pullik kontentlarni sotib olish pullik hizmat bo'limi bilan tanishib chiqing\n\n"
        "👇 Xabaringizni yozing va yuboring:"
    )
    
    await update.message.reply_text(
        instruction_text,
        reply_markup=get_admin_contact_menu()
    )
    context.user_data['waiting_for_message'] = True

async def show_payment_instructions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment_text = (
        "💳 To'lov va buyurtma tartibi:\n\n"
        "1️⃣ Pullik hizmatlar bilan tanishgan bo'lsangiz\n"
        "2️⃣ Quyidagi ma'lumotlarni yuboring:\n\n"
        "📸 To'lov chek surati\n"
        "📝 Kontent nomi (aniq va xatolarsiz)\n\n"
        "💳 To'lov qilish uchun karta raqami:\n"
        "8600 1104 7759 4067\n\n"
        "📞 Qo'shimcha ma'lumot uchun: @Operator_1985"
    )
    
    await update.message.reply_text(
        payment_text,
        reply_markup=get_admin_contact_menu()
    )

async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_message'):
        user_message = update.message.text
        user_id = update.effective_user.id
        user_name = update.effective_user.first_name
        
        if user_message == "🔙 Orqaga":
            await update.message.reply_text(
                "💼 Pullik Hizmatlar:",
                reply_markup=get_premium_menu()
            )
            context.user_data['waiting_for_message'] = False
            return
        
        if user_message == "📝 Kontent so'rovi yuborish":
            await update.message.reply_text(
                "📝 Kontent so'rovi yuborish:\n\n"
                "Iltimos, qiziqtirgan kontent nomini yozing:",
                reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
            )
            context.user_data['waiting_for_content_request'] = True
            return
            
        if user_message == "💳 To'lov chekini yuborish":
            await update.message.reply_text(
                "💳 To'lov chekini yuborish:\n\n"
                "Iltimos, to'lov chekini rasm shaklida yuboring yoki "
                "chek ma'lumotlarini matn shaklida yozing:",
                reply_markup=ReplyKeyboardMarkup([["🔙 Orqaga"]], resize_keyboard=True)
            )
            context.user_data['waiting_for_payment'] = True
            return
        
        # Kontent so'rovi yuborish
        if context.user_data.get('waiting_for_content_request'):
            if ADMIN_ID:
                try:
                    await context.bot.send_message(
                        int(ADMIN_ID),
                        f"📨 Yangi kontent so'rovi:\n\n"
                        f"👤 Foydalanuvchi: {user_name}\n"
                        f"🆔 ID: {user_id}\n"
                        f"📛 Username: @{update.effective_user.username if update.effective_user.username else 'Noma lum'}\n\n"
                        f"📝 So'rov: {user_message}\n\n"
                        f"💬 Javob berish uchun: /reply_{user_id}"
                    )
                except Exception as e:
                    logging.error(f"Adminga xabar yuborishda xatolik: {e}")
            
            await update.message.reply_text(
                "✅ Kontent so'rovingiz adminga yuborildi!\n\n"
                "⏳ Tez orada javob beradi.\n"
                "👀 Javobni 'Javobni Ko'rish' bo'limida ko'rashingiz mumkin.",
                reply_markup=get_premium_menu()
            )
            context.user_data['waiting_for_content_request'] = False
            
        # To'lov cheki yuborish
        elif context.user_data.get('waiting_for_payment'):
            if ADMIN_ID:
                try:
                    await context.bot.send_message(
                        int(ADMIN_ID),
                        f"💳 Yangi to'lov ma'lumoti:\n\n"
                        f"👤 Foydalanuvchi: {user_name}\n"
                        f"🆔 ID: {user_id}\n"
                        f"📛 Username: @{update.effective_user.username if update.effective_user.username else 'Noma lum'}\n\n"
                        f"📝 To'lov ma'lumoti: {user_message}\n\n"
                        f"💬 Tasdiqlash uchun: /confirm_{user_id}"
                    )
                except Exception as e:
                    logging.error(f"Adminga to'lov ma'lumoti yuborishda xatolik: {e}")
            
            await update.message.reply_text(
                "✅ To'lov ma'lumotingiz adminga yuborildi!\n\n"
                "⏳ To'lov tekshirilgach kontent yuboriladi.\n"
                "👀 Javobni 'Javobni Ko'rish' bo'limida ko'rashingiz mumkin.",
                reply_markup=get_premium_menu()
            )
            context.user_data['waiting_for_payment'] = False
            
        else:
            # Oddiy xabar yuborish
            if ADMIN_ID:
                try:
                    await context.bot.send_message(
                        int(ADMIN_ID),
                        f"📨 Yangi xabar:\n\n"
                        f"👤 Foydalanuvchi: {user_name}\n"
                        f"🆔 ID: {user_id}\n"
                        f"📛 Username: @{update.effective_user.username if update.effective_user.username else 'Noma lum'}\n\n"
                        f"📝 Xabar: {user_message}\n\n"
                        f"💬 Javob berish uchun: /reply_{user_id}"
                    )
                except Exception as e:
                    logging.error(f"Adminga xabar yuborishda xatolik: {e}")
            
            await update.message.reply_text(
                "✅ Xabaringiz adminga yuborildi!\n\n"
                "⏳ Tez orada javob beradi.\n"
                "👀 Javobni 'Javobni Ko'rish' bo'limida ko'rashingiz mumkin.",
                reply_markup=get_premium_menu()
            )
        
        context.user_data['waiting_for_message'] = False

async def check_admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(
        "👀 Javobni ko'rish:\n\n"
        "📨 Hozircha sizga hech qanday javob kelmagan.\n"
        "⏳ Agar admin javob yuborgan bo'lsa, tez orada shu yerda ko'rasiz.\n\n"
        "📞 Shoshilgan bo'lsangiz: @Operator_1985",
        reply_markup=get_premium_menu()
    )

# ==================== PROFIL VA TIL HANDLERLARI ====================
async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_user(user.id)
    if user_data:
        await update.message.reply_text(
            "👤 Profil:\n" +
            "🆔 ID: " + str(user_data[0]) + "\n" +
            "📛 Ism: " + user_data[2] + "\n" +
            "📞 Tel: " + user_data[3]
        )
    else:
        await update.message.reply_text("❌ Profil topilmadi")

# ==================== TIL O'ZGARTIRISH ====================
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tilni o'zgartirish"""
    await update.message.reply_text(
        "🌐 Tilni tanlang:",
        reply_markup=get_language_menu()
    )
    
# ==================== ADMIN PANELDAN CHIQISH ====================
async def admin_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    if await admin_panel.check_admin(user_id):
        await update.message.reply_text(
            "👋 Admin paneldan chiqildi. Asosiy menyuga qaytingiz.",
            reply_markup=get_main_menu()
        )
    else:
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=get_main_menu())

# ==================== YANGI UNIVERSAL HANDLER ====================
async def universal_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha xabarlarni qayta ishlash"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    print(f"DEBUG: Foydalanuvchi {user_id} '{message_text}' deb yozdi")
    
    # Asosiy menyu tugmalari
    if message_text == "📋 Kategoriyalar":
        await show_categories(update, context)
    elif message_text == "🎬 Kino qidirish":
        await search_movies(update, context)
    elif message_text == "👤 Profil":
        await show_profile(update, context)
    elif message_text == "💼 Pullik Hizmatlar":
        await show_premium_services(update, context)
    elif message_text == "🌐 Tilni tanlash":
        await change_language(update, context)
    else:
        print(f"DEBUG: '{message_text}' uchun handler topilmadi")
        
# ==================== UNIVERSAL ADMIN HANDLER ====================
async def universal_admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Barcha admin xabarlarini qayta ishlash"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    print(f"DEBUG ADMIN: User {user_id} sent: '{message_text}'")
    
    # Admin tekshirish
    admin_panel = AdminPanel()
    if not await admin_panel.check_admin(user_id):
        print(f"DEBUG ADMIN: User {user_id} is not admin")
        return
    
    print(f"DEBUG ADMIN: User {user_id} is admin, processing command: '{message_text}'")
    
    # Admin komandalari
    if message_text == "➕ Kontent Qo'shish":
        await admin_panel.show_add_content(update, context)
    elif message_text == "🗑️ Kontent O'chirish":
        await admin_panel.show_delete_content(update, context)
    elif message_text == "📊 Kontent Statistikasi":
        await admin_panel.show_stats(update, context)
    elif message_text == "👥 Foydalanuvchilar":
        await admin_panel.show_users(update, context)
    elif message_text == "🚫 Bloklash":
        await admin_panel.show_block_user(update, context)
    elif message_text == "✅ Blokdan Ochish":
        await admin_panel.show_unblock_user(update, context)
    elif message_text == "📢 Xabar Yuborish":
        await admin_panel.show_broadcast(update, context)
    elif message_text == "📨 Foydalanuvchi Xabarlari":
        await admin_panel.show_user_messages(update, context)
    elif message_text == "💬 Javob Qaytarish":
        await admin_panel.show_reply(update, context)
    elif message_text == "💳 To'lov Cheklari":
        await admin_panel.show_payments(update, context)
    elif message_text == "💰 Pullik Hizmatlar":
        await admin_panel.show_premium(update, context)
    elif message_text == "🔙 Admin menyu":
        await admin_panel.admin_panel(update, context)
    elif message_text == "🔙 Asosiy menyu":
        await admin_exit(update, context)
    else:
        print(f"DEBUG ADMIN: No handler for admin command: '{message_text}'")   

# ==================== YANGI: KONTENT QULFLASH FUNKSIYASI ====================
async def send_paginated_content(update: Update, context: ContextTypes.DEFAULT_TYPE, 
                               category, subject, category_type="hollywood"):
    """Kontentlarni sahifalab ko'rsatish - QULFLASH QO'SHILGAN"""
    try:
        user_id = update.effective_user.id
        
        # Kontent pullikligini tekshirish
        if db.is_premium_content(category, subject):
            # Foydalanuvchi ruxsatini tekshirish
            if not db.check_user_access(user_id, category, subject):
                await update.message.reply_text(
                    f"🔒 *Bu kontent pullik!*\n\n"
                    f"🎬 **{subject}** ko'rish uchun to'lov qilishingiz kerak.\n\n"
                    f"💳 Narx: {db.get_premium_price(category, subject):,} so'm\n\n"
                    f"⬇️ To'lov qilish uchun quyidagi tugmani bosing:",
                    reply_markup=ReplyKeyboardMarkup([
                        ["💳 Pullik Hizmatlar"], 
                        ["🔙 Orqaga"]
                    ], resize_keyboard=True),
                    parse_mode='Markdown'
                )
                return
        
        # Sahifa raqamini olish
        page = context.user_data.get(f'page_{category}_{subject}', 1)
        
        print(f"DEBUG: Kontent ko'rsatish - Category: {category}, Subject: {subject}, Page: {page}")
        
        # Kontentlarni olish
        contents, total_pages, total_count = db.get_content_by_subject_paginated(
            category, subject, page
        )
        
        print(f"DEBUG: Bazadan qaytgan kontentlar: {len(contents)} ta, Jami sahifalar: {total_pages}")
        
        if contents:
            # Faqat bitta kontentni ko'rsatish
            content = contents[0]
            content_id = content[0]  # ID ni olish
            title = content[1]
            description = content[2]
            file_id = content[4]
            file_type = content[5]
            
            caption = f"🎬 {title}\n📝 {description}\n\n📄 Sahifa: {page}/{total_pages} | Jami: {total_count} ta"
            
            # Agar kontent pullik bo'lsa va foydalanuvchi to'lov qilgan bo'lsa
            if db.is_premium_content(category, subject) and db.check_user_access(user_id, category, subject):
                caption += "\n\n✅ **Siz bu kontentga ega bo'ldingiz!**"
            
            # Navigatsiya menyusini yaratish
            reply_markup = get_content_navigation_menu(page, total_pages, subject, category_type)
            
            # Kontentni yuborish
            try:
                if file_type == "video":
                    await update.message.reply_video(video=file_id, caption=caption, reply_markup=reply_markup)
                elif file_type == "photo":
                    await update.message.reply_photo(photo=file_id, caption=caption, reply_markup=reply_markup)
                elif file_type == "audio":
                    await update.message.reply_audio(audio=file_id, caption=caption, reply_markup=reply_markup)
                elif file_type == "document":
                    await update.message.reply_document(document=file_id, caption=caption, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(caption, reply_markup=reply_markup)
                
                print(f"DEBUG: Kontent yuborildi: {title}")
                
            except Exception as e:
                logging.error(f"Kontent yuborishda xatolik: {e}")
                await update.message.reply_text(f"❌ Fayl yuborishda xatolik: {caption}", reply_markup=reply_markup)
            
        else:
            await update.message.reply_text(
                f"❌ Hozircha {subject} mavjud emas.\n\n"
                "⏳ Tez orada qo'shiladi yoki\n"
                "💼 Pullik hizmatlar bo'limidan so'rab olishingiz mumkin.",
                reply_markup=get_categories_menu()
            )
            
    except Exception as e:
        logging.error(f"Kontent ko'rsatishda xatolik: {e}")
        await update.message.reply_text(
            "❌ Kontentlarni yuklashda xatolik yuz berdi. Iltimos qayta urinib ko'ring.",
            reply_markup=get_categories_menu()
        )
        

# ==================== BOT ISHGA TUSHIRISH ====================
async def post_init(application):
    try:
        scheduler = setup_scheduler(application)
        application.bot_data['scheduler'] = scheduler
        logging.info("Scheduler ishga tushdi")
    except Exception as e:
        logging.error(f"Scheduler xatosi: {e}")
    
    if ADMIN_ID:
        try:
            await application.bot.send_message(int(ADMIN_ID), "🤖 Bot ishga tushdi!")
        except Exception as e:
            print(f"Adminga xabar yuborishda xatolik: {e}")
            

# ==================== ASOSIY BOT ISHGA TUSHIRISH ====================
def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN topilmadi!")
        return
    
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # ==================== ADMIN FILTER ====================
    admin_user_id = int(ADMIN_ID) if ADMIN_ID else None
    
    def admin_filter(message):
        """Faqat adminlar uchun filter"""
        if not admin_user_id:
            return False
        return message.from_user.id == admin_user_id

    # ==================== CONVERSATION HANDLER ====================
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [
                MessageHandler(filters.Regex("^(🇺🇿 O'zbek tili|🇷🇺 Русский язык|🇺🇸 English)$"), choose_language),
            ],
            NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)
            ],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)
            ],
        },
        fallbacks=[],
    )

    application.add_handler(conv_handler)
    
    # ==================== DEBUG HANDLERLARI ====================
    application.add_handler(CommandHandler("debug", debug_content))
    application.add_handler(CommandHandler("status", check_database))
    application.add_handler(CommandHandler("check_uzbek", check_uzbek_content))
    
    # ==================== COMMAND HANDLERLARI ====================
    application.add_handler(CommandHandler("admin", admin_panel.admin_panel))
    application.add_handler(CommandHandler("reply", reply_to_user))
    application.add_handler(CommandHandler("confirm", confirm_payment))
    application.add_handler(CommandHandler("start", start))

    # ==================== ADMIN HANDLERLARI (BIRINCHI BO'LIB!) ====================
    # Asosiy admin menyu handlerlari
    application.add_handler(MessageHandler(filters.Regex("^➕ Kontent Qo'shish$") & filters.User(admin_user_id) if admin_user_id else filters.ALL, admin_panel.show_add_content))
    application.add_handler(MessageHandler(filters.Regex("^🗑️ Kontent O'chirish$") & filters.User(admin_user_id) if admin_user_id else filters.ALL, admin_panel.show_delete_content))
    application.add_handler(MessageHandler(filters.Regex("^📊 Kontent Statistikasi$") & filters.User(admin_user_id) if admin_user_id else filters.ALL, admin_panel.show_stats))
    application.add_handler(MessageHandler(filters.Regex("^👥 Foydalanuvchilar$") & filters.User(admin_user_id) if admin_user_id else filters.ALL, admin_panel.show_users))
    application.add_handler(MessageHandler(filters.Regex("^🚫 Bloklash$") & filters.User(admin_user_id) if admin_user_id else filters.ALL, admin_panel.show_block_user))
    application.add_handler(MessageHandler(filters.Regex("^✅ Blokdan Ochish$") & filters.User(admin_user_id) if admin_user_id else filters.ALL, admin_panel.show_unblock_user))
    application.add_handler(MessageHandler(filters.Regex("^📢 Xabar Yuborish$") & filters.User(admin_user_id) if admin_user_id else filters.ALL, admin_panel.show_broadcast))
    application.add_handler(MessageHandler(filters.Regex("^📨 Foydalanuvchi Xabarlari$") & filters.User(admin_user_id) if admin_user_id else filters.ALL, admin_panel.show_user_messages))
    application.add_handler(MessageHandler(filters.Regex("^💬 Javob Qaytarish$") & filters.User(admin_user_id) if admin_user_id else filters.ALL, admin_panel.show_reply))
    application.add_handler(MessageHandler(filters.Regex("^💳 To'lov Cheklari$") & filters.User(admin_user_id) if admin_user_id else filters.ALL, admin_panel.show_payments))
    application.add_handler(MessageHandler(filters.Regex("^💰 Pullik Hizmatlar$") & filters.User(admin_user_id) if admin_user_id else filters.ALL, admin_panel.show_premium))
    application.add_handler(MessageHandler(filters.Regex("^🔙 Admin menyu$") & filters.User(admin_user_id) if admin_user_id else filters.ALL, admin_panel.admin_panel))
    
    # Admin kontent qo'shish kategoriya handlerlari (faqat admin uchun)
    if admin_user_id:
        # Asosiy kategoriyalar
        application.add_handler(MessageHandler(
            filters.Regex("^(🎭 Hollywood Kinolari|🇮🇳 Hind Filmlari|🇷🇺 Rus Kinolari|🇺🇿 O'zbek Kinolari|🕌 Islomiy Kinolar|📺 Turk Seriallari|👶 Bolalar Kinolari|🐰 Bolalar Multfilmlari|🇰🇷 Koreys Kinolari|📺 Koreys Seriallari|🎵 Musiqa)$") & 
            filters.User(admin_user_id), 
            admin_panel.handle_add_category_selection
        ))
        
        # Hollywood subyektlari
        application.add_handler(MessageHandler(
            filters.Regex("^(🎬 Mel Gibson Kinolari|💪 Arnold Schwarzenegger Kinolari|🥊 Sylvester Stallone Kinolari|🚗 Jason Statham Kinolari|🐉 Jeki Chan Kinolari|🥋 Skod Adkins Kinolari|🎭 Denzil Washington Kinolari|💥 Jan Clod Van Dam Kinolari|👊 Brus Li Kinolari|😂 Jim Cerry Kinolari|🎩 Jonni Depp Kinolari|🌟 Boshqa Hollywood Kinolari)$") & 
            filters.User(admin_user_id), 
            admin_panel.handle_add_subject_selection
        ))
        
        # Hind subyektlari
        application.add_handler(MessageHandler(
            filters.Regex("^(🤴 Shakruhkhan Kinolari|🎯 Amirkhan Kinolari|🦸 Akshay Kumar Kinolari|👑 Salmonkhan Kinolari|🌟 SayfAlihon Kinolari|🎭 Amitahbachchan Kinolari|💃 MethunChakraborty Kinolari|👨‍🦳 Dharmendra Kinolari|🎬 Raj Kapur Kinolari|📀 Boshqa Hind Kinolari)$") & 
            filters.User(admin_user_id), 
            admin_panel.handle_add_subject_selection
        ))
        
        # Rus subyektlari
        application.add_handler(MessageHandler(
            filters.Regex("^(💘 Ishdagi Ishq|🎭 Shurikning Sarguzashtlari|🔄 Ivan Vasilivich|🔥 Gugurtga Ketib|🕵️ If Qalqasing Mahbuzi|👶 O'nta Neger Bolasi|⚔️ Qo'lga Tushmas Qasoskorlar|🎬 Barcha Rus Kinolari)$") & 
            filters.User(admin_user_id), 
            admin_panel.handle_add_subject_selection
        ))
        
        # O'zbek subyektlari
        application.add_handler(MessageHandler(
            filters.Regex("^(🏘️ Mahallada Duv-Duv Gap|👰 Kelinlar Qo'zg'aloni|👨 Abdullajon|😊 Suyinchi|🌳 Chinor Ositidagi Duel|🙏 Yaratganga Shukur|💃 Yor-Yor|🎉 To'ylar Muborak|💣 Bomba|😜 Shum Bola|⚡ Temir Xotin|🎬 Barcha UZ Klassik Kinolari)$") & 
            filters.User(admin_user_id), 
            admin_panel.handle_add_subject_selection
        ))

    # ==================== ASOSIY MENYU HANDLERLARI ====================
    application.add_handler(MessageHandler(filters.Regex("^📋 Kategoriyalar$"), show_categories))
    application.add_handler(MessageHandler(filters.Regex("^🎬 Kino qidirish$"), search_movies))
    application.add_handler(MessageHandler(filters.Regex("^👤 Profil$"), show_profile))
    application.add_handler(MessageHandler(filters.Regex("^💼 Pullik Hizmatlar$"), show_premium_services))
    application.add_handler(MessageHandler(filters.Regex("^🌐 Tilni tanlash$"), change_language))
    application.add_handler(MessageHandler(filters.Regex("^(🏠 Asosiy menyu|🔙 Asosiy menyu)$"), universal_main_menu))
     
    # ==================== KATEGORIYA HANDLERLARI (FOYDALANUVCHI UCHUN) ====================
    application.add_handler(MessageHandler(filters.Regex("^🎭 Hollywood Kinolari$"), show_hollywood))
    application.add_handler(MessageHandler(filters.Regex("^🇮🇳 Hind Filmlari$"), show_hindi))
    application.add_handler(MessageHandler(filters.Regex("^🇷🇺 Rus Kinolari$"), show_russian_movies))
    application.add_handler(MessageHandler(filters.Regex("^🇺🇿 O'zbek Kinolari$"), show_uzbek_movies))
    application.add_handler(MessageHandler(filters.Regex("^🕌 Islomiy Kinolar$"), show_islamic_movies))
    application.add_handler(MessageHandler(filters.Regex("^📺 Turk Seriallari$"), show_turkish_series))
    application.add_handler(MessageHandler(filters.Regex("^👶 Bolalar Kinolari$"), show_kids_movies))
    application.add_handler(MessageHandler(filters.Regex("^🐰 Bolalar Multfilmlari$"), show_cartoons))
    application.add_handler(MessageHandler(filters.Regex("^🇰🇷 Koreys Kinolari$"), show_korean_movies))
    application.add_handler(MessageHandler(filters.Regex("^📺 Koreys Seriallari$"), show_korean_series))
    application.add_handler(MessageHandler(filters.Regex("^🎵 Musiqa$"), show_music))
    
    # ==================== FOYDALANUVCHI SUB-MENYU HANDLERLARI ====================
    # Hollywood
    application.add_handler(MessageHandler(filters.Regex("^🎬 Mel Gibson Kinolari$"), show_mel_gibson_movies))
    application.add_handler(MessageHandler(filters.Regex("^💪 Arnold Schwarzenegger Kinolari$"), show_arnold_movies))
    application.add_handler(MessageHandler(filters.Regex("^🥊 Sylvester Stallone Kinolari$"), show_stallone_movies))
    application.add_handler(MessageHandler(filters.Regex("^🚗 Jason Statham Kinolari$"), show_statham_movies))
    application.add_handler(MessageHandler(filters.Regex("^🐉 Jeki Chan Kinolari$"), show_jackie_chan_movies))
    application.add_handler(MessageHandler(filters.Regex("^🥋 Skod Adkins Kinolari$"), show_adkins_movies))
    application.add_handler(MessageHandler(filters.Regex("^🎭 Denzil Washington Kinolari$"), show_denzel_movies))
    application.add_handler(MessageHandler(filters.Regex("^💥 Jan Clod Van Dam Kinolari$"), show_van_damme_movies))
    application.add_handler(MessageHandler(filters.Regex("^👊 Brus Li Kinolari$"), show_bruce_lee_movies))
    application.add_handler(MessageHandler(filters.Regex("^😂 Jim Cerry Kinolari$"), show_jim_carrey_movies))
    application.add_handler(MessageHandler(filters.Regex("^🎩 Jonni Depp Kinolari$"), show_johnny_depp_movies))
    application.add_handler(MessageHandler(filters.Regex("^🌟 Boshqa Hollywood Kinolari$"), show_other_hollywood_movies))

    # Hind
    application.add_handler(MessageHandler(filters.Regex("^🤴 Shakruhkhan Kinolari$"), show_shahrukh_khan_movies))
    application.add_handler(MessageHandler(filters.Regex("^🎯 Amirkhan Kinolari$"), show_amir_khan_movies))
    application.add_handler(MessageHandler(filters.Regex("^🦸 Akshay Kumar Kinolari$"), show_akshay_kumar_movies))
    application.add_handler(MessageHandler(filters.Regex("^👑 Salmonkhan Kinolari$"), show_salman_khan_movies))
    application.add_handler(MessageHandler(filters.Regex("^🌟 SayfAlihon Kinolari$"), show_saif_ali_khan_movies))
    application.add_handler(MessageHandler(filters.Regex("^🎭 Amitahbachchan Kinolari$"), show_amitabh_bachchan_movies))
    application.add_handler(MessageHandler(filters.Regex("^💃 MethunChakraborty Kinolari$"), show_mithun_movies))
    application.add_handler(MessageHandler(filters.Regex("^👨‍🦳 Dharmendra Kinolari$"), show_dharmendra_movies))
    application.add_handler(MessageHandler(filters.Regex("^🎬 Raj Kapur Kinolari$"), show_raj_kapur_movies))
    application.add_handler(MessageHandler(filters.Regex("^📀 Boshqa Hind Kinolari$"), show_other_hindi_movies))

    # Rus
    application.add_handler(MessageHandler(filters.Regex("^💘 Ishdagi Ishq$"), show_love_in_work))
    application.add_handler(MessageHandler(filters.Regex("^🎭 Shurikning Sarguzashtlari$"), show_shurik_adventures))
    application.add_handler(MessageHandler(filters.Regex("^🔄 Ivan Vasilivich$"), show_ivan_vasilivich))
    application.add_handler(MessageHandler(filters.Regex("^🔥 Gugurtga Ketib$"), show_match_going))
    application.add_handler(MessageHandler(filters.Regex("^🕵️ If Qalqasing Mahbuzi$"), show_diamond_arm))
    application.add_handler(MessageHandler(filters.Regex("^👶 O'nta Neger Bolasi$"), show_ten_negro_children))
    application.add_handler(MessageHandler(filters.Regex("^⚔️ Qo'lga Tushmas Qasoskorlar$"), show_elusive_avengers))
    application.add_handler(MessageHandler(filters.Regex("^🎬 Barcha Rus Kinolari$"), show_all_russian_movies))

    # O'zbek
    application.add_handler(MessageHandler(filters.Regex("^🏘️ Mahallada Duv-Duv Gap$"), show_mahalla_duv_duv_gap))
    application.add_handler(MessageHandler(filters.Regex("^👰 Kelinlar Qo'zg'aloni$"), show_kelinlar_qozgaloni))
    application.add_handler(MessageHandler(filters.Regex("^👨 Abdullajon$"), show_abdullajon))
    application.add_handler(MessageHandler(filters.Regex("^😊 Suyinchi$"), show_suyinchi))
    application.add_handler(MessageHandler(filters.Regex("^🌳 Chinor Ositidagi Duel$"), show_chinor_duel))
    application.add_handler(MessageHandler(filters.Regex("^🙏 Yaratganga Shukur$"), show_yaratganga_shukur))
    application.add_handler(MessageHandler(filters.Regex("^💃 Yor-Yor$"), show_yor_yor))
    application.add_handler(MessageHandler(filters.Regex("^🎉 To'ylar Muborak$"), show_tuylar_muborak))
    application.add_handler(MessageHandler(filters.Regex("^💣 Bomba$"), show_bomba))
    application.add_handler(MessageHandler(filters.Regex("^😜 Shum Bola$"), show_shum_bola))
    application.add_handler(MessageHandler(filters.Regex("^⚡ Temir Xotin$"), show_temir_xotin))
    application.add_handler(MessageHandler(filters.Regex("^🎬 Barcha UZ Klassik Kinolari$"), show_all_uzbek_classic))

    # Islomiy
    application.add_handler(MessageHandler(filters.Regex("^📿 Umar Ibn Ali Hattob To'liq$"), show_umar_ibn_hattab))
    application.add_handler(MessageHandler(filters.Regex("^🌙 Olamga Nur Sochgan Oy To'liq$"), show_nur_scattering_moon))
    application.add_handler(MessageHandler(filters.Regex("^🎬 Barcha Islomiy Kinolar$"), show_all_islamic_movies))
    application.add_handler(MessageHandler(filters.Regex("^📺 Barcha Islomiy Seriallar$"), show_all_islamic_series))

    # Turk
    application.add_handler(MessageHandler(filters.Regex("^👑 Sulton Abdulhamidhon$"), show_sultan_abdulhamid))
    application.add_handler(MessageHandler(filters.Regex("^🐺 Qashqirlar Makoni$"), show_wolves_lair))
    application.add_handler(MessageHandler(filters.Regex("^📺 Barcha Turk Seriallari$"), show_all_turkish_series))

    # Bolalar
    application.add_handler(MessageHandler(filters.Regex("^👦 Bola Uyda Yolg'iz 1-3$"), show_home_alone))
    application.add_handler(MessageHandler(filters.Regex("^✈️ Uchuvchi Devid$"), show_flying_david))
    application.add_handler(MessageHandler(filters.Regex("^⚡ Garry Poter 1-4$"), show_harry_potter))
    application.add_handler(MessageHandler(filters.Regex("^🎬 Barcha Bolalar Kinolari$"), show_all_kids_movies))

    # Multfilmlar
    application.add_handler(MessageHandler(filters.Regex("^❄️ Muzlik Davri 1-3$"), show_ice_age))
    application.add_handler(MessageHandler(filters.Regex("^🐭 Tom & Jerry$"), show_tom_jerry))
    application.add_handler(MessageHandler(filters.Regex("^🐻 Bori va Quyon$"), show_winnie_pooh))
    application.add_handler(MessageHandler(filters.Regex("^🍯 Ayiq va Masha$"), show_bear_and_masha))
    application.add_handler(MessageHandler(filters.Regex("^🐼 Kungfu Panda 1-4$"), show_kungfu_panda))
    application.add_handler(MessageHandler(filters.Regex("^🐎 Mustang$"), show_mustang))
    application.add_handler(MessageHandler(filters.Regex("^🎬 Barcha Multfilmlar$"), show_all_cartoons))

    # Koreys
    application.add_handler(MessageHandler(filters.Regex("^🏙️ Jinoyatchilar Shahri 1-4$"), show_criminals_city))
    application.add_handler(MessageHandler(filters.Regex("^🎬 Barcha Koreys Kinolari$"), show_all_korean_movies))
    application.add_handler(MessageHandler(filters.Regex("^❄️ Qish Sonatasi 1-20$"), show_winter_sonata))
    application.add_handler(MessageHandler(filters.Regex("^☀️ Yoz Ifori 1-20$"), show_summer_fever))
    application.add_handler(MessageHandler(filters.Regex("^🏦 Va Bank 1-20$"), show_and_bank))
    application.add_handler(MessageHandler(filters.Regex("^👑 Jumong Barcha Qismlar$"), show_jumong))
    application.add_handler(MessageHandler(filters.Regex("^⚓ Dengiz Hukumdori Barcha Qismlar$"), show_sea_ruler))
    application.add_handler(MessageHandler(filters.Regex("^📺 Barcha Koreys Seriallari$"), show_all_korean_series))
    application.add_handler(MessageHandler(filters.Regex("^💖 Qalbim Chechagi 1-17$"), show_heartbeat))
    
    # Musiqa
    application.add_handler(MessageHandler(filters.Regex("^🎵 O'zbek Musiqalari$"), show_uzbek_music))
    application.add_handler(MessageHandler(filters.Regex("^🎶 Rus Musiqalari$"), show_russian_music))
    application.add_handler(MessageHandler(filters.Regex("^🎼 Hind Musiqalari$"), show_hindi_music))
    application.add_handler(MessageHandler(filters.Regex("^🎧 Turk Musiqalari$"), show_turkish_music))
    application.add_handler(MessageHandler(filters.Regex("^🎤 Koreys Musiqalari$"), show_korean_music))
    application.add_handler(MessageHandler(filters.Regex("^🎹 Barcha Musiqalar$"), show_all_music))

    # ==================== NAVIGATSIYA HANDLERLARI ====================
    application.add_handler(MessageHandler(filters.Regex("^⬅️ Oldingi$"), handle_previous_page))
    application.add_handler(MessageHandler(filters.Regex("^Keyingi ➡️$"), handle_next_page))
    application.add_handler(MessageHandler(filters.Regex("^🏠 Asosiy menyu$"), handle_main_menu_return))

    # Orqaga qaytish handlerlari
    application.add_handler(MessageHandler(filters.Regex("^🔙 Hollywood Kinolari$"), show_hollywood))
    application.add_handler(MessageHandler(filters.Regex("^🔙 Hind Filmlari$"), show_hindi))
    application.add_handler(MessageHandler(filters.Regex("^🔙 Rus Kinolari$"), show_russian_movies))
    application.add_handler(MessageHandler(filters.Regex("^🔙 O'zbek Kinolari$"), show_uzbek_movies))
    application.add_handler(MessageHandler(filters.Regex("^🔙 Islomiy Kinolar$"), show_islamic_movies))
    application.add_handler(MessageHandler(filters.Regex("^🔙 Turk Seriallari$"), show_turkish_series))
    application.add_handler(MessageHandler(filters.Regex("^🔙 Bolalar Kinolari$"), show_kids_movies))
    application.add_handler(MessageHandler(filters.Regex("^🔙 Bolalar Multfilmlari$"), show_cartoons))
    application.add_handler(MessageHandler(filters.Regex("^🔙 Koreys Kinolari$"), show_korean_movies))
    application.add_handler(MessageHandler(filters.Regex("^🔙 Koreys Seriallari$"), show_korean_series))
    application.add_handler(MessageHandler(filters.Regex("^🔙 Musiqa$"), show_music))
    application.add_handler(MessageHandler(filters.Regex("^🔙 Kategoriyalar$"), show_categories))

    # Sahifa raqamlari handleri
    application.add_handler(MessageHandler(
        filters.Regex(r"^(\d+|🔹 \d+)$"), 
        handle_page_selection
    ))
    
    # ==================== PULLIK HIZMATLAR HANDLERLARI ====================
    application.add_handler(MessageHandler(filters.Regex("^💰 Pullik Kinolar$"), show_paid_movies))
    application.add_handler(MessageHandler(filters.Regex("^📞 Adminga Xabar$"), contact_admin))
    application.add_handler(MessageHandler(filters.Regex("^👀 Javobni Ko'rish$"), check_admin_response))
    application.add_handler(MessageHandler(filters.Regex("^🔙 Orqaga$"), show_premium_services))
    application.add_handler(MessageHandler(filters.Regex("^ℹ️ Qo'llanma$"), show_payment_instructions))
    application.add_handler(MessageHandler(filters.Regex("^📝 Kontent so'rovi yuborish$"), contact_admin))
    application.add_handler(MessageHandler(filters.Regex("^💳 To'lov chekini yuborish$"), contact_admin))
    
    # ==================== YANGI: PULLIK KONTENT HANDLERLARI ====================
    application.add_handler(MessageHandler(filters.Regex("^🎬 Kino Sotib olish$"), show_paid_movies_purchase))
    application.add_handler(MessageHandler(filters.Regex("^📺 Serial Sotib olish$"), show_paid_series_purchase))
    application.add_handler(MessageHandler(filters.Regex("^🐰 Multfilm Sotib olish$"), show_paid_cartoons_purchase))
    
    # Pullik kontent tanlash handlerlari
    application.add_handler(MessageHandler(filters.Regex("^💰 .+$"), handle_paid_content_selection))
    
    # To'lov tasdiqlash handlerlari
    application.add_handler(MessageHandler(filters.Regex("^💳 To'lov qilish$"), handle_payment_confirmation))
    application.add_handler(MessageHandler(filters.Regex("^📸 Chek yuborish$"), handle_payment_confirmation))
    
    # To'lov cheki handleri
    application.add_handler(MessageHandler(
        filters.PHOTO | (filters.TEXT & ~filters.COMMAND), 
        handle_payment_receipt
    ))
    
    # ==================== QIDIRUV HANDLERI ====================
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_search))

    # ==================== ADMIN XABAR HANDLERI ====================
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.User(admin_user_id) if admin_user_id else filters.ALL, 
        handle_admin_messages
    ))

    # ==================== ADMIN FILE HANDLERLARI ====================
    application.add_handler(MessageHandler(
        (filters.VIDEO | filters.AUDIO | filters.PHOTO | filters.Document.ALL) & 
        filters.User(admin_user_id) if admin_user_id else filters.Document.ALL, 
        handle_admin_files
    ))

    # ==================== TO'LOV CHEKI HANDLERI ====================
    application.add_handler(MessageHandler(
        filters.PHOTO | (filters.TEXT & ~filters.COMMAND), 
        handle_payment_receipt
    ))
    
    # ==================== TIL HANDLERLARI ====================
    application.add_handler(MessageHandler(filters.Regex("^🌐 Tilni tanlash$"), change_language))
    application.add_handler(MessageHandler(filters.Regex("^🌐 Сменить язык$"), change_language))
    application.add_handler(MessageHandler(filters.Regex("^🌐 Change language$"), change_language))

    print("🚀 Bot ishga tushmoqda...")
    application.run_polling()

if __name__ == '__main__':
    main()