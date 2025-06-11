import cv2
import numpy as np
import time

class GameDisplay:
    def __init__(self, frame_width=1920, frame_height=1080):
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Animation paths
        self.idle_video_path = "Assets/mageIdle.mkv"
        self.attack_video_path = "Assets/MageAttack.mkv"
        
        # Video captures
        self.idle_cap = None
        self.attack_cap = None
        
        # Camera settings
        self.camera_width = 480  # Bigger camera size
        self.camera_height = 360
        self.camera_x = 20  # Bottom left position
        self.camera_y = frame_height - self.camera_height - 20
        
        # Animation state
        self.current_animation = "idle"  # "idle" or "attack"
        self.attack_start_time = None
        self.attack_duration = None  # Will be set based on video length
        self.last_frame_time = 0
        self.frame_interval = 1.0 / 120.0  # Target 120 FPS
        
        # Load animations
        self.load_animations()
    
    def load_animations(self):
        """Load both idle and attack animations"""
        # Load idle animation
        self.idle_cap = cv2.VideoCapture(self.idle_video_path)
        if not self.idle_cap.isOpened():
            print(f"Warning: Could not open {self.idle_video_path}")
        
        # Load attack animation
        self.attack_cap = cv2.VideoCapture(self.attack_video_path)
        if not self.attack_cap.isOpened():
            print(f"Warning: Could not open {self.attack_video_path}")
        else:
            # Get attack video duration
            fps = self.attack_cap.get(cv2.CAP_PROP_FPS)
            frame_count = self.attack_cap.get(cv2.CAP_PROP_FRAME_COUNT)
            if fps > 0 and frame_count > 0:
                self.attack_duration = frame_count / fps
                print(f"Attack animation duration: {self.attack_duration:.2f} seconds")
            else:
                self.attack_duration = 2.0  # Fallback duration
    
    def get_animation_frame(self):
        """Get the current animation frame based on state"""
        current_time = time.time()
        
        # Check if we should update the frame (maintain consistent FPS)
        if current_time - self.last_frame_time < self.frame_interval:
            return None  # Skip this frame to maintain FPS
        
        self.last_frame_time = current_time
        
        # Get frame from appropriate animation
        if self.current_animation == "attack" and self.attack_cap and self.attack_cap.isOpened():
            # Calculate which frame to show based on elapsed time and reaction time
            elapsed_time = current_time - self.attack_start_time
            video_duration = self.attack_cap.get(cv2.CAP_PROP_FRAME_COUNT) / self.attack_cap.get(cv2.CAP_PROP_FPS)
            
            # Map elapsed time to video progress
            video_progress = min(elapsed_time / self.attack_duration, 1.0)
            target_frame = int(video_progress * self.attack_cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Set video to the correct frame
            self.attack_cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            ret, frame = self.attack_cap.read()
            
            if not ret:
                # Attack animation finished, switch back to idle
                self.return_to_idle()
                ret, frame = self.idle_cap.read()
        else:
            # Use idle animation
            if self.idle_cap and self.idle_cap.isOpened():
                ret, frame = self.idle_cap.read()
                if not ret:
                    # Loop idle animation
                    self.idle_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    ret, frame = self.idle_cap.read()
            else:
                ret = False
                frame = None
        
        if ret:
            # Stretch the mage animation to fill the full display (no dead space)
            frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            return frame
        else:
            # Fallback: create a dark background
            fallback = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
            fallback[:] = (30, 30, 50)  # Dark blue background
            return fallback
    
    def start_attack_animation(self, reaction_time):
        """Start the attack animation synchronized with reaction time"""
        self.current_animation = "attack"
        self.attack_start_time = time.time()
        self.attack_duration = reaction_time  # Use reaction time instead of video duration
        # Reset attack video to beginning
        if self.attack_cap and self.attack_cap.isOpened():
            self.attack_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    def return_to_idle(self):
        """Explicitly return to idle animation"""
        self.current_animation = "idle"
        self.attack_start_time = None
        # Reset idle video to beginning for smooth transition
        if self.idle_cap and self.idle_cap.isOpened():
            self.idle_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    def create_game_display(self, camera_frame, mage_spell=None, player_spell=None, 
                           countdown=None, player_hp=100, mage_hp=100, round_num=1, hand_landmarks=None, mp_draw=None, mp_hands=None):
        """Create the complete game display with mage animation and user camera"""
        
        # Get the main animation frame
        animation_frame = self.get_animation_frame()
        
        # Create the main display canvas
        display = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
        display[:] = (20, 20, 30)  # Dark background
        
        # Place the mage animation as the full background
        if animation_frame is not None:
            display = animation_frame.copy()
        
        # Resize and place user camera in bottom left
        if camera_frame is not None:
            camera_resized = cv2.resize(camera_frame, (self.camera_width, self.camera_height))
            # Draw hand tracking on the user camera if landmarks are provided
            if hand_landmarks is not None and mp_draw is not None and mp_hands is not None:
                for handLms in hand_landmarks:
                    mp_draw.draw_landmarks(camera_resized, handLms, mp_hands.HAND_CONNECTIONS)
            display[self.camera_y:self.camera_y + self.camera_height, 
                   self.camera_x:self.camera_x + self.camera_width] = camera_resized
            # Add border around camera
            cv2.rectangle(display, (self.camera_x - 2, self.camera_y - 2), 
                         (self.camera_x + self.camera_width + 2, self.camera_y + self.camera_height + 2), 
                         (255, 255, 255), 2)
        
        # Add game UI elements
        self.draw_game_ui(display, mage_spell, player_spell, countdown, player_hp, mage_hp, round_num)
        
        return display
    
    def draw_game_ui(self, display, mage_spell, player_spell, countdown, player_hp, mage_hp, round_num):
        """Draw all UI elements on the display"""
        
        # Round number
        cv2.putText(display, f"ROUND {round_num}", (50, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)
        
        # Mage spell announcement - make it very prominent
        if mage_spell:
            spell_text = f"MAGE CASTS: {mage_spell.upper()}"
            # Add large background rectangle for maximum visibility
            text_size = cv2.getTextSize(spell_text, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 5)[0]
            # Position in center-top area for maximum visibility
            x = (self.frame_width - text_size[0]) // 2
            y = 150
            
            # Large black background with white border
            cv2.rectangle(display, (x - 30, y - text_size[1] - 20), 
                         (x + text_size[0] + 30, y + 20), (0, 0, 0), -1)
            cv2.rectangle(display, (x - 30, y - text_size[1] - 20), 
                         (x + text_size[0] + 30, y + 20), (255, 255, 255), 3)
            
            # Draw the text in bright red
            cv2.putText(display, spell_text, (x, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2.0, (0, 0, 255), 5, cv2.LINE_AA)
        
        # Countdown timer (accurate and visually clear)
        if countdown is not None and countdown > 0:
            cv2.putText(display, f"Counter in: {countdown:.1f}s", (50, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3, cv2.LINE_AA)
        elif countdown is not None:
            cv2.putText(display, f"Counter in: 0.0s", (50, 250), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3, cv2.LINE_AA)
        
        # Player spell display (move to bottom right)
        if player_spell:
            player_text = f"YOUR SPELL: {player_spell.upper()}"
            text_size = cv2.getTextSize(player_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            x = self.frame_width - text_size[0] - 60
            y = self.frame_height - 60
            cv2.putText(display, player_text, (x, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        
        # Health bars (always visible, top left and right)
        self.draw_health_bars(display, player_hp, mage_hp)
        
        # Instructions (move to bottom right)
        instructions = [
            "Use hand gestures to cast spells!",
            "Press Q to quit"
        ]
        for i, text in enumerate(instructions):
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0]
            x = self.frame_width - text_size[0] - 60
            y = self.frame_height - 30 + i * 25
            cv2.putText(display, text, (x, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1, cv2.LINE_AA)
    
    def draw_health_bars(self, display, player_hp, mage_hp):
        """Draw health bars for both player and mage"""
        bar_width = 350
        bar_height = 35
        max_hp = 100
        
        # Player health bar (top right)
        player_x = self.frame_width - bar_width - 40
        player_y = 30
        
        # Background
        cv2.rectangle(display, (player_x, player_y), (player_x + bar_width, player_y + bar_height), 
                     (60, 60, 60), -1)
        # Health
        current_width = int(bar_width * (max(0, player_hp) / max_hp))
        cv2.rectangle(display, (player_x, player_y), (player_x + current_width, player_y + bar_height), 
                     (0, 255, 0), -1)
        # Border
        cv2.rectangle(display, (player_x, player_y), (player_x + bar_width, player_y + bar_height), 
                     (255, 255, 255), 2)
        # Text
        cv2.putText(display, f"PLAYER: {max(0, player_hp)}/{max_hp}", (player_x + 10, player_y + bar_height - 7), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Mage health bar (top left)
        mage_x = 40
        mage_y = 30
        
        # Background
        cv2.rectangle(display, (mage_x, mage_y), (mage_x + bar_width, mage_y + bar_height), 
                     (60, 60, 60), -1)
        # Health
        current_width = int(bar_width * (max(0, mage_hp) / max_hp))
        cv2.rectangle(display, (mage_x, mage_y), (mage_x + current_width, mage_y + bar_height), 
                     (0, 0, 255), -1)
        # Border
        cv2.rectangle(display, (mage_x, mage_y), (mage_x + bar_width, mage_y + bar_height), 
                     (255, 255, 255), 2)
        # Text
        cv2.putText(display, f"MAGE: {max(0, mage_hp)}/{max_hp}", (mage_x + 10, mage_y + bar_height - 7), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    def cleanup(self):
        """Clean up resources"""
        if self.idle_cap:
            self.idle_cap.release()
        if self.attack_cap:
            self.attack_cap.release() 