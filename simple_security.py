import cv2
import time
import os
import smtplib
from datetime import datetime
from playsound3 import playsound
from ultralytics import YOLO
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import pytz

EMAIL_SENDER = "b30613155@gmail.com"
EMAIL_PASSWORD = "kvihqbphddvmdnwo"
EMAIL_RECEIVER = "bela216.1111@gmail.com"

ALERT_DIR = "alerts"
COOLDOWN = 60
CAMERA_NAME = "CAMERA 01 - FRONT GATE"

os.makedirs(ALERT_DIR, exist_ok=True)

model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

last_alert_time = 0

def now():
    tz = pytz.timezone('Africa/Addis_Ababa')
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

def send_email(frame, boxes):
    print("...Saving detected persons")
    image_paths = []

    for i, (x1, y1, x2, y2) in enumerate(boxes):
        crop = frame[y1:y2, x1:x2]
        cv2.putText(crop, now(), (5, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        path = os.path.join(ALERT_DIR, f"person_{i+1}.jpg")
        cv2.imwrite(path, crop)
        image_paths.append(path)

    if not image_paths:
        return

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = f"SECURITY ALERT: {len(image_paths)} Person(s) Detected!"

    body = f"""
        SECURITY ALERT

        Time: {now()}
        Detected: {len(image_paths)} person(s)
        Location: {CAMERA_NAME}
    """
    msg.attach(MIMEText(body, "plain"))

    for path in image_paths:
        with open(path, "rb") as f:
            img = MIMEImage(f.read())
            img.add_header("Content-Disposition",
                        "attachment",
                        filename=os.path.basename(path))
            msg.attach(img)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

    print("Email sent!")


print("Security system started. Press Q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)[0]
    boxes = []

    for box, cls in zip(results.boxes.xyxy, results.boxes.cls):
        if int(cls) == 0:
            x1, y1, x2, y2 = map(int, box)
            boxes.append((x1, y1, x2, y2))
            cv2.rectangle(frame, (x1, y1),
                        (x2, y2), (0, 255, 0), 2)

    cv2.putText(frame, CAMERA_NAME, (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, now(),
                (10, frame.shape[0]-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow("Security Camera", frame)

    current_time = time.time()

    if boxes and current_time - last_alert_time > COOLDOWN:
        print(f"[{now()}] Person detected!")
        try:
            playsound("alarm.wav", block=False)
        except:
            print("alarm.wav missing")

        send_email(frame, boxes)
        last_alert_time = current_time

    elif boxes:
        print("Cooldown active...")

    if cv2.waitKey(1) & 0xFF in [ord("q"), 27]:
        break

cap.release()
cv2.destroyAllWindows()
print("System stopped.")