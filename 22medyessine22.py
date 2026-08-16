import streamlit as st
from textblob import TextBlob
from deep_translator import GoogleTranslator
import requests
from bidi.algorithm import get_display
from datetime import datetime
import socket
import nltk
from langdetect import detect

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('brown')
nltk.download('averaged_perceptron_tagger')
user_input = ""
st.set_page_config(page_title="ai med yessine")
class SmartAnalyticBot:
    def __init__(self):
       # """إعداد المتغيرات الأساسية للبوت"""
        self.bot_name = "🤖 AI Assistant"
        self.trigger_words = ['traduire', 'translate', 'ترجم']
        self.exit_words = ['exit', 'quit', 'خروج']
        self.log_file = "chat_history.txt"  # اسم ملف الذاكرة
        self.info_triggers = ['info', 'search', 'معلومة', 'بحث']
        reponse = ""
        reponse1 = ""
        user_input = ""
        
        
    def clean_command_words(self, text, triggers=None):
        #"""دالة مخصصة لحذف كلمات الأوامر وعلامات الترقيم من النص"""
        if triggers is None:
            triggers = self.trigger_words
        clean_text = text
        for word in triggers:
            clean_text = clean_text.replace(word, "")
        return clean_text.replace(":", "").strip()

    def fix_arabic_text(self, text):
        #"""دالة مخصصة لإصلاح الحروف العربية المفتتة والاتجاه المعكوس"""
        #reshaped_text = arabic_reshaper.reshape(text)
        #return get_display(reshaped_text)
        return text
    def get_sentiment_label(self, score):
        #"""دالة مخصصة لتحليل نتيجة المشاعر وإعطاء الوصف المناسب"""
        if score > 0:
            return "good 😊"
        elif score < 0:
            return "oh no ☹️"
        return "ok 😐"

    def save_to_log(self, original, corrected, keywords, sentiment):
        #"""دالة مخصصة لحفظ تفاصيل كل دورة في ملف نصي خارجي (الذاكرة)"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(f"Time: {current_time}\n")
            file.write(f"Original Text: {original}\n")
            file.write(f"Corrected Text: {corrected}\n")
            file.write(f"Keywords Found: {keywords}\n")
            file.write(f"Sentiment Analysis: {sentiment}\n")
            file.write("-" * 40 + "\n")

    

    def fetch_internet_info(self, query):
        #"""دالة جديدة مخصصة للبحث وجلب المعلومات من الإنترنت"""
        
        headers = {
            'User-Agent': 'MySmartBot/1.0 (Contact: example@email.com)'
        }
        
        # تنظيف الكلمة لتفادي أخطاء اللغة
        query = query.strip()
        if not query:
            return "يرجى كتابة كلمة للبحث عنها."

        # روابط API لويكيبيديا
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
        url2 = f"https://ar.wikipedia.org/api/rest_v1/page/summary/{query}"
        url3 = f"https://fr.wikipedia.org/api/rest_v1/page/summary/{query}"
        
        try:
            # حماية دالة اكتشاف اللغة
            try:
                user_lang = detect(query)
            except:
                user_lang = 'en' # لغة افتراضية عند الفشل
                
            if user_lang == 'ar':
                response = requests.get(url2, headers=headers, timeout=5)
            elif user_lang == 'fr':
                response = requests.get(url3, headers=headers, timeout=5)
            else:
                response = requests.get(url, headers=headers, timeout=5)
                
            # إرجاع النتيجة بشكل صحيح
            if response.status_code == 200:
                data = response.json()
                return data.get("extract", "لا يوجد ملخص متاح.")
            else:
                return "لم يتم العثور على مقال بهذا الاسم."
                
        except Exception as e:
            return f"حدث خطأ: {e}"
        
    def process_message(self, raw_input):
        reponse=""

        #"""الدالة الرئيسية التي تدير المحادثة بالكامل (Chat Loop)"""
        
        # استقبال النص
        
        user_input = raw_input.lower()
        
         
        # شرط الخروج
        if user_input in self.exit_words:
            reponse +=(f"\n{self.bot_name}: وداعاً! تم حفظ سجل المحادثة بنجاح. 👋")
            self.start_conversation=False
        if not user_input:
            self.start_conversation=True
        # معالجة النص وتصحيحه عبر TextBlob
        blob = TextBlob(user_input)
        corrected_text = str(blob.correct())
        corrected_blob = TextBlob(corrected_text)
        
        reponse +=("-" * 40)
        # 1. طباعة التصحيح الإملائي
        
        if any(word in user_input for word in self.info_triggers):
            search_query = user_input.replace("search"," ")
            reponse +=(f"🌐 جاري البحث في الإنترنت عن: [{search_query}] ...")
            info_result = self.fetch_internet_info(search_query)
            info_result2 = info_result.replace("info", " ")
            reponse +=(f"📚 النتيجة: {info_result2}")
        # 3. حساب المشاعر
        
    
             # 4. فحص شرط الترجمة والتعامل معه
        elif any(word in user_input for word in self.trigger_words):
            clean_text = self.clean_command_words(corrected_text)
            clean_text2 = clean_text  # استخدام النص المنظف من كلمات الأمر
            sentiment_type = "Translate"
            try:
                translated = GoogleTranslator(source='auto', target='ar').translate(clean_text2)
                fixed_arabic = self.fix_arabic_text(translated)
                reponse +=(f" {sentiment_type} |  {fixed_arabic}")
            except Exception as e:
                print(f"DEBUG Translation Error: {e}")
                reponse +=("❌ عذراً، حدث خطأ في الاتصال بخدمة الترجمة.")
        else:
            score = corrected_blob.sentiment.polarity
            sentiment_type = self.get_sentiment_label(score)
            if score < 0:
                reponse +=(f" {sentiment_type} ,but why that(Score: {score})")
            elif score > 0:
                reponse +=(f" {sentiment_type} , tell me more about that(Score: {score})")
            else:
                reponse +=(f" {sentiment_type} ,ok (Score: {score})")
                    
            joined_nouns = ", ".join(corrected_blob.noun_phrases)
            self.save_to_log(raw_input, corrected_text, joined_nouns, sentiment_type)
            if user_input != corrected_text:
                reponse +=(f"🔧 التصحيح المقترح: {corrected_text}")
            # 2. استخراج الكلمات المفتاحية
            if joined_nouns :
                reponse +=(f"🔑 Bot: Oh, so you are talking about ({joined_nouns})?")
            else:
                reponse +=("🔑 Bot: I couldn't capture specific keywords, but I'm listening!")   
        # 5. استدعاء دالة حفظ الذاكرة
        return reponse
    # ربط زر Enter بالدالة
    
if __name__ == "__main__":
    bot = SmartAnalyticBot()
    reponse1=""
    reponse1 +=("=" * 50)
    reponse1 +=(f"ai medyessine:Welcome to the organized version with external memory!")
    reponse1 +=("=" * 50)
    st.title("المعلم")

    # شاشة العرض
    
    st.write(reponse1)
    # دالة زر Enter
    raw_input = st.text_input("اكتب سؤالك أو الأمر هنا (مثال: search او translate ثم اكمل الجملة)")
    

    # 2. التحقق والتنفيذ
    if raw_input:
        result = bot.process_message(raw_input)
        st.write(result)  # 👈 طباعة متغير result الصحيح
