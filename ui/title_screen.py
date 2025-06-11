import cv2
import numpy as np
import time

class TitleScreen:
    def __init__(self):
        self.idle_video_path = "assets/mageIdle.mkv"
        self.cap = None
        self.frame_width = 800
        self.frame_height = 600
        self.title = "WIZARD FIGHT"
        self.difficulties = [
            {"name": "EASY", "key": "1", "color": (0, 255, 0)},
            {"name": "MEDIUM", "key": "2", "color": (0, 255, 255)},
            {"name": "HARD", "key": "3", "color": (0, 0, 255)}
        ]
        self.selected_difficulty = 0
        self.animation_frame = None
        self.frame_count = 0
        
    def load_idle_animation(self):
        """Load the idle animation video"""
        self.cap = cv2.VideoCapture(self.idle_video_path)
        if not self.cap.isOpened():
            print(f"Error: Could not open {self.idle_video_path}")
            return False
        return True
    
    def get_next_animation_frame(self):
        """Get the next frame from the idle animation"""
        if self.cap is None:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            # Loop the animation
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()
            
        if ret:
            # Resize frame to fit our display
            frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            return frame
        return None
    
    def draw_title(self, image):
        """Draw the main title with a magical effect"""
        # Create a gradient background for the title area
        title_height = 120
        title_y = 50  # Keep banner position the same
        
        # Draw semi-transparent overlay for title area
        overlay = image.copy()
        cv2.rectangle(overlay, (0, title_y - 20), (self.frame_width, title_y + title_height), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
        
        # Draw title with shadow effect
        title_size = cv2.getTextSize(self.title, cv2.FONT_HERSHEY_DUPLEX, 2.5, 4)[0]
        
        # Calculate box dimensions to perfectly center the title
        box_width = title_size[0] + 40  # 20 pixels padding on each side
        box_height = title_size[1] + 20  # 10 pixels padding on top and bottom
        box_x = (self.frame_width - box_width) // 2
        box_y = title_y + 20  # Move the text box down within the banner
        
        # Calculate text position to be perfectly centered within the box
        text_x = box_x + (box_width - title_size[0]) // 2
        text_y = box_y + (box_height + title_size[1]) // 2
        
        # Draw title box with outline
        cv2.rectangle(image, (box_x, box_y), (box_x + box_width, box_y + box_height), (255, 215, 0), 2)
        
        # Shadow
        cv2.putText(image, self.title, (text_x + 3, text_y), 
                   cv2.FONT_HERSHEY_DUPLEX, 2.5, (50, 50, 50), 4, cv2.LINE_AA)
        # Main text
        cv2.putText(image, self.title, (text_x, text_y), 
                   cv2.FONT_HERSHEY_DUPLEX, 2.5, (255, 215, 0), 4, cv2.LINE_AA)
        
        # Add magical sparkle effect
        sparkle_color = (255, 255, 255)
        sparkle_positions = [
            (box_x - 30, box_y + box_height // 2),
            (box_x + box_width + 30, box_y + box_height // 2),
            (box_x + box_width // 2, box_y - 10)
        ]
        
        for pos in sparkle_positions:
            cv2.circle(image, pos, 3, sparkle_color, -1)
            cv2.circle(image, pos, 6, sparkle_color, 1)
    
    def draw_difficulty_options(self, image):
        """Draw the difficulty selection options with a glow effect for the selected one"""
        options_start_y = 250
        option_height = 50  # Reduced from 60
        option_spacing = 15  # Increased slightly to prevent overlap
        
        # Draw semi-transparent background for options
        overlay = image.copy()
        cv2.rectangle(overlay, (50, options_start_y - 20), 
                     (self.frame_width - 50, options_start_y + len(self.difficulties) * (option_height + option_spacing) + 20), 
                     (30, 30, 60), -1)
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
        
        for i, difficulty in enumerate(self.difficulties):
            y_pos = options_start_y + i * (option_height + option_spacing)
            text = f"{difficulty['name']}"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.5, 3)[0]
            
            # Calculate box dimensions to perfectly center the text
            box_width = text_size[0] + 30  # 15 pixels padding on each side
            box_height = option_height
            box_x = (self.frame_width - box_width) // 2
            box_y = y_pos
            
            # Calculate text position to be perfectly centered within the box
            text_x = box_x + (box_width - text_size[0]) // 2
            text_y = box_y + (box_height + text_size[1]) // 2  # Center vertically within the box
            
            if i == self.selected_difficulty:
                # Smaller glow effect: draw smaller colored rectangle behind
                glow_color = tuple(int(c * 0.7 + 180) for c in difficulty['color'])
                for g in range(8, 0, -2):  # Reduced glow size
                    cv2.rectangle(image, (box_x-g, box_y-g), (box_x+box_width+g, box_y+box_height+g), glow_color, -1)
                # Perfectly centered selection box
                cv2.rectangle(image, (box_x, box_y), (box_x+box_width, box_y+box_height), (255,255,255), 2)
            
            # Shadow
            cv2.putText(image, text, (text_x+2, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (40,40,40), 3, cv2.LINE_AA)
            # Main text
            cv2.putText(image, text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, difficulty['color'], 3, cv2.LINE_AA)
    
    def draw_instructions(self, image):
        """Draw smaller instructions at the bottom with proper centering and outline"""
        instructions = [
            "Use W/S to select difficulty",
            "Press ENTER to start the game",
            "Press Q to quit"
        ]
        
        # Calculate total height needed for all instructions
        instruction_height = 18  # Height per instruction
        total_height = len(instructions) * instruction_height
        y_start = self.frame_height - 70  # Moved up slightly
        
        # Calculate the widest instruction for centering
        max_width = 0
        for instruction in instructions:
            text_size = cv2.getTextSize(instruction, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            max_width = max(max_width, text_size[0])
        
        # Calculate box dimensions
        box_width = max_width + 40  # 20 pixels padding on each side
        box_height = total_height + 20  # 10 pixels padding on top and bottom
        box_x = (self.frame_width - box_width) // 2
        box_y = y_start - 10
        
        # Semi-transparent background
        overlay = image.copy()
        cv2.rectangle(overlay, (box_x, box_y), (box_x + box_width, box_y + box_height), (30,30,60), -1)
        cv2.addWeighted(overlay, 0.7, image, 0.3, 0, image)
        
        # Draw outline around instructions
        cv2.rectangle(image, (box_x, box_y), (box_x + box_width, box_y + box_height), (220, 220, 255), 1)
        
        for i, instruction in enumerate(instructions):
            text_size = cv2.getTextSize(instruction, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
            
            # Calculate text position to be perfectly centered within the box
            text_x = box_x + (box_width - text_size[0]) // 2
            text_y = box_y + 15 + i * instruction_height  # Start 15 pixels from top of box
            
            cv2.putText(image, instruction, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 255), 1, cv2.LINE_AA)

    def handle_input(self, key):
        """Handle keyboard input for menu navigation (W/S/Enter only)"""
        if key == ord('w'):
            self.selected_difficulty = (self.selected_difficulty - 1) % len(self.difficulties)
        elif key == ord('s'):
            self.selected_difficulty = (self.selected_difficulty + 1) % len(self.difficulties)
        elif key == 13:  # Enter key
            return self.difficulties[self.selected_difficulty]['name'].lower()
        elif key == ord('q'):
            return "quit"
        return None
    
    def cleanup(self, destroy_all=True):
        """Clean up resources"""
        if self.cap:
            self.cap.release()
        if destroy_all:
            cv2.destroyAllWindows()
        else:
            # Just destroy the title screen window, keep other windows open
            try:
                cv2.destroyWindow("Wizard Fight - Title Screen")
            except:
                pass  # Window might not exist
    
    def show(self):
        """Display the title screen and return selected difficulty"""
        if not self.load_idle_animation():
            print("Failed to load idle animation, using fallback")
            return "easy"  # Fallback difficulty
        
        # Create a unique window name to avoid conflicts
        window_name = "Wizard Fight - Title Screen"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, self.frame_width, self.frame_height)
        
        print("Welcome to Wizard Fight!")
        print("Select your difficulty and press ENTER to begin...")
        
        while True:
            # Get animation frame
            animation_frame = self.get_next_animation_frame()
            if animation_frame is None:
                # Fallback: create a dark background
                image = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
                image[:] = (30, 30, 50)  # Dark blue background
            else:
                image = animation_frame.copy()
            
            # Draw UI elements
            self.draw_title(image)
            self.draw_difficulty_options(image)
            self.draw_instructions(image)
            
            # Display the frame
            cv2.imshow(window_name, image)
            
            # Handle input
            key = cv2.waitKey(30) & 0xFF
            result = self.handle_input(key)
            
            if result:
                # Don't destroy all windows if we're transitioning to the game
                self.cleanup(destroy_all=(result == "quit"))
                return result

def main():
    """Main function to test the title screen"""
    title_screen = TitleScreen()
    selected_difficulty = title_screen.show()
    
    if selected_difficulty == "quit":
        print("Game cancelled by user")
    else:
        print(f"Selected difficulty: {selected_difficulty.upper()}")
        print("Starting game...")
        # Here you would start the main game with the selected difficulty
        return selected_difficulty

if __name__ == "__main__":
    main() 