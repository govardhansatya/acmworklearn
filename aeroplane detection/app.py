import numpy as np
import cv2
from ultralytics import YOLO
import streamlit as st
# Load the trained YOLO model
st.title("aer0planes detection in airport imagery")
st.markdown("realtime detection using webcam ")
model=YOLO("best (1).pt")

start_button = st.button("Start Webcam")

# Create a placeholder for the video feed
video_placeholder = st.empty()

# Open webcam if the button is pressed
if start_button:
    cap = cv2.VideoCapture(0)  # Use 1 for external webcam

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLO inference
        results = model(frame,conf=0.8)

        # Annotate the frame with detection results
        annotated_frame = results[0].plot()

        # Convert frame to RGB (Streamlit requires RGB format)
        annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

        # Display the frame in Streamlit
        video_placeholder.image(annotated_frame, channels="RGB", use_column_width=True)

        # Break loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

