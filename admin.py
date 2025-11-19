# ==================== IMPORT QISM ====================
import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler
from database import Database

db = Database()

# ==================== ADMIN PANEL CLASS ====================
class AdminPanel:
    def __init__(self):
        self.admin_id = None
        self.load_admin_id()
    
    # ==================== ADMIN ID YUKLASH ====================
    def load_admin_id(self):
        admin_id = os.getenv('ADMIN_ID')
        if admin_id:
            try:
                self.admin_id = int(admin_id)
                logging.info(f"Admin ID loaded: {self.admin_id}")
            except (ValueError, TypeError):
                logging.error("Invalid ADMIN_ID in environment variables")
                self.admin_id = None
        else:
            logging.warning("ADMIN_ID not found in environment variables")
    
    # ==================== ADMIN TEKSHIRISH ====================
    async def check_admin(self, user_id):
        if not self.admin_id:
            return False
        return user_id == self.admin_id
    
    # ==================== ASOSIY ADMIN MENYU ====================
    def get_admin_main_menu(self):
        keyboard = [
            ["➕ Kontent Qo'shish", "🗑️ Kontent O'chirish"],
            ["📊 Kontent Statistikasi", "👥 Foydalanuvchilar"],
            ["🚫 Bloklash", "✅ Blokdan Ochish"],
            ["📢 Xabar Yuborish", "📨 Foydalanuvchi Xabarlari"],
            ["💬 Javob Qaytarish", "💳 To'lov Cheklari"],
            ["💰 Pullik Hizmatlar", "🔙 Asosiy menyu"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # ==================== KONTENT QO'SHISH MENYUSI ====================
    def get_add_content_menu(self):
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
            ["📺 Koreys Seriallari"],
            ["🎵 Musiqa"],
            ["🔙 Admin menyu"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # ==================== HOLLYWOOD SUB-MENYU ====================
    def get_hollywood_subjects_menu(self):
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
            ["🔙 Kategoriyalar", "🔙 Admin menyu"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # ==================== HIND SUB-MENYU ====================
    def get_hindi_subjects_menu(self):
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
            ["🔙 Kategoriyalar", "🔙 Admin menyu"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # ==================== RUS SUB-MENYU ====================
    def get_russian_subjects_menu(self):
        keyboard = [
            ["💘 Ishdagi Ishq"],
            ["🎭 Shurikning Sarguzashtlari"],
            ["🔄 Ivan Vasilivich"],
            ["🔥 Gugurtga Ketib"],
            ["🕵️ If Qalqasing Mahbuzi"],
            ["👶 O'nta Neger Bolasi"],
            ["⚔️ Qo'lga Tushmas Qasoskorlar"],
            ["🎬 Barcha Rus Kinolari"],
            ["🔙 Kategoriyalar", "🔙 Admin menyu"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # ==================== O'ZBEK SUB-MENYU ====================
    def get_uzbek_subjects_menu(self):
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
            ["🔙 Kategoriyalar", "🔙 Admin menyu"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # ==================== ISLOMIY SUB-MENYU ====================
    def get_islamic_subjects_menu(self):
        keyboard = [
            ["📿 Umar Ibn Ali Hattob To'liq"],
            ["🌙 Olamga Nur Sochgan Oy To'liq"],
            ["🎬 Barcha Islomiy Kinolar"],
            ["📺 Barcha Islomiy Seriallar"],
            ["🔙 Kategoriyalar", "🔙 Admin menyu"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # ==================== TURK SUB-MENYU ====================
    def get_turkish_subjects_menu(self):
        keyboard = [
            ["👑 Sulton Abdulhamidhon"],
            ["🐺 Qashqirlar Makoni"],
            ["📺 Barcha Turk Seriallari"],
            ["🔙 Kategoriyalar", "🔙 Admin menyu"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # ==================== BOLALAR SUB-MENYU ====================
    def get_kids_subjects_menu(self):
        keyboard = [
            ["👦 Bola Uyda Yolg'iz 1-3"],
            ["✈️ Uchuvchi Devid"],
            ["⚡ Garry Poter 1-4"],
            ["🎬 Barcha Bolalar Kinolari"],
            ["🔙 Kategoriyalar", "🔙 Admin menyu"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # ==================== MULTFILMLAR SUB-MENYU ====================
    def get_cartoons_subjects_menu(self):
        keyboard = [
            ["❄️ Muzlik Davri 1-3"],
            ["🐭 Tom & Jerry"],
            ["🐻 Bori va Quyon"],
            ["🍯 Ayiq va Masha"],
            ["🐼 Kungfu Panda 1-4"],
            ["🐎 Mustang"],
            ["🎬 Barcha Multfilmlar"],
            ["🔙 Kategoriyalar", "🔙 Admin menyu"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # ==================== KOREYS KINOLARI SUB-MENYU ====================
    def get_korean_movies_subjects_menu(self):
        keyboard = [
            ["🏙️ Jinoyatchilar Shahri 1-4"],
            ["🎬 Barcha Koreys Kinolari"],
            ["🔙 Kategoriyalar", "🔙 Admin menyu"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # ==================== KOREYS SERIALLARI SUB-MENYU ====================
    def get_korean_series_subjects_menu(self):
        """Koreys Seriallari sub-menyusi - YANGILANGAN"""
        keyboard = [
            ["❄️ Qish Sonatasi 1-20"],
            ["☀️ Yoz Ifori 1-20"],
            ["🏦 Va Bank 1-20"],
            ["👑 Jumong Barcha Qismlar"],
            ["⚓ Dengiz Hukumdori Barcha Qismlar"],
            ["💖 Qalbim Chechagi 1-17"],  # YANGI QO'SHILDI
            ["📺 Barcha Koreys Seriallari"],
            ["🔙 Kategoriyalar", "🔙 Admin menyu"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # ==================== MUSIQA SUB-MENYU ====================
    def get_music_subjects_menu(self):
        keyboard = [
            ["🎵 O'zbek Musiqalari"],
            ["🎶 Rus Musiqalari"],
            ["🎼 Hind Musiqalari"],
            ["🎧 Turk Musiqalari"],
            ["🎤 Koreys Musiqalari"],
            ["🎹 Barcha Musiqalar"],
            ["🔙 Kategoriyalar", "🔙 Admin menyu"]
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    # ==================== ASOSIY ADMIN PANEL ====================
    async def admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if not await self.check_admin(user_id):
            await update.message.reply_text("❌ Siz admin emassiz!")
            return
        
        await update.message.reply_text(
            "👨‍💻 *Admin Panel*\n\n"
            "Quyidagi bo'limlardan birini tanlang:",
            reply_markup=self.get_admin_main_menu(),
            parse_mode='Markdown'
        )
    
    # ==================== KONTENT QO'SHISH BO'LIMI ====================
    async def show_add_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data['adding_content'] = True
        await update.message.reply_text(
            "➕ *Kontent Qo'shish*\n\n"
            "Qaysi kategoriyaga kontent qo'shmoqchisiz?",
            reply_markup=self.get_add_content_menu(),
            parse_mode='Markdown'
        )
    
    # ==================== KATEGORIYA TANLASH (QO'SHISH) ====================
    async def handle_add_category_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        category_map = {
            "🎭 Hollywood Kinolari": "hollywood",
            "🇮🇳 Hind Filmlari": "hindi", 
            "🇷🇺 Rus Kinolari": "russian",
            "🇺🇿 O'zbek Kinolari": "uzbek",
            "🕌 Islomiy Kinolar": "islamic",
            "📺 Turk Seriallari": "turkish",
            "👶 Bolalar Kinolari": "kids",
            "🐰 Bolalar Multfilmlari": "cartoons",
            "🇰🇷 Koreys Kinolari": "korean_movies",
            "📺 Koreys Seriallari": "korean_series",
            "🎵 Musiqa": "music"
        }
        
        selected_category = update.message.text
        category_key = category_map.get(selected_category)
        
        if category_key:
            context.user_data['add_category'] = category_key
            
            # Subyekt menyusini ko'rsatish
            if category_key == "hollywood":
                await update.message.reply_text(
                    "🎭 *Hollywood Kinolari*\n\n"
                    "Qaysi aktyor/aktyorlar uchun kontent qo'shmoqchisiz?",
                    reply_markup=self.get_hollywood_subjects_menu(),
                    parse_mode='Markdown'
                )
            elif category_key == "hindi":
                await update.message.reply_text(
                    "🇮🇳 *Hind Filmlari*\n\n"
                    "Qaysi aktyor/aktyorlar uchun kontent qo'shmoqchisiz?",
                    reply_markup=self.get_hindi_subjects_menu(),
                    parse_mode='Markdown'
                )
            elif category_key == "russian":
                await update.message.reply_text(
                    "🇷🇺 *Rus Kinolari*\n\n"
                    "Qaysi film uchun kontent qo'shmoqchisiz?",
                    reply_markup=self.get_russian_subjects_menu(),
                    parse_mode='Markdown'
                )
            elif category_key == "uzbek":
                await update.message.reply_text(
                    "🇺🇿 *O'zbek Kinolari*\n\n"
                    "Qaysi film uchun kontent qo'shmoqchisiz?",
                    reply_markup=self.get_uzbek_subjects_menu(),
                    parse_mode='Markdown'
                )
            elif category_key == "islamic":
                await update.message.reply_text(
                    "🕌 *Islomiy Kinolar*\n\n"
                    "Qaysi film/serial uchun kontent qo'shmoqchisiz?",
                    reply_markup=self.get_islamic_subjects_menu(),
                    parse_mode='Markdown'
                )
            elif category_key == "turkish":
                await update.message.reply_text(
                    "📺 *Turk Seriallari*\n\n"
                    "Qaysi serial uchun kontent qo'shmoqchisiz?",
                    reply_markup=self.get_turkish_subjects_menu(),
                    parse_mode='Markdown'
                )
            elif category_key == "kids":
                await update.message.reply_text(
                    "👶 *Bolalar Kinolari*\n\n"
                    "Qaysi film uchun kontent qo'shmoqchisiz?",
                    reply_markup=self.get_kids_subjects_menu(),
                    parse_mode='Markdown'
                )
            elif category_key == "cartoons":
                await update.message.reply_text(
                    "🐰 *Bolalar Multfilmlari*\n\n"
                    "Qaysi multfilm uchun kontent qo'shmoqchisiz?",
                    reply_markup=self.get_cartoons_subjects_menu(),
                    parse_mode='Markdown'
                )
            elif category_key == "korean_movies":
                await update.message.reply_text(
                    "🇰🇷 *Koreys Kinolari*\n\n"
                    "Qaysi film uchun kontent qo'shmoqchisiz?",
                    reply_markup=self.get_korean_movies_subjects_menu(),
                    parse_mode='Markdown'
                )
            elif category_key == "korean_series":
                await update.message.reply_text(
                    "📺 *Koreys Seriallari*\n\n"
                    "Qaysi serial uchun kontent qo'shmoqchisiz?",
                    reply_markup=self.get_korean_series_subjects_menu(),
                    parse_mode='Markdown'
                )
            elif category_key == "music":
                await update.message.reply_text(
                    "🎵 *Musiqa*\n\n"
                    "Qaysi musiqalar uchun kontent qo'shmoqchisiz?",
                    reply_markup=self.get_music_subjects_menu(),
                    parse_mode='Markdown'
                )
            
            context.user_data['waiting_for_subject'] = True
    
    # ==================== SUBYEKT TANLASH (QO'SHISH) ====================
    async def handle_add_subject_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        selected_subject = update.message.text
        category = context.user_data.get('add_category')
        
        if category and selected_subject not in ["🔙 Kategoriyalar", "🔙 Admin menyu"]:
            context.user_data['add_subject'] = selected_subject
            context.user_data['waiting_for_subject'] = False
            context.user_data['waiting_for_content_title'] = True
            
            await update.message.reply_text(
                f"📝 *Kontent Qo'shish*: {selected_subject}\n\n"
                "Kontentning to'liq nomini kiriting:",
                reply_markup=ReplyKeyboardMarkup([["🔙 Kategoriyalar"]], resize_keyboard=True),
                parse_mode='Markdown'
            )
    
    # ==================== KONTENT MA'LUMOTLARINI QABUL QILISH ====================
    async def handle_content_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        
        if context.user_data.get('waiting_for_content_title'):
            # Title qabul qilish
            context.user_data['content_title'] = update.message.text
            context.user_data['waiting_for_content_title'] = False
            context.user_data['waiting_for_content_description'] = True
            
            await update.message.reply_text(
                "📝 Kontentning tavsifini kiriting:",
                reply_markup=ReplyKeyboardMarkup([["🔙 Kategoriyalar"]], resize_keyboard=True)
            )
            
        elif context.user_data.get('waiting_for_content_description'):
            # Description qabul qilish
            context.user_data['content_description'] = update.message.text
            context.user_data['waiting_for_content_description'] = False
            context.user_data['waiting_for_content_file'] = True
            
            await update.message.reply_text(
                "📁 Kontent faylini yuboring (video, audio, rasm):",
                reply_markup=ReplyKeyboardMarkup([["🔙 Kategoriyalar"]], resize_keyboard=True)
            )
    
    # ==================== KONTENT O'CHIRISH BO'LIMI ====================
    async def show_delete_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🗑️ *Kontent O'chirish*\n\n"
            "Bu funksiya hozircha ishlamaydi. Tez orada qo'shiladi.",
            reply_markup=self.get_admin_main_menu(),
            parse_mode='Markdown'
        )
    
    # ==================== KONTENT STATISTIKASI BO'LIMI ====================
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        total_users = len(db.get_all_users())
        total_content = len(db.get_all_content())
        
        stats_text = (
            "📊 *Kontent Statistikasi*\n\n"
            f"👥 Jami foydalanuvchilar: {total_users}\n"
            f"🎬 Jami kontentlar: {total_content}\n"
            f"💰 Pullik so'rovlar: 0\n\n"
            "📈 *Oxirgi 7 kun:*\n"
            "• Yangi foydalanuvchilar: 0\n"
            "• Aktiv foydalanuvchilar: 0\n"
            "• Pullik buyurtmalar: 0"
        )
        
        await update.message.reply_text(
            stats_text,
            reply_markup=self.get_admin_main_menu(),
            parse_mode='Markdown'
        )
    
    # ==================== FOYDALANUVCHILAR BO'LIMI ====================
    async def show_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        users = db.get_all_users()
        users_text = "👥 *Foydalanuvchilar Ro'yxati*\n\n"
        
        for i, user_id in enumerate(users[:10], 1):
            user_data = db.get_user(user_id)
            if user_data:
                users_text += f"{i}. ID: {user_data[0]}\n   Ism: {user_data[2]}\n   Tel: {user_data[3]}\n\n"
        
        if len(users) > 10:
            users_text += f"... va yana {len(users) - 10} ta foydalanuvchi"
        
        await update.message.reply_text(
            users_text,
            reply_markup=self.get_admin_main_menu(),
            parse_mode='Markdown'
        )
    
    # ==================== XABAR YUBORISH BO'LIMI ====================
    async def show_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📢 *Barcha Foydalanuvchilarga Xabar Yuborish*\n\n"
            "Yubormoqchi bo'lgan xabaringizni kiriting:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Admin menyu"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        context.user_data['waiting_for_broadcast'] = True
    
    # ==================== JAVOB QAYTARISH BO'LIMI ====================
    async def show_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "💬 *Foydalanuvchiga Javob Qaytarish*\n\n"
            "Javob yubormoqchi bo'lgan foydalanuvchi ID sini kiriting:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Admin menyu"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        context.user_data['waiting_for_reply_id'] = True
    
    # ==================== BLOKLASH BO'LIMI ====================
    async def show_block_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🚫 *Foydalanuvchini Bloklash*\n\n"
            "Bloklamoqchi bo'lgan foydalanuvchi ID sini yuboring:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Admin menyu"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        context.user_data['waiting_for_block_id'] = True

    # ==================== BLOKDAN OCHISH BO'LIMI ====================
    async def show_unblock_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "✅ *Foydalanuvchini Blokdan Ochish*\n\n"
            "Blokdan ochmoqchi bo'lgan foydalanuvchi ID sini yuboring:",
            reply_markup=ReplyKeyboardMarkup([["🔙 Admin menyu"]], resize_keyboard=True),
            parse_mode='Markdown'
        )
        context.user_data['waiting_for_unblock_id'] = True

    # ==================== FOYDALANUVCHI XABARLARI BO'LIMI ====================
    async def show_user_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "📨 *Foydalanuvchi Xabarlari*\n\n"
            "Hozircha yangi xabarlar mavjud emas.\n"
            "Foydalanuvchilar xabar yuborganida shu yerda ko'rasiz.",
            reply_markup=self.get_admin_main_menu(),
            parse_mode='Markdown'
        )

    # ==================== TO'LOV CHEKLARI BO'LIMI ====================
    async def show_payments(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "💳 *To'lov Cheklari*\n\n"
            "Hozircha yangi to'lov cheklari mavjud emas.\n"
            "Foydalanuvchilar to'lov qilganda shu yerda ko'rasiz.",
            reply_markup=self.get_admin_main_menu(),
            parse_mode='Markdown'
        )

    # ==================== PULLIK HIZMATLAR BO'LIMI ====================
    async def show_premium(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "💰 *Pullik Hizmatlar So'rovlari*\n\n"
            "Hozircha yangi pullik so'rovlar mavjud emas.\n"
            "Foydalanuvchilar pullik so'rov yuborganida shu yerda ko'rasiz.",
            reply_markup=self.get_admin_main_menu(),
            parse_mode='Markdown'
        )
    
    # ==================== YORDAMCHI FUNKSIYALAR ====================
    def _clear_content_data(self, context):
        """Kontent qo'shish ma'lumotlarini tozalash"""
        keys_to_remove = [
            'add_category', 'add_subject', 'content_title', 
            'content_description', 'waiting_for_subject',
            'waiting_for_content_title', 'waiting_for_content_description',
            'waiting_for_content_file', 'adding_content'
        ]
        
        for key in keys_to_remove:
            if key in context.user_data:
                del context.user_data[key]

# ==================== ADMIN XABARLARINI QAYTA ISHLASH ====================
async def handle_admin_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    if not await admin_panel.check_admin(user_id):
        return
    
    message_text = update.message.text
    
    # Admin menyusi tugmalarini tekshirish
    if message_text == "➕ Kontent Qo'shish":
        await admin_panel.show_add_content(update, context)
        return
        
    elif message_text == "🗑️ Kontent O'chirish":
        await admin_panel.show_delete_content(update, context)
        return
        
    elif message_text == "📊 Kontent Statistikasi":
        await admin_panel.show_stats(update, context)
        return
        
    elif message_text == "👥 Foydalanuvchilar":
        await admin_panel.show_users(update, context)
        return
        
    elif message_text == "🚫 Bloklash":
        await admin_panel.show_block_user(update, context)
        return
        
    elif message_text == "✅ Blokdan Ochish":
        await admin_panel.show_unblock_user(update, context)
        return
        
    elif message_text == "📢 Xabar Yuborish":
        await admin_panel.show_broadcast(update, context)
        return
        
    elif message_text == "📨 Foydalanuvchi Xabarlari":
        await admin_panel.show_user_messages(update, context)
        return
        
    elif message_text == "💬 Javob Qaytarish":
        await admin_panel.show_reply(update, context)
        return
        
    elif message_text == "💳 To'lov Cheklari":
        await admin_panel.show_payments(update, context)
        return
        
    elif message_text == "💰 Pullik Hizmatlar":
        await admin_panel.show_premium(update, context)
        return
        
    elif message_text == "🔙 Admin menyu":
        await admin_panel.admin_panel(update, context)
        admin_panel._clear_content_data(context)
        return

    elif message_text == "🔙 Asosiy menyu":
        from main import get_main_menu
        await update.message.reply_text(
            "🏠 Asosiy menyuga qaytingiz:",
            reply_markup=get_main_menu()
        )
        admin_panel._clear_content_data(context)
        return

    # ==================== KONTENT QO'SHISH KATEGORIYA TANLASH ====================
    if context.user_data.get('adding_content'):
        if message_text in ["🔙 Kategoriyalar"]:
            await admin_panel.show_add_content(update, context)
            admin_panel._clear_content_data(context)
            return
        
        if message_text in ["🎭 Hollywood Kinolari", "🇮🇳 Hind Filmlari", "🇷🇺 Rus Kinolari", 
                          "🇺🇿 O'zbek Kinolari", "🕌 Islomiy Kinolar", "📺 Turk Seriallari",
                          "👶 Bolalar Kinolari", "🐰 Bolalar Multfilmlari", "🇰🇷 Koreys Kinolari",
                          "📺 Koreys Seriallari", "🎵 Musiqa"]:
            await admin_panel.handle_add_category_selection(update, context)
            return

    # ==================== KONTENT QO'SHISH SUBYEKT TANLASH ====================
    if context.user_data.get('waiting_for_subject'):
        if message_text in ["🔙 Kategoriyalar", "🔙 Admin menyu"]:
            await admin_panel.show_add_content(update, context)
            admin_panel._clear_content_data(context)
            return
        
        # Hollywood subyektlarini tekshirish
        if message_text in ["🎬 Mel Gibson Kinolari", "💪 Arnold Schwarzenegger Kinolari", 
                          "🥊 Sylvester Stallone Kinolari", "🚗 Jason Statham Kinolari",
                          "🐉 Jeki Chan Kinolari", "🥋 Skod Adkins Kinolari",
                          "🎭 Denzil Washington Kinolari", "💥 Jan Clod Van Dam Kinolari",
                          "👊 Brus Li Kinolari", "😂 Jim Cerry Kinolari",
                          "🎩 Jonni Depp Kinolari", "🌟 Boshqa Hollywood Kinolari"]:
            await admin_panel.handle_add_subject_selection(update, context)
            return
            
        # Hind subyektlarini tekshirish
        if message_text in ["🤴 Shakruhkhan Kinolari", "🎯 Amirkhan Kinolari", 
                          "🦸 Akshay Kumar Kinolari", "👑 Salmonkhan Kinolari",
                          "🌟 SayfAlihon Kinolari", "🎭 Amitahbachchan Kinolari",
                          "💃 MethunChakraborty Kinolari", "👨‍🦳 Dharmendra Kinolari",
                          "🎬 Raj Kapur Kinolari", "📀 Boshqa Hind Kinolari"]:
            await admin_panel.handle_add_subject_selection(update, context)
            return
            
        # Rus subyektlarini tekshirish
        if message_text in ["💘 Ishdagi Ishq", "🎭 Shurikning Sarguzashtlari", 
                          "🔄 Ivan Vasilivich", "🔥 Gugurtga Ketib",
                          "🕵️ If Qalqasing Mahbuzi", "👶 O'nta Neger Bolasi",
                          "⚔️ Qo'lga Tushmas Qasoskorlar", "🎬 Barcha Rus Kinolari"]:
            await admin_panel.handle_add_subject_selection(update, context)
            return
            
        # O'zbek subyektlarini tekshirish
        if message_text in ["🏘️ Mahallada Duv-Duv Gap", "👰 Kelinlar Qo'zg'aloni", 
                          "👨 Abdullajon", "😊 Suyinchi",
                          "🌳 Chinor Ositidagi Duel", "🙏 Yaratganga Shukur",
                          "💃 Yor-Yor", "🎉 To'ylar Muborak",
                          "💣 Bomba", "😜 Shum Bola",
                          "⚡ Temir Xotin", "🎬 Barcha UZ Klassik Kinolari"]:
            await admin_panel.handle_add_subject_selection(update, context)
            return
            
        # Boshqa kategoriyalar subyektlarini ham shu tarzda qo'shing...

    # ==================== KONTENT MA'LUMOTLARI ====================
    if (context.user_data.get('waiting_for_content_title') or 
        context.user_data.get('waiting_for_content_description')):
        
        if message_text == "🔙 Kategoriyalar":
            await admin_panel.show_add_content(update, context)
            admin_panel._clear_content_data(context)
            return
        
        await admin_panel.handle_content_details(update, context)
        return

    # ==================== BROADCAST XABARINI QAYTA ISHLASH ====================
    if context.user_data.get('waiting_for_broadcast'):
        if message_text == "🔙 Admin menyu":
            await admin_panel.admin_panel(update, context)
            context.user_data['waiting_for_broadcast'] = False
            return
            
        broadcast_message = message_text
        users = db.get_all_users()
        
        success_count = 0
        fail_count = 0
        
        for user_id in users:
            try:
                await context.bot.send_message(chat_id=user_id, text=broadcast_message)
                success_count += 1
            except Exception as e:
                logging.error(f"Foydalanuvchi {user_id} ga xabar yuborishda xatolik: {e}")
                fail_count += 1
        
        await update.message.reply_text(
            f"📊 Xabar yuborish natijasi:\n"
            f"✅ Muvaffaqiyatli: {success_count}\n"
            f"❌ Xatolik: {fail_count}\n"
            f"👥 Jami: {len(users)}",
            reply_markup=admin_panel.get_admin_main_menu()
        )
        context.user_data['waiting_for_broadcast'] = False
        return
    
    # ==================== JAVOB QAYTARISH XABARINI QAYTA ISHLASH ====================
    if context.user_data.get('waiting_for_reply_id'):
        if message_text == "🔙 Admin menyu":
            await admin_panel.admin_panel(update, context)
            context.user_data['waiting_for_reply_id'] = False
            return
            
        try:
            reply_id = int(message_text)
            context.user_data['reply_user_id'] = reply_id
            context.user_data['waiting_for_reply_id'] = False
            context.user_data['waiting_for_reply_message'] = True
            
            await update.message.reply_text(
                f"💬 Foydalanuvchi {reply_id} ga javob yozing:",
                reply_markup=ReplyKeyboardMarkup([["🔙 Admin menyu"]], resize_keyboard=True)
            )
        except ValueError:
            await update.message.reply_text("❌ Noto'g'ri ID format! Faqat raqam kiriting.")
        return
    
    # ==================== JAVOB XABARINI QAYTA ISHLASH ====================
    if context.user_data.get('waiting_for_reply_message'):
        if message_text == "🔙 Admin menyu":
            await admin_panel.admin_panel(update, context)
            context.user_data['waiting_for_reply_message'] = False
            context.user_data['reply_user_id'] = None
            return
            
        reply_message = message_text
        target_user_id = context.user_data.get('reply_user_id')
        
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"👨‍💼 Admin javobi:\n\n{reply_message}"
            )
            await update.message.reply_text(
                f"✅ Javob {target_user_id} foydalanuvchiga yuborildi!",
                reply_markup=admin_panel.get_admin_main_menu()
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {e}")
        
        context.user_data['waiting_for_reply_message'] = False
        context.user_data['reply_user_id'] = None
        return
    
    # ==================== BLOKLASH XABARINI QAYTA ISHLASH ====================
    if context.user_data.get('waiting_for_block_id'):
        if message_text == "🔙 Admin menyu":
            await admin_panel.admin_panel(update, context)
            context.user_data['waiting_for_block_id'] = False
            return
            
        try:
            block_id = int(message_text)
            # Bu yerda bloklash logikasi qo'shish kerak
            await update.message.reply_text(
                f"✅ Foydalanuvchi {block_id} bloklandi!",
                reply_markup=admin_panel.get_admin_main_menu()
            )
        except ValueError:
            await update.message.reply_text("❌ Noto'g'ri ID format! Faqat raqam kiriting.")
        context.user_data['waiting_for_block_id'] = False
        return
    
    # ==================== BLOKDAN OCHISH XABARINI QAYTA ISHLASH ====================
    if context.user_data.get('waiting_for_unblock_id'):
        if message_text == "🔙 Admin menyu":
            await admin_panel.admin_panel(update, context)
            context.user_data['waiting_for_unblock_id'] = False
            return
            
        try:
            unblock_id = int(message_text)
            # Bu yerda blokdan ochish logikasi qo'shish kerak
            await update.message.reply_text(
                f"✅ Foydalanuvchi {unblock_id} blokdan olindi!",
                reply_markup=admin_panel.get_admin_main_menu()
            )
        except ValueError:
            await update.message.reply_text("❌ Noto'g'ri ID format! Faqat raqam kiriting.")
        context.user_data['waiting_for_unblock_id'] = False
        return

    # Agar hech qanday shart bajarilmasa, debug ma'lumotini chiqarish
    print(f"DEBUG ADMIN: No handler for: '{message_text}'")
    print(f"DEBUG ADMIN: User data: {context.user_data}")

# ==================== KONTENTLARNI TEKSHIRISH COMMAND ====================
async def check_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kontentlarni tekshirish"""
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    if not await admin_panel.check_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    if context.args:
        category = context.args[0]
        subject = context.args[1] if len(context.args) > 1 else None
        
        if subject:
            contents = db.get_content_by_subject(category, subject)
        else:
            contents = db.get_content_by_category(category)
        
        if contents:
            content_info = f"📊 Kontentlar ({len(contents)} ta):\n\n"
            for content in contents[:5]:  # Faqat birinchi 5 tasini ko'rsatish
                content_info += f"🎬 {content[1]}\n📁 {content[3]}\n📄 {content[5]}\n\n"
            
            await update.message.reply_text(content_info)
        else:
            await update.message.reply_text("❌ Hech qanday kontent topilmadi")
    else:
        await update.message.reply_text("❌ Format: /check category [subject]")

# ==================== YANGILANGAN ADMIN FILE HANDLER ====================
async def handle_admin_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    if not await admin_panel.check_admin(user_id):
        return
    
    # Agar admin kontent qo'shish jarayonida bo'lsa
    if context.user_data.get('waiting_for_content_file'):
        try:
            if update.message.video:
                file_id = update.message.video.file_id
                file_type = "video"
            elif update.message.audio:
                file_id = update.message.audio.file_id
                file_type = "audio"
            elif update.message.photo:
                file_id = update.message.photo[-1].file_id
                file_type = "photo"
            elif update.message.document:
                file_id = update.message.document.file_id
                file_type = "document"
            else:
                await update.message.reply_text("❌ Iltimos, video, audio yoki rasm fayl yuboring!")
                return
            
            # Ma'lumotlarni olish
            category = context.user_data.get('add_category')
            subject = context.user_data.get('add_subject')
            title = context.user_data.get('content_title')
            description = context.user_data.get('content_description')
            
            if not all([category, subject, title, description]):
                await update.message.reply_text("❌ Ma'lumotlar to'liq emas!")
                return
            
            # Kategoriya va subyektni birlashtirish
            full_category = f"{category}_{subject}"
            
            # Bazaga qo'shish
            success = db.add_content(title, description, full_category, file_id, file_type, user_id)
            
            if success:
                await update.message.reply_text(
                    f"✅ Kontent muvaffaqiyatli qo'shildi!\n\n"
                    f"📁 Kategoriya: {category}\n"
                    f"🎬 Subyekt: {subject}\n"
                    f"📝 Nomi: {title}\n"
                    f"📄 Fayl turi: {file_type}\n\n"
                    f"👤 Foydalanuvchilar endi bu kontentni ko'rishi mumkin!",
                    reply_markup=admin_panel.get_admin_main_menu()
                )
                
                # Kontent qo'shilganligi haqida log
                logging.info(f"Yangi kontent qo'shildi: {title} | {full_category}")
                
            else:
                await update.message.reply_text(
                    "❌ Kontent qo'shishda xatolik!",
                    reply_markup=admin_panel.get_admin_main_menu()
                )
            
            # User data ni tozalash
            admin_panel._clear_content_data(context)
            
        except Exception as e:
            logging.error(f"Fayl qo'shishda xatolik: {e}")
            await update.message.reply_text(
                f"❌ Xatolik yuz berdi: {str(e)}",
                reply_markup=admin_panel.get_admin_main_menu()
            )
            
# ==================== FOYDALANUVCHIGA JAVOB QAYTARISH COMMAND ====================
async def reply_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    if not await admin_panel.check_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    if len(context.args) >= 2:
        target_user_id = context.args[0]
        message_text = ' '.join(context.args[1:])
        
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"👨‍💼 Admin javobi:\n\n{message_text}"
            )
            await update.message.reply_text(f"✅ Javob {target_user_id} foydalanuvchiga yuborildi!")
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {e}")
    else:
        await update.message.reply_text("❌ Format: /reply user_id xabar_matni")

# ==================== TO'LOVNI TASDIQLASH COMMAND ====================
async def confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    if not await admin_panel.check_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    if context.args:
        target_user_id = context.args[0]
        
        try:
            await context.bot.send_message(
                chat_id=target_user_id,
                text="✅ To'lovingiz tasdiqlandi! Kontent tez orada yuboriladi."
            )
            await update.message.reply_text(f"✅ To'lov {target_user_id} foydalanuvchi uchun tasdiqlandi!")
        except Exception as e:
            await update.message.reply_text(f"❌ Xatolik: {e}")
    else:
        await update.message.reply_text("❌ Format: /confirm user_id")
        
# ==================== TO'LOVNI TASDIQLASH COMMANDI ====================
async def confirm_payment_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    if not await admin_panel.check_admin(user_id):
        await update.message.reply_text("❌ Siz admin emassiz!")
        return
    
    if context.args:
        # Format: /confirm_123456_Avatar_2
        command_text = ' '.join(context.args)
        if '_' in command_text:
            parts = command_text.split('_')
            if len(parts) >= 3:
                target_user_id = parts[1]
                content_name = ' '.join(parts[2:])
                
                try:
                    # To'lovni tasdiqlash
                    # Bu yerda to'lovni tasdiqlash logikasi qo'shish kerak
                    
                    await context.bot.send_message(
                        chat_id=int(target_user_id),
                        text=f"✅ To'lovingiz tasdiqlandi! 🎉\n\n"
                             f"🎬 Kontent: {content_name}\n"
                             f"📦 Endi bu kontentni ko'rishingiz mumkin!\n\n"
                             f"📞 Savollar bo'lsa: @Operator_1985"
                    )
                    
                    await update.message.reply_text(
                        f"✅ To'lov {target_user_id} foydalanuvchi uchun tasdiqlandi!\n"
                        f"Kontent: {content_name}"
                    )
                    
                except Exception as e:
                    await update.message.reply_text(f"❌ Xatolik: {e}")
            else:
                await update.message.reply_text("❌ Noto'g'ri format!")
        else:
            await update.message.reply_text("❌ Format: /confirm_user_id_content_name")
    else:
        await update.message.reply_text("❌ Format: /confirm_user_id_content_name") 
        
# ==================== PULLIK KONTENT QO'SHISH ====================
async def show_add_premium_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pullik kontent qo'shish menyusi"""
    await update.message.reply_text(
        "💰 *Pullik Kontent Qo'shish*\n\n"
        "Bu bo'lim hozircha ishlamaydi. Tez orada qo'shiladi.",
        reply_markup=self.get_admin_main_menu(),
        parse_mode='Markdown'
    )        

# ==================== TO'LOVLARNI KO'RISH BO'LIMI ====================
async def show_payments(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """To'lov cheklarini ko'rish"""
    payments = db.get_pending_payments()
    
    if payments:
        payments_text = "💳 *Kutilayotgan To'lovlar:*\n\n"
        
        for payment in payments[:10]:  # Faqat birinchi 10 tasi
            payments_text += (
                f"🆔 To'lov ID: {payment[0]}\n"
                f"👤 Foydalanuvchi: {payment[1]}\n"
                f"🎬 Kontent: {payment[3]}\n"
                f"💰 Narx: {payment[4]:,} so'm\n"
                f"📅 Sana: {payment[7]}\n"
                f"✅ Tasdiqlash: /confirm_{payment[0]}\n"
                f"❌ Rad etish: /reject_{payment[0]}\n"
                f"────────────────────\n\n"
            )
        
        if len(payments) > 10:
            payments_text += f"... va yana {len(payments) - 10} ta to'lov"
    else:
        payments_text = "💳 *Kutilayotgan To'lovlar:*\n\nHozircha yangi to'lovlar mavjud emas."
    
    await update.message.reply_text(
        payments_text,
        reply_markup=self.get_admin_main_menu(),
        parse_mode='Markdown'
    )

# ==================== TO'LOVNI TASDIQLASH COMMANDI ====================
async def confirm_payment_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """To'lovni tasdiqlash"""
    if context.args:
        try:
            payment_id = int(context.args[0])
            admin_id = update.effective_user.id
            
            # To'lovni tasdiqlash
            success = db.confirm_payment(payment_id, admin_id)
            
            if success:
                # Foydalanuvchiga xabar yuborish
                payment_info = db.get_payment_by_id(payment_id)
                if payment_info:
                    user_id = payment_info[1]
                    content_name = payment_info[3]
                    
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"🎉 *Tabriklaymiz! To'lovingiz tasdiqlandi!*\n\n"
                                 f"🎬 **{content_name}** endi sizning!\n\n"
                                 f"📦 Kontentni ko'rish uchun kategoriyalar bo'limiga o'ting.\n"
                                 f"📞 Savollar bo'lsa: @Operator_1985",
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logging.error(f"Foydalanuvchiga xabar yuborishda xatolik: {e}")
                
                await update.message.reply_text(
                    f"✅ To'lov #{payment_id} muvaffaqiyatli tasdiqlandi!",
                    reply_markup=self.get_admin_main_menu()
                )
            else:
                await update.message.reply_text("❌ To'lovni tasdiqlashda xatolik!")
                
        except ValueError:
            await update.message.reply_text("❌ Noto'g'ri to'lov ID si!")
    else:
        await update.message.reply_text("❌ Format: /confirm payment_id")        

# ==================== ADMIN START FUNKSIYASI ====================
async def admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    if not await admin_panel.check_admin(user_id):
        from main import start
        await start(update, context)
        return
    
    existing_user = db.get_user(user_id)
    
    if existing_user:
        await update.message.reply_text(
            "🤗 Assalomu Aleykum Admin!\n\n"
            "Siz admin paneldasiz. Quyidagi bo'limlardan birini tanlang:",
            reply_markup=admin_panel.get_admin_main_menu()
        )
    else:
        from main import get_language_menu, LANGUAGE
        await update.message.reply_text(
            "🤗 Assalomu Aleykum Admin!\n\n"
            "Avval ro'yxatdan o'ting:",
            reply_markup=get_language_menu()
        )
        return LANGUAGE

# ==================== ADMIN PANELDAN CHIQISH ====================
async def admin_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_panel = AdminPanel()
    
    if await admin_panel.check_admin(user_id):
        from main import get_main_menu
        await update.message.reply_text(
            "👋 Admin paneldan chiqildi. Asosiy menyuga qaytingiz.",
            reply_markup=get_main_menu()
        )
    else:
        from main import get_main_menu
        await update.message.reply_text("🏠 Asosiy menyu:", reply_markup=get_main_menu())

# ==================== HANDLERLARNI QO'SHISH ====================
def setup_admin_handlers(application):
    # Admin xabarlari handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_messages))
    
    # Admin fayllari handler
    application.add_handler(MessageHandler(filters.VIDEO | filters.AUDIO | filters.PHOTO | filters.DOCUMENT, handle_admin_files))
    
    # Admin commandlari
    application.add_handler(CommandHandler("admin", admin_start))
    application.add_handler(CommandHandler("reply", reply_to_user))
    application.add_handler(CommandHandler("confirm", confirm_payment))
    
    