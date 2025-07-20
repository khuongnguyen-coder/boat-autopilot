import cv2

def list_available_cameras(max_index=10):
    available_cameras = []
    for index in range(max_index):
        cap = cv2.VideoCapture(index)
        if cap is not None and cap.isOpened():
            print(f"[OK] Camera found at index {index}")
            available_cameras.append(index)
            cap.release()
        else:
            print(f"[ERR] No camera at index {index}")
    return available_cameras

if __name__ == "__main__":
    cameras = list_available_cameras()
    print("Available camera indices:", cameras)

