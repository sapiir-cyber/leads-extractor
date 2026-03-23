import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
from PIL import Image

# מפתח ה-API שלך
MY_API_KEY = "AIzaSyB4t7TkPwPdR_d5sBPPig6NuekB5yINzt4"

st.set_page_config(page_title="מחלץ לידים חכם", layout="wide")
st.title("מחלץ לידים מצילומי מסך 📥")

# אתחול ה-API
genai.configure(api_key=MY_API_KEY)

uploaded_files = st.file_uploader("גררי לכאן צילומי מסך", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

if st.button("התחל עיבוד") and uploaded_files:
    all_leads = []
    progress_bar = st.progress(0)
    
    # הגדרת המודל בגרסה הכי בסיסית ויציבה
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    for i, file in enumerate(uploaded_files):
        try:
            img = Image.open(file)
            
            # פרומפט פשוט וברור
            prompt = "Scan this chat. Return ONLY a JSON with: first_name, phone (no 972 prefix, start with 0), interest (write 'ארון' or 'מזרן')."
            
            response = model.generate_content([prompt, img])
            text = response.text.strip()
            
            # ניקוי סימני קוד מה-JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(text)
            all_leads.append(data)
            
        except Exception as e:
            st.warning(f"בעיה קלה בקובץ {file.name}, ממשיך הלאה...")
        
        progress_bar.progress((i + 1) / len(uploaded_files))

    if all_leads:
        df = pd.DataFrame(all_leads)
        # תיקון שמות עמודות והצגת הטבלה
        df.columns = ["שם פרטי", "טלפון", "התעניינות"]
        st.success("הצלחנו!")
        st.table(df) # שימוש ב-table פשוט במקום dataframe ליציבות
        
        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("הורד טבלה ל-Google Sheets", data=csv, file_name="leads.csv", mime="text/csv")
