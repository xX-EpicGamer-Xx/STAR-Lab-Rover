from flask import Flask, render_template, Response, jsonify
from picamera2 import Picamera2
from io import BytesIO
from PIL import Image

app = Flask(__name__)

# Initialize the Picamera2
picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"size": (640, 480)}))
picam2.start()

def take_picture():
    # Capture an image
    image = picam2.capture_array()
    # Save the image to file
    img = Image.fromarray(image)
    img.save('captured_image.jpg')
    print("Picture taken!")

# Route to display the main page with the live camera feed
@app.route('/')
def index():
    return render_template('index.html')

# Stream video frames to the web page
def gen_frames():
    while True:
        # Capture frame-by-frame
        frame = picam2.capture_array()
        
        # Convert the frame to JPEG format
        img = Image.fromarray(frame)
        output = BytesIO()
        img.save(output, format="JPEG")
        frame_data = output.getvalue()
        
        # Yield the output frame in byte format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

@app.route('/video_feed')
def video_feed():
    # Return the streaming response
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/take_picture', methods=['POST'])
def take_picture_route():
    take_picture()  # Trigger the picture function
    return jsonify({"status": "Picture taken"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
