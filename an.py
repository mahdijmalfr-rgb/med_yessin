import random
from textblob import TextBlob
from deep_translator import GoogleTranslator
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
import wikipedia
from tkinter import *
root=Tk()
root.geometry("400x500")
root.title("ai mohamed yessine")
lbe1=Label(root)
txt=Text(root)
lbe1.pack
txt.pack
root=mainloop()
class SmartAnalyticBot:
    def __init__(self):
        """إعداد المتغيرات الأساسية للبوت"""
        self.bot_name = "🤖 AI Assistant"
        self.trigger_words = ['traduire', 'translate', 'ترجم']
        self.exit_words = ['exit', 'quit', 'خروج']
        self.log_file = "chat_history.txt"  # اسم ملف الذاكرة
        self.info_triggers = ['info', 'search', 'معلومة', 'بحث']

    def clean_command_words(self, text, triggers=None):
        """دالة مخصصة لحذف كلمات الأوامر وعلامات الترقيم من النص"""
        if triggers is None:
            triggers = self.trigger_words
        clean_text = text
        for word in triggers:
            clean_text = clean_text.replace(word, "")
        return clean_text.replace(":", "").strip()

    def fix_arabic_text(self, text):
        """دالة مخصصة لإصلاح الحروف العربية المفتتة والاتجاه المعكوس"""
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)

    def get_sentiment_label(self, score):
        """دالة مخصصة لتحليل نتيجة المشاعر وإعطاء الوصف المناسب"""
        if score > 0:
            return "good 😊"
        elif score < 0:
            return "oh no ☹️"
        return "ok 😐"

    def save_to_log(self, original, corrected, keywords, sentiment):
        """دالة مخصصة لحفظ تفاصيل كل دورة في ملف نصي خارجي (الذاكرة)"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(f"Time: {current_time}\n")
            file.write(f"Original Text: {original}\n")
            file.write(f"Corrected Text: {corrected}\n")
            file.write(f"Keywords Found: {keywords}\n")
            file.write(f"Sentiment Analysis: {sentiment}\n")
            file.write("-" * 40 + "\n")

    def fetch_internet_info(self, query):
        """دالة جديدة مخصصة للبحث وجلب المعلومات من الإنترنت"""
        try:
            # البحث باللغة العربية أولاً، وإذا لم يجد يبحث بالفرنسية/الإنجليزي تلقائياً
            wikipedia.set_lang("fr")  # ضبطنا البحث على الفرنسية والإنجليزية بدقة
            summary = wikipedia.summary(query, sentences=2)
            return summary
        except wikipedia.exceptions.PageError:
            try:
                wikipedia.set_lang("ar")
                summary = wikipedia.summary(query, sentences=2)
                return self.fix_arabic_text(summary)
            except Exception:
                return f"عذراً، لم أجد أي معلومات عن هذا الموضوع."
        except Exception:
            return "❌ حدث خطأ أثناء الاتصال بالإنترنت."

    def start_conversation(self):
        """الدالة الرئيسية التي تدير المحادثة بالكامل (Chat Loop)"""
        print("=" * 50)
        print(f"{self.bot_name}:Welcome to the organized version with external memory!")
        print("=" * 50)
        while True:
            # استقبال النص
            raw_input = input("\n👤 You: ").strip()
            user_input = raw_input.lower()
            score = corrected_blob.sentiment.polarity
            sentiment_type = self.get_sentiment_label(score)
            joined_nouns = ", ".join(corrected_blob.noun_phrases) 
            # شرط الخروج
            if user_input in self.exit_words:
                print(f"\n{self.bot_name}: وداعاً! تم حفظ سجل المحادثة بنجاح. 👋")
                break
                
            if not user_input:
                continue

            # معالجة النص وتصحيحه عبر TextBlob
            blob = TextBlob(user_input)
            corrected_text = str(blob.correct())
            corrected_blob = TextBlob(corrected_text)
            
            print("-" * 40)

            # 1. طباعة التصحيح الإملائي
            if user_input != corrected_text:
                print(f"🔧 التصحيح المقترح: {corrected_text}")

            if any(word in user_input for word in self.info_triggers):
                search_query = user_input
                print(f"🌐 جاري البحث في الإنترنت عن: [{search_query}] ...")
                info_result = self.fetch_internet_info(search_query)
                info_result2 = info_result.replace("info", " ")
                print(f"📚 النتيجة: {info_result2}")

            # 3. حساب المشاعر
            
        

                 # 4. فحص شرط الترجمة والتعامل معه
            elif any(word in user_input for word in self.trigger_words):
                clean_text = self.clean_command_words(corrected_text)
                clean_text2 = clean_text  # استخدام النص المنظف من كلمات الأمر
               
                try:
                    translated = GoogleTranslator(source='auto', target='ar').translate(clean_text2)
                    fixed_arabic = self.fix_arabic_text(translated)
                    print(f" {sentiment_type} |  {fixed_arabic}")
                except Exception:
                    print("❌ عذراً، حدث خطأ في الاتصال بخدمة الترجمة.")
            else:
                if score < 0:
                    print(f" {sentiment_type} ,but why that(Score: {score})")
                elif score > 0:
                    print(f" {sentiment_type} , tell me more about that(Score: {score})")
                else:
                    print(f" {sentiment_type} ,ok (Score: {score})")
                
                # 2. استخراج الكلمات المفتاحية
                if joined_nouns != "None":
                    print(f"🔑 Bot: Oh, so you are talking about ({joined_nouns})?")
                else:
                    print("🔑 Bot: I couldn't capture specific keywords, but I'm listening!")   

            # 5. استدعاء دالة حفظ الذاكرة
            self.save_to_log(raw_input, corrected_text, joined_nouns, sentiment_type)

            print("-" * 40)

if __name__ == "__main__":
    bot = SmartAnalyticBot()
    bot.start_conversation()
