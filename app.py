import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
from PIL import Image

# מפתח ה-API שלך
MY_API_KEY = "AIzaSyB4t7TkPwPdR_d5sBPPig6NuekB5yINzt4"

st.set_page_config(page_title="מחלץ לידים חכם", layout="wide")
st.title("מחלץ לידים מצילומי מסך 📥")

genai.configure(api_key=MY_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_files = st.file_uploader("גררי לכאן צילומי מסך", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

if st.button("התחל עיבוד") and uploaded_files:
    all_leads = []
    progress_bar = st.progress(0)
    
    for i, file in enumerate(uploaded_files):
        try:
            img = Image.open(file)
            
            prompt = """
            Extract from this chat:
            1. first_name: Name
            2. phone: Number (remove 972, must start with 05)
            3. interest: 'ארון' or 'מזרן'
            Return ONLY JSON.
            """
            
            response = model.generate_content([prompt, img])
            res_text = response.text.strip()
            
            # ניקוי תגיות קוד
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            elif "```" in res_text:
                res_text = res_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(res_text)
            all_leads.append(data)
            
        except Exception as e:
            # כאן התיקון - זה יציג לנו מה הבעיה האמיתית
            st.error(f"שגיאה בקובץ {file.name}: {str(e)}")
        
        progress_bar.progress((i + 1) / len(uploaded_files))

    if all_leads:
        df = pd.DataFrame(all_leads)
        # מיפוי עמודות לעברית
        column_map = {"first_name": "שם פרטי", "phone": "טלפון", "interest": "במה התעניינו"}
        df = df.rename(columns=column_map)
        
        st.success("העיבוד הושלם!")
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("הורד טבלה ל-Google Sheets", data=csv, file_name="leads_list.csv", mime="text/csv")
    else:
        st.warning("לא הצלחנו לחלץ נתונים מאף קובץ. נסי להעלות תמונה ברורה יותר של הצ'אט.")
