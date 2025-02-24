import numpy as np
import cv2
from ultralytics import YOLO
import streamlit as st

# Streamlit UI
st.title("Aeroplanes Detection in Airport Imagery")
st.markdown("Real-time detection using webcam")

# Load the trained YOLO model
model = YOLO("best.pt")

# Session state for webcam control
if "webcam_active" not in st.session_state:
    st.session_state.webcam_active = False

start_button = st.button("Start Webcam")
stop_button = st.button("Stop Webcam")

# Create a placeholder for the video feed
video_placeholder = st.empty()

# Start webcam
if start_button:
    st.session_state.webcam_active = True

# Stop webcam
if stop_button:
    st.session_state.webcam_active = False

# Open webcam if the session state is active
if st.session_state.webcam_active:
    cap = cv2.VideoCapture(0)  # Use 1 for external webcam

    while cap.isOpened() and st.session_state.webcam_active:
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLO inference
        results = model(frame, conf=0.8)

        # Annotate the frame with detection results
        annotated_frame = results[0].plot()

        # Convert frame to RGB (Streamlit requires RGB format)
        annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

        # Display the frame in Streamlit
        video_placeholder.image(annotated_frame, channels="RGB", use_column_width=True)

        # Break loop when the stop button is pressed
        if not st.session_state.webcam_active:
            break

    cap.release()
    cv2.destroyAllWindows()
    video_placeholder.empty() 
