import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd

# הגדרות בסיסיות
st.set_page_config(page_title="מחלץ לידים", layout="wide")
st.title("מחלץ לידים מצילומי מסך 📥")

# מפתח ה-API שלך
genai.configure(api_key="AIzaSyB4t7TkPwPdR_d5sBPPig6NuekB5yINzt4")
model = genai.GenerativeModel('gemini-1.5-flash')

uploaded_files = st.file_uploader("העלי צילומי מסך", accept_multiple_files=True)

if st.button("התחל עיבוד") and uploaded_files:
    leads = []
    for file in uploaded_files:
        try:
            img = Image.open(file)
            # בקשה ברורה מה-AI
            prompt = "Extract from this image: Name, Phone (start with 0, no 972), and Interest (ארון/מזרן). Return as simple text: Name | Phone | Interest"
            response = model.generate_content([prompt, img])
            
            # עיבוד הטקסט שחזר
            row = response.text.strip().split("|")
            if len(row) >= 2:
                leads.append({
                    "שם": row[0].strip(),
                    "טלפון": row[1].strip(),
                    "התעניינות": row[2].strip() if len(row)>2 else "לא צוין"
                })
        except:
            st.error(f"שגיאה בקובץ {file.name}")

    if leads:
        df = pd.DataFrame(leads)
        st.table(df)
        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button("הורדה ל-Excel/CSV", data=csv, file_name="leads.csv")
