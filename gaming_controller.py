import time
import threading
from collections import deque
from pynput import keyboard, mouse
from pynput.keyboard import Key
import numpy as np

class GamingGestureController:
    def __init__(self):
        # Initialize input controllers
        self.keyboard_controller = keyboard.Controller()
        self.mouse_controller = mouse.Controller()
        
        # Gesture state tracking
        self.gesture_history = deque(maxlen=30)  # Store last 30 frames of gestures
        self.last_blink_time = 0
        self.last_double_blink_time = 0
        self.blink_count = 0
        self.blink_sequence = []
        
        # Gaze tracking
        self.gaze_center = (0, 0)
        self.gaze_history = deque(maxlen=10)
        self.dwell_start_time = None
        self.dwell_position = None
        self.dwell_threshold = 1.5  # seconds
        
        # Head movement tracking
        self.head_position = {'tilt': 0, 'nod': 0}
        self.head_history = deque(maxlen=10)
        
        # Facial expression tracking
        self.mouth_open = False
        self.eyebrow_raised = False
        self.smile_detected = False
        
        # Gaming modes
        self.current_mode = "fps"  # fps, racing, strategy, platformer
        self.gesture_enabled = True
        
        # Calibration settings
        self.sensitivity = {
            'gaze': 1.0,
            'blink': 1.0,
            'head': 1.0,
            'dwell': 1.5
        }
        
        # Key mappings for different game modes
        self.key_mappings = {
            'fps': {
                'gaze_left': 'a',
                'gaze_right': 'd',
                'gaze_up': 'w',
                'gaze_down': 's',
                'single_blink': Key.space,  # Jump/shoot
                'double_blink': 'r',  # Reload
                'long_blink': Key.shift,  # Run
                'dwell': Key.ctrl,  # Aim
                'head_tilt_left': 'q',
                'head_tilt_right': 'e',
                'mouth_open': 't',  # Voice chat
                'smile': 'g'  # Gesture/taunt
            },
            'racing': {
                'head_tilt_left': 'a',  # Steer left
                'head_tilt_right': 'd',  # Steer right
                'gaze_up': 'w',  # Accelerate
                'gaze_down': 's',  # Brake
                'single_blink': Key.space,  # Handbrake
                'double_blink': 'r',  # Reset
                'long_blink': Key.shift,  # Boost
                'dwell': 'c'  # Camera change
            },
            'strategy': {
                'dwell': 'mouse_left',  # Select
                'single_blink': 'mouse_right',  # Context menu
                'double_blink': Key.delete,  # Delete
                'gaze_movement': 'mouse_move',  # Camera pan
                'head_nod': Key.enter,  # Confirm
                'mouth_open': Key.space  # Pause
            },
            'platformer': {
                'gaze_left': 'a',
                'gaze_right': 'd',
                'single_blink': Key.space,  # Jump
                'double_blink': 'x',  # Attack
                'long_blink': 'z',  # Special
                'head_nod': 's',  # Duck
                'dwell': Key.shift  # Run
            }
        }
        
        print(f"Gaming Controller initialized in {self.current_mode} mode")
    
    def set_game_mode(self, mode):
        """Switch between different gaming modes"""
        if mode in self.key_mappings:
            self.current_mode = mode
            print(f"Switched to {mode} mode")
        else:
            print(f"Unknown mode: {mode}")
    
    def calibrate_sensitivity(self, gesture_type, value):
        """Adjust sensitivity for different gestures"""
        if gesture_type in self.sensitivity:
            self.sensitivity[gesture_type] = value
            print(f"Set {gesture_type} sensitivity to {value}")
    
    def detect_blink_pattern(self, left_ear, right_ear, timestamp):
        """Detect different blink patterns"""
        avg_ear = (left_ear + right_ear) / 2.0
        blink_threshold = 0.25
        
        current_time = time.time()
        
        if avg_ear < blink_threshold:
            if current_time - self.last_blink_time > 0.3:  # New blink
                self.blink_count += 1
                self.blink_sequence.append(current_time)
                self.last_blink_time = current_time
                
                # Clean old blinks (older than 2 seconds)
                self.blink_sequence = [t for t in self.blink_sequence if current_time - t < 2.0]
                
                # Detect patterns
                if len(self.blink_sequence) == 1:
                    # Single blink detected
                    threading.Thread(target=self._trigger_single_blink, daemon=True).start()
                elif len(self.blink_sequence) == 2 and current_time - self.blink_sequence[0] < 0.8:
                    # Double blink detected
                    threading.Thread(target=self._trigger_double_blink, daemon=True).start()
                    self.blink_sequence.clear()
        
        # Detect long blink (wink)
        if left_ear < blink_threshold and right_ear > blink_threshold + 0.1:
            threading.Thread(target=self._trigger_left_wink, daemon=True).start()
        elif right_ear < blink_threshold and left_ear > blink_threshold + 0.1:
            threading.Thread(target=self._trigger_right_wink, daemon=True).start()
    
    def detect_gaze_movement(self, left_eye_center, right_eye_center, frame_width, frame_height):
        """Detect gaze direction and dwell"""
        # Calculate average gaze position
        gaze_x = (left_eye_center[0] + right_eye_center[0]) / 2
        gaze_y = (left_eye_center[1] + right_eye_center[1]) / 2
        
        # Normalize to screen coordinates
        norm_x = gaze_x / frame_width
        norm_y = gaze_y / frame_height
        
        self.gaze_center = (norm_x, norm_y)
        self.gaze_history.append(self.gaze_center)
        
        # Detect gaze direction
        if len(self.gaze_history) >= 5:
            recent_x = [pos[0] for pos in list(self.gaze_history)[-5:]]
            recent_y = [pos[1] for pos in list(self.gaze_history)[-5:]]
            
            avg_x = sum(recent_x) / len(recent_x)
            avg_y = sum(recent_y) / len(recent_y)
            
            # Trigger directional movements
            if avg_x < 0.3:  # Looking left
                self._trigger_gaze_left()
            elif avg_x > 0.7:  # Looking right
                self._trigger_gaze_right()
            
            if avg_y < 0.3:  # Looking up
                self._trigger_gaze_up()
            elif avg_y > 0.7:  # Looking down
                self._trigger_gaze_down()
        
        # Detect dwell (sustained gaze)
        self._detect_dwell(norm_x, norm_y)
    
    def _detect_dwell(self, x, y):
        """Detect when user dwells on a position"""
        current_time = time.time()
        
        if self.dwell_position is None:
            self.dwell_position = (x, y)
            self.dwell_start_time = current_time
        else:
            # Check if still looking at same position (within threshold)
            distance = np.sqrt((x - self.dwell_position[0])**2 + (y - self.dwell_position[1])**2)
            
            if distance < 0.1:  # Still dwelling
                if current_time - self.dwell_start_time > self.sensitivity['dwell']:
                    self._trigger_dwell()
                    self.dwell_position = None
            else:
                # Moved away, reset dwell
                self.dwell_position = (x, y)
                self.dwell_start_time = current_time
    
    def detect_head_movement(self, face_landmarks, frame_width, frame_height):
        """Detect head tilt and nod movements"""
        # Get key points for head orientation
        nose_tip = face_landmarks.landmark[1]
        left_ear = face_landmarks.landmark[234]
        right_ear = face_landmarks.landmark[454]
        forehead = face_landmarks.landmark[10]
        chin = face_landmarks.landmark[152]
        
        # Calculate head tilt (roll)
        ear_diff = (right_ear.y - left_ear.y) * frame_height
        head_tilt = np.arctan2(ear_diff, (right_ear.x - left_ear.x) * frame_width) * 180 / np.pi
        
        # Calculate head nod (pitch) - approximate
        face_height = abs(forehead.y - chin.y) * frame_height
        nose_y_relative = (nose_tip.y - forehead.y) / (chin.y - forehead.y)
        
        self.head_position['tilt'] = head_tilt
        self.head_position['nod'] = nose_y_relative
        
        self.head_history.append(self.head_position.copy())
        
        # Trigger head movements
        if abs(head_tilt) > 15:  # Significant tilt
            if head_tilt > 15:
                self._trigger_head_tilt_right()
            elif head_tilt < -15:
                self._trigger_head_tilt_left()
        
        if nose_y_relative > 0.6:  # Head down (nod)
            self._trigger_head_nod_down()
        elif nose_y_relative < 0.4:  # Head up
            self._trigger_head_nod_up()
    
    def detect_facial_expressions(self, face_landmarks):
        """Detect facial expressions like smile, mouth open, eyebrow raise"""
        # Mouth landmarks
        mouth_top = face_landmarks.landmark[13]
        mouth_bottom = face_landmarks.landmark[14]
        mouth_left = face_landmarks.landmark[61]
        mouth_right = face_landmarks.landmark[291]
        
        # Calculate mouth opening
        mouth_height = abs(mouth_top.y - mouth_bottom.y)
        mouth_width = abs(mouth_left.x - mouth_right.x)
        
        # Detect mouth open
        if mouth_height > 0.02:  # Threshold for mouth open
            if not self.mouth_open:
                self.mouth_open = True
                self._trigger_mouth_open()
        else:
            self.mouth_open = False
        
        # Smile detection (simplified)
        mouth_corners_up = (mouth_left.y + mouth_right.y) / 2 < mouth_top.y
        if mouth_corners_up and mouth_width > 0.05:
            if not self.smile_detected:
                self.smile_detected = True
                self._trigger_smile()
        else:
            self.smile_detected = False
    
    # Gesture trigger methods
    def _trigger_single_blink(self):
        if not self.gesture_enabled:
            return
        key = self.key_mappings[self.current_mode].get('single_blink')
        if key:
            self._press_key(key)
            print("Single blink -> Action triggered")
    
    def _trigger_double_blink(self):
        if not self.gesture_enabled:
            return
        key = self.key_mappings[self.current_mode].get('double_blink')
        if key:
            self._press_key(key)
            print("Double blink -> Secondary action triggered")
    
    def _trigger_left_wink(self):
        if not self.gesture_enabled:
            return
        key = self.key_mappings[self.current_mode].get('long_blink')
        if key:
            self._press_key(key)
            print("Left wink -> Special action triggered")
    
    def _trigger_right_wink(self):
        if not self.gesture_enabled:
            return
        # Right wink could be mapped to different action
        print("Right wink detected")
    
    def _trigger_gaze_left(self):
        if not self.gesture_enabled:
            return
        key = self.key_mappings[self.current_mode].get('gaze_left')
        if key:
            self._press_key(key)
    
    def _trigger_gaze_right(self):
        if not self.gesture_enabled:
            return
        key = self.key_mappings[self.current_mode].get('gaze_right')
        if key:
            self._press_key(key)
    
    def _trigger_gaze_up(self):
        if not self.gesture_enabled:
            return
        key = self.key_mappings[self.current_mode].get('gaze_up')
        if key:
            self._press_key(key)
    
    def _trigger_gaze_down(self):
        if not self.gesture_enabled:
            return
        key = self.key_mappings[self.current_mode].get('gaze_down')
        if key:
            self._press_key(key)
    
    def _trigger_dwell(self):
        if not self.gesture_enabled:
            return
        key = self.key_mappings[self.current_mode].get('dwell')
        if key:
            if key == 'mouse_left':
                self.mouse_controller.click(mouse.Button.left)
            else:
                self._press_key(key)
            print("Dwell -> Select/Aim triggered")
    
    def _trigger_head_tilt_left(self):
        if not self.gesture_enabled:
            return
        key = self.key_mappings[self.current_mode].get('head_tilt_left')
        if key:
            self._press_key(key)
    
    def _trigger_head_tilt_right(self):
        if not self.gesture_enabled:
            return
        key = self.key_mappings[self.current_mode].get('head_tilt_right')
        if key:
            self._press_key(key)
    
    def _trigger_head_nod_down(self):
        if not self.gesture_enabled:
            return
        key = self.key_mappings[self.current_mode].get('head_nod')
        if key:
            self._press_key(key)
    
    def _trigger_head_nod_up(self):
        if not self.gesture_enabled:
            return
        print("Head nod up detected")
    
    def _trigger_mouth_open(self):
        if not self.gesture_enabled:
            return
        key = self.key_mappings[self.current_mode].get('mouth_open')
        if key:
            self._press_key(key)
            print("Mouth open -> Voice/Shout triggered")
    
    def _trigger_smile(self):
        if not self.gesture_enabled:
            return
        key = self.key_mappings[self.current_mode].get('smile')
        if key:
            self._press_key(key)
            print("Smile -> Positive action triggered")
    
    def _press_key(self, key):
        """Helper method to press keys safely"""
        try:
            if isinstance(key, str):
                self.keyboard_controller.press(key)
                self.keyboard_controller.release(key)
            else:  # Special keys
                self.keyboard_controller.press(key)
                self.keyboard_controller.release(key)
        except Exception as e:
            print(f"Error pressing key {key}: {e}")
    
    def toggle_gestures(self):
        """Enable/disable gesture recognition"""
        self.gesture_enabled = not self.gesture_enabled
        status = "enabled" if self.gesture_enabled else "disabled"
        print(f"Gestures {status}")
    
    def get_status_info(self):
        """Get current status for display"""
        return {
            'mode': self.current_mode,
            'gestures_enabled': self.gesture_enabled,
            'gaze_position': self.gaze_center,
            'head_tilt': self.head_position.get('tilt', 0),
            'blink_count': len(self.blink_sequence)
        }
