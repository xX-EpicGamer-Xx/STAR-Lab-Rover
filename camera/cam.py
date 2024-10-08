from picamera2 import Picamera2, Preview
import cv2

# Initialize Picamera2
picam2 = Picamera2()

# Configure camera preview
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)

# Start the camera
picam2.start()

# Capture frames continuously
while True:
    # Capture image from the camera
    frame = picam2.capture_array()

    # Display the frame using OpenCV
    cv2.imshow("Live Feed", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cv2.destroyAllWindows()
picam2.stop()
