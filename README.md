# CoFoundersLab Automation Bot

A desktop application that automates messaging on CoFoundersLab.com. The bot can automatically send messages to multiple users across different pages of the CoFoundersLab search results.

## Features

- **User-friendly GUI**: Simple interface with text input and control buttons
- **Automated Web Navigation**: Opens CoFoundersLab website using Selenium WebDriver
- **Smart User Detection**: Automatically finds and clicks message buttons on user cards
- **Bulk Messaging**: Sends the same message to all users on the current page
- **Pagination Support**: Automatically navigates to next pages and continues messaging
- **Real-time Logging**: Shows activity log and progress status
- **Error Handling**: Robust error handling with detailed logging

## Requirements

- Python 3.7 or higher
- Google Chrome browser
- ChromeDriver (automatically managed by webdriver-manager)

## Installation

1. **Clone or download the project files**
   ```bash
   # If you have git
   git clone <repository-url>
   cd cofounderslab_bot
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python cofounderslab_bot.py
   ```

## Usage

### Step 1: Setup
1. Run the application using `python cofounderslab_bot.py`
2. Enter your message in the text input field
3. Click "Open Site" to launch CoFoundersLab in Chrome

### Step 2: Manual Login and Navigation
1. **Login to CoFoundersLab** manually in the opened browser window
2. **Navigate to the target page** where you want to send messages
   - Go to the search page: `https://cofounderslab.com/search?countryCode=US&page=1`
   - Or any other page with user cards

### Step 3: Start Automation
1. Click "Start Messaging" to begin the automation
2. The bot will:
   - Find all user cards with message buttons
   - Click each message button
   - Fill the modal with your message
   - Send the message
   - Move to the next page when done
   - Repeat the process

### Step 4: Monitor Progress
- Watch the activity log for real-time updates
- Use "Stop" button to halt automation at any time
- Check the status bar for current operation

## How It Works

### 1. Website Detection
The bot automatically detects if you're on a CoFoundersLab search page and extracts the current page number.

### 2. User Card Detection
The bot uses multiple CSS selectors to find message buttons on user cards:
- `button[class*='message']`
- `button[class*='Message']`
- Buttons containing "message" text
- Various other selectors for different page layouts

### 3. Modal Interaction
When a message button is clicked:
- Waits for the modal to appear
- Finds the text input field
- Enters your message
- Clicks the send button
- Closes the modal

### 4. Pagination
After messaging all users on a page:
- Extracts current page number from URL
- Increments the page number
- Navigates to the next page
- Continues the process

## URL Pattern Support

The bot supports URLs like:
- `https://cofounderslab.com/search?countryCode=US&page=79`
- `https://cofounderslab.com/search?page=1`
- Any URL with `page=` parameter

## Safety Features

- **Rate Limiting**: 2-second delay between messages to avoid being flagged
- **Error Recovery**: Continues operation even if individual messages fail
- **Manual Control**: Stop button to halt automation at any time
- **Detailed Logging**: Complete activity log for monitoring

## Troubleshooting

### Common Issues

1. **"No message buttons found"**
   - Ensure you're on a page with user cards
   - Check if the page has loaded completely
   - Try refreshing the page

2. **"Modal did not appear"**
   - The message button might not be clickable
   - Check if you need to be logged in
   - Verify the page structure

3. **ChromeDriver issues**
   - The bot automatically manages ChromeDriver
   - Ensure Chrome browser is installed
   - Check internet connection

4. **Website changes**
   - CoFoundersLab might update their interface
   - The bot uses multiple selectors for compatibility
   - Contact support if selectors need updating

### Debug Mode

The application includes detailed logging. Check the activity log for:
- Current page number
- Number of users found
- Individual message success/failure
- Navigation status

## Legal and Ethical Considerations

⚠️ **Important**: This bot is for educational purposes. Please ensure you:

1. **Respect Terms of Service**: Check CoFoundersLab's ToS before using
2. **Use Reasonably**: Don't spam users with excessive messages
3. **Personal Use Only**: Use appropriate message content
4. **Rate Limiting**: The bot includes delays to be respectful

## Technical Details

### Dependencies
- `selenium`: Web automation framework
- `webdriver-manager`: Automatic ChromeDriver management
- `tkinter`: GUI framework (included with Python)

### Browser Compatibility
- Google Chrome (recommended)
- ChromeDriver automatically managed
- Headless mode not supported (manual login required)

### Performance
- Processes ~20 users per page
- 2-second delay between messages
- Automatic pagination
- Memory efficient operation

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the activity log for error messages
3. Ensure all requirements are installed
4. Verify Chrome browser is up to date

## Version History

- **v1.0**: Initial release with basic automation features
- GUI interface with message input
- Automated user detection and messaging
- Pagination support
- Real-time logging and status updates
