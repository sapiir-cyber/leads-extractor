import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
from PIL import Image

# מפתח ה-API שלך
MY_API_KEY = "AIzaSyB4t7TkPwPdR_d5sBPPig6NuekB5yINzt4"

st.set_page_config(page_title="מחלץ לידים חכם", layout="wide")
st.title("מחלץ לידים מצילומי מסך 📥")

# הגדרה בטוחה של המודל
genai.configure(api_key=MY_API_KEY)

def get_model():
    # ניסיון להשתמש בשם המודל הבטוח ביותר לגרסה הזו
    return genai.GenerativeModel('gemini-1.5-flash')

uploaded_files = st.file_uploader("גררי לכאן צילומי מסך", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

if st.button("התחל עיבוד") and uploaded_files:
    all_leads = []
    progress_bar = st.progress(0)
    model = get_model()
    
    for i, file in enumerate(uploaded_files):
        try:
            img = Image.open(file)
            
            prompt = """
            Extract:
            1. first_name: Name
            2. phone: Number (remove 972, start with 05)
            3. interest: 'ארון' or 'מזרן'
            Return ONLY JSON.
            """
            
            # שליחה ישירה ללא הגדרות גרסה מיותרות
            response = model.generate_content([prompt, img])
            res_text = response.text.strip()
            
            if "```json" in res_text:
                res_text = res_text.split("```json")[1].split("```")[0].strip()
            elif "```" in res_text:
                res_text = res_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(res_text)
            all_leads.append(data)
            
        except Exception as e:
            # הצגת השגיאה בצורה נקייה
            st.warning(f"דילגתי על קובץ {file.name} בגלל בעיה טכנית במודל.")
        
        progress_bar.progress((i + 1) / len(uploaded_files))

    if all_leads:
        df = pd.DataFrame(all_leads)
        df = df.rename(columns={"first_name": "שם פרטי", "phone": "טלפון", "interest": "במה התעניינו"})
        st.success("העיבוד הושלם!")
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("הורד טבלה ל-Google Sheets", data=csv, file_name="leads_list.csv", mime="text/csv")
    else:
        st.error("לא הצלחנו לחלץ נתונים. וודאי שמפתח ה-API תקין ושהתמונות ברורות.")
