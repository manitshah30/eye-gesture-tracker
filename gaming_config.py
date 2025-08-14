"""
Gaming Configuration for Eye Tracking Controller
Customize key mappings, sensitivity, and game modes here
"""

from pynput.keyboard import Key

# Default sensitivity settings
DEFAULT_SENSITIVITY = {
    'gaze': 1.0,        # Gaze movement sensitivity
    'blink': 1.0,       # Blink detection sensitivity
    'head': 1.0,        # Head movement sensitivity
    'dwell': 1.5,       # Dwell time in seconds
    'facial': 1.0       # Facial expression sensitivity
}

# Gesture thresholds
THRESHOLDS = {
    'blink_ear': 0.25,          # Eye Aspect Ratio for blink detection
    'double_blink_window': 0.8,  # Time window for double blink (seconds)
    'head_tilt_angle': 15,       # Minimum head tilt angle (degrees)
    'gaze_boundary': 0.3,        # Gaze boundary for directional detection
    'mouth_open_threshold': 0.02, # Mouth opening threshold
    'smile_width_threshold': 0.05 # Smile width threshold
}

# Game mode configurations
GAME_MODES = {
    'fps': {
        'name': 'First Person Shooter',
        'description': 'Optimized for FPS games like Counter-Strike, Call of Duty',
        'mappings': {
            'gaze_left': 'a',           # Strafe left
            'gaze_right': 'd',          # Strafe right
            'gaze_up': 'w',             # Move forward
            'gaze_down': 's',           # Move backward
            'single_blink': Key.space,   # Jump/Primary fire
            'double_blink': 'r',        # Reload
            'long_blink': Key.shift,    # Run/Sprint
            'left_wink': Key.ctrl,      # Crouch
            'right_wink': 'f',          # Use/Interact
            'dwell': Key.alt,           # Aim down sights
            'head_tilt_left': 'q',      # Lean left
            'head_tilt_right': 'e',     # Lean right
            'head_nod': 'c',            # Crouch toggle
            'mouth_open': 't',          # Voice chat/Team speak
            'smile': 'g',               # Gesture/Taunt
            'eyebrow_raise': Key.tab    # Scoreboard
        }
    },
    
    'racing': {
        'name': 'Racing Game',
        'description': 'Optimized for racing games like Forza, Gran Turismo',
        'mappings': {
            'head_tilt_left': 'a',      # Steer left
            'head_tilt_right': 'd',     # Steer right
            'gaze_up': 'w',             # Accelerate
            'gaze_down': 's',           # Brake/Reverse
            'single_blink': Key.space,   # Handbrake
            'double_blink': 'r',        # Reset car
            'long_blink': Key.shift,    # Nitro/Boost
            'left_wink': 'q',           # Look left
            'right_wink': 'e',          # Look right
            'dwell': 'c',               # Change camera
            'head_nod': 'x',            # Look back
            'mouth_open': Key.enter,    # Horn
            'smile': 'h',               # Headlights
            'gaze_left': Key.left,      # Menu left
            'gaze_right': Key.right     # Menu right
        }
    },
    
    'strategy': {
        'name': 'Real-Time Strategy',
        'description': 'Optimized for RTS games like StarCraft, Age of Empires',
        'mappings': {
            'dwell': 'mouse_left',      # Select units/buildings
            'single_blink': 'mouse_right', # Context menu/Move command
            'double_blink': Key.delete,  # Delete/Cancel
            'long_blink': Key.shift,    # Add to selection
            'gaze_movement': 'mouse_move', # Camera pan
            'head_nod': Key.enter,      # Confirm action
            'head_tilt_left': Key.left, # Scroll left
            'head_tilt_right': Key.right, # Scroll right
            'mouth_open': Key.space,    # Pause game
            'smile': Key.f1,            # Help/Info
            'left_wink': '1',           # Control group 1
            'right_wink': '2',          # Control group 2
            'gaze_up': Key.up,          # Scroll up
            'gaze_down': Key.down       # Scroll down
        }
    },
    
    'platformer': {
        'name': 'Platformer Game',
        'description': 'Optimized for platform games like Mario, Sonic',
        'mappings': {
            'gaze_left': 'a',           # Move left
            'gaze_right': 'd',          # Move right
            'single_blink': Key.space,   # Jump
            'double_blink': 'x',        # Attack/Action
            'long_blink': 'z',          # Special ability
            'left_wink': 's',           # Duck/Slide
            'right_wink': 'w',          # Look up
            'dwell': Key.shift,         # Run/Sprint
            'head_tilt_left': Key.left, # Fine movement left
            'head_tilt_right': Key.right, # Fine movement right
            'head_nod': 's',            # Duck/Crouch
            'mouth_open': Key.enter,    # Pause/Menu
            'smile': 'c',               # Celebrate/Taunt
            'gaze_up': 'w',             # Climb/Look up
            'gaze_down': 's'            # Duck/Look down
        }
    },
    
    'adventure': {
        'name': 'Adventure/RPG',
        'description': 'Optimized for adventure and RPG games',
        'mappings': {
            'gaze_left': 'a',           # Move left
            'gaze_right': 'd',          # Move right
            'gaze_up': 'w',             # Move forward
            'gaze_down': 's',           # Move backward
            'single_blink': Key.space,   # Jump/Confirm
            'double_blink': 'e',        # Interact/Use
            'long_blink': Key.shift,    # Run/Sprint
            'left_wink': 'i',           # Inventory
            'right_wink': 'm',          # Map
            'dwell': 'f',               # Focus/Target
            'head_tilt_left': 'q',      # Quick item left
            'head_tilt_right': 'r',     # Quick item right
            'head_nod': Key.ctrl,       # Sneak/Crouch
            'mouth_open': Key.enter,    # Menu/Pause
            'smile': 'h',               # Hello/Greet
            'eyebrow_raise': Key.tab    # Character sheet
        }
    }
}

