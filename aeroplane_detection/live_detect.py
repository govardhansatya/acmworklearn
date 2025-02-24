import cv2
from ultralytics import YOLO

model = YOLO("best.pt")  
# Open the webcam (0 is the default webcam, change it if needed)
cap = cv2.VideoCapture(0)

cap.set(3, 640)  # Width
cap.set(4, 480)  # Height

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break  # Exit if the frame is not captured

    # Run YOLO inference on the frame
    results = model(frame, conf = 0.8)

    # Plot the results directly on the frame
    annotated_frame = results[0].plot()

    # Display the frame with detections
    cv2.imshow("res", annotated_frame)

    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
