"""
Script to create a simple icon for the CoFoundersLab Bot executable
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Create a simple icon for the bot"""
    try:
        # Create a 64x64 icon
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a robot-like icon
        # Head (circle)
        draw.ellipse([10, 10, 54, 54], fill=(70, 130, 180), outline=(0, 0, 0), width=2)
        
        # Eyes
        draw.ellipse([20, 20, 26, 26], fill=(255, 255, 255))
        draw.ellipse([38, 20, 44, 26], fill=(255, 255, 255))
        
        # Eye pupils
        draw.ellipse([22, 22, 24, 24], fill=(0, 0, 0))
        draw.ellipse([40, 22, 42, 24], fill=(0, 0, 0))
        
        # Mouth
        draw.arc([25, 35, 39, 45], 0, 180, fill=(0, 0, 0), width=2)
        
        # Body (rectangle)
        draw.rectangle([20, 50, 44, 60], fill=(70, 130, 180), outline=(0, 0, 0), width=2)
        
        # Save as ICO file
        img.save('icon.ico', format='ICO', sizes=[(64, 64), (32, 32), (16, 16)])
        print("✅ Icon created: icon.ico")
        return True
        
    except ImportError:
        print("❌ PIL (Pillow) not installed. Creating simple icon...")
        # Create a simple text-based icon
        try:
            with open('icon.ico', 'wb') as f:
                # Minimal ICO file header
                f.write(b'\x00\x00\x01\x00\x01\x00\x10\x10\x00\x00\x01\x00\x08\x00\x68\x05\x00\x00')
                f.write(b'\x00' * 1400)  # Simple placeholder
            print("✅ Simple icon created: icon.ico")
            return True
        except:
            print("❌ Could not create icon")
            return False
    except Exception as e:
        print(f"❌ Error creating icon: {e}")
        return False

if __name__ == "__main__":
    print("🎨 Creating CoFoundersLab Bot Icon...")
    create_icon()
