from flask import Flask, render_template, Response
import cv2
import pytesseract
import time
import platform
import os

# เงื่อนไขเฉพาะ Windows เท่านั้น
if platform.system() == 'Windows':
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    import pyttsx3
    def text_to_speech(text):
        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate - 50)
        engine.say(text)
        engine.runAndWait()
else:
    def text_to_speech(text):
        print(f"[TTS skipped] {text}")  # บน Render ไม่มีเสียง

# สร้างแอป Flask
app = Flask(__name__, static_folder="static", template_folder="templates")

# ตัวแปรจับเวลา
frame_counter = 0
DETECTION_INTERVAL = 10

# ฟังก์ชันแสดงกล้อง
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
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if frame_counter % DETECTION_INTERVAL == 0:
            text = pytesseract.image_to_string(gray, lang='eng')
            if text.strip():
                print(f"ข้อความ: {text.strip()}")
                text_to_speech(text.strip())

        cv2.putText(frame, text if frame_counter % DETECTION_INTERVAL == 0 else "",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        time.sleep(0.2)

    cap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
