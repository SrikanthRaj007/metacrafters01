import json
import cv2
import numpy as np

def process_blueprint(image_path):
    # Load the blueprint image
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian Blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use adaptive thresholding for shapes detection
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)

    # Morphological operations to clean up the image
    kernel = np.ones((5, 5), np.uint8)
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Find contours for shapes
    contours, _ = cv2.findContours(morphed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    detected_objects = []  # List to store detected objects

    # Process contours for shapes
    for contour in contours:
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Check for various shapes (polygons with more than 4 vertices)
        if len(approx) >= 4:  
            x, y, w, h = cv2.boundingRect(approx)
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Draw detected shapes
            detected_objects.append({"class": "detected shape", "box": [int(x), int(y), int(w), int(h)]})

    # Canny edge detection for lines
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

    # Find lines using Hough Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=30, maxLineGap=10)

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 255), 2)  # Draw detected lines
            detected_objects.append({"class": "detected line", "box": [int(x1), int(y1), int(x2 - x1), int(y2 - y1)]})

    # YOLO model integration
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    height, width = image.shape[:2]

    # Prepare image for YOLO
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    detections = net.forward(output_layers)

    for output in detections:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.3:  # Lowered confidence threshold
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Calculate bounding box coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                detected_objects.append({
                    "class": classes[class_id],
                    "confidence": float(confidence),  # Ensure confidence is a float
                    "box": [int(x), int(y), int(w), int(h)]  # Ensure bounding box is int
                })

                # Draw bounding box for visualization
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(image, f"{classes[class_id]}: {confidence:.2f}", (x, y - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Save the detected objects to a JSON file
    with open('detected_objects.json', 'w') as f:
        json.dump(detected_objects, f)

    return image, detected_objects

# Example usage
image_path = '0001.jpg'
image, objects = process_blueprint(image_path)

# Show the original image with detected lines and bounding boxes
cv2.imshow("Blueprint with Detected Objects", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