# Accessibility presets
ACCESSIBILITY_PRESETS = {
    'high_sensitivity': {
        'description': 'For users with limited mobility',
        'sensitivity': {
            'gaze': 1.5,
            'blink': 0.8,
            'head': 1.5,
            'dwell': 1.0,
            'facial': 1.2
        }
    },
    
    'low_sensitivity': {
        'description': 'For users who prefer more deliberate gestures',
        'sensitivity': {
            'gaze': 0.7,
            'blink': 1.2,
            'head': 0.8,
            'dwell': 2.0,
            'facial': 0.8
        }
    },
    
    'blink_only': {
        'description': 'Primarily blink-based controls',
        'sensitivity': {
            'gaze': 0.3,
            'blink': 1.5,
            'head': 0.2,
            'dwell': 3.0,
            'facial': 0.5
        }
    },
    
    'head_only': {
        'description': 'Primarily head movement controls',
        'sensitivity': {
            'gaze': 0.2,
            'blink': 0.5,
            'head': 1.8,
            'dwell': 2.5,
            'facial': 0.3
        }
    }
}

# Visual feedback settings
VISUAL_FEEDBACK = {
    'show_gaze_indicator': True,
    'show_gesture_feedback': True,
    'show_mode_indicator': True,
    'show_sensitivity_bars': False,
    'gesture_feedback_duration': 1.0,  # seconds
    'colors': {
        'active_gesture': (0, 255, 0),
        'inactive_gesture': (128, 128, 128),
        'mode_indicator': (0, 255, 255),
        'warning': (0, 165, 255),
        'error': (0, 0, 255)
    }
}

# Audio feedback settings (for future implementation)
AUDIO_FEEDBACK = {
    'enabled': False,
    'gesture_sounds': True,
    'mode_change_sounds': True,
    'error_sounds': True,
    'volume': 0.5
}

# Performance settings
PERFORMANCE = {
    'gesture_cooldown': 0.1,        # Minimum time between gesture triggers (seconds)
    'max_fps': 30,                  # Maximum processing FPS
    'gesture_confidence_threshold': 0.7,  # Minimum confidence for gesture recognition
    'smoothing_frames': 3           # Number of frames to smooth gestures over
}

def get_game_mode_info(mode_name):
    """Get information about a specific game mode"""
    return GAME_MODES.get(mode_name, None)

def get_all_game_modes():
    """Get list of all available game modes"""
    return list(GAME_MODES.keys())

def apply_accessibility_preset(preset_name):
    """Apply an accessibility preset"""
    return ACCESSIBILITY_PRESETS.get(preset_name, {})

def get_default_config():
    """Get default configuration"""
    return {
        'sensitivity': DEFAULT_SENSITIVITY.copy(),
        'thresholds': THRESHOLDS.copy(),
        'visual_feedback': VISUAL_FEEDBACK.copy(),
        'performance': PERFORMANCE.copy()
    }
