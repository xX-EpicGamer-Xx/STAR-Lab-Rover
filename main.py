from flask import Flask, Response, render_template, request
from picamera2 import Picamera2
import RPi.GPIO as GPIO
import cv2
import libcamera
import time
import smtplib
import socket
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_ip_address():
    try:
        # Create a socket connection to an external server to get the local network IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Connect to a public DNS server, doesn't actually send any data
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception as e:
        return f"Error retrieving IP address: {e}"

def send_email(subject, body, to_email):
    from_email = "cyrilljhonb@gmail.com"
    password = "epky ernx rzeo sbuh"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")
        
# Set up Flask app
app = Flask(__name__)

# Initialize the camera with 180-degree rotation
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration()
preview_config["transform"] = libcamera.Transform(hflip=1, vflip=1)
picam2.configure(preview_config)
picam2.start()

# Motor Pin Definitions
ENA = 15
IN1 = 13
IN2 = 11
ENB = 3
IN3 = 7
IN4 = 5

# GPIO Setup
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Setup motor pins as output
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

# Set up PWM for speed control
pwm_a = GPIO.PWM(ENA, 1000)  # Frequency = 1KHz
pwm_b = GPIO.PWM(ENB, 1000)  # Frequency = 1KHz
pwm_a.start(0)
pwm_b.start(0)

# Motor control functions
def move_forward():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_a.ChangeDutyCycle(100)
    pwm_b.ChangeDutyCycle(100)

def move_backward():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_a.ChangeDutyCycle(100)
    pwm_b.ChangeDutyCycle(100)

def move_left():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_a.ChangeDutyCycle(100)
    pwm_b.ChangeDutyCycle(100)

def move_right():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_a.ChangeDutyCycle(100)
    pwm_b.ChangeDutyCycle(100)

def stop():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwm_a.ChangeDutyCycle(0)
    pwm_b.ChangeDutyCycle(0)

# Web interface for motor control and camera feed
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    direction = request.form['direction']
    
    if direction == 'forward':
        move_forward()
    elif direction == 'backward':
        move_backward()
    elif direction == 'left':
        move_left()
    elif direction == 'right':
        move_right()
    elif direction == 'stop':
        stop()
    
    return ('', 204)  # No response content

# Ensure the 'pictures' folder exists
if not os.path.exists('pictures'):
    os.makedirs('pictures')

# Function to capture a picture and save it
def capture_picture():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    picture_path = f"pictures/capture_{timestamp}.jpg"
    picam2.capture_file(picture_path)
    print(f"Picture saved: {picture_path}")
    return picture_path

# Add a route to handle picture capture
@app.route('/capture', methods=['POST'])
def capture():
    picture_path = capture_picture()
    return ('', 204)  # No content response

def gen_frames():
    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Clean up on exit
@app.route('/cleanup')
def cleanup():
    GPIO.cleanup()
    picam2.stop()
    return 'GPIO and camera cleaned up.'

if __name__ == '__main__':
    ip_address = get_ip_address()
    subject = "Rover IP Address and Port"
    body = f"{ip_address}:5000"

    recipient_email = "cyrill.john.becina@adamson.edu.ph"
    send_email(subject, body, recipient_email)
    try:
        app.run(host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        GPIO.cleanup()
        picam2.stop()

