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
            self.log_message("Opening CoFoundersLab website...")
            self.driver.get("https://cofounderslab.com/")
            time.sleep(3)  # Wait 3 seconds for initial load
            
            # Wait for initial page load
            self.log_message("Waiting for CoFoundersLab to load...")
            self.wait_for_page_load()
            
            # Verify page opened successfully
            self.log_message("Verifying page opened successfully...")
            try:
                # Check if we're on the correct page
                current_url = self.driver.current_url
                if "cofounderslab.com" in current_url:
                    self.log_message("Page verification successful - on CoFoundersLab")
                else:
                    self.log_message(f"Warning: Unexpected URL: {current_url}")
                
                # Check for key elements
                WebDriverWait(self.driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button, [class*='login'], [class*='sign']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='search'], [class*='profile']"))
                    )
                )
                self.log_message("Key page elements detected")
            except TimeoutException:
                self.log_message("Warning: Key page elements not detected, but continuing...")
            
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
                            
                            # Wait for any remaining modals to close
                            time.sleep(2)
                            
                            # Check stop condition after each message
                            if not self.is_running:
                                self.log_message("Stopping automation - stop button clicked")
                                break
                            time.sleep(3)  # Wait 3 seconds between messages
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
            self.log_message("Waiting for message buttons to load (max 30 seconds)...")
            
            # Wait for page to load with extended timeout
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='message'], [class*='Message'], button"))
            )
            self.log_message("Basic buttons detected, waiting for dynamic content...")
            
            # Wait longer for dynamic content to load
            time.sleep(5)
            
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
            
    def extract_user_name(self, message_button):
        """Extract user name from the user card containing the message button"""
        try:
            self.log_message("Extracting user name from user card...")
            
            # Method 1: Look for the specific structure you provided
            # <div class="flex items-center gap-1"><p>Alex Marouf</p></div>
            try:
                name_element = message_button.find_element(By.XPATH, ".//div[contains(@class, 'flex') and contains(@class, 'items-center')]//p")
                if name_element and name_element.text.strip():
                    user_name = name_element.text.strip()
                    self.log_message(f"Found user name (method 1): {user_name}")
                    return user_name
            except:
                pass
            
            # Method 2: Look in parent elements for the name structure
            user_card = message_button
            max_levels = 8  # Prevent infinite loop
            
            for level in range(max_levels):
                try:
                    # Look for the specific div structure with p tag
                    name_element = user_card.find_element(By.XPATH, ".//div[contains(@class, 'flex') and contains(@class, 'items-center')]//p")
                    if name_element and name_element.text.strip():
                        user_name = name_element.text.strip()
                        self.log_message(f"Found user name (method 2, level {level}): {user_name}")
                        return user_name
                except:
                    pass
                
                # Also try direct p tag search
                try:
                    name_element = user_card.find_element(By.CSS_SELECTOR, "p")
                    if name_element and name_element.text.strip():
                        user_name = name_element.text.strip()
                        self.log_message(f"Found user name (method 2b, level {level}): {user_name}")
                        return user_name
                except:
                    pass
                
                # Move to parent element
                try:
                    user_card = user_card.find_element(By.XPATH, "..")
                except:
                    break
            
            # Method 3: Search for names near the button by position
            try:
                button_location = message_button.location
                all_p_elements = self.driver.find_elements(By.CSS_SELECTOR, "p")
                
                for p_element in all_p_elements:
                    try:
                        p_location = p_element.location
                        p_text = p_element.text.strip()
                        
                        # Check if p element is near the button and has text
                        if (p_text and 
                            abs(p_location['x'] - button_location['x']) < 300 and 
                            abs(p_location['y'] - button_location['y']) < 150):
                            user_name = p_text
                            self.log_message(f"Found user name (method 3): {user_name}")
                            return user_name
                    except:
                        continue
            except:
                pass
                
            self.log_message("Could not extract user name")
            return None
            
        except Exception as e:
            self.log_message(f"Error extracting user name: {str(e)}")
            return None
            
    def extract_user_name_from_modal(self, modal):
        """Extract user name from modal title"""
        try:
            self.log_message("Extracting user name from modal title...")
            
            # Look for the modal title with user name
            # <h3 class="text-lg font-semibold leading-6">Send Otwan a message</h3>
            try:
                title_element = modal.find_element(By.CSS_SELECTOR, "h3")
                if title_element and title_element.text.strip():
                    title_text = title_element.text.strip()
                    self.log_message(f"Found modal title: {title_text}")
                    
                    # Extract name from "Send [Name] a message"
                    if "Send" in title_text and "a message" in title_text:
                        # Extract name between "Send" and "a message"
                        start = title_text.find("Send") + 4  # After "Send"
                        end = title_text.find("a message")
                        if start < end:
                            user_name = title_text[start:end].strip()
                            if user_name:
                                self.log_message(f"Extracted user name from modal: {user_name}")
                                return user_name
            except:
                pass
            
            # Alternative: look for any h3 with text
            try:
                h3_elements = modal.find_elements(By.CSS_SELECTOR, "h3")
                for h3 in h3_elements:
                    if h3.text.strip():
                        title_text = h3.text.strip()
                        self.log_message(f"Found h3 text: {title_text}")
                        
                        # Try to extract name from various patterns
                        if "Send" in title_text and "message" in title_text:
                            # Pattern: "Send [Name] a message"
                            import re
                            match = re.search(r'Send\s+([^a]+?)\s+a\s+message', title_text)
                            if match:
                                user_name = match.group(1).strip()
                                self.log_message(f"Extracted user name (regex): {user_name}")
                                return user_name
            except:
                pass
                
            self.log_message("Could not extract user name from modal")
            return None
            
        except Exception as e:
            self.log_message(f"Error extracting user name from modal: {str(e)}")
            return None

    def send_message_to_user(self, message_button):
        """Send message to a specific user"""
        try:
            # Check stop condition before starting
            if not self.is_running:
                return False
                
            # Extract user name for personalization (will try again from modal if needed)
            user_name = self.extract_user_name(message_button)
            
            # Create personalized message (will be updated if we find name in modal)
            if user_name:
                personalized_message = self.message_text.replace("Hi there", f"Hi {user_name}")
                if personalized_message == self.message_text:  # If no "Hi there" found, add greeting
                    personalized_message = f"Hi {user_name},\n\n{self.message_text}"
                self.log_message(f"Personalized message for {user_name}")
            else:
                personalized_message = self.message_text
                self.log_message("Using original message (no user name found from button)")
                
            self.log_message("Attempting to send message to user...")
                
            # Click the message button
            self.log_message("Clicking message button...")
            self.driver.execute_script("arguments[0].click();", message_button)
            time.sleep(2)  # Wait 2 seconds after clicking
            
            # Verify button click was successful by checking if modal appears
            self.log_message("Verifying message button click was successful...")
            try:
                # Wait for any loading indicators or modal to start appearing
                WebDriverWait(self.driver, 5).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='modal'], [class*='Modal'], [role='dialog']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='loading'], [class*='spinner']"))
                    )
                )
                self.log_message("Message button click verified - modal/loading detected")
            except TimeoutException:
                self.log_message("Warning: No immediate response to button click, but continuing...")
            
            # Check stop condition after clicking
            if not self.is_running:
                return False
            
            # Wait for modal to appear
            try:
                self.log_message("Waiting for message modal to appear (max 30 seconds)...")
                modal = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='modal'], [class*='Modal'], [role='dialog']"))
                )
                self.log_message("Modal detected, waiting for it to fully load...")
                time.sleep(5)  # Wait 5 seconds for modal to fully load
            except TimeoutException:
                self.log_message("Modal did not appear within 30 seconds")
                return False
                
            # Try to extract user name from modal title
            modal_user_name = self.extract_user_name_from_modal(modal)
            if modal_user_name and not user_name:
                user_name = modal_user_name
                # Update personalized message with modal user name
                personalized_message = self.message_text.replace("Hi there", f"Hi {user_name}")
                if personalized_message == self.message_text:  # If no "Hi there" found, add greeting
                    personalized_message = f"Hi {user_name},\n\n{self.message_text}"
                self.log_message(f"Found user name in modal: {user_name}")
            elif modal_user_name and user_name:
                # Confirm user name matches
                if modal_user_name.lower().strip() == user_name.lower().strip():
                    self.log_message(f"User name confirmed from modal: {modal_user_name}")
                else:
                    self.log_message(f"User name mismatch! Button: '{user_name}' vs Modal: '{modal_user_name}'")
                    # Use modal name as it's more reliable
                    user_name = modal_user_name
                    personalized_message = self.message_text.replace("Hi there", f"Hi {user_name}")
                    if personalized_message == self.message_text:
                        personalized_message = f"Hi {user_name},\n\n{self.message_text}"
                    self.log_message(f"Using modal user name: {user_name}")
            elif not modal_user_name and user_name:
                self.log_message(f"Using user name from button: {user_name}")
            else:
                self.log_message("No user name found from either source")
            
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
                
            # Clear and enter personalized message
            self.log_message("Clearing text input field...")
            text_input.clear()
            time.sleep(1)  # Wait 1 second after clearing
            
            # Verify field was cleared
            try:
                field_value = text_input.get_attribute("value")
                if field_value.strip():
                    self.log_message("Warning: Text field not fully cleared, trying again...")
                    text_input.clear()
                    time.sleep(0.5)
            except:
                pass
            
            # Log the personalized message for confirmation
            self.log_message(f"Sending personalized message to {user_name if user_name else 'unknown user'}")
            self.log_message(f"Message preview: {personalized_message[:100]}{'...' if len(personalized_message) > 100 else ''}")
            
            self.log_message("Typing personalized message...")
            text_input.send_keys(personalized_message)
            time.sleep(2)  # Wait 2 seconds after typing
            
            # Verify message was entered correctly
            try:
                entered_text = text_input.get_attribute("value")
                if entered_text.strip():
                    self.log_message("Message entered successfully")
                else:
                    self.log_message("Warning: Message may not have been entered correctly")
            except:
                self.log_message("Could not verify message entry, but continuing...")
            
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
            time.sleep(3)  # Wait 3 seconds after sending
            
            # Verify send button click was successful
            self.log_message("Verifying send button click was successful...")
            try:
                # Check if modal starts to close or loading appears
                WebDriverWait(self.driver, 5).until(
                    EC.any_of(
                        EC.invisibility_of_element_located(send_button),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='loading'], [class*='spinner'], [class*='success']"))
                    )
                )
                self.log_message("Send button click verified - modal closing or loading detected")
            except TimeoutException:
                self.log_message("Warning: No immediate response to send button click, but continuing...")
            
            # Check stop condition after sending
            if not self.is_running:
                return False
            
            # Try to close modal or wait for it to disappear
            self.log_message("Closing message modal...")
            modal_closed = False
            
            try:
                # Try to find and click cancel button
                cancel_button = modal.find_element(By.CSS_SELECTOR, "button[class*='cancel'], button[class*='Cancel'], button:contains('Cancel')")
                self.driver.execute_script("arguments[0].click();", cancel_button)
                time.sleep(2)  # Wait 2 seconds after clicking cancel
                modal_closed = True
                self.log_message("Modal closed using cancel button")
            except (NoSuchElementException, TimeoutException):
                self.log_message("Cancel button not found, trying alternative methods...")
                
                # Try pressing Escape key
                try:
                    from selenium.webdriver.common.keys import Keys
                    text_input.send_keys(Keys.ESCAPE)
                    time.sleep(2)  # Wait 2 seconds after pressing escape
                    modal_closed = True
                    self.log_message("Modal closed using Escape key")
                except:
                    pass
                
                # Try clicking outside modal
                try:
                    self.driver.execute_script("document.body.click();")
                    time.sleep(2)
                    modal_closed = True
                    self.log_message("Modal closed by clicking outside")
                except:
                    pass
            
            # Wait for modal to actually disappear
            if modal_closed:
                try:
                    WebDriverWait(self.driver, 15).until(
                        EC.invisibility_of_element_located(modal)
                    )
                    self.log_message("Modal successfully closed and disappeared")
                except TimeoutException:
                    self.log_message("Modal still visible after close attempt, trying additional methods...")
                    # Try additional close methods
                    try:
                        from selenium.webdriver.common.keys import Keys
                        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                        time.sleep(2)
                    except:
                        pass
                    
                    # Final check
                    try:
                        WebDriverWait(self.driver, 5).until(
                            EC.invisibility_of_element_located(modal)
                        )
                        self.log_message("Modal finally closed with additional methods")
                    except TimeoutException:
                        self.log_message("Warning: Modal may still be visible, but continuing...")
            
            # Additional wait to ensure modal is fully closed
            time.sleep(3)
            
            # Final verification that modal is closed
            try:
                modal_still_visible = modal.is_displayed()
                if modal_still_visible:
                    self.log_message("Warning: Modal may still be visible")
                else:
                    self.log_message("Modal closure confirmed")
            except:
                self.log_message("Could not verify modal closure, but continuing...")
                
            self.log_message("Message sent and modal closed successfully")
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
                
            self.log_message(f"Navigating to page {self.current_page + 1}...")
            self.driver.get(new_url)
            time.sleep(2)  # Wait 2 seconds for page navigation
            
            # Verify navigation was successful
            self.log_message("Verifying page navigation was successful...")
            try:
                # Wait for page to start loading
                WebDriverWait(self.driver, 10).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button, [class*='card'], [class*='user']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[class*='loading'], [class*='spinner']"))
                    )
                )
                self.log_message("Page navigation verified - content detected")
            except TimeoutException:
                self.log_message("Warning: No immediate content detected after navigation, but continuing...")
            
            self.current_page += 1
            
            # Wait for page to fully load before saving progress
            self.log_message("Waiting for page to fully load before saving progress...")
            time.sleep(3)
            
            # Save progress after navigating to next page
            self.save_progress(new_url, self.current_page, 0)  # 0 because we haven't messaged anyone on new page yet
            
            self.log_message(f"Successfully navigated to page {self.current_page}")
            return True
            
        except (WebDriverException, ValueError) as e:
            self.log_message(f"Error navigating to next page: {str(e)}")
            return False
            
    def wait_for_page_load(self):
        """Wait for page to fully load"""
        try:
            self.log_message("Waiting for page to fully load (max 20 seconds)...")
            
            # Wait for document ready state
            WebDriverWait(self.driver, 30).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            self.log_message("Document ready state: complete")
            
            # Wait for any loading indicators to disappear
            time.sleep(5)
            
            # Wait for user cards to be present
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button, [class*='card'], [class*='user']"))
            )
            self.log_message("User cards detected on page")
            
            # Additional wait for dynamic content
            time.sleep(3)
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
