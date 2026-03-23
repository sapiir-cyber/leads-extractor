import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
from PIL import Image

# מפתח ה-API שלך
MY_API_KEY = "AIzaSyB4t7TkPwPdR_d5sBPPig6NuekB5yINzt4"

# הגדרות עמוד
st.set_page_config(page_title="מחלץ לידים חכם", layout="wide")
st.title("מחלץ לידים מצילומי מסך 📥")

# הגדרת ה-API בצורה מפורשת
try:
    genai.configure(api_key=MY_API_KEY)
    # שימוש בשם המודל המלא והמעודכן ביותר
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"שגיאה בהתחברות ל-AI: {e}")

uploaded_files = st.file_uploader("גררי לכאן צילומי מסך", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

if st.button("התחל עיבוד") and uploaded_files:
    all_leads = []
    progress_bar = st.progress(0)
    
    for i, file in enumerate(uploaded_files):
        try:
            # פתיחת תמונה בצורה יציבה
            img = Image.open(file)
            
            # הנחיה מדויקת כולל דרישה לניקוי 972
            prompt = """
            Look at this WhatsApp screenshot and extract:
            1. first_name: The person's name.
            2. phone: The phone number. REMOVE '972' prefix if exists. Must start with '05'.
            3. interest: If they asked about a closet, write 'ארון'. If mattress, write 'מזרן'.
            
            Return ONLY a valid JSON object like this:
            {"first_name": "ישראל", "phone": "0501234567", "interest": "ארון"}
            """
            
            # שליחה למודל
            response = model.generate_content([prompt, img])
            
            # ניקוי הטקסט מהתשובה (הסרת סימני קוד אם יש)
            res_text = response.text.strip()
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            elif "```" in res_text:
                res_text = res_text.split("```")[1].split("```")[0].strip()
            
            # המרה לנתונים
            data = json.loads(res_text)
            all_leads.append(data)
            
        except Exception as e:
            st.error(f"שגי
