from flask import Flask, render_template, Response, url_for
import cv2
import pytesseract
import pyttsx3
import time
import platform 

if platform.system() == 'Windows':
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
app = Flask(__name__, static_folder="static", template_folder="templates")

# ตั้งค่าตัวแปรจับเวลา
frame_counter = 0
DETECTION_INTERVAL = 10  

def generate_frames():
    global frame_counter
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        yield b""
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_counter += 1  

        # แปลงภาพเป็นขาวดำ
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # ตรวจจับข้อความทุก ๆ DETECTION_INTERVAL เฟรม
        if frame_counter % DETECTION_INTERVAL == 0:
            text = pytesseract.image_to_string(gray, lang='eng')
            if text.strip():
                print(f"ข้อความ: {text.strip()}")
                text_to_speech(text.strip())

        # แสดงข้อความบนเฟรม
        cv2.putText(frame, text if frame_counter % DETECTION_INTERVAL == 0 else "",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # เข้ารหัสภาพเป็น JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        time.sleep(0.2)
        
    cap.release()

def text_to_speech(text):
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 50)
    engine.say(text)
    engine.runAndWait()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
