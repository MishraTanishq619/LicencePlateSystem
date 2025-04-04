import cv2

def test_camera():
    # Open the camera (0 is usually the default camera)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Camera not detected. Please check the connection.")
        return

    print("Camera is working. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to read frame.")
            break
        
        # Display the captured frame in a window
        cv2.imshow('Camera Test', frame)
        
        # Wait for 'q' key to exit the loop and close the window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting the camera test.")
            break

    # Release the camera and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    test_camera()

