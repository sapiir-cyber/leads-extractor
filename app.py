import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
from PIL import Image
import io

# ───────────────────────────────────────────────
#                הגדרות ראשוניות
# ───────────────────────────────────────────────

# NEVER commit your real API key to GitHub!
# Use st.secrets instead (create .streamlit/secrets.toml in your repo)
# Example secrets.toml:
# GOOGLE_API_KEY = "your-real-key-here"

try:
    MY_API_KEY = st.secrets["GOOGLE_API_KEY"]
except:
    MY_API_KEY = "AIzaSyB4t7TkPwPdR_d5sBPPig6NuekB5yINzt4"  # ← מחק את זה לפני העלאה לגיטהאב!

st.set_page_config(page_title="מחלץ לידים חכם 📥", layout="wide")
st.title("מחלץ לידים מצילומי מסך וואטסאפ")

genai.configure(api_key=MY_API_KEY)

# עדיף להשתמש ב-1.5-flash-8b אם יש לך גישה – מהיר וזול יותר
# אם אין – תשאיר gemini-1.5-flash
model = genai.GenerativeModel('gemini-1.5-flash')   # אפשר לנסות גם gemini-1.5-flash-8b-exp

# ───────────────────────────────────────────────
#               פרומפט משופר מאוד
# ───────────────────────────────────────────────

PROMPT = """
אתה עוזר חילוץ לידים מצילומי מסך של שיחות וואטסאפ בעברית.

חלץ מהתמונה **רק** את ההודעה האחרונה / הרלוונטית ביותר שמכילה פרטי ליד.

החזר **רק** JSON תקין בפורמט הבא, בלי שום טקסט נוסף לפני או אחרי:

{
  "first_name": "שם פרטי בעברית",
  "phone": "מספר טלפון שמתחיל ב-05 (בלי 972, בלי +, בלי רווחים או מקפים)",
  "interest": "ארון או מזרן או שניהם או ריק אם לא ברור"
}

חוקים חשובים:
- אם אין שם → "לא נמצא"
- אם אין טלפון תקין שמתחיל ב-05 → "לא נמצא"
- הסר כל קידומת 972 / +972 / 00972
- אם כתוב 058 → תשמור 058...
- interest חייב להיות אחד מ: "ארון", "מזרן", "ארון ומזרן", או מחרוזת ריקה ""
- אל תוסיף הסברים, אל תוסיף ```json, רק JSON נקי
"""

# ───────────────────────────────────────────────
#                   ממשק
# ───────────────────────────────────────────────

uploaded_files = st.file_uploader(
    "גרור/י לכאן צילומי מסך של שיחות (אפשר כמה)",
    accept_multiple_files=True,
    type=['png', 'jpg', 'jpeg']
)

if st.button("⚡ התחל עיבוד") and uploaded_files:

    all_leads = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, file in enumerate(uploaded_files):
        status_text.text(f"מעבד: {file.name} ({i+1}/{len(uploaded_files)})")

        try:
            # קוראים את התמונה כ-bytes → יותר יציב
            img_bytes = file.read()
            img = Image.open(io.BytesIO(img_bytes))

            response = model.generate_content([PROMPT, img])

            res_text = response.text.strip()

            # ניקוי מאוד אגרסיבי – Gemini לפעמים עדיין מוסיף דברים
            if res_text.startswith("```json"):
                res_text = res_text.split("```json", 1)[1].split("```", 1)[0]
            elif "```" in res_text:
                res_text = res_text.split("```", 1)[1].split("```", 1)[0]
            res_text = res_text.strip().removeprefix("json").strip()

            try:
                data = json.loads(res_text)
            except json.JSONDecodeError as json_err:
                st.warning(f"JSON לא תקין בקובץ {file.name}: {json_err}\n\nתוכן גולמי:\n{res_text}")
                continue

            # ולידציה בסיסית
            if "phone" in data and data["phone"] not in ["לא נמצא", ""]:
                if not data["phone"].startswith("05"):
                    data["phone"] = "פורמט לא תקין"

            all_leads.append(data)

        except Exception as e:
            st.error(f"שגיאה חמורה בקובץ {file.name}: {type(e).__name__} – {str(e)}")

        progress_bar.progress((i + 1) / len(uploaded_files))

    status_text.text("")

    if all_leads:
        df = pd.DataFrame(all_leads)

        column_map = {
            "first_name": "שם פרטי",
            "phone": "טלפון",
            "interest": "במה התעניינו"
        }
        df = df.rename(columns=column_map)

        st.success(f"העיבוד הסתיים – נמצאו {len(df)} לידים תקינים")
        st.dataframe(df, use_container_width=True, hide_index=True)

        # הורדה עם encoding לעברית
        csv = df.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
        st.download_button(
            label="הורד כקובץ CSV (מתאים ל-Google Sheets / Excel)",
            data=csv,
            file_name="לידים_מחולצים.csv",
            mime="text/csv"
        )
    else:
        st.warning("לא הצלחנו לחלץ אף ליד. נסי/ה תמונות יותר ברורות או פרומפט אחר.")
