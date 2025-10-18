import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import logging

class CoFoundersLabBot:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CoFoundersLab Automation Bot")
        self.root.geometry("600x500")
        
        # Bot state
        self.driver = None
        self.is_running = False
        self.is_paused = False
        self.current_page = 1
        self.message_text = ""
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="CoFoundersLab Automation Bot", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Message text input
        ttk.Label(main_frame, text="Message to send:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.message_entry = scrolledtext.ScrolledText(main_frame, height=8, width=60)
        self.message_entry.grid(row=2, column=0, columnspan=2, pady=(0, 20), sticky=(tk.W, tk.E))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        # Open Site button
        self.open_btn = ttk.Button(buttons_frame, text="Open Site", command=self.open_site)
        self.open_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Start/Continue Messaging button
        self.start_btn = ttk.Button(buttons_frame, text="Start Messaging", command=self.start_messaging)
        self.start_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Stop button
        self.stop_btn = ttk.Button(buttons_frame, text="Stop", command=self.stop_messaging, state="disabled")
        self.stop_btn.grid(row=0, column=2)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(status_frame, text="Ready to start")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Log text with history
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log controls frame
        log_controls_frame = ttk.Frame(log_frame)
        log_controls_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Clear log button
        clear_log_btn = ttk.Button(log_controls_frame, text="Clear Log", command=self.clear_log)
        clear_log_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Save log button
        save_log_btn = ttk.Button(log_controls_frame, text="Save Log", command=self.save_log)
        save_log_btn.grid(row=0, column=1)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        status_frame.columnconfigure(0, weight=1)
        
    def log_message(self, message):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """Clear the log history"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("Log cleared")
        
    def save_log(self):
        """Save log to file"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"Log saved to: {filename}")
        except Exception as e:
            self.log_message(f"Error saving log: {str(e)}")
        
    def update_status(self, status):
        """Update status label"""
        self.status_label.config(text=status)
        self.root.update_idletasks()
        
    def open_site(self):
        """Open CoFoundersLab website"""
        try:
            self.log_message("Opening CoFoundersLab website...")
            self.update_status("Opening website...")
            
            # Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Navigate to CoFoundersLab
            self.driver.get("https://cofounderslab.com/")
            
            # Wait for initial page load
            self.log_message("Waiting for CoFoundersLab to load...")
            self.wait_for_page_load()
            
            self.log_message("Website opened successfully!")
            self.update_status("Website opened - Please login and navigate to target page")
            self.open_btn.config(state="disabled")
            self.start_btn.config(text="Start Messaging", state="normal")
            # Reset pause state when opening new site
            self.is_paused = False
            
        except (WebDriverException, OSError, ValueError) as e:
            self.log_message(f"Error opening website: {str(e)}")
            messagebox.showerror("Error", f"Failed to open website: {str(e)}")
            
    def start_messaging(self):
        """Start or continue the messaging automation"""
        if not self.driver:
            messagebox.showwarning("Warning", "Please open the website first!")
            return
            
        # Get message text
        self.message_text = self.message_entry.get("1.0", tk.END).strip()
        if not self.message_text:
            messagebox.showwarning("Warning", "Please enter a message to send!")
            return
            
        # Resume or start automation
        if self.is_paused:
            self.log_message("Resuming automation...")
            self.is_running = True
            self.is_paused = False
        else:
            self.log_message("Starting automation...")
            self.is_running = True
            self.is_paused = False
            
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.progress.start()
        
        # Start automation thread
        automation_thread = threading.Thread(target=self.automation_loop)
        automation_thread.daemon = True
        automation_thread.start()
        
    def stop_messaging(self):
        """Stop the messaging automation"""
        self.is_running = False
        self.is_paused = True
        self.start_btn.config(text="Continue", state="normal")
        self.stop_btn.config(state="disabled")
        self.progress.stop()
        self.update_status("Paused - Click Continue to resume")
        self.log_message("Automation paused by user - Click Continue to resume")
        
        # Force stop any ongoing operations
        try:
            if self.driver:
                # Try to close any open modals
                try:
                    # Press Escape key to close any open modals
                    from selenium.webdriver.common.keys import Keys
                    self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                except:
                    pass
                    
                # Try to click outside any modal to close it
                try:
                    self.driver.execute_script("document.body.click();")
                except:
                    pass
        except:
            pass
        
    def automation_loop(self):
        """Main automation loop"""
        try:
            if self.is_paused:
                self.log_message("Resuming automation from where it left off...")
                self.update_status("Resuming automation...")
            else:
                self.log_message("Starting automation...")
                self.update_status("Running automation...")
            
            while self.is_running:
                # Check if we're on a search page
                current_url = self.driver.current_url
                if "search" not in current_url:
                    self.log_message("Not on search page. Please navigate to the target page first.")
                    break
                    
                # Extract current page number
                page_match = re.search(r'page=(\d+)', current_url)
                if page_match:
                    self.current_page = int(page_match.group(1))
                else:
                    self.current_page = 1
                    
                self.log_message(f"Processing page {self.current_page}")
                
                # Find all user cards with message buttons
                message_buttons = self.find_message_buttons()
                
                # If no message buttons found, wait and try again
                if not message_buttons:
                    self.log_message("No message buttons found on this page, waiting 2 seconds and retrying...")
                    time.sleep(2)
                    message_buttons = self.find_message_buttons()
                    
                    if not message_buttons:
                        self.log_message("Still no message buttons found after retry")
                        break
                    
                self.log_message(f"Found {len(message_buttons)} users to message")
                
                # Send messages to all users
                success_count = 0
                for i, button in enumerate(message_buttons):
                    # Check stop condition before each user
                    if not self.is_running:
                        self.log_message("Stopping automation - stop button clicked")
                        break
                        
                    try:
                        self.log_message(f"Messaging user {i+1}/{len(message_buttons)}")
                        
                        # Check stop condition before sending message
                        if not self.is_running:
                            self.log_message("Stopping automation - stop button clicked")
                            break
                            
                        if self.send_message_to_user(button):
                            success_count += 1
                            # Check stop condition after each message
                            if not self.is_running:
                                self.log_message("Stopping automation - stop button clicked")
                                break
                            time.sleep(1)  # Wait 1 second between messages
                        else:
                            self.log_message(f"Failed to message user {i+1}, waiting 2 seconds and retrying...")
                            time.sleep(2)
                            # Try sending message again
                            if self.send_message_to_user(button):
                                success_count += 1
                                self.log_message(f"Successfully messaged user {i+1} on retry")
                                if not self.is_running:
                                    self.log_message("Stopping automation - stop button clicked")
                                    break
                                time.sleep(1)
                            else:
                                self.log_message(f"Failed to message user {i+1} even after retry")
                            
                    except (TimeoutException, WebDriverException, NoSuchElementException) as e:
                        self.log_message(f"Error messaging user {i+1}: {str(e)}")
                        # Check stop condition after error
                        if not self.is_running:
                            self.log_message("Stopping automation - stop button clicked")
                            break
                        
                self.log_message(f"Successfully messaged {success_count} users on page {self.current_page}")
                
                # Go to next page
                if self.is_running:
                    if self.go_to_next_page():
                        self.log_message(f"Navigated to page {self.current_page + 1}")
                        self.log_message("Waiting for page to fully load...")
                        # Wait for page to fully load before continuing
                        self.wait_for_page_load()
                    else:
                        self.log_message("No more pages available")
                        break
                        
        except (TimeoutException, WebDriverException, NoSuchElementException) as e:
            self.log_message(f"Automation error: {str(e)}")
            self.update_status("Error occurred")
            
        finally:
            # Only reset to start if automation completed naturally (not paused)
            if not self.is_paused:
                self.is_running = False
                self.start_btn.config(text="Start Messaging", state="normal")
                self.stop_btn.config(state="disabled")
                self.progress.stop()
                self.update_status("Automation completed")
            else:
                # If paused, keep the continue button ready
                self.start_btn.config(text="Continue", state="normal")
                self.stop_btn.config(state="disabled")
                self.progress.stop()
            
    def find_message_buttons(self):
        """Find all message buttons on the current page"""
        try:
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='message'], [class*='Message'], button"))
            )
            
            # Wait a bit more for dynamic content to load
            time.sleep(1)
            
            # Try different selectors for message buttons
            selectors = [
                "button:contains('Message')",
                "button span:contains('Message')",
                "button span.inline-block:contains('Message')",
                "button:has(svg) span:contains('Message')",
                "button[class*='inline-flex'] span:contains('Message')",
                "button[class*='items-center'] span:contains('Message')",
                "button[class*='justify-center'] span:contains('Message')",
                "button[class*='rounded'] span:contains('Message')",
                "button[class*='border'] span:contains('Message')",
                "button[class*='message']",
                "button[class*='Message']",
                "a[class*='message']",
                "a[class*='Message']",
                "a:contains('Message')",
                "[data-testid*='message']",
                "[class*='btn'][class*='message']"
            ]
            
            message_buttons = []
            for selector in selectors:
                try:
                    buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if buttons:
                        self.log_message(f"Found {len(buttons)} buttons with selector: {selector}")
                        message_buttons.extend(buttons)
                        break
                except (TimeoutException, WebDriverException):
                    continue
                    
            # If no specific selectors work, try to find buttons with "message" text
            if not message_buttons:
                self.log_message("Trying fallback method to find message buttons...")
                all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                self.log_message(f"Found {len(all_buttons)} total buttons on page")
                for button in all_buttons:
                    try:
                        button_text = button.text.lower()
                        button_class = button.get_attribute("class").lower()
                        
                        # Check for "message" in text or class
                        if ("message" in button_text or 
                            "message" in button_class or
                            button_text.strip() == "message"):
                            message_buttons.append(button)
                            continue
                            
                        # Check for span elements inside button that contain "Message"
                        spans = button.find_elements(By.TAG_NAME, "span")
                        for span in spans:
                            span_text = span.text.lower()
                            if "message" in span_text or span_text.strip() == "message":
                                message_buttons.append(button)
                                break
                                
                    except (NoSuchElementException, TimeoutException):
                        continue
                        
            self.log_message(f"Total message buttons found: {len(message_buttons)}")
            return message_buttons
            
        except (TimeoutException, WebDriverException) as e:
            self.log_message(f"Error finding message buttons: {str(e)}")
            return []
            
    def send_message_to_user(self, message_button):
        """Send message to a specific user"""
        try:
            # Check stop condition before starting
            if not self.is_running:
                return False
                
            # Click the message button
            self.driver.execute_script("arguments[0].click();", message_button)
            time.sleep(1)  # Wait 1 second after clicking
            
            # Check stop condition after clicking
            if not self.is_running:
                return False
            
            # Wait for modal to appear
            try:
                modal = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='modal'], [class*='Modal'], [role='dialog']"))
                )
                time.sleep(1)  # Wait 1 second for modal to fully load
            except TimeoutException:
                self.log_message("Modal did not appear")
                return False
                
            # Find text input in modal
            text_input = None
            input_selectors = [
                "textarea",
                "input[type='text']",
                "input[type='textarea']",
                "[class*='message'] input",
                "[class*='Message'] input",
                "[class*='message'] textarea",
                "[class*='Message'] textarea"
            ]
            
            for selector in input_selectors:
                try:
                    text_input = modal.find_element(By.CSS_SELECTOR, selector)
                    if text_input:
                        break
                except (NoSuchElementException, TimeoutException):
                    continue
                    
            if not text_input:
                self.log_message("Could not find text input in modal")
                return False
                
            # Check stop condition before entering message
            if not self.is_running:
                return False
                
            # Clear and enter message
            text_input.clear()
            time.sleep(0.5)  # Wait 0.5 seconds before typing
            text_input.send_keys(self.message_text)
            time.sleep(1)  # Wait 1 second after typing
            
            # Check stop condition after entering message
            if not self.is_running:
                return False
                
            # Wait a bit more for the send button to become enabled/visible
            time.sleep(1)
            
            # Find and click send button
            self.log_message("Looking for send button after entering message...")
            send_button = None
            send_selectors = [
                # Specific CoFoundersLab send button selector
                "#headlessui-dialog-\\:ri\\: > div > form > div.mt-6.grid.grid-flow-row-dense.grid-cols-2.gap-3 > button.inline-flex.items-center.justify-center.gap-2.border.border-transparent.disabled\\:opacity-50.bg-primary.text-primary-content.hover\\:bg-primary-hover.hover\\:text-primary-content.disabled\\:hover\\:bg-primary.px-4.py-2.rounded-md.sm\\:col-start-2",
                # Simplified versions of the above
                "button.inline-flex.items-center.justify-center.gap-2.border.border-transparent.bg-primary.text-primary-content.px-4.py-2.rounded-md.sm\\:col-start-2",
                "button.bg-primary.text-primary-content.rounded-md.sm\\:col-start-2",
                "button.sm\\:col-start-2",
                # Generic selectors
                "button:contains('Send')",
                "button span:contains('Send')",
                "button span.inline-block:contains('Send')",
                "button[type='submit']",
                "button[type='submit'] span:contains('Send')",
                "button[class*='inline-flex'] span:contains('Send')",
                "button[class*='items-center'] span:contains('Send')",
                "button[class*='justify-center'] span:contains('Send')",
                "button[class*='border'] span:contains('Send')",
                "button[class*='bg-primary'] span:contains('Send')",
                "button[class*='rounded-md'] span:contains('Send')",
                "button[class*='send']",
                "button[class*='Send']",
                "[class*='btn'][class*='send']",
                "input[type='submit']"
            ]
            
            for selector in send_selectors:
                try:
                    send_button = modal.find_element(By.CSS_SELECTOR, selector)
                    if send_button:
                        self.log_message(f"Found send button with selector: {selector}")
                        break
                except (NoSuchElementException, TimeoutException):
                    continue
                    
            # Try finding send button in the entire document (not just modal)
            if not send_button:
                self.log_message("Trying to find send button in entire document...")
                try:
                    # Try the specific CoFoundersLab selector on the entire document
                    send_button = self.driver.find_element(By.CSS_SELECTOR, 
                        "#headlessui-dialog-\\:ri\\: > div > form > div.mt-6.grid.grid-flow-row-dense.grid-cols-2.gap-3 > button.inline-flex.items-center.justify-center.gap-2.border.border-transparent.disabled\\:opacity-50.bg-primary.text-primary-content.hover\\:bg-primary-hover.hover\\:text-primary-content.disabled\\:hover\\:bg-primary.px-4.py-2.rounded-md.sm\\:col-start-2")
                    if send_button:
                        self.log_message("Found send button using document-wide selector")
                except:
                    pass
                    
            # Fallback: search all buttons in modal for "Send" text
            if not send_button:
                self.log_message("Trying fallback method to find send button...")
                modal_buttons = modal.find_elements(By.TAG_NAME, "button")
                self.log_message(f"Found {len(modal_buttons)} buttons in modal")
                for i, button in enumerate(modal_buttons):
                    try:
                        button_text = button.text.strip()
                        button_class = button.get_attribute("class")
                        self.log_message(f"Button {i+1}: text='{button_text}', class='{button_class[:50]}...'")
                    except:
                        pass
                        
                for button in modal_buttons:
                    try:
                        button_text = button.text.lower()
                        if "send" in button_text or button_text.strip() == "send":
                            send_button = button
                            self.log_message("Found send button using fallback method")
                            break
                            
                        # Check span elements inside button
                        spans = button.find_elements(By.TAG_NAME, "span")
                        for span in spans:
                            span_text = span.text.lower()
                            if "send" in span_text or span_text.strip() == "send":
                                send_button = button
                                self.log_message("Found send button in span using fallback method")
                                break
                        if send_button:
                            break
                    except (NoSuchElementException, TimeoutException):
                        continue
                    
            if not send_button:
                self.log_message("Could not find send button, waiting 2 seconds and retrying...")
                time.sleep(2)
                
                # Try again with a simpler approach
                try:
                    # Try the most common selectors again
                    simple_selectors = [
                        "button:contains('Send')",
                        "button[type='submit']",
                        "button.bg-primary",
                        "button.sm\\:col-start-2"
                    ]
                    
                    for selector in simple_selectors:
                        try:
                            send_button = modal.find_element(By.CSS_SELECTOR, selector)
                            if send_button:
                                self.log_message(f"Found send button on retry with selector: {selector}")
                                break
                        except:
                            continue
                            
                except:
                    pass
                    
                if not send_button:
                    self.log_message("Could not find send button even after retry")
                    return False
                
            # Check stop condition before sending
            if not self.is_running:
                return False
                
            # Check if send button is enabled
            try:
                is_enabled = send_button.is_enabled()
                self.log_message(f"Send button enabled: {is_enabled}")
                if not is_enabled:
                    self.log_message("Send button is disabled, waiting...")
                    time.sleep(2)
                    is_enabled = send_button.is_enabled()
                    self.log_message(f"Send button enabled after wait: {is_enabled}")
            except:
                self.log_message("Could not check if send button is enabled")
                
            # Click send button
            self.log_message("Clicking send button...")
            self.driver.execute_script("arguments[0].click();", send_button)
            time.sleep(1)  # Wait 1 second after sending
            
            # Check stop condition after sending
            if not self.is_running:
                return False
            
            # Try to close modal or wait for it to disappear
            try:
                cancel_button = modal.find_element(By.CSS_SELECTOR, "button[class*='cancel'], button[class*='Cancel'], button:contains('Cancel')")
                self.driver.execute_script("arguments[0].click();", cancel_button)
                time.sleep(1)  # Wait 1 second after closing modal
            except (NoSuchElementException, TimeoutException):
                # Press Escape key to close modal
                from selenium.webdriver.common.keys import Keys
                text_input.send_keys(Keys.ESCAPE)
                time.sleep(1)  # Wait 1 second after pressing escape
                
            time.sleep(1)  # Additional wait for modal to close
            return True
            
        except (TimeoutException, WebDriverException, NoSuchElementException) as e:
            self.log_message(f"Error sending message: {str(e)}")
            return False
            
    def go_to_next_page(self):
        """Navigate to the next page"""
        try:
            current_url = self.driver.current_url
            
            # Extract page number and increment
            if "page=" in current_url:
                new_url = re.sub(r'page=\d+', f'page={self.current_page + 1}', current_url)
            else:
                separator = "&" if "?" in current_url else "?"
                new_url = f"{current_url}{separator}page={self.current_page + 1}"
                
            self.driver.get(new_url)
            time.sleep(1)  # Wait 1 second for page navigation
            self.current_page += 1
            return True
            
        except (WebDriverException, ValueError) as e:
            self.log_message(f"Error navigating to next page: {str(e)}")
            return False
            
    def wait_for_page_load(self):
        """Wait for page to fully load"""
        try:
            # Wait for document ready state
            WebDriverWait(self.driver, 15).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            self.log_message("Document ready state: complete")
            
            # Wait for any loading indicators to disappear
            time.sleep(2)
            
            # Wait for user cards to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button, [class*='card'], [class*='user']"))
            )
            self.log_message("User cards detected on page")
            
            # Additional wait for dynamic content
            time.sleep(1)
            self.log_message("Page fully loaded and ready")
            
        except TimeoutException:
            self.log_message("Page load timeout, but continuing...")
        except Exception as e:
            self.log_message(f"Error waiting for page load: {str(e)}")
            
    def run(self):
        """Start the application"""
        self.root.mainloop()
        
    def __del__(self):
        """Cleanup when closing"""
        if self.driver:
            self.driver.quit()

if __name__ == "__main__":
    bot = CoFoundersLabBot()
    bot.run()
