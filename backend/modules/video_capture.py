import cv2

def capture_photo(save_path="data/sample_images/live_photo.jpg"):
    cam = cv2.VideoCapture(0)
    print("Press SPACE to take photo, ESC to cancel")

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Camera not working")
            break

        cv2.imshow("Live Capture - Press SPACE", frame)
        key = cv2.waitKey(1)

        if key % 256 == 27:
            print("Cancelled")
            break
        elif key % 256 == 32:
            cv2.imwrite(save_path, frame)
            print(f"Photo saved at {save_path}")
            break

    cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    capture_photo()