# -*-*- AVTOMATIK XABAR YUBORISH TIZIMI -*-*-
import asyncio
import logging
from datetime import datetime, timedelta
from aiogram import Bot
from database import Database

# Pytz o'rniga oddiy datetime
try:
    import pytz
    TASHKENT_TZ = pytz.timezone('Asia/Tashkent')
    USE_PYTZ = True
except ImportError:
    print("⚠️ pytz moduli topilmadi, oddiy vaqt ishlatiladi")
    USE_PYTZ = False

class AutoMessager:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.db = Database()
        self.logger = logging.getLogger(__name__)
    
    def _get_tashkent_time(self):
        """Toshkent vaqtini olish"""
        if USE_PYTZ:
            return datetime.now(TASHKENT_TZ)
        else:
            # UTC+5 (Toshkent vaqti)
            return datetime.utcnow() + timedelta(hours=5)
    
    async def send_message_to_all_users(self, message_text: str):
        """Barcha foydalanuvchilarga xabar yuborish"""
        try:
            users = self.db.get_all_users()
            success_count = 0
            fail_count = 0
            
            for user in users:
                try:
                    await self.bot.send_message(user[0], message_text, parse_mode='HTML')
                    success_count += 1
                    # 0.1 soniya kutish (spamdan qochish)
                    await asyncio.sleep(0.1)
                except Exception as e:
                    fail_count += 1
                    self.logger.error(f"Xabar yuborishda xatolik user_id {user[0]}: {e}")
            
            self.logger.info(f"✅ Xabar yuborildi: {success_count} ta, Xatolik: {fail_count} ta")
            return success_count, fail_count
            
        except Exception as e:
            self.logger.error(f"Xabar yuborishda umumiy xatolik: {e}")
            return 0, 0
    
    async def get_daily_message(self):
        """Kunlik xabarlarni olish"""
        now = self._get_tashkent_time()
        current_time = now.strftime("%H:%M")
        day_of_week = now.strftime("%A")
        
        # Juma kuni tekshirish
        is_friday = (day_of_week.lower() == "friday")
        
        messages = {
            "08:00": {
                "message": self._get_morning_message(is_friday)
            },
            "12:00": {
                "message": self._get_noon_message()
            },
            "21:00": {
                "message": self._get_evening_message()
            }
        }
        
        return messages.get(current_time)
    
    def _get_morning_message(self, is_friday: bool):
        """Tongi salomlashuv"""
        if is_friday:
            return """
🌅 <b>ASSALOMU ALAYKUM! JUMA MUBORAK!</b> 🌙

📿 <i>«Ey imonli kishilar, juma kuni namozga chaqirilgach, Allohning zikriga shoshiling...»</i> (Juma surasi, 9-oyat)

🎉 <b>MUQADDAS JUMA KUNI BILAN TABRIKLAYMIZ!</b>

✨ <b>Bugungi tavsiyalar:</b>
• 🕌 Bomdod namozini o'qib, kunningizni barakali boshlang
• 📖 Qur'on tilovati bilan kuningizni nurlandiring
• 🤲 Duolaringizni unutmang - bu kunning duolari ijobat bo'lur
• 🎗️ Savobli amallar qiling - juma kuni qilingan har bir yaxshilik baraka olib keladi

🕋 <b>Juma namozi:</b>
• 🕰️ Bomdod namozidan keyin tavba istig'for qiling
• 🛁 G'usl qiling va toza kiyim keting
• 🕌 Masjidga erta borib, juma namozi uchun tayyorlaning
• 📿 Namozdan oldin Qur'on o'qib, Ollohning rahmatiga suyaning

🎬 <b>Dam olish vaqti:</b>
Juma kuni oilangiz bilan vaqt o'tkazing va bizning kinoteksimizdan foydalanib, dam oling!

<b>🌺 Alloh hammamizning gunohlarimizni kechirsin, duolarimizni ijobat qilsin va juma kunningizni barakali qilsin! AMIN! 🌺</b>

<i>#JumaMuborak #BarakaliKun #Islom</i>
"""
        else:
            return """
🌅 <b>ASSALOMU ALAYKUM! XAYRLI TONG!</b> 🌄

✨ Yangi kun, yangi imkoniyatlar bilan sizni tabriklaymiz!

🕌 <b>Bomdod namozini o'qib, kunningizni barakali boshlang!</b>

📿 <i>«Har kuni ertalab tong otganda, inson uchun yangi hayot boshlanadi»</i>

🎯 <b>Bugungi kun uchun tavsiyalar:</b>
• 🤲 Duo qiling - kunningiz muvaffaqiyatli o'tsin
• 🏃 Sog'lom nonushta qiling va energiya to'plang
• 📚 Birorta yangi narsa o'rganing
• 🎬 Dam olish vaqtida sevimli filmlaringizni tomosha qiling

🎭 <b>Bizda siz uchun:</b>
• 🎥 1000+ turli janrdagi filmlar
• 📺 Eng yangi seriallar
• 🎞️ HD sifatda tomosha qilish
• 📥 Yuklab olish imkoniyati

<b>🌺 Kuningiz barakali, ishlaringiz rivojli, omadingiz yog'don bo'lsin! 🌺</b>

<i>#XayrliTong #YangiKun #Baraka</i>
"""
    
    def _get_noon_message(self):
        """Tushlik salomlashuvi"""
        return """
☀️ <b>HAYRLI KUN! KUN YARMI BO'LDI!</b> 🕛

🏢 Ish vaqti davom etmoqda, biroz dam olish vaqti keldi!

🕌 <b>Peshin namozini o'qib, kuningizni davom ettiring!</b>

🎯 <b>Kunning ikkinchi yarmi uchun energiya to'plang:</b>
• ☕ Bir piyola choy yoki kofe iching
• 🍎 Sog'lom ovqatlaning
• 🧘 Bir necha daqiqa dam oling
• 🎬 Qisqa tanaffusda qiziqarli film ko'ring

🎭 <b>Dam olish takliflarimiz:</b>
• 🎞️ Qisqa metrajli filmlar
• 🎬 Komediya janri - kayfiyatingizni ko'taring
• 📚 Bilim oshiruvchi hujjatli filmlar
• 🎵 Musiqiy videolar

<b>🌞 Kuningizning qolgan qismi ham omadli va barakali o'tsin!</b>

💫 <i>«Har bir dam olish - yangi kuchlanish uchun imkoniyat»</i>

<i>#KunYarmi #DamOlish #Energiya</i>
"""
    
    def _get_evening_message(self):
        """Kechki salomlashuv"""
        return """
🌙 <b>HAYRLI KECH! KUN YAKUNLANDI!</b> 🌆

🕌 <b>Shom va Xufton namozlarini o'qib, kuningizni xayrli yakunlang!</b>

📖 <i>«Kechki payt - kun davomida qilingan ishlarni hisob-kitob qilish vaqti»</i>

🌟 <b>Kechki dam olish tavsiyalari:</b>
• 📿 Kunning hisobini chiqaring - nima yaxshi, nima yomon bo'ldi?
• 🤲 Kechki duolarini o'qib, tinch uxlashga tayyorlaning
• 👨‍👩‍👧‍👦 Oilangiz bilan sifatli vaqt o'tkazing
• 🎬 Sevimli filmlaringiz bilan dam oling

🎬 <b>Kechgi tomosha takliflari:</b>
• 🌙 Kechgi melodramalar
• 🎭 Sarguzasht filmlari
• 📀 Klassik kinolar
• 🎞️ Oilaviy filmlar

🛌 <b>Uxlashdan oldingi odatlar:</b>
• 📖 Qur'on o'qing yoki ilmiy kitob o'qing
• 🤲 Ollohga shukr ayting
• 🧘 Bemorlar uchun duo o'qing
• 💭 Ijobiy fikrlash bilan kunni yakunlang

<b>🌜 Xayrli tun, sog'-salomat uxlashingizni tilaymiz! Ertaga yana yangi imkoniyatlar bilan uyg'aning! 🌛</b>

<i>#HayrliKech #XayrliTun #DamOlish</i>
"""
    
    async def check_and_send_messages(self):
        """Xabarlarni vaqtini tekshirish va yuborish"""
        try:
            message_data = await self.get_daily_message()
            if message_data:
                message_text = message_data["message"]
                current_time = self._get_tashkent_time().strftime('%H:%M')
                self.logger.info(f"🕒 Vaqt: {current_time} - Xabar yuborilmoqda...")
                
                success, failed = await self.send_message_to_all_users(message_text)
                
                self.logger.info(f"✅ Xabar yuborildi: {success} ta foydalanuvchiga")
                if failed > 0:
                    self.logger.warning(f"⚠️ {failed} ta foydalanuvchiga xabar yuborilmadi")
            
        except Exception as e:
            self.logger.error(f"Xabar yuborishda xatolik: {e}")
    
    async def start_scheduler(self):
        """Xabar yuborishni boshlash"""
        self.logger.info("🕒 Avtomatik xabar yuborish ishga tushdi...")
        
        while True:
            try:
                await self.check_and_send_messages()
                # Har 1 daqiqada tekshirish
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Scheduler xatoligi: {e}")
                await asyncio.sleep(60)