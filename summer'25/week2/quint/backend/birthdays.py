import streamlit as st
import pandas as pd
from datetime import datetime
from config.settings import LOCAL_CONTACTS_PATH
from backend.whatsapp import send_whatsapp

def load_contacts():
    return pd.read_csv(LOCAL_CONTACTS_PATH)

def check_today_birthdays(df):
    today = datetime.now().strftime("%m-%d")
    return df[df['dob'].str[5:] == today]

def render_birthday_ui(user):
    st.write(f"🎂 Checking birthdays for **{user}**")
    df = load_contacts()
    bdays = check_today_birthdays(df)

    if not bdays.empty:
        for _, row in bdays.iterrows():
            st.markdown(f"🎉 {row['name']} - {row['dob']}")
            if st.button(f"Wish {row['name']} via WhatsApp"):
                msg = f"Happy Birthday, {row['name']}! 🎉"
                send_whatsapp(row['phone'], msg)
    else:
        st.info("No birthdays today.")
