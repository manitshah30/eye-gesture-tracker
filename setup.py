import subprocess
import sys

def install_requirements():
    """Install required packages for the eye tracking application"""
    print("Installing required packages...")
    
    try:
        # Install packages from requirements.txt
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        print("Please try installing manually: pip install -r requirements.txt")
        return False

def check_webcam():
    """Check if webcam is accessible"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("Webcam detected and accessible!")
            cap.release()
            return True
        else:
            print("Warning: Could not access webcam. Make sure it's connected and not in use.")
            return False
    except ImportError:
        print("OpenCV not installed yet. Will check webcam after installation.")
        return True

if __name__ == "__main__":
    print("Setting up Eye Tracking Application...")
    print("This application uses MediaPipe for advanced eye and iris tracking.")
    
    # Install requirements
    if install_requirements():
        print("\nChecking webcam access...")
        check_webcam()
        print("\nSetup complete! You can now run the eye tracker with:")
        print("python eye_tracking.py")
    else:
        print("\nSetup failed. Please install requirements manually.")
