import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import re
import os
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
        self.messaged_users = set()  # Track messaged users to prevent duplicates
        self.currently_messaging = set()  # Track users currently being messaged
        self.progress_file = "bot_progress.txt"  # File to save progress
        
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
        save_log_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Load progress button
        load_progress_btn = ttk.Button(log_controls_frame, text="Load Progress", command=self.load_progress)
        load_progress_btn.grid(row=0, column=2)
        
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
            
    def save_progress(self, url, page_number, messaged_count):
        """Save current progress to file"""
        try:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            progress_data = {
                "last_url": url,
                "page_number": page_number,
                "messaged_count": messaged_count,
                "timestamp": timestamp,
                "total_messaged": len(self.messaged_users)
            }
            
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                f.write(f"CoFoundersLab Bot Progress\n")
                f.write(f"========================\n")
                f.write(f"Last URL: {url}\n")
                f.write(f"Page Number: {page_number}\n")
                f.write(f"Users Messaged on Last Page: {messaged_count}\n")
                f.write(f"Total Users Messaged: {len(self.messaged_users)}\n")
                f.write(f"Last Updated: {timestamp}\n")
                f.write(f"\nSession Data:\n")
                f.write(f"Messaged Users: {', '.join(sorted(self.messaged_users))}\n")
            
            self.log_message(f"Progress saved: Page {page_number}, {len(self.messaged_users)} total users messaged")
            
        except Exception as e:
            self.log_message(f"Error saving progress: {str(e)}")
            
    def load_progress(self):
        """Load progress from file"""
        try:
            if not os.path.exists(self.progress_file):
                self.log_message("No previous progress file found")
                messagebox.showinfo("No Progress", "No previous progress file found.")
                return None
                
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract information from progress file
            lines = content.split('\n')
            progress_info = {}
            
            for line in lines:
                if line.startswith("Last URL:"):
                    progress_info['url'] = line.split(":", 1)[1].strip()
                elif line.startswith("Page Number:"):
                    progress_info['page'] = int(line.split(":", 1)[1].strip())
                elif line.startswith("Total Users Messaged:"):
                    progress_info['total_messaged'] = int(line.split(":", 1)[1].strip())
                    
            if progress_info:
                self.log_message(f"Loaded previous progress: Page {progress_info.get('page', 'unknown')}, {progress_info.get('total_messaged', 0)} users messaged")
                messagebox.showinfo("Progress Loaded", 
                    f"Previous progress found:\n"
                    f"Page: {progress_info.get('page', 'unknown')}\n"
                    f"Total Users Messaged: {progress_info.get('total_messaged', 0)}\n"
                    f"Last URL: {progress_info.get('url', 'unknown')}")
                return progress_info
            else:
                self.log_message("Could not parse progress file")
                messagebox.showerror("Parse Error", "Could not parse progress file.")
                return None
                
        except Exception as e:
            self.log_message(f"Error loading progress: {str(e)}")
            messagebox.showerror("Error", f"Error loading progress: {str(e)}")
            return None
        
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
            # Reset pause state and clear tracking when opening new site
            self.is_paused = False
            self.messaged_users.clear()
            self.currently_messaging.clear()
            self.log_message("Reset messaged users and messaging tracking")
            
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
                
                # If no message buttons found, move to next page
                if not message_buttons:
                    self.log_message("No message buttons found on this page")
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
                        # Create a unique identifier for this user button
                        user_id = f"page_{self.current_page}_user_{i}"
                        
                        # Check if we've already messaged this user
                        if user_id in self.messaged_users:
                            self.log_message(f"User {i+1} already messaged, skipping...")
                            continue
                            
                        # Check if we're currently messaging this user
                        if user_id in self.currently_messaging:
                            self.log_message(f"User {i+1} currently being messaged, skipping...")
                            continue
                            
                        # Mark user as currently being messaged
                        self.currently_messaging.add(user_id)
                        self.log_message(f"Messaging user {i+1}/{len(message_buttons)}")
                        
                        # Check stop condition before sending message
                        if not self.is_running:
                            self.log_message("Stopping automation - stop button clicked")
                            self.currently_messaging.discard(user_id)
                            break
                            
                        # Try to send message to user
                        message_sent = self.send_message_to_user(button)
                        
                        if message_sent:
                            # Mark user as messaged immediately after successful send
                            self.messaged_users.add(user_id)
                            success_count += 1
                            self.log_message(f"Successfully messaged user {i+1}")
                            # Remove from currently messaging
                            self.currently_messaging.discard(user_id)
                            # Check stop condition after each message
                            if not self.is_running:
                                self.log_message("Stopping automation - stop button clicked")
                                break
                            time.sleep(1)  # Wait 1 second between messages
                        else:
                            # Message failed, log and continue to next user
                            self.log_message(f"Failed to message user {i+1}")
                            # Remove from currently messaging
                            self.currently_messaging.discard(user_id)
                            
                    except (TimeoutException, WebDriverException, NoSuchElementException) as e:
                        self.log_message(f"Error messaging user {i+1}: {str(e)}")
                        # Check stop condition after error
                        if not self.is_running:
                            self.log_message("Stopping automation - stop button clicked")
                            break
                        
                self.log_message(f"Successfully messaged {success_count} users on page {self.current_page}")
                self.log_message(f"Total users messaged so far: {len(self.messaged_users)}")
                
                # Save progress after completing the page
                current_url = self.driver.current_url
                self.save_progress(current_url, self.current_page, success_count)
                
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
            self.log_message("Waiting for message buttons to load (max 20 seconds)...")
            
            # Wait for page to load with extended timeout
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='message'], [class*='Message'], button"))
            )
            self.log_message("Basic buttons detected, waiting for dynamic content...")
            
            # Wait longer for dynamic content to load
            time.sleep(3)
            
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
                
            # Additional safety check - this should not happen due to outer logic
            # but adding as extra protection
            self.log_message("Attempting to send message to user...")
                
            # Click the message button
            self.driver.execute_script("arguments[0].click();", message_button)
            time.sleep(1)  # Wait 1 second after clicking
            
            # Check stop condition after clicking
            if not self.is_running:
                return False
            
            # Wait for modal to appear
            try:
                self.log_message("Waiting for message modal to appear (max 20 seconds)...")
                modal = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='modal'], [class*='Modal'], [role='dialog']"))
                )
                self.log_message("Modal detected, waiting for it to fully load...")
                time.sleep(3)  # Wait 3 seconds for modal to fully load
            except TimeoutException:
                self.log_message("Modal did not appear within 20 seconds")
                return False
                
            # Find text input in modal
            self.log_message("Waiting for text input field to be available...")
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
            
            # Wait for text input to be present
            try:
                WebDriverWait(modal, 20).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "textarea")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='textarea']"))
                    )
                )
                self.log_message("Text input field detected")
            except TimeoutException:
                self.log_message("Text input not detected within 20 seconds, but continuing...")
            
            for selector in input_selectors:
                try:
                    text_input = modal.find_element(By.CSS_SELECTOR, selector)
                    if text_input:
                        self.log_message(f"Found text input with selector: {selector}")
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
            self.log_message("Waiting for send button to be available (max 20 seconds)...")
            
            # Wait for send button to be present and clickable
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button:contains('Send')")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button.bg-primary"))
                    )
                )
                self.log_message("Send button detected, proceeding...")
            except TimeoutException:
                self.log_message("Send button not detected within 20 seconds, but continuing...")
            
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
                self.log_message("Could not find send button")
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
            
            # Save progress after navigating to next page
            self.save_progress(new_url, self.current_page, 0)  # 0 because we haven't messaged anyone on new page yet
            
            return True
            
        except (WebDriverException, ValueError) as e:
            self.log_message(f"Error navigating to next page: {str(e)}")
            return False
            
    def wait_for_page_load(self):
        """Wait for page to fully load"""
        try:
            self.log_message("Waiting for page to fully load (max 20 seconds)...")
            
            # Wait for document ready state
            WebDriverWait(self.driver, 20).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            self.log_message("Document ready state: complete")
            
            # Wait for any loading indicators to disappear
            time.sleep(3)
            
            # Wait for user cards to be present
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button, [class*='card'], [class*='user']"))
            )
            self.log_message("User cards detected on page")
            
            # Additional wait for dynamic content
            time.sleep(2)
            self.log_message("Page fully loaded and ready")
            
        except TimeoutException:
            self.log_message("Page load timeout after 20 seconds, but continuing...")
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
