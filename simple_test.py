#!/usr/bin/env python3
"""
Simple test to verify title screen and camera integration
"""

import cv2
import time

def main():
    print("🧪 Simple Integration Test 🧪")
    print("=" * 30)
    
    # Initialize camera first
    print("1. Initializing camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Failed to open camera!")
        return
    
    print("✅ Camera initialized successfully!")
    
    # Test title screen
    print("2. Testing title screen...")
    from title_screen import TitleScreen
    
    title_screen = TitleScreen()
    difficulty = title_screen.show()
    
    print(f"✅ Title screen completed. Selected: {difficulty}")
    
    if difficulty == "quit":
        print("User quit, cleaning up...")
        cap.release()
        cv2.destroyAllWindows()
        return
    
    # Test camera still works after title screen
    print("3. Testing camera after title screen...")
    
    # Try to read a few frames
    for i in range(3):
        ret, frame = cap.read()
        if ret:
            print(f"✅ Frame {i+1}: {frame.shape}")
        else:
            print(f"❌ Frame {i+1}: Failed to read")
            break
    
    # Show a simple camera feed for a few seconds
    print("4. Showing camera feed for 3 seconds...")
    start_time = time.time()
    while time.time() - start_time < 3:
        ret, frame = cap.read()
        if ret:
            cv2.putText(frame, "Camera working!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("Camera Test", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("❌ Failed to read camera frame!")
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    print("✅ Test completed successfully!")
    print("You can now run the full game!")

if __name__ == "__main__":
    main() 