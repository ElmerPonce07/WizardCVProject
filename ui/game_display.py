import cv2
import numpy as np
import time

class GameDisplay:
    def __init__(self, frame_width=1920, frame_height=1080):
        self.frame_width = frame_width
        self.frame_height = frame_height
        
        # Animation paths
        self.idle_video_path = "assets/mageIdle.mkv"
        self.attack_video_path = "assets/MageAttack.mkv"
        self.mage_defeat_video_path = "assets/mageDefeat.mkv"  # User wins
        self.mage_victory_video_path = "assets/mageVictory.mkv"  # Mage wins
        
        # Video captures
        self.idle_cap = None
        self.attack_cap = None
        self.defeat_cap = None
        self.victory_cap = None
        
        # Camera settings
        self.camera_width = 480  # Bigger camera size
        self.camera_height = 360
        self.camera_x = 20  # Bottom left position
        self.camera_y = frame_height - self.camera_height - 20
        
        # Animation state
        self.current_animation = "idle"  # "idle", "attack", "defeat", "victory"
        self.attack_start_time = None
        self.attack_duration = None  # Will be set based on video length
        self.last_frame_time = 0
        self.frame_interval = 1.0 / 120.0  # Target 120 FPS
        
        # Load animations
        self.load_animations()
    
    def load_animations(self):
        """Load all animations including defeat and victory"""
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
        
        # Load defeat animation (user wins)
        self.defeat_cap = cv2.VideoCapture(self.mage_defeat_video_path)
        if not self.defeat_cap.isOpened():
            print(f"Warning: Could not open {self.mage_defeat_video_path}")
        
        # Load victory animation (mage wins)
        self.victory_cap = cv2.VideoCapture(self.mage_victory_video_path)
        if not self.victory_cap.isOpened():
            print(f"Warning: Could not open {self.mage_victory_video_path}")
    
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
        elif self.current_animation == "defeat" and self.defeat_cap and self.defeat_cap.isOpened():
            # Play defeat animation (user wins)
            ret, frame = self.defeat_cap.read()
            if not ret:
                # Loop defeat animation
                self.defeat_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.defeat_cap.read()
        elif self.current_animation == "victory" and self.victory_cap and self.victory_cap.isOpened():
            # Play victory animation (mage wins)
            ret, frame = self.victory_cap.read()
            if not ret:
                # Loop victory animation
                self.victory_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.victory_cap.read()
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
        
        # Resize and place user camera in bottom left with optimized styling
        if camera_frame is not None:
            camera_resized = cv2.resize(camera_frame, (self.camera_width, self.camera_height))
            # Draw hand tracking on the user camera if landmarks are provided
            # Show only finger tip dots, no connecting lines
            if hand_landmarks is not None and mp_draw is not None and mp_hands is not None:
                for handLms in hand_landmarks:
                    # Draw only the finger tip landmarks (dots) without connections
                    for landmark in handLms.landmark:
                        # Convert normalized coordinates to pixel coordinates
                        x = int(landmark.x * self.camera_width)
                        y = int(landmark.y * self.camera_height)
                        # Draw small dots for finger tips
                        cv2.circle(camera_resized, (x, y), 2, (0, 255, 0), -1)
            
            # Place camera frame
            display[self.camera_y:self.camera_y + self.camera_height, 
                   self.camera_x:self.camera_x + self.camera_width] = camera_resized
            
            # Simple modern border
            cv2.rectangle(display, (self.camera_x - 3, self.camera_y - 3), 
                         (self.camera_x + self.camera_width + 3, self.camera_y + self.camera_height + 3), 
                         (100, 100, 150), 1)
            cv2.rectangle(display, (self.camera_x - 2, self.camera_y - 2), 
                         (self.camera_x + self.camera_width + 2, self.camera_y + self.camera_height + 2), 
                         (255, 255, 255), 2)
        
        # Add game UI elements
        self.draw_game_ui(display, mage_spell, player_spell, countdown, player_hp, mage_hp, round_num)
        
        return display
    
    def draw_game_ui(self, display, mage_spell, player_spell, countdown, player_hp, mage_hp, round_num):
        """Draw all UI elements on the display with optimized modern styling"""
        
        # Round number with simple glow effect
        round_text = f"ROUND {round_num}"
        round_x = 50
        round_y = 60
        
        # Simple glow effect for round number
        cv2.putText(display, round_text, (round_x + 2, round_y + 2), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (100, 100, 150), 3, cv2.LINE_AA)
        cv2.putText(display, round_text, (round_x, round_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)
        
        # Mage spell announcement - optimized but still prominent
        if mage_spell:
            spell_text = f"MAGE CASTS: {mage_spell.upper()}"
            text_size = cv2.getTextSize(spell_text, cv2.FONT_HERSHEY_SIMPLEX, 2.0, 5)[0]
            x = (self.frame_width - text_size[0]) // 2
            y = 150
            
            # Get spell-specific colors
            if mage_spell.upper() == "FIRE":
                text_color = (0, 0, 255)  # Red (BGR)
                glow_color = (50, 0, 0)   # Dark red glow
                border_color = (0, 0, 255)  # Red border
            elif mage_spell.upper() == "WATER":
                text_color = (255, 0, 0)  # Blue (BGR)
                glow_color = (0, 0, 50)   # Dark blue glow
                border_color = (255, 0, 0)  # Blue border
            elif mage_spell.upper() == "EARTH":
                text_color = (19, 69, 139)  # Brown (BGR)
                glow_color = (10, 35, 70)   # Dark brown glow
                border_color = (19, 69, 139)  # Brown border
            else:
                # Default colors
                text_color = (0, 0, 255)  # Red
                glow_color = (50, 0, 0)   # Dark red
                border_color = (255, 255, 255)  # White border
            
            # Simple background with colored border
            cv2.rectangle(display, (x - 30, y - text_size[1] - 20), 
                         (x + text_size[0] + 30, y + 20), (0, 0, 0), -1)
            cv2.rectangle(display, (x - 30, y - text_size[1] - 20), 
                         (x + text_size[0] + 30, y + 20), border_color, 3)
            
            # Glow effect with spell color
            cv2.putText(display, spell_text, (x + 2, y + 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2.0, glow_color, 5, cv2.LINE_AA)
            cv2.putText(display, spell_text, (x, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2.0, text_color, 5, cv2.LINE_AA)
        
        # Countdown timer with simple styling
        if countdown is not None and countdown > 0:
            countdown_text = f"Counter in: {countdown:.1f}s"
            countdown_size = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
            countdown_x = 50
            countdown_y = 250
            
            # Simple background
            cv2.rectangle(display, (countdown_x - 10, countdown_y - countdown_size[1] - 10), 
                         (countdown_x + countdown_size[0] + 10, countdown_y + 10), (0, 0, 0), -1)
            cv2.rectangle(display, (countdown_x - 10, countdown_y - countdown_size[1] - 10), 
                         (countdown_x + countdown_size[0] + 10, countdown_y + 10), (255, 255, 0), 2)
            
            cv2.putText(display, countdown_text, (countdown_x, countdown_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3, cv2.LINE_AA)
        elif countdown is not None:
            countdown_text = f"Counter in: 0.0s"
            countdown_size = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)[0]
            countdown_x = 50
            countdown_y = 250
            
            # Simple background
            cv2.rectangle(display, (countdown_x - 10, countdown_y - countdown_size[1] - 10), 
                         (countdown_x + countdown_size[0] + 10, countdown_y + 10), (0, 0, 0), -1)
            cv2.rectangle(display, (countdown_x - 10, countdown_y - countdown_size[1] - 10), 
                         (countdown_x + countdown_size[0] + 10, countdown_y + 10), (0, 0, 255), 2)
            
            cv2.putText(display, countdown_text, (countdown_x, countdown_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3, cv2.LINE_AA)
        
        # Player spell display with simple styling - positioned on top of webcam
        if player_spell:
            player_text = f"YOUR SPELL: {player_spell.upper()}"
            text_size = cv2.getTextSize(player_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            
            # Position above webcam (bottom left area) - moved higher
            x = self.camera_x + 10  # 10 pixels from left edge of webcam
            y = self.camera_y - 40  # 40 pixels above webcam (moved up from 10)
            
            # Get spell-specific colors (same as mage)
            if player_spell.upper() == "FIRE":
                text_color = (0, 0, 255)  # Red (BGR)
                glow_color = (50, 0, 0)   # Dark red glow
                border_color = (0, 0, 255)  # Red border
            elif player_spell.upper() == "WATER":
                text_color = (255, 0, 0)  # Blue (BGR)
                glow_color = (0, 0, 50)   # Dark blue glow
                border_color = (255, 0, 0)  # Blue border
            elif player_spell.upper() == "EARTH":
                text_color = (19, 69, 139)  # Brown (BGR)
                glow_color = (10, 35, 70)   # Dark brown glow
                border_color = (19, 69, 139)  # Brown border
            else:
                # Default colors
                text_color = (0, 255, 0)  # Green
                glow_color = (0, 100, 0)   # Dark green
                border_color = (0, 255, 0)  # Green border
            
            # Simple background with colored border
            cv2.rectangle(display, (x - 10, y - text_size[1] - 5), 
                         (x + text_size[0] + 10, y + 5), (0, 0, 0), -1)
            cv2.rectangle(display, (x - 10, y - text_size[1] - 5), 
                         (x + text_size[0] + 10, y + 5), border_color, 2)
            
            # Glow effect with spell color
            cv2.putText(display, player_text, (x + 1, y + 1), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, glow_color, 2, cv2.LINE_AA)
            cv2.putText(display, player_text, (x, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2, cv2.LINE_AA)
        
        # Health bars (optimized)
        self.draw_health_bars(display, player_hp, mage_hp)
        
        # Instructions with simple styling
        instructions = [
            "Use hand gestures to cast spells!",
            "Press Q to quit"
        ]
        for i, text in enumerate(instructions):
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1)[0]
            x = self.frame_width - text_size[0] - 60
            y = self.frame_height - 30 + i * 25
            
            # Simple semi-transparent background
            cv2.rectangle(display, (x - 10, y - text_size[1] - 5), 
                         (x + text_size[0] + 10, y + 5), (30, 30, 60), -1)
            
            cv2.putText(display, text, (x, y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1, cv2.LINE_AA)
    
    def draw_health_bars(self, display, player_hp, mage_hp):
        """Draw optimized health bars for both player and mage"""
        bar_width = 350
        bar_height = 35
        max_hp = 100
        
        # Player health bar (top right) with simple styling
        player_x = self.frame_width - bar_width - 40
        player_y = 30
        
        # Simple background
        cv2.rectangle(display, (player_x, player_y), (player_x + bar_width, player_y + bar_height), 
                     (60, 60, 60), -1)
        
        # Health fill
        current_width = int(bar_width * (max(0, player_hp) / max_hp))
        cv2.rectangle(display, (player_x, player_y), (player_x + current_width, player_y + bar_height), 
                     (0, 255, 0), -1)
        
        # Simple glow effect
        cv2.rectangle(display, (player_x - 2, player_y - 2), (player_x + bar_width + 2, player_y + bar_height + 2), 
                     (0, 100, 0), 1)
        
        # Border
        cv2.rectangle(display, (player_x, player_y), (player_x + bar_width, player_y + bar_height), 
                     (255, 255, 255), 2)
        
        # Text with simple glow
        text = f"PLAYER: {max(0, player_hp)}/{max_hp}"
        cv2.putText(display, text, (player_x + 10 + 1, player_y + bar_height - 7 + 1), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 100, 0), 2)
        cv2.putText(display, text, (player_x + 10, player_y + bar_height - 7), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        # Mage health bar (top left) with simple styling
        mage_x = 40
        mage_y = 30
        
        # Simple background
        cv2.rectangle(display, (mage_x, mage_y), (mage_x + bar_width, mage_y + bar_height), 
                     (60, 60, 60), -1)
        
        # Health fill
        current_width = int(bar_width * (max(0, mage_hp) / max_hp))
        cv2.rectangle(display, (mage_x, mage_y), (mage_x + current_width, mage_y + bar_height), 
                     (0, 0, 255), -1)
        
        # Simple glow effect
        cv2.rectangle(display, (mage_x - 2, mage_y - 2), (mage_x + bar_width + 2, mage_y + bar_height + 2), 
                     (0, 0, 100), 1)
        
        # Border
        cv2.rectangle(display, (mage_x, mage_y), (mage_x + bar_width, mage_y + bar_height), 
                     (255, 255, 255), 2)
        
        # Text with simple glow
        text = f"MAGE: {max(0, mage_hp)}/{max_hp}"
        cv2.putText(display, text, (mage_x + 10 + 1, mage_y + bar_height - 7 + 1), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 100), 2)
        cv2.putText(display, text, (mage_x + 10, mage_y + bar_height - 7), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    def create_win_defeat_screen(self, result, player_hp, mage_hp, round_num):
        """Create a win/defeat screen using video animations"""
        # Don't override animation state - it should already be set correctly
        if result == "player":
            # Player defeated (mage wins)
            result_text = "DEFEAT"
            result_color = (0, 0, 255)  # Red
            subtitle = "The mage has defeated you!"
        elif result == "mage":
            # Mage defeated (player wins)
            result_text = "VICTORY"
            result_color = (0, 255, 0)  # Green
            subtitle = "You have defeated the mage!"
        else:
            # Fallback
            result_text = "GAME OVER"
            result_color = (255, 255, 0)  # Yellow
            subtitle = "The battle has ended!"
        
        # Get the animation frame as background
        display = self.get_animation_frame()
        if display is None:
            # Fallback: create a dark background
            display = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
            display[:] = (20, 20, 30)
        
        # Semi-transparent overlay for the UI elements
        overlay = display.copy()
        cv2.rectangle(overlay, (0, 0), (self.frame_width, self.frame_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.3, display, 0.7, 0, display)
        
        # Draw main result text with glow effect
        text_size = cv2.getTextSize(result_text, cv2.FONT_HERSHEY_DUPLEX, 4.0, 6)[0]
        text_x = (self.frame_width - text_size[0]) // 2
        text_y = self.frame_height // 2 - 50
        
        # Glow effect
        for g in range(8, 0, -2):
            glow_color = tuple(int(c * 0.3) for c in result_color)
            cv2.putText(display, result_text, (text_x + g, text_y + g), 
                       cv2.FONT_HERSHEY_DUPLEX, 4.0, glow_color, 6, cv2.LINE_AA)
        
        # Main text
        cv2.putText(display, result_text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_DUPLEX, 4.0, result_color, 6, cv2.LINE_AA)
        
        # Draw subtitle
        subtitle_size = cv2.getTextSize(subtitle, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
        subtitle_x = (self.frame_width - subtitle_size[0]) // 2
        subtitle_y = text_y + 100
        
        cv2.putText(display, subtitle, (subtitle_x, subtitle_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)
        
        # Draw final stats
        stats_y = subtitle_y + 80
        stats_text = f"Final Round: {round_num} | Player HP: {max(0, player_hp)} | Mage HP: {max(0, mage_hp)}"
        stats_size = cv2.getTextSize(stats_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
        stats_x = (self.frame_width - stats_size[0]) // 2
        
        cv2.putText(display, stats_text, (stats_x, stats_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 200), 2, cv2.LINE_AA)
        
        # Draw instructions
        instructions = [
            "Press ENTER to play again",
            "Press Q to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_size = cv2.getTextSize(instruction, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
            inst_x = (self.frame_width - inst_size[0]) // 2
            inst_y = self.frame_height - 100 + i * 40
            
            # Background for instruction
            cv2.rectangle(display, (inst_x - 20, inst_y - inst_size[1] - 10), 
                         (inst_x + inst_size[0] + 20, inst_y + 10), (0, 0, 0), -1)
            cv2.rectangle(display, (inst_x - 20, inst_y - inst_size[1] - 10), 
                         (inst_x + inst_size[0] + 20, inst_y + 10), (255, 255, 255), 2)
            
            cv2.putText(display, instruction, (inst_x, inst_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
        
        return display
    
    def cleanup(self):
        """Clean up resources"""
        if self.idle_cap:
            self.idle_cap.release()
        if self.attack_cap:
            self.attack_cap.release()
        if self.defeat_cap:
            self.defeat_cap.release()
        if self.victory_cap:
            self.victory_cap.release()
    
    def start_defeat_animation(self):
        """Start the defeat animation (user wins)"""
        self.current_animation = "defeat"
        # Reset defeat video to beginning
        if self.defeat_cap and self.defeat_cap.isOpened():
            self.defeat_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    
    def start_victory_animation(self):
        """Start the victory animation (mage wins)"""
        self.current_animation = "victory"
        # Reset victory video to beginning
        if self.victory_cap and self.victory_cap.isOpened():
            self.victory_cap.set(cv2.CAP_PROP_POS_FRAMES, 0) 