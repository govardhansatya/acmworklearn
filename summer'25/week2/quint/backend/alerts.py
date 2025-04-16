import streamlit as st
from datetime import datetime
from data.db import SessionLocal
from data.schemas import Alert

def render_alert_ui(user):
    db = SessionLocal()
    st.text_input("Reminder Message", key="reminder_msg")
    st.time_input("Trigger Time", key="trigger_time")

    if st.button("Add Alert"):
        new_alert = Alert(
            user=user,
            message=st.session_state.reminder_msg,
            trigger_time=str(st.session_state.trigger_time)
        )
        db.add(new_alert)
        db.commit()
        st.success("Alert set!")

    st.markdown("---")
    st.subheader("Your Alerts:")
    alerts = db.query(Alert).filter(Alert.user == user).all()
    for alert in alerts:
        st.write(f"⏰ {alert.trigger_time} → {alert.message}")
