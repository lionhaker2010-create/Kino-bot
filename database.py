# -*-*- MA'LUMOTLAR BAZASI KONFIGURATSIYASI -*-*-
# -*-*- SQLite bazasi bilan ishlash uchun klass -*-*-

import sqlite3
import logging

# ==============================================================================
# -*-*- ASOSIY DATABASE KLASSI -*-*-
# ==============================================================================
class Database:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_db()
    
    # ==========================================================================
    # -*-*- BAZANI YARATISH VA ISHGA TUSHIRISH -*-*-
    # ==========================================================================
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    phone_number TEXT,
                    language TEXT DEFAULT 'uz',
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
                    
        # Barcha jadvallarni yaratish
        self.init_premium_tables()
        self.init_content_tables()
        self.init_user_purchases_table()
        self.init_blocked_users_table()
        self.init_user_credits_table()
        
    def init_blocked_users_table(self):
        """Bloklangan foydalanuvchilar jadvali"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS blocked_users (
                    block_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    reason TEXT,
                    block_duration TEXT,
                    blocked_until TIMESTAMP,
                    blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    blocked_by INTEGER,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            conn.commit()
            
    def init_user_credits_table(self):
        """Foydalanuvchi kreditlari jadvali"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_credits (
                    user_id INTEGER PRIMARY KEY,
                    download_credits INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
                
    # -*-*- PULLIK HIZMATLAR JADVALLARI -*-*-
    def init_premium_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Premium obuna jadvali
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS premium_subscriptions (
                    user_id INTEGER PRIMARY KEY,
                    start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_date TIMESTAMP,
                    plan_type TEXT DEFAULT 'monthly',
                    payment_amount INTEGER DEFAULT 130000,
                    payment_status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Yuklab olishlar jadvali
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS downloads (
                    download_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    content_id TEXT,
                    content_name TEXT,
                    download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    price_paid INTEGER,
                    download_type TEXT,
                    status TEXT DEFAULT 'completed'
                )
            ''')
            
            # Qo'llab-quvvatlash ticketlari jadvali
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS support_tickets (
                    ticket_id TEXT PRIMARY KEY,
                    user_id INTEGER,
                    user_name TEXT,
                    issue_text TEXT,
                    status TEXT DEFAULT 'open',
                    assigned_to TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    resolved_at TIMESTAMP
                )
            ''')
            
            # To'lovlar jadvali
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount INTEGER,
                    payment_type TEXT,
                    content_id INTEGER,
                    content_type TEXT,
                    status TEXT DEFAULT 'pending',
                    receipt_file_id TEXT,
                    service_details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP
                )
            ''')
            conn.commit()

    # -*-*- KONTENT BAZASI -*-*-
    def init_content_tables(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Kinolar jadvali
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movies (
                    movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    file_id TEXT,
                    price INTEGER DEFAULT 0,
                    is_premium BOOLEAN DEFAULT FALSE,
                    actor_name TEXT,
                    banner_file_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    added_by INTEGER
                )
            ''')
            
            # Seriallar jadvali
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS series (
                    series_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT,
                    total_episodes INTEGER,
                    price INTEGER DEFAULT 0,
                    is_premium BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    added_by INTEGER
                )
            ''')
            
            # Serial qismlari jadvali
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS episodes (
                    episode_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    series_id INTEGER,
                    episode_number INTEGER,
                    title TEXT,
                    file_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (series_id) REFERENCES series (series_id)
                )
            ''')
            conn.commit()
            
    # ==============================================================================
    # -*-*- FOYDALANUVCHI SOTIB OLGANLAR JADVALI -*-*-
    # ==============================================================================
    def init_user_purchases_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_purchases (
                    purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    movie_id INTEGER,
                    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (movie_id) REFERENCES movies (movie_id)
                )
            ''')
            conn.commit()

    # ==============================================================================
    # -*-*- JADVALNI YANGILASH -*-*-
    # ==============================================================================
    def update_movies_table(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('ALTER TABLE movies ADD COLUMN actor_name TEXT')
                print("✅ actor_name ustuni qo'shildi")
            except sqlite3.OperationalError:
                print("✅ actor_name ustuni allaqachon mavjud")
            
            try:
                cursor.execute('ALTER TABLE movies ADD COLUMN banner_file_id TEXT')
                print("✅ banner_file_id ustuni qo'shildi")
            except sqlite3.OperationalError:
                print("✅ banner_file_id ustuni allaqachon mavjud")

    # ==============================================================================
    # -*-*- KINO QO'SHISH -*-*-
    # ==============================================================================
    def add_movie(self, title, description, category, file_id, price, is_premium, added_by, actor_name=None, banner_file_id=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO movies (title, description, category, file_id, price, is_premium, added_by, actor_name, banner_file_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, description, category, file_id, price, is_premium, added_by, actor_name, banner_file_id))
            conn.commit()
            return cursor.lastrowid

    # ==============================================================================
    # -*-*- KINOLARNI OLISH -*-*-
    # ==============================================================================
    def get_movies_by_category(self, category):
        """Kategoriya bo'yicha kinolarni olish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT movie_id, title, description, category, file_id, price, 
                       is_premium, actor_name, banner_file_id, created_at, added_by 
                FROM movies 
                WHERE category LIKE ? 
                ORDER BY created_at DESC
            ''', (f'{category}%',))
            return cursor.fetchall()

    def get_all_movies_by_main_category(self, main_category):
        """Asosiy kategoriya bo'yicha barcha kinolarni olish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Barcha mumkin bo'lgan kategoriya variantlari
            cursor.execute('''
                SELECT movie_id, title, description, category, file_id, price, 
                       is_premium, actor_name, banner_file_id, created_at, added_by 
                FROM movies 
                WHERE category LIKE ? OR category LIKE ? OR category = ?
                ORDER BY created_at DESC
            ''', (f'{main_category}%', f'{main_category} -%', main_category))
            
            return cursor.fetchall()

    def get_movie(self, movie_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM movies WHERE movie_id = ?', (movie_id,))
            return cursor.fetchone()

    def get_movie_by_id(self, movie_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM movies WHERE movie_id = ?', (movie_id,))
            return cursor.fetchone()

    # ==============================================================================
    # -*-*- BARCHA KINOLARNI OLISH -*-*-
    # ==============================================================================
    def get_all_movies(self):
        """Barcha kinolarni olish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT movie_id, title, description, category, file_id, price, 
                       is_premium, actor_name, banner_file_id, created_at, added_by 
                FROM movies 
                ORDER BY created_at DESC
            ''')
            return cursor.fetchall()
            
    def get_free_movies(self):
        """Barcha bepul kinolarni olish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT movie_id, title, description, category, file_id, price, 
                       is_premium, actor_name, banner_file_id, created_at, added_by 
                FROM movies 
                WHERE price = 0
                ORDER BY created_at DESC
            ''')
            return cursor.fetchall()

    def get_all_movies_sorted(self):
        """Barcha kinolarni saralab olish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT movie_id, title, description, category, file_id, price, 
                       is_premium, actor_name, banner_file_id, created_at, added_by 
                FROM movies 
                ORDER BY 
                    CASE WHEN price = 0 THEN 0 ELSE 1 END,
                    created_at DESC
            ''')
            return cursor.fetchall()

    # ==============================================================================
    # -*-*- QIDIRUV -*-*-
    # ==============================================================================
    def search_movies(self, search_query):
        """Kinolarni qidirish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            search_pattern = f'%{search_query}%'
            cursor.execute('''
                SELECT movie_id, title, description, category, file_id, price, 
                       is_premium, actor_name, banner_file_id, created_at, added_by 
                FROM movies 
                WHERE title LIKE ? OR actor_name LIKE ? OR category LIKE ? OR description LIKE ?
                ORDER BY 
                    CASE WHEN price = 0 THEN 0 ELSE 1 END,
                    created_at DESC
            ''', (search_pattern, search_pattern, search_pattern, search_pattern))
            return cursor.fetchall()

    # ==============================================================================
    # -*-*- KINO O'CHIRISH -*-*-
    # ==============================================================================
    def delete_movie(self, movie_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM movies WHERE movie_id = ?', (movie_id,))
            conn.commit()
            return cursor.rowcount > 0

    def get_movies_by_category_for_admin(self, category):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT movie_id, title, actor_name, price, created_at 
                FROM movies 
                WHERE category LIKE ? 
                ORDER BY created_at DESC
            ''', (f'{category}%',))
            return cursor.fetchall()

    def get_movie_title_by_id(self, movie_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT title FROM movies WHERE movie_id = ?', (movie_id,))
            result = cursor.fetchone()
            return result[0] if result else "Noma'lum"

    # ==============================================================================
    # -*-*- PREMIUM OBUNA FUNKSIYALARI -*-*-
    # ==============================================================================
    def add_premium_subscription(self, user_id, duration_days=30, amount=130000):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            from datetime import datetime, timedelta
            start_date = datetime.now()
            end_date = start_date + timedelta(days=duration_days)
            
            cursor.execute('''
                INSERT OR REPLACE INTO premium_subscriptions 
                (user_id, start_date, end_date, payment_amount) 
                VALUES (?, ?, ?, ?)
            ''', (user_id, start_date, end_date, amount))
            conn.commit()

    def check_premium_status(self, user_id):
        """Foydalanuvchi premium obunasi borligini tekshirish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT end_date FROM premium_subscriptions 
                WHERE user_id = ? AND payment_status = 'active'
            ''', (user_id,))
            result = cursor.fetchone()
            if result:
                from datetime import datetime
                is_active = datetime.now() < datetime.fromisoformat(result[0])
                return is_active
            return False

    def remove_premium_subscription(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM premium_subscriptions WHERE user_id = ?', (user_id,))
            conn.commit()

    # ==============================================================================
    # -*-*- FOYDALANUVCHI FUNKSIYALARI -*-*-
    # ==============================================================================
    def add_user(self, user_id, username, first_name, phone_number, language):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, phone_number, language) 
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, first_name, phone_number, language))
            conn.commit()
    
    def get_user(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            return cursor.fetchone()

    def get_user_info(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            return cursor.fetchone()

    def update_user_language(self, user_id, language):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
            conn.commit()

    def get_users_count(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users')
            return cursor.fetchone()[0]

    def get_all_users(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT user_id, first_name, username FROM users')
            return cursor.fetchall()

    def get_all_users_with_details(self):
        """Barcha foydalanuvchilarni to'liq ma'lumotlari bilan olish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 
                    u.user_id, 
                    u.username, 
                    u.first_name, 
                    u.phone_number, 
                    u.language,
                    u.registered_at,
                    CASE WHEN ps.user_id IS NOT NULL THEN 1 ELSE 0 END as is_premium
                FROM users u
                LEFT JOIN premium_subscriptions ps ON u.user_id = ps.user_id 
                    AND ps.payment_status = 'active'
                ORDER BY u.registered_at DESC
            ''')
            return cursor.fetchall()

    def get_today_users(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users WHERE DATE(registered_at) = DATE("now")')
            return cursor.fetchone()[0]

    # ==============================================================================
    # -*-*- YUKLAB OLISH FUNKSIYALARI -*-*-
    # ==============================================================================
    def log_download(self, user_id, content_id, content_name, price, download_type):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO downloads 
                (user_id, content_id, content_name, price_paid, download_type) 
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, content_id, content_name, price, download_type))
            conn.commit()

    def can_user_download(self, user_id, movie_id):
        """Foydalanuvchi kino yuklab olish huquqiga ega ekanligini tekshirish"""
        movie = self.get_movie_by_id(movie_id)
        if not movie:
            return False
        
        # Faqat PULLIK kinolarni yuklab olish mumkin
        if movie[5] == 0:  # price = 0 (bepul)
            return False
        
        # Agar foydalanuvchi kino sotib olgan bo'lsa
        if self.check_user_purchase(user_id, movie_id):
            return True
        
        # Agar foydalanuvchi premium bo'lsa
        if self.check_premium_status(user_id):
            return True
        
        return False

    # ==============================================================================
    # -*-*- FOYDALANUVCHI SOTIB OLGAN KONTENTLAR -*-*-
    # ==============================================================================
    def add_user_purchase(self, user_id, movie_id, purchase_date=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_purchases (user_id, movie_id) 
                VALUES (?, ?)
            ''', (user_id, movie_id))
            conn.commit()

    def check_user_purchase(self, user_id, movie_id):
        """Foydalanuvchi kino sotib olganini tekshirish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM user_purchases 
                WHERE user_id = ? AND movie_id = ?
            ''', (user_id, movie_id))
            return cursor.fetchone() is not None

    def get_user_purchases(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT m.* FROM movies m
                JOIN user_purchases up ON m.movie_id = up.movie_id
                WHERE up.user_id = ?
            ''', (user_id,))
            return cursor.fetchall()

    # ==============================================================================
    # -*-*- TO'LOVLAR -*-*-
    # ==============================================================================
    def add_payment(self, user_id, amount, service_type, service_name, description, receipt_file_id=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO payments (user_id, amount, payment_type, content_id, content_type, receipt_file_id, service_details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, amount, service_type, 0, service_name, receipt_file_id, description))
            conn.commit()
            return cursor.lastrowid

    def get_payment_by_id(self, payment_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM payments WHERE payment_id = ?', (payment_id,))
            return cursor.fetchone()

    def get_pending_payments(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.*, u.first_name, m.title 
                FROM payments p
                LEFT JOIN users u ON p.user_id = u.user_id
                LEFT JOIN movies m ON p.content_id = m.movie_id
                WHERE p.status = 'pending'
            ''')
            return cursor.fetchall()

    def update_payment_status(self, payment_id, status):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE payments SET status = ?, completed_at = CURRENT_TIMESTAMP 
                WHERE payment_id = ?
            ''', (status, payment_id))
            conn.commit()

    # ==============================================================================
    # -*-*- YUKLAB OLISH CREDITLARI -*-*-
    # ==============================================================================
    def add_download_credits(self, user_id, credits):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO user_credits (user_id, download_credits)
                VALUES (?, ?)
            ''', (user_id, credits))
            conn.commit()

    def get_download_credits(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT download_credits FROM user_credits WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0

    # ==============================================================================
    # -*-*- QO'LLAB-QUVVATLASH -*-*-
    # ==============================================================================
    def create_support_ticket(self, ticket_id, user_id, user_name, issue_text):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO support_tickets 
                (ticket_id, user_id, user_name, issue_text) 
                VALUES (?, ?, ?, ?)
            ''', (ticket_id, user_id, user_name, issue_text))
            conn.commit()

    # ==============================================================================
    # -*-*- STATISTIKA -*-*-
    # ==============================================================================
    def get_premium_stats(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM premium_subscriptions WHERE payment_status = "active"')
            premium_users = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT SUM(payment_amount) FROM premium_subscriptions 
                WHERE strftime('%Y-%m', start_date) = strftime('%Y-%m', 'now')
            ''')
            monthly_income = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT COUNT(*) FROM downloads')
            downloads_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM support_tickets WHERE status = "open"')
            active_tickets = cursor.fetchone()[0]
            
            return {
                'premium_users': premium_users,
                'monthly_income': monthly_income,
                'downloads_count': downloads_count,
                'active_tickets': active_tickets,
                'most_downloaded': "Kinolar"
            }

    def get_users_statistics(self):
        """Foydalanuvchilar statistikasi"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM premium_subscriptions WHERE payment_status = "active"')
            premium_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE DATE(registered_at) = DATE("now")')
            today_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE registered_at >= DATE("now", "-7 days")')
            weekly_growth = cursor.fetchone()[0]
            
            return {
                'total_users': total_users,
                'premium_users': premium_users,
                'today_users': today_users,
                'weekly_growth': weekly_growth
            }

    # ==============================================================================
    # -*-*- KATEGORIYALAR -*-*-
    # ==============================================================================
    def get_all_categories(self):
        """Barcha asosiy va ichki bo'limlarni qaytarish"""
        return {
            "main_categories": [
                "🎭 Hollywood Kinolari", "🎬 Hind Filmlari", "📺 Hind Seriallari",
                "🎥 Rus Kinolari", "📟 Rus Seriallari", "🎞️ O'zbek Kinolari", 
                "📱 O'zbek Seriallari", "🕌 Islomiy Kinolar", "📖 Islomiy Seriallar",
                "🇹🇷 Turk Kinolari", "📺 Turk Seriallari", "👶 Bolalar Kinolari",
                "🐰 Bolalar Multfilmlari", "🇰🇷 Koreys Kinolari", "📡 Koreys Seriallari",
                "🎯 Qisqa Filmlar", "🎤 Konsert Dasturlari"
            ],
            "sub_categories": {
                "🎭 Hollywood Kinolari": [
                    "🎬 Mel Gibson", "💪 Arnold Schwarzenegger", "🥊 Sylvester Stallone",
                    "🚗 Jason Statham", "🐲 Jeki Chan", "🥋 Skod Adkins",
                    "🎭 Denzil Washington", "💥 Jan Clod Van Dam", "👊 Brus lee",
                    "😂 Jim Cerry", "🏴‍☠️ Jonni Depp", "🥋 Jet Lee", 
                    "👊 Mark Dacascos", "🎬 Bred Pitt", "🎭 Leonardo Dicaprio"
                ],
                "🎬 Hind Filmlari": [
                    "🤴 Shakruhkhan", "🎬 Amirkhan", "💪 Akshay Kumar",
                    "👑 Salmonkhan", "🌟 SayfAlihon", "🎭 Amitahbachchan",
                    "🔥 MethunChakraborty", "🎥 Dharmendra", "🎞️ Raj Kapur"
                ],
                "📺 Hind Seriallari": [],
                "🎥 Rus Kinolari": [],
                "📟 Rus Seriallari": [],
                "🎞️ O'zbek Kinolari": [],
                "📱 O'zbek Seriallari": [],
                "🕌 Islomiy Kinolar": [],
                "📖 Islomiy Seriallar": [],
                "🇹🇷 Turk Kinolari": [],
                "📺 Turk Seriallari": [],
                "👶 Bolalar Kinolari": [],
                "🐰 Bolalar Multfilmlari": [],
                "🇰🇷 Koreys Kinolari": [],
                "📡 Koreys Seriallari": [],
                "🎯 Qisqa Filmlari": [],
                "🎤 Konsert Dasturlari": []
            }
        }

    # ==============================================================================
    # -*-*- BLOKLASH FUNKSIYALARI -*-*-
    # ==============================================================================
    def block_user(self, user_id, reason, block_duration, blocked_by):
        """Foydalanuvchini bloklash"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            from datetime import datetime, timedelta
            blocked_until = None
            
            if block_duration == "24_soat":
                blocked_until = datetime.now() + timedelta(hours=24)
            elif block_duration == "7_kun":
                blocked_until = datetime.now() + timedelta(days=7)
            
            cursor.execute('''
                INSERT OR REPLACE INTO blocked_users 
                (user_id, reason, block_duration, blocked_until, blocked_by, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, reason, block_duration, blocked_until, blocked_by, True))
            conn.commit()
            return True

    def unblock_user(self, user_id):
        """Foydalanuvchini blokdan ochish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE blocked_users 
                SET is_active = FALSE 
                WHERE user_id = ? AND is_active = TRUE
            ''', (user_id,))
            conn.commit()
            return cursor.rowcount > 0

    def is_user_blocked(self, user_id):
        """Foydalanuvchi bloklanganligini tekshirish"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT reason, block_duration, blocked_until 
                FROM blocked_users 
                WHERE user_id = ? AND is_active = TRUE
            ''', (user_id,))
            result = cursor.fetchone()
            
            if result:
                reason, block_duration, blocked_until = result
                if blocked_until:
                    from datetime import datetime
                    current_time = datetime.now()
                    blocked_until_time = datetime.fromisoformat(blocked_until)
                    
                    if current_time > blocked_until_time:
                        self.unblock_user(user_id)
                        return False
                return True
            return False

    def get_blocked_user_info(self, user_id):
        """Bloklangan foydalanuvchi ma'lumotlari"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT reason, block_duration, blocked_until, blocked_at, blocked_by
                FROM blocked_users 
                WHERE user_id = ? AND is_active = TRUE
            ''', (user_id,))
            return cursor.fetchone()

    def get_all_blocked_users(self):
        """Barcha bloklangan foydalanuvchilar"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT bu.user_id, u.first_name, bu.reason, bu.block_duration, bu.blocked_at
                FROM blocked_users bu
                LEFT JOIN users u ON bu.user_id = u.user_id
                WHERE bu.is_active = TRUE
            ''')
            return cursor.fetchall()

    # ==============================================================================
    # -*-*- DEBUG FUNKSIYALARI -*-*-
    # ==============================================================================
    def debug_category_movies(self):
        """Barcha kategoriyalar va ularning kinolarini ko'rsatish (debug uchun)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT category FROM movies ORDER BY category')
            categories = cursor.fetchall()
            
            result = {}
            for category in categories:
                cat_name = category[0]
                cursor.execute('SELECT COUNT(*) FROM movies WHERE category = ?', (cat_name,))
                count = cursor.fetchone()[0]
                result[cat_name] = count
                
            return result

    def get_pending_activations(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, payment_date FROM payments 
                WHERE status = 'pending' AND payment_type = 'premium'
            ''')

            return cursor.fetchall()
     
    # database.py faylining oxiriga qo'shing:
    def get_movies_by_main_category(self, main_category):
        """Asosiy kategoriya bo'yicha kinolarni olish"""
        return self.get_all_movies_by_main_category(main_category) 