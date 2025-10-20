"""
Script to build the CoFoundersLab Bot into an executable file
"""
import subprocess
import sys
import os

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller is already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building CoFoundersLab Bot executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",  # Create a single executable file
        "--windowed",  # Don't show console window
        "--name=CoFoundersLab_Bot",  # Name of the executable
        "--icon=icon.ico",  # Icon file (if exists)
        "--add-data=requirements.txt;.",  # Include requirements file
        "cofounderslab_bot.py"
    ]
    
    # Remove icon parameter if icon file doesn't exist
    if not os.path.exists("icon.ico"):
        cmd.remove("--icon=icon.ico")
    
    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Executable created successfully!")
        print("📁 Location: dist/CoFoundersLab_Bot.exe")
        print("\n📋 Instructions:")
        print("1. Copy the .exe file to any folder")
        print("2. Make sure Chrome browser is installed")
        print("3. Run the .exe file")
        print("4. The bot will automatically download ChromeDriver")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building executable: {e}")
        return False
    
    return True

def main():
    print("🚀 CoFoundersLab Bot - Executable Builder")
    print("=" * 50)
    
    # Check if main script exists
    if not os.path.exists("cofounderslab_bot.py"):
        print("❌ Error: cofounderslab_bot.py not found!")
        print("Make sure you're running this script in the same folder as cofounderslab_bot.py")
        return
    
    # Install PyInstaller
    install_pyinstaller()
    
    # Build executable
    if build_executable():
        print("\n🎉 Build completed successfully!")
    else:
        print("\n💥 Build failed!")

if __name__ == "__main__":
    main()
