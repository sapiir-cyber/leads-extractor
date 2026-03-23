import streamlit as st
import google.generativeai as genai
import pandas as pd
import json

# הגדרת ה-API Key שלך מראש
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
            prompt = "Extract name, phone (no 972), and interest (closet/mattress) as JSON: first_name, phone, interest."
            img_data = {"mime_type": "image/jpeg", "data": file.getvalue()}
            response = model.generate_content([prompt, img_data])
            
            res_text = response.text.replace("```json", "").replace("```", "").strip()
            data = json.loads(res_text)
            all_leads.append(data)
        except:
            st.error(f"שגיאה בקובץ {file.name}")
        
        progress_bar.progress((i + 1) / len(uploaded_files))

    if all_leads:
        df = pd.DataFrame(all_leads)
        df.columns = ["שם פרטי", "טלפון", "במה התעניינו"]
        st.dataframe(df)
        
        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("הורד טבלה ל-Google Sheets", data=csv, file_name="leads.csv", mime="text/csv")
