import cv2
import time
import subprocess

def release_and_reinitialize_camera(cap):
    # Release and reinitialize the camera
    cap.release()
    time.sleep(1)
    cap = cv2.VideoCapture(1)  # Re-initialize with the correct camera index (0)
    return cap

def reset_camera_driver():
    # Reset the camera driver (e.g., uvcvideo for USB cameras)
    subprocess.run(['sudo', 'modprobe', '-r', 'uvcvideo'], check=True)  # Remove the camera driver
    time.sleep(1)
    subprocess.run(['sudo', 'modprobe', 'uvcvideo'], check=True)  # Reload the camera driver

def check_camera(cap):
    # Try to capture a frame to check if the camera is working
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        return False
    return True

def main():
    # Initialize the camera
    cap = cv2.VideoCapture(1)
    
    # Check if the camera was successfully initialized
    if not cap.isOpened():
        print("Error: Camera not detected. Please check the connection.")
        return

    while True:
        # Try to read a frame
        if not check_camera(cap):
            print("Reinitializing camera...")
            cap = release_and_reinitialize_camera(cap)
            
            # After reinitializing, we can also reset the camera driver if needed
            reset_camera_driver()

            # Check again after reinitializing
            if not check_camera(cap):
                print("Camera still not working, retrying...")
                continue

        # Proceed with the frame processing (example: display the frame)
        ret, frame = cap.read()
        if ret:
            cv2.imshow("Camera Feed", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
