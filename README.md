# D-Day Counter Widget

A beautiful, interactive desktop widget for tracking special days with real-time chat functionality. Built with Python and tkinter, featuring Firebase integration for seamless communication between users.

## Features

### 🎯 Core Functionality
- **Day Counter**: Track days since a special date with automatic updates
- **Real-time Chat**: Firebase-powered messaging system for instant communication
- **Desktop Widget**: Always-on-top, semi-transparent overlay that adapts to your desktop
- **User Authentication**: Secure login system with password protection
- **System Tray Integration**: Minimize to system tray for background operation

### 🎨 Visual Effects
- **Animated Heart**: Pulsating heart with gradient color transitions
- **Sparkle Effects**: Magical sparkle animations across the widget
- **Dynamic Background**: Automatically adapts colors based on desktop background
- **Notification System**: Visual and audio alerts for new messages
- **Celebration Effects**: Special animations for milestone days (every 100 days)

### 💬 Chat Features
- **Expandable Chat Interface**: Toggle between compact and full chat view
- **Message History**: Last 5 messages with auto-cleanup
- **User Identification**: Color-coded messages for different users
- **Timestamp Display**: Time stamps for all messages
- **Emoji Support**: Rich emoji support in messages
- **Read Status Tracking**: Keep track of read/unread messages

## Demo

### 🎬 Application Overview
![D-Day Widget Demo](./media/demo.gif)
*Complete demonstration of the D-Day widget featuring day counter, animations, and chat functionality*

### 📱 Widget in Action

#### Compact Mode
![Compact Widget](./media/compact-mode.gif)
*Widget in compact mode showing day counter with animated heart and sparkle effects*

#### Chat Interface
![Chat Demo](./media/chat-demo.gif)
*Real-time chat functionality with message exchange between users*

#### Visual Effects
![Effects Demo](./media/effects-demo.gif)
*Animated heart, sparkle effects, and milestone celebrations*

### 🖥️ Screenshots

<div align="center">
  <img src="./media/screenshot-compact.png" alt="Compact Mode" width="300"/>
  <img src="./media/screenshot-chat.png" alt="Chat Interface" width="300"/>
</div>

*Left: Widget in compact mode | Right: Expanded chat interface*

### 🎥 Video Tutorial

[![Setup and Usage Tutorial](./media/video-thumbnail.png)](./media/setup-tutorial.mp4)
*Click to watch the complete setup and usage tutorial*

## Installation

### Prerequisites

Before running the application, ensure you have the following installed:

```bash
# Python 3.7 or higher
python --version

# Required packages
pip install tkinter
pip install pillow
pip install pystray
pip install requests
pip install pywin32
```

### Required Python Packages

Install all dependencies using pip:

```bash
pip install -r requirements.txt
```

Create a `requirements.txt` file with the following content:

```
Pillow>=8.0.0
pystray>=0.19.0
requests>=2.25.0
pywin32>=300; sys_platform == "win32"
```

## Firebase Setup

This application uses Firebase Realtime Database for the chat functionality. Follow these steps to set up Firebase:

### 1. Create a Firebase Project

