import cv2

# Open the default webcam (usually /dev/video0)
cap = cv2.VideoCapture(0)

# Optionally set resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("[ERR] Failed to open webcam.")
    exit(1)

print("[OK] Webcam opened. Press ESC to quit.")

# Create a named window first
cv2.namedWindow("Webcam Test", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Webcam Test", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Failed to grab frame.")
        break

    cv2.imshow("Webcam Test", frame)

    key = cv2.waitKey(1)
    if key == 27:  # ESC key
        print("👋 Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
