import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
from PIL import Image

# המפתח שלך
MY_API_KEY = "AIzaSyB4t7TkPwPdR_d5sBPPig6NuekB5yINzt4"

st.set_page_config(page_title="מחלץ לידים חכם", layout="wide")
st.title("מחלץ לידים מצילומי מסך 📥")

# הגדרת ה-API
genai.configure(api_key=MY_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_files = st.file_uploader("גררי לכאן צילומי מסך", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

if st.button("התחל עיבוד") and uploaded_files:
    all_leads = []
    progress_bar = st.progress(0)
    
    for i, file in enumerate(uploaded_files):
        try:
            # פתיחת התמונה באמצעות ספריית PIL - זה פותר המון בעיות תאימות
            img = Image.open(file)
            
            prompt = """
            Scan this image and extract:
            1. first_name: The person's name.
            2. phone: The phone number. REMOVE the '972' prefix if it exists. Ensure it starts with 0.
            3. interest: If they mention 'ארון' write 'ארון', if 'מזרן' write 'מזרן'.
            
            Return ONLY a JSON object.
            """
            
            # שליחה למודל בפורמט היציב ביותר
            response = model.generate_content([prompt, img])
            
            # חילוץ הטקסט הנקי
            raw_text = response.text.strip()
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(raw_text)
            all_leads.append(data)
            
        except Exception as e:
            st.error(f"שגיאה בעיבוד {file.name}: {str(e)}")
        
        progress_bar.progress((i + 1) / len(uploaded_files))

    if all_leads:
        df = pd.DataFrame(all_leads)
        # וידוא שמות עמודות
        df.columns = ["שם פרטי", "טלפון", "במה התעניינו"]
        st.success("העיבוד הושלם!")
        st.dataframe(df, use_container_width=True)
        
        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("הורד טבלה ל-Google Sheets", data=csv, file_name="leads_list.csv", mime="text/csv")
