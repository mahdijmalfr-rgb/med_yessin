import streamlit as st
from textblob import TextBlob
from deep_translator import GoogleTranslator
import requests
from datetime import datetime
import nltk
from langdetect import detect

# تحميل متطلبات NLTK
nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)
nltk.download('brown', quiet=True)
nltk.download('averaged_perceptron_tagger', quiet=True)

# إعداد واجهة الصفحة
st.set_page_config(page_title="المعلم - AI Assistant")

class SmartAnalyticBot:
    def __init__(self):
        """إعداد المتغيرات الأساسية للبوت"""
        self.bot_name = "🤖 AI Assistant"
        self.trigger_words = ['traduire', 'translate', 'ترجم']
        self.exit_words = ['exit', 'quit', 'خروج']
        self.log_file = "chat_history.txt"
        self.info_triggers = ['recherche', 'search','ابحث', 'معلومة', 'بحث']
        
    def clean_command_words(self, text, triggers):
        """دالة مخصصة لحذف كلمات الأوامر وعلامات الترقيم من النص"""
        clean_text = text
        for word in triggers:
            clean_text = clean_text.replace(word, "")
        return clean_text.replace(":", "").strip()

    def fix_arabic_text(self, text):
        """إصلاح اتجاه النص العربي (غير ضروري غالباً في Streamlit لكن تُركت كدالة)"""
        return text

    def get_sentiment_label(self, score):
        """تحليل نتيجة المشاعر"""
        if score > 0:
            return "good 😊"
        elif score < 0:
            return "oh no ☹️"
        return "ok 😐"

    def save_to_log(self, original, corrected, keywords, sentiment):
        """حفظ تفاصيل المحادثة في الذاكرة الخارجية"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(self.log_file, "a", encoding="utf-8") as file:
                file.write(f"Time: {current_time}\n")
                file.write(f"Original Text: {original}\n")
                file.write(f"Corrected Text: {corrected}\n")
                file.write(f"Keywords Found: {keywords}\n")
                file.write(f"Sentiment Analysis: {sentiment}\n")
                file.write("-" * 40 + "\n")
        except Exception as e:
            print(f"Error saving log: {e}")

    def fetch_internet_info(self, query):
        """دالة للبحث وجلب المعلومات من ويكيبيديا"""
        headers = {'User-Agent': 'MySmartBot/1.0'}
        query = query.strip()
        if not query:
            return "يرجى كتابة كلمة للبحث عنها."

        url_en = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        url_ar = f"https://ar.wikipedia.org/api/rest_v1/page/summary/{query}"
        url_fr = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{query}"
        
        try:
            is_arabic = any("\u0600" <= char <= "\u06FF" for char in query)
            if is_arabic:
                response = requests.get(url_ar, headers=headers, timeout=5)
            else:
                try:
                    user_lang = detect(query)
                except:
                    user_lang = 'en'
                
                if user_lang == 'ar':
                    response = requests.get(url_ar, headers=headers, timeout=5)
                elif user_lang == 'fr':
                    response = requests.get(url_fr, headers=headers, timeout=5)
                else:
                    response = requests.get(url_en, headers=headers, timeout=5)
                
            if response.status_code == 200:
                data = response.json()
                return data.get("extract", "لا يوجد ملخص متاح.")
            else:
                return "لم يتم العثور على مقال بهذا الاسم."
                
        except Exception as e:
            return f"حدث خطأ في الاتصال: {e}"
        
    def process_message(self, raw_input):
        """الدالة الرئيسية لمعالجة الأوامر"""
        reponse = ""
        user_input = raw_input.lower()
         
        # شرط الخروج
        if user_input in self.exit_words:
            return f"\n{self.bot_name}: وداعاً! تم حفظ سجل المحادثة بنجاح. 👋"

        blob = TextBlob(user_input)
        corrected_text = str(blob.correct())
        corrected_blob = TextBlob(corrected_text)
        
        reponse += "-" * 40 + "\n\n"
        
        # 1. حالة البحث
        if any(word in user_input for word in self.info_triggers):
            trigger_words = ['info', 'search', 'بحث', 'معلومة','ابحث' , 'recherche']
            info_result2 = user_input
            
            for word in trigger_words:
                info_result2 = info_result2.replace(word, "")

            info_result2 = info_result2.strip() 
            reponse += f"🌐 **جاري البحث في الإنترنت عن:** [{info_result2}] ...\n\n"
            info_result = self.fetch_internet_info(info_result2)
            reponse += f"📚 **النتيجة:** {info_result}\n"
            
        # 2. حالة الترجمة
        elif any(word in user_input for word in self.trigger_words):
            clean_text = self.clean_command_words(corrected_text, self.trigger_words)
            sentiment_type = "Translate"
            try:
                translated = GoogleTranslator(source='auto', target='ar').translate(clean_text)
                reponse += f"🔤 **{sentiment_type}** | {translated}\n"
            except Exception as e:
                reponse += "❌ عذراً، حدث خطأ في الاتصال بخدمة الترجمة.\n"
                
        # 3. حالة الدردشة العادية (تحليل المشاعر)
        else:
            score = corrected_blob.sentiment.polarity
            sentiment_type = self.get_sentiment_label(score)
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
                
        return reponse

# ----------------- تشغيل واجهة Streamlit -----------------
if __name__ == "__main__":
    bot = SmartAnalyticBot()
    
    # الترحيب الافتراضي
    welcome_msg = """
    ==================================================
    **AI Assistant:** Welcome to the organized version with external memory!
    ==================================================
    """
    st.title("المعلم")
    st.markdown(welcome_msg)
    
    # مربع الإدخال
    raw_input = st.text_input("اكتب سؤالك أو الأمر هنا (مثال: search Tunisia أو translate hello)")
    
    # التنفيذ وعرض النتيجة
    if raw_input:
        final_response = bot.process_message(raw_input)
        st.write(final_response)

