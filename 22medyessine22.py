import streamlit as st
from textblob import TextBlob
from deep_translator import GoogleTranslator
import requests
from datetime import datetime
import nltk
from langdetect import detect
from gnews import GNews


# ⬅️ التغيير 1: إضافة quiet=True لمنع مكتبة NLTK من طباعة رسائل التحميل في واجهة المستخدم
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('brown', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# ⬅️ التغيير 2: نقل إعداد الصفحة (set_page_config) ليكون في الأعلى خارج الـ Class
st.set_page_config(page_title="المعلم - AI Assistant")

class SmartAnalyticBot:
    def __init__(self):
        """إعداد المتغيرات الأساسية للبوت"""
        self.bot_name = "🤖 AI Assistant"
        self.trigger_words = ['traduire', 'translate', 'ترجم']
        self.exit_words = ['exit', 'quit', 'خروج']
        self.log_file = "chat_history.txt"
        self.info_triggers = ['recherche','ابحث', 'search', 'معلومة', 'بحث']
        
        # ⬅️ التغيير 3: مسح المتغيرات (reponse1, user_input) من هنا لأنها كانت فارغة ولا داعي لتعريفها في دالة التهيئة (__init__)

    def clean_command_words(self, text, triggers):
        """دالة مخصصة لحذف كلمات الأوامر وعلامات الترقيم من النص"""
        # ⬅️ التغيير 4: إصلاح المنطق البرمجي للدالة؛ تعريف clean_text أولاً ثم استبدال الكلمات، وإضافة () للـ strip في النهاية
        clean_text = text
        for word in triggers:
            clean_text = clean_text.replace(word, "")
        return clean_text.replace(":", "").strip()

    def fix_arabic_text(self, text):
        return text

    def get_sentiment_label(self, score):
        if score > 0:
            return "good 😊"
        elif score < 0:
            return "oh no ☹️"
        return "ok 😐"

    def save_to_log(self, original, corrected, keywords, sentiment):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try: # ⬅️ التغيير 5: وضع كود الحفظ داخل try/except لحماية التطبيق من التوقف إذا فشل فتح ملف الذاكرة
            with open(self.log_file, "a", encoding="utf-8") as file:
                file.write(f"Time: {current_time}\n")
                file.write(f"Original Text: {original}\n")
                file.write(f"Corrected Text: {corrected}\n")
                file.write(f"Keywords Found: {keywords}\n")
                file.write(f"Sentiment Analysis: {sentiment}\n")
                file.write("-" * 40 + "\n")
        except Exception as e:
            print(f"Error saving log: {e}")

    def detect_language(self, user_input):
        """تحديد اللغة بناءً على كلمة الأمر التي كتبها المستخدم"""
        if any(w in user_input for w in ['recherche']):
            return 'fr'
        elif any(w in user_input for w in ['ابحث', 'بحث', 'معلومة']):
            return 'ar'
        else:
            return 'en'  # لـ 'search' أو 'info' أو أي حالة أخرى
    def new_info(self, query,user_lang):
        try:

        
            google_news = GNews(language= user_lang)
            news = google_news.get_news (query.strip())

            if not news:
                return []
        
            results = []
            for n in news[:5]:
                results=results.append((n['title'], n['url']))
            return results
        
        except Exception as e:
            return f"حدث خطأ أثناء جلب الأخبار: {e}"
    def fetch_internet_info(self, query, user_lang):
        headers = {'User-Agent': 'MySmartBot/1.0'}
        query = query.strip()
        if not query:
            return "يرجى كتابة كلمة للبحث عنها."

        url_en = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        url_ar = f"https://ar.wikipedia.org/api/rest_v1/page/summary/{query}"
        url_fr = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{query}"

        if user_lang == 'ar':
            response = requests.get(url_ar, headers=headers, timeout=5)
        elif user_lang == 'fr':
            
            response =requests.get(url_fr, headers=headers, timeout=5)
        else:
            response =requests.get(url_en, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return data.get("extract", "لا يوجد لخص متاح.")
        else:
            return""
    def word_info(self, query, user_lang):
        headers = {'User-Agent': 'MySmartBot/1.0'}
        query = query.strip()
        try:
            urll = f"https://{user_lang}.wiktionary.org/api/rest_v1/page/definition/{query}"
            response = requests.get(urll, headers=headers, timeout=5)  # حذفنا params
            if response.status_code == 200:
                data = response.json()
                return data.get("extract", "لا يوجد ملخص متاح.")# لاحظ: هذا الـ API بيرجع شكل مختلف عن wikipedia، لازم تتأكد منه لاحقًا
            else:
                return "لم يتم العثور على معنى لهذه الكلمة."
        except Exception as e:
            return f"حدث خطأ في الاتصال: {e}"
    
        
    def process_message(self, raw_input):
        reponse = ""
        user_input = raw_input.lower()
        user_lang = self.detect_language(user_input)

        if user_input in self.exit_words:
            # ⬅️ التغيير 6: جعل الدالة تعيد (return) النص بدلاً من إضافته للمتغير فقط
            return f"\n{self.bot_name}: وداعاً! تم حفظ سجل المحادثة بنجاح. 👋"

        blob = TextBlob(user_input)
        corrected_text = str(blob.correct())
        corrected_blob = TextBlob(corrected_text)
        
        reponse += "-" * 40 + "\n\n"
        
        if any(word in user_input for word in self.info_triggers):
            trigger_words = ['la ', 'le ', "l'", 'les ','info', 'search' ,'بحث', 'معلومة' ,'ابحث','recherche']
            # ⬅️ التغيير 7: تعريف المتغير info_result2 وإعطائه قيمة الإدخال قبل بدء حلقة الاستبدال لمنع خطأ (UnboundLocalError)
            info_result2 = user_input 
            for word in trigger_words:
                info_result2 = info_result2.replace(word, "")
            
                    
            info_result2 = info_result2.strip() 
            reponse += f"🌐 **جاري البحث في الإنترنت عن:** [{info_result2}] ...\n\n"
            info_result = self.word_info(info_result2,user_lang )
            info_result += self.fetch_internet_info(info_result2,user_lang )
            news_results = self.new_info(info_result2, user_lang)
            if isinstance(news_results, list) and news_results:
                for title, url in news_results:
                    info_result+= f"📰 {title}\n🔗 {url}\n\n"
            else:
                info_result += "لم يتم العثور على أخبار.\n"
            reponse += f"📚 **النتيجة:** {info_result}\n"
            
        elif any(word in user_input for word in self.trigger_words):
            # ⬅️ التغيير 8: تمرير متغير الكلمات المفتاحية (self.trigger_words) للدالة لتعرف ماذا تحذف
            clean_text = self.clean_command_words(corrected_text, self.trigger_words)
            sentiment_type = "Translate"
            try:
                translated = GoogleTranslator(source='auto', target='ar').translate(clean_text)
                reponse += f"🔤 **{sentiment_type}** | {translated}\n"
            except Exception as e:
                reponse += "❌ عذراً، حدث خطأ في الاتصال بخدمة الترجمة.\n"
                
        else:
            score = corrected_blob.sentiment.polarity
            sentiment_type = self.get_sentiment_label(score)
            
            # ⬅️ التغيير 9: تنسيق المتغيرات داخل النص باستخدام f-string لتبدو أجمل مثل {score:.2f} لتقليل الأرقام العشرية
            if score < 0:
                reponse += f"**{sentiment_type}**, but why that? (Score: {score:.2f})\n\n"
            elif score > 0:
                reponse += f"**{sentiment_type}**, tell me more about that! (Score: {score:.2f})\n\n"
            else:
                reponse += f"**{sentiment_type}**, ok. (Score: {score:.2f})\n\n"
                    
            joined_nouns = ", ".join(corrected_blob.noun_phrases)
            self.save_to_log(raw_input, corrected_text, joined_nouns, sentiment_type)
            
            if user_input != corrected_text:
                reponse += f"🔧 **التصحيح المقترح:** {corrected_text}\n\n"
                
            if joined_nouns:
                reponse += f"🔑 **Bot:** Oh, so you are talking about ({joined_nouns})?\n"
            else:
                reponse += "🔑 **Bot:** I couldn't capture specific keywords, but I'm listening!\n"
                
        # ⬅️ التغيير 10: الدالة تعيد الجواب الكامل ليتم طباعته لاحقاً في Streamlit
        return reponse

# ----------------- تشغيل واجهة Streamlit -----------------
if __name__ == "__main__":
    bot = SmartAnalyticBot()
    
    # ⬅️ التغيير 11: استخدام st.markdown لعرض رسالة الترحيب بشكل أنيق
    welcome_msg = """==================================================
    welcome in my project!!
    ================================================== """ 
   
   
    st.title("المعلم")
    st.chat_message("bot").markdown(welcome_msg)
    
    raw_input = st.chat_input("اكتب سؤالك أو الأمر هنا (مثال: search Tunisia أو translate hello)")
    st.chat_message("user").markdown(raw_input)
    if raw_input:
        # ⬅️ التغيير 12: استقبال النتيجة المعادة (return) من الدالة وعرضها في الشاشة باستخدام st.write
        final_response = bot.process_message(raw_input)
        st.chat_message("bot").markdown(final_response)
            
