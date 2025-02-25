import streamlit as st
import cv2
import av
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from ultralytics import YOLO

# Load YOLO model
model = YOLO("best.pt")

# Streamlit UI
st.title("Aeroplanes Detection in Airport Imagery")
st.markdown("Real-time detection using webcam")

# Session state for webcam control
if "webcam_active" not in st.session_state:
    st.session_state.webcam_active = False

start_button = st.button("Start Webcam")
stop_button = st.button("Stop Webcam")

# Start webcam
if start_button:
    st.session_state.webcam_active = True

# Stop webcam
if stop_button:
    st.session_state.webcam_active = False

class VideoTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # Run YOLO inference
        results = model(img, conf=0.8)

        # Annotate the frame
        annotated_frame = results[0].plot()
        return av.VideoFrame.from_ndarray(annotated_frame, format="bgr24")

# Only start webcam if active
if st.session_state.webcam_active:
    webrtc_streamer(key="example", video_transformer_factory=VideoTransformer)