1. Go to the [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter your project name (e.g., "dday-widget")
4. Choose whether to enable Google Analytics (optional)
5. Click "Create project"

### 2. Set up Realtime Database

1. In your Firebase project, navigate to "Realtime Database" in the left sidebar
2. Click "Create Database"
3. Choose your database location (preferably closest to your users)
4. Start in **test mode** for development (you can configure security rules later)
5. Click "Done"

### 3. Get Your Database URL

1. In the Realtime Database section, you'll see your database URL
2. It will look like: `https://your-project-name-default-rtdb.region.firebasedatabase.app/`
3. Copy this URL

### 4. Configure the Application

1. Open `dday_widget.py`
2. Find the line: `self.firebase_url = "YOUR_FIREBASE_REALTIME_DATABASE_URL"`
3. Replace `"YOUR_FIREBASE_REALTIME_DATABASE_URL"` with your actual Firebase URL

Example:
```python
self.firebase_url = "https://my-dday-widget-default-rtdb.asia-southeast1.firebasedatabase.app/"
```

### 5. Security Rules (Recommended for Production)

For production use, configure your Firebase security rules. In the Firebase Console:

1. Go to Realtime Database > Rules
2. Replace the default rules with:

```json
{
  "rules": {
    "messages": {
      ".read": true,
      ".write": true,
      "$messageId": {
        ".validate": "newData.hasChildren(['user', 'text', 'timestamp'])"
      }
    }
  }
}
```

This allows read/write access to the messages node while validating the data structure.

### 6. Database Structure

The application will automatically create the following structure in your Firebase database:

```
your-database/
└── messages/
    ├── -messageId1/
    │   ├── user: "User1"
    │   ├── user_id: "unique-uuid"
    │   ├── text: "Hello!"
    │   └── timestamp: "2024-01-01 12:00:00"
    └── -messageId2/
        ├── user: "User2"
        ├── user_id: "unique-uuid"
        ├── text: "Hi there!"
        └── timestamp: "2024-01-01 12:01:00"
```

## Configuration

### Application Settings

You can customize the application by modifying these variables in `dday_widget.py`:

```python
# Starting date for the counter
self.start_date = date(2024, 1, 1)  # Change to your special date

# Authentication password
SECRET_PASSWORD = "1234"  # Change to your preferred password

# Data storage directory
self.app_data_dir = r'C:\DdayWidget'  # Customize storage location
```

### User Configuration

- **Password**: Default is "1234" - change this in the code for security
- **Users**: Two users are supported: "User1" and "User2"
- **Start Date**: Modify `self.start_date` to your special date

## Usage

### Running the Application

1. **Direct Python execution**:
   ```bash
   python dday_widget.py
   ```

2. **Using PyInstaller** (for standalone executable):
   ```bash
   pyinstaller --onefile --windowed --icon=image.ico --name="dday_widget" --uac-admin dday_widget.py
   ```

### First Time Setup

1. **Authentication**: Enter the password (default: "1234") and select your user
2. **Positioning**: Drag the widget to your preferred screen location
3. **Chat Setup**: Click the chat button to expand the messaging interface

### Controls

- **Drag**: Click and drag anywhere on the widget to reposition
- **Right-click**: Access the context menu
- **Double-click**: Show exit confirmation dialog
- **Chat Button**: Toggle between compact and expanded modes
- **System Tray**: Minimize to tray, restore from tray icon

### Chat Usage

1. **Expand Chat**: Click the "💬 Chat" button
2. **Send Messages**: Type in the input field and press Enter or click ❤️
3. **View History**: Scroll through the last 5 messages
4. **Close Chat**: Click "🔼 Close" to return to compact mode

## File Structure

```
dday_project/
├── dday_widget.py          # Main application file
├── dday_widget.spec        # PyInstaller specification
├── anaconda_command.txt    # Build command reference
├── image.ico              # Application icon
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Generated Files (Runtime)

The application creates these files in `C:\DdayWidget\`:

- `dday_config.json`: Window position and settings
- `read_messages.json`: Message read status tracking
- `user_info.json`: User authentication data

## Building Executable

To create a standalone executable:

1. **Install PyInstaller**:
   ```bash
   pip install pyinstaller
   ```

2. **Build the executable**:
   ```bash
   pyinstaller dday_widget.spec
   ```

3. **Find your executable**:
   - The built executable will be in the `dist/` folder
   - File name: `dday_widget.exe`

### Build Options

The PyInstaller configuration includes:
- `--onefile`: Single executable file
- `--windowed`: No console window
- `--icon=image.ico`: Custom application icon
- `--uac-admin`: Request administrator privileges (if needed)

## Troubleshooting

### Common Issues

1. **Firebase Connection Errors**:
   - Verify your Firebase URL is correct
   - Check internet connection
   - Ensure Firebase project is active

2. **Authentication Issues**:
   - Delete `C:\DdayWidget\user_info.json` to reset authentication
   - Verify password matches the one in code

3. **Visual Issues**:
   - Try running as administrator if widgets don't appear correctly
   - Check if Windows transparency effects are enabled

4. **Performance Issues**:
   - The widget updates every 40ms for smooth animations
   - Disable animations by modifying the code if needed

### Debug Mode

To enable debug output, run from command line:

```bash
python dday_widget.py
```

This will show Firebase connection status and error messages in the console.

## Security Considerations

### For Production Use

1. **Change Default Password**: Modify `SECRET_PASSWORD` in the code
2. **Firebase Security Rules**: Implement proper authentication rules
3. **Data Validation**: The app includes basic data validation
4. **Local Data**: User data is stored locally in JSON files

### Privacy

- User messages are stored in Firebase Realtime Database
- Local storage includes user preferences and read status
- No personal data is transmitted beyond user-provided messages

## Customization

### Themes and Colors

Modify these variables in the code for different color schemes:

```python
# Gradient colors for heart animation
self.gradient_colors = ['#ff6b6b', '#ff8e8e', '#ffb3b3', '#ff8e8e', '#ff6b6b']

# Background and text colors
self.current_bg_color = '#2d2d3d'
```

### Animation Speed

Adjust animation timing:

```python
# Heart animation speed (milliseconds)
self.root.after(50, self.animate_heart)

# Sparkle frequency
self.root.after(3000, self.animate_sparkles)
```

### Message Limits

Change message history settings:

```python
# Maximum messages to keep
if len(messages) > 5:  # Change 5 to your preferred limit
    messages = messages[-5:]
```

## Media Files Setup

### 📁 Creating Demo Content

To add the demo GIFs and videos shown above, follow these steps:

#### Required Media Files
```
media/
├── demo.gif                 # Main application demo (10-15 seconds)
├── compact-mode.gif         # Compact widget animation (5-8 seconds)
├── chat-demo.gif           # Chat functionality demo (8-10 seconds)
├── effects-demo.gif        # Visual effects showcase (6-8 seconds)
├── screenshot-compact.png   # Static screenshot of compact mode
├── screenshot-chat.png     # Static screenshot of chat interface
├── video-thumbnail.png     # Thumbnail for video tutorial
└── setup-tutorial.mp4      # Complete setup tutorial (2-5 minutes)
```

#### 🎬 Recording Guidelines

**For GIF Creation:**
1. **Tools**: Use [ScreenToGif](https://www.screentogif.com/) (Windows) or [LICEcap](https://www.cockos.com/licecap/) (Cross-platform)
2. **Settings**: 
   - Frame rate: 10-15 FPS
   - Resolution: 800x600 or smaller
   - Duration: Keep under 15 seconds
   - File size: Aim for under 5MB per GIF

**Recording Scenarios:**

1. **demo.gif** - Main Demo:
   - Start with authentication dialog
   - Show compact widget with animations
   - Expand to chat interface
   - Send a few messages
   - Show notification effects
   - Return to compact mode

2. **compact-mode.gif** - Widget Animation:
   - Focus on the compact widget
   - Show heart animation and color changes
   - Include sparkle effects
   - Demonstrate drag functionality

3. **chat-demo.gif** - Chat Functionality:
   - Show expanded chat interface
   - Demonstrate typing and sending messages
   - Show message history
   - Include notification animations

4. **effects-demo.gif** - Visual Effects:
   - Capture celebration effects (milestone days)
   - Show heart animations
   - Demonstrate sparkle effects
   - Include background color adaptation

**For Screenshots:**
- Use high resolution (1920x1080 or higher)
- Crop to show only relevant parts
- Save as PNG for better quality
- Include both light and dark desktop backgrounds

**For Video Tutorial:**
- Use [OBS Studio](https://obsproject.com/) for recording
- Include audio narration
- Cover complete setup process:
  - Firebase configuration
  - Application installation
  - First-time usage
  - Feature demonstration
- Export as MP4 with H.264 codec

#### 📱 Optimization Tips

**GIF Optimization:**
```bash
# Using gifsicle (install via npm: npm install -g gifsicle)
gifsicle -O3 --resize-width 600 input.gif -o output.gif

# Using ffmpeg for better compression
ffmpeg -i input.gif -vf "fps=12,scale=600:-1" -loop 0 output.gif
```

**Image Optimization:**
```bash
# Using ImageOptim (macOS) or TinyPNG (web service)
# Aim for balance between quality and file size
```

### 🚀 Adding Media to Repository

1. **Create media folder**:
   ```bash
   mkdir media
   ```

2. **Add your files**:
   ```bash
   git add media/
   git commit -m "Add demo GIFs and screenshots"
   git push origin main
   ```

3. **Verify links**: Check that all media files display correctly on GitHub

### 📋 Media Checklist

- [ ] Record main demo GIF (demo.gif)
- [ ] Record compact mode GIF (compact-mode.gif)
- [ ] Record chat demo GIF (chat-demo.gif)
- [ ] Record effects demo GIF (effects-demo.gif)
- [ ] Take compact mode screenshot (screenshot-compact.png)
- [ ] Take chat interface screenshot (screenshot-chat.png)
- [ ] Create video thumbnail (video-thumbnail.png)
- [ ] Record setup tutorial video (setup-tutorial.mp4)
- [ ] Optimize all media files for web
- [ ] Test all links in README.md

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

### Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up Firebase (see Firebase Setup section)
4. Run the application: `python dday_widget.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Firebase for real-time database services
- Python tkinter for GUI framework
- PIL (Pillow) for image processing
- pystray for system tray integration

## Version History

- **v1.0**: Initial release with core functionality
  - Day counter with animated heart
  - Real-time chat via Firebase
  - System tray integration
  - Basic authentication system

## Support

For support, issues, or feature requests:
1. Check the [Issues](https://github.com/JIsseokOh/dday_project/issues) page
2. Create a new issue with detailed description
3. Include system information and error messages

---

**Note**: This application is designed for Windows systems and requires an active internet connection for the chat functionality.