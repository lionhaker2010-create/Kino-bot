import sqlite3
import logging

# ==================== DATABASE CLASS ====================
class Database:
    def __init__(self, db_name='kino.db'):
        self.db_name = db_name
        self.init_db()
    
    # ==================== DATABASENI ISHGA TUSHIRISH ====================
    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # FOYDALANUVCHILAR JADVALI
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    phone TEXT,
                    language TEXT DEFAULT 'uz',
                    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')    
        
        # KONTENT JADVALI
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                file_id TEXT,
                file_type TEXT,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ==================== TO'LOVLAR JADVALI ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                content_type TEXT NOT NULL,  -- 'movie', 'series', 'cartoon'
                content_name TEXT NOT NULL,
                amount INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',  -- 'pending', 'confirmed', 'rejected'
                receipt_photo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confirmed_at TIMESTAMP,
                confirmed_by INTEGER
            )
        ''')

        # ==================== FOYDALANUVCHI RUXSATLARI JADVALI ====================
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                content_id INTEGER,
                content_type TEXT,
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content (id)
            )
        ''')
        
         # PULLIK KONTENTLAR JADVALI
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS premium_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id INTEGER,
                category TEXT NOT NULL,
                subject TEXT NOT NULL,
                title TEXT NOT NULL,
                price INTEGER NOT NULL,
                is_premium BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (content_id) REFERENCES content (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logging.info("Database initialized")
        
        # ==================== KONTENT PULLIKLIGINI TEKSHIRISH ====================
    def is_premium_content(self, category, subject):
        """Kontent pullik yoki yo'qligini tekshirish"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM premium_content 
            WHERE category = ? AND subject = ? AND is_premium = TRUE
        ''', (category, subject))
        result = cursor.fetchone()
        conn.close()
        return result is not None

    # ==================== PULLIK KONTENT QO'SHISH ====================
    def add_premium_content(self, content_id, category, subject, title, price):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO premium_content 
            (content_id, category, subject, title, price, is_premium)
            VALUES (?, ?, ?, ?, ?, TRUE)
        ''', (content_id, category, subject, title, price))
        conn.commit()
        conn.close()
        return True
        
    # ==================== PULLIK KONTENTLARNI OLISH ====================
    def get_premium_content_by_category(self, category, subject):
        """Kategoriya bo'yicha pullik kontentlarni olish"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, pc.price 
            FROM content c 
            JOIN premium_content pc ON c.id = pc.content_id 
            WHERE c.category = ? AND pc.is_premium = TRUE
            ORDER BY c.added_at DESC
        ''', (f"{category}_{subject}",))
        contents = cursor.fetchall()
        conn.close()
        return contents

    def get_last_content_id(self):
        """Oxirgi qo'shilgan kontent ID sini olish"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM content ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def get_premium_content_by_name(self, content_name):
        """Nomi bo'yicha pullik kontentni olish"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, pc.price 
            FROM content c 
            JOIN premium_content pc ON c.id = pc.content_id 
            WHERE c.title = ? AND pc.is_premium = TRUE
        ''', (content_name,))
        content = cursor.fetchone()
        conn.close()
        return content    

    # ==================== FOYDALANUVCHINING RUXSATLARINI TEKSHIRISH ====================
    def check_user_access(self, user_id, category, subject):
        """Foydalanuvchi kontentga ruxsatiga ega yoki yo'qligini tekshirish"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # 1. To'lovlarni tekshirish
        cursor.execute('''
            SELECT * FROM payments 
            WHERE user_id = ? AND content_name LIKE ? AND status = 'confirmed'
        ''', (user_id, f'%{subject}%'))
        payment = cursor.fetchone()
        
        # 2. User access jadvalidan tekshirish
        cursor.execute('''
            SELECT * FROM user_access 
            WHERE user_id = ? AND content_type = ?
        ''', (user_id, f"{category}_{subject}"))
        access = cursor.fetchone()
        
        conn.close()
        return payment is not None or access is not None
        
    # ==================== TO'LOVLARNI OLISH ====================
    def get_pending_payments(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments WHERE status = "pending" ORDER BY created_at DESC')
        payments = cursor.fetchall()
        conn.close()
        return payments

    def get_payment_by_id(self, payment_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments WHERE id = ?', (payment_id,))
        payment = cursor.fetchone()
        conn.close()
        return payment

    def confirm_payment(self, payment_id, admin_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE payments 
            SET status = "confirmed", confirmed_at = CURRENT_TIMESTAMP, confirmed_by = ?
            WHERE id = ?
        ''', (admin_id, payment_id))
        conn.commit()
        conn.close()
        return True

    def get_premium_price(self, category, subject):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT price FROM premium_content WHERE category = ? AND subject = ?', (category, subject))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 30000    
       
    def reject_payment(self, payment_id, admin_id):
        """To'lovni rad etish"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE payments 
            SET status = "rejected", confirmed_at = CURRENT_TIMESTAMP, confirmed_by = ?
            WHERE id = ?
        ''', (admin_id, payment_id))
        conn.commit()
        conn.close()
        return True    
        
    
    # ==================== FOYDALANUVCHI QO'SHISH ====================
    def add_user(self, user_id, username, first_name, phone, language='uz'):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, phone, language)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, phone, language))
        conn.commit()
        conn.close()
        return True
    
    # ==================== FOYDALANUVCHINI OLISH ====================
    def get_user(self, user_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    # ==================== BARCHA FOYDALANUVCHILARNI OLISH ====================
    def get_all_users(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT user_id FROM users')
        users = cursor.fetchall()
        conn.close()
        return [user[0] for user in users]
    
    # ==================== KONTENT QO'SHISH ====================
    def add_content(self, title, description, category, file_id, file_type, added_by):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO content (title, description, category, file_id, file_type, added_by)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, description, category, file_id, file_type, added_by))
        conn.commit()
        conn.close()
        return True
    
        # ==================== YANGILANGAN SUBYEKT BO'YICHA KONTENT OLISH ====================
    def get_content_by_subject(self, category, subject):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Kategoriya va subyektni to'g'ri formatda qidirish
        search_pattern = f"{category}_{subject}"
        print(f"DEBUG: Qidirilayotgan pattern: {search_pattern}")  # Debug uchun
        
        cursor.execute('SELECT * FROM content WHERE category = ?', (search_pattern,))
        content = cursor.fetchall()
        
        print(f"DEBUG: Topilgan kontentlar: {len(content)} ta")  # Debug uchun
        for item in content:
            print(f"DEBUG: Kontent: {item[1]} | {item[3]}")  # Har bir kontentni ko'rsatish
        
        conn.close()
        return content

   # ==================== YANGILANGAN SAHIFALAB KONTENT OLISH ====================
    def get_content_by_subject_paginated(self, category, subject, page=1, limit=1):  # limit 1 ga o'zgartirildi
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        offset = (page - 1) * limit
        
        # Kategoriya va subyektni to'g'ri formatda qidirish
        search_pattern = f"{category}_{subject}"
        print(f"DEBUG: Sahifalab qidirish - Pattern: {search_pattern}, Sahifa: {page}, Limit: {limit}")
        
        cursor.execute(
            'SELECT * FROM content WHERE category = ? LIMIT ? OFFSET ?', 
            (search_pattern, limit, offset)
        )
        content = cursor.fetchall()
        
        print(f"DEBUG: Sahifada topilgan kontentlar: {len(content)} ta")
        
        # JAMI SAHIFALAR SONINI HISOBLASH
        cursor.execute(
            'SELECT COUNT(*) FROM content WHERE category = ?', 
            (search_pattern,)
        )
        total_count = cursor.fetchone()[0]
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
        
        print(f"DEBUG: Jami: {total_count} ta, Sahifalar: {total_pages}")
        
        conn.close()
        return content, total_pages, total_count

    # ==================== BAZANI TEKSHIRISH FUNKSIYASI ====================
    def debug_content(self):
        """Barcha kontentlarni ko'rish uchun debug funksiya"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM content')
        all_content = cursor.fetchall()
        
        conn.close()
        return all_content
    
    # ==================== QIDIRUV BO'YICHA KONTENT OLISH ====================
    def search_content(self, query):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM content WHERE title LIKE ?', (f'%{query}%',))
        results = cursor.fetchall()
        conn.close()
        return results
    
    # ==================== BARCHA KONTENTLARNI OLISH ====================
    def get_all_content(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM content')
        content = cursor.fetchall()
        conn.close()
        return content
        
    # ==================== BARCHA KATEGORIYALARNI OLISH ====================
    def get_all_categories(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT DISTINCT category FROM content')
        categories = cursor.fetchall()
        conn.close()
        return [category[0] for category in categories]

    # ==================== KATEGORIYA BO'YICHA KONTENT OLISH ====================
    def get_content_by_category(self, category):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM content WHERE category = ?', (category,))
        content = cursor.fetchall()
        conn.close()
        return content    
        
    # ==================== TO'LOV QO'SHISH ====================
    def add_payment(self, user_id, content_type, content_name, amount, receipt_photo=None):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (user_id, content_type, content_name, amount, receipt_photo)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, content_type, content_name, amount, receipt_photo))
        conn.commit()
        conn.close()
        return True

    # ==================== TO'LOVLARNI OLISH ====================
    def get_pending_payments(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM payments WHERE status = "pending"')
        payments = cursor.fetchall()
        conn.close()
        return payments

    # ==================== TO'LOVNI TASDIQLASH ====================
    def confirm_payment(self, payment_id, admin_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE payments 
            SET status = "confirmed", confirmed_at = CURRENT_TIMESTAMP, confirmed_by = ?
            WHERE id = ?
        ''', (admin_id, payment_id))
        conn.commit()
        conn.close()
        return True

        # ==================== PULLIK KONTENTNI NOMI BO'YICHA OLISH ====================
    def get_premium_content_by_name(self, content_name):
        """Nomi bo'yicha pullik kontentni olish"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.*, pc.price 
            FROM content c 
            JOIN premium_content pc ON c.id = pc.content_id 
            WHERE c.title = ? AND pc.is_premium = TRUE
        ''', (content_name,))
        content = cursor.fetchone()
        conn.close()
        return content

    # ==================== FOYDALANUVCHI RUXSATI QO'SHISH ====================
    def add_user_access(self, user_id, content_id, content_type):
        """Foydalanuvchiga kontent ruxsati qo'shish"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_access (user_id, content_id, content_type)
            VALUES (?, ?, ?)
        ''', (user_id, content_id, content_type))
        conn.commit()
        conn.close()
        return True

    # ==================== FOYDALANUVCHINING RUXSATLARINI TEKSHIRISH ====================
    def check_user_access(self, user_id, content_id):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM user_access 
            WHERE user_id = ? AND content_id = ?
        ''', (user_id, content_id))
        access = cursor.fetchone()
        conn.close()
        return access is not None    