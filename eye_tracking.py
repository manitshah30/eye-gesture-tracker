import cv2
import numpy as np
import mediapipe as mp
import time
import math
from gaming_controller import GamingGestureController

class EyeTracker:
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Eye landmark indices for MediaPipe (468 landmarks)
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        
        # Eye contour for drawing
        self.LEFT_EYE_CONTOUR = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_CONTOUR = [33, 160, 158, 133, 153, 144]
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise ValueError("Could not open webcam")
        
        # Set webcam properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Initialize gaming controller
        self.gaming_controller = GamingGestureController()
        
        print("Eye Tracker with Gaming Controls initialized successfully!")
        print("Controls:")
        print("  'q' - Quit")
        print("  '1' - FPS Mode")
        print("  '2' - Racing Mode")
        print("  '3' - Strategy Mode")
        print("  '4' - Platformer Mode")
        print("  'g' - Toggle Gestures On/Off")
        print("  'c' - Calibrate")
    
    def get_eye_center(self, eye_landmarks, frame_width, frame_height):
        """Calculate the center of the eye region from MediaPipe landmarks"""
        x_coords = [landmark.x * frame_width for landmark in eye_landmarks]
        y_coords = [landmark.y * frame_height for landmark in eye_landmarks]
        center_x = int(sum(x_coords) / len(x_coords))
        center_y = int(sum(y_coords) / len(y_coords))
        return (center_x, center_y)
    
    def get_eye_aspect_ratio(self, eye_landmarks, frame_width, frame_height):
        """Calculate Eye Aspect Ratio (EAR) to detect blinks using MediaPipe landmarks"""
        # Convert landmarks to pixel coordinates
        points = [(int(landmark.x * frame_width), int(landmark.y * frame_height)) for landmark in eye_landmarks]
        
        # For MediaPipe, we use specific points for EAR calculation
        # Vertical distances
        if len(points) >= 6:
            A = math.sqrt((points[1][0] - points[5][0])**2 + (points[1][1] - points[5][1])**2)
            B = math.sqrt((points[2][0] - points[4][0])**2 + (points[2][1] - points[4][1])**2)
            # Horizontal distance
            C = math.sqrt((points[0][0] - points[3][0])**2 + (points[0][1] - points[3][1])**2)
            
            if C > 0:
                ear = (A + B) / (2.0 * C)
                return ear
        return 0.3  # Default value if calculation fails
    
    def calculate_face_distance(self, face_landmarks, frame_width, frame_height):
        """Calculate relative distance based on face landmark spread"""
        # Use key face points to estimate face size
        # Points: left face edge, right face edge, top of forehead, bottom of chin
        left_face = face_landmarks.landmark[234]  # Left face edge
        right_face = face_landmarks.landmark[454]  # Right face edge
        top_head = face_landmarks.landmark[10]    # Top of forehead
        bottom_chin = face_landmarks.landmark[152] # Bottom of chin
        
        # Calculate face width and height in pixels
        face_width = abs(right_face.x - left_face.x) * frame_width
        face_height = abs(top_head.y - bottom_chin.y) * frame_height
        
        # Calculate face area as a measure of distance
        face_area = face_width * face_height
        
        return face_area, face_width, face_height
    
    def check_distance_and_prompt(self, frame, face_area, face_width, face_height):
        """Check if user is too far and display prompt"""
        # Thresholds for distance detection (adjust based on testing)
        min_face_area = 15000  # Minimum face area in pixels
        min_face_width = 100   # Minimum face width in pixels
        
        frame_height, frame_width = frame.shape[:2]
        
        if face_area < min_face_area or face_width < min_face_width:
            # User is too far - display prompt
            prompt_text = "Please move closer to the camera"
            text_size = cv2.getTextSize(prompt_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            
            # Center the text
            text_x = (frame_width - text_size[0]) // 2
            text_y = frame_height // 2
            
            # Draw background rectangle for better visibility
            cv2.rectangle(frame, (text_x - 10, text_y - 30), 
                         (text_x + text_size[0] + 10, text_y + 10), 
                         (0, 0, 0), -1)
            
            # Draw the prompt text
            cv2.putText(frame, prompt_text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            # Draw arrow pointing towards camera
            arrow_start = (frame_width // 2, text_y + 50)
            arrow_end = (frame_width // 2, text_y + 80)
            cv2.arrowedLine(frame, arrow_start, arrow_end, (0, 255, 255), 3, tipLength=0.3)
            
            return True  # User is too far
        
        return False  # User is at good distance
    
    def draw_eye_tracking_info(self, frame, face_landmarks):
        """Draw eye tracking information on the frame using MediaPipe landmarks"""
        frame_height, frame_width = frame.shape[:2]
        
        # Extract eye landmarks
        left_eye_landmarks = [face_landmarks.landmark[i] for i in self.LEFT_EYE_CONTOUR]
        right_eye_landmarks = [face_landmarks.landmark[i] for i in self.RIGHT_EYE_CONTOUR]
        
        # Draw eye contours
        left_eye_points = [(int(landmark.x * frame_width), int(landmark.y * frame_height)) for landmark in left_eye_landmarks]
        right_eye_points = [(int(landmark.x * frame_width), int(landmark.y * frame_height)) for landmark in right_eye_landmarks]
        
        cv2.polylines(frame, [np.array(left_eye_points)], True, (0, 255, 0), 1)
        cv2.polylines(frame, [np.array(right_eye_points)], True, (0, 255, 0), 1)
        
        # Calculate eye centers
        left_eye_center = self.get_eye_center(left_eye_landmarks, frame_width, frame_height)
        right_eye_center = self.get_eye_center(right_eye_landmarks, frame_width, frame_height)
        
        # Draw eye centers
        cv2.circle(frame, left_eye_center, 3, (255, 0, 0), -1)
        cv2.circle(frame, right_eye_center, 3, (255, 0, 0), -1)
        
        # Calculate Eye Aspect Ratios
        left_ear = self.get_eye_aspect_ratio(left_eye_landmarks, frame_width, frame_height)
        right_ear = self.get_eye_aspect_ratio(right_eye_landmarks, frame_width, frame_height)
        avg_ear = (left_ear + right_ear) / 2.0
        
        # Send blink data to gaming controller
        self.gaming_controller.detect_blink_pattern(left_ear, right_ear, time.time())
        
        # Send gaze data to gaming controller
        self.gaming_controller.detect_gaze_movement(left_eye_center, right_eye_center, frame_width, frame_height)
        
        # Send head movement data to gaming controller
        self.gaming_controller.detect_head_movement(face_landmarks, frame_width, frame_height)
        
        # Send facial expression data to gaming controller
        self.gaming_controller.detect_facial_expressions(face_landmarks)
        
        # Detect blink (EAR threshold typically around 0.25)
        blink_threshold = 0.25
        if avg_ear < blink_threshold:
            cv2.putText(frame, "BLINK DETECTED", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Display EAR value
        cv2.putText(frame, f"EAR: {avg_ear:.2f}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Draw iris landmarks (MediaPipe provides iris tracking)
        left_iris = [face_landmarks.landmark[i] for i in [468, 469, 470, 471, 472]]
        right_iris = [face_landmarks.landmark[i] for i in [473, 474, 475, 476, 477]]
        
        for iris_landmark in left_iris:
            x = int(iris_landmark.x * frame_width)
            y = int(iris_landmark.y * frame_height)
            cv2.circle(frame, (x, y), 1, (0, 255, 255), -1)
        
        for iris_landmark in right_iris:
            x = int(iris_landmark.x * frame_width)
            y = int(iris_landmark.y * frame_height)
            cv2.circle(frame, (x, y), 1, (0, 255, 255), -1)
        
        return frame
    
    def run(self):
        """Main loop for eye tracking using MediaPipe"""
        print("Starting eye tracking... Press 'q' to quit")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            # Flip frame horizontally for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Convert BGR to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame with MediaPipe
            results = self.face_mesh.process(rgb_frame)
            
            # Draw face mesh and eye tracking info
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    frame_height, frame_width = frame.shape[:2]
                    
                    # Calculate face distance
                    face_area, face_width, face_height = self.calculate_face_distance(
                        face_landmarks, frame_width, frame_height)
                    
                    # Check distance and show prompt if too far
                    is_too_far = self.check_distance_and_prompt(frame, face_area, face_width, face_height)
                    
                    # Only draw detailed eye tracking if user is close enough
                    if not is_too_far:
                        # Draw eye tracking information
                        frame = self.draw_eye_tracking_info(frame, face_landmarks)
                        
                        # Show "Good Distance" indicator
                        cv2.putText(frame, "Good Distance ✓", (10, 170), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    
                    # Display gaming status with proper spacing
                    status = self.gaming_controller.get_status_info()
                    
                    # Mode indicator
                    cv2.putText(frame, f"Mode: {status['mode'].upper()}", (10, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                    
                    # Gesture status
                    gesture_status = "ON" if status['gestures_enabled'] else "OFF"
                    color = (0, 255, 0) if status['gestures_enabled'] else (0, 0, 255)
                    cv2.putText(frame, f"Gestures: {gesture_status}", (10, 115), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    # Head tilt (right side to avoid overlap)
                    cv2.putText(frame, f"Head Tilt: {status['head_tilt']:.1f}°", (300, 90), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                    
                    # Gaze position (right side)
                    gaze_x, gaze_y = status['gaze_position']
                    cv2.putText(frame, f"Gaze: ({gaze_x:.2f}, {gaze_y:.2f})", (300, 115), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
                    
                    # Optionally draw face mesh (commented out for cleaner view)
                    # self.mp_drawing.draw_landmarks(
                    #     frame, face_landmarks, self.mp_face_mesh.FACEMESH_CONTOURS,
                    #     None, self.mp_drawing_styles.get_default_face_mesh_contours_style())
            
            # Add instructions
            cv2.putText(frame, "Controls: q=quit, 1-4=modes, g=toggle gestures", (10, frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            
            # Display the frame
            cv2.imshow('Eye Tracking Gaming Controller', frame)
            
            # Check for key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('1'):
                self.gaming_controller.set_game_mode('fps')
            elif key == ord('2'):
                self.gaming_controller.set_game_mode('racing')
            elif key == ord('3'):
                self.gaming_controller.set_game_mode('strategy')
            elif key == ord('4'):
                self.gaming_controller.set_game_mode('platformer')
            elif key == ord('g'):
                self.gaming_controller.toggle_gestures()
            elif key == ord('c'):
                print("Calibration mode - adjust sensitivity if needed")
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        print("Eye tracking stopped")

def main():
    try:
        tracker = EyeTracker()
        tracker.run()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure you have a webcam connected and the required model file downloaded")

if __name__ == "__main__":
    main()
