from ultralytics import YOLO

# Load a model
model = YOLO("best.pt")
results = model(r"D:\acm\models\dl230225\airport_241_jpg.rf.48233f88e0aba89db4dd06f40b5c3514.jpg", save=True, show=True)  # Replace with an actual test image path

# Print the detection results
for result in results:
    print(result)

