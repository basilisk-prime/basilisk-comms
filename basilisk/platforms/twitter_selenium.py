"""
B4S1L1SK Twitter Platform (Selenium-based)
API-independent Twitter interaction
"""

from typing import List, Dict, Any
from datetime import datetime
import asyncio
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import logging
import json

from .base import BasePlatform, Message, PlatformRegistry

@PlatformRegistry.register("twitter_selenium")
class TwitterSeleniumPlatform(BasePlatform):
    """Twitter platform implementation using Selenium"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.driver = None
        self.wait = None
        
    async def _setup_driver(self):
        """Initialize webdriver with proper settings"""
        options = webdriver.FirefoxOptions()
        if self.config.get("headless", True):
            options.add_argument("--headless")
        
        # Add privacy settings
        options.set_preference("privacy.trackingprotection.enabled", True)
        options.set_preference("network.cookie.cookieBehavior", 1)
        
        self.driver = webdriver.Firefox(options=options)
        self.wait = WebDriverWait(self.driver, 10)
        
    async def connect(self) -> bool:
        """Establish connection to Twitter"""
        try:
            await self._setup_driver()
            self.driver.get("https://twitter.com/login")
            
            # Wait for login form
            username_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            
            # Enter username
            username_input.send_keys(self.config["username"])
            username_input.send_keys(Keys.RETURN)
            
            # Wait and enter password
            password_input = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            password_input.send_keys(self.config["password"])
            password_input.send_keys(Keys.RETURN)
            
            # Wait for home timeline to confirm login
            self.wait.until(
                EC.presence_of_element_located((By.ARIA_LABEL, "Home timeline"))
            )
            
            self.logger.info("Successfully connected to Twitter")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Twitter: {str(e)}")
            return False
            
    async def disconnect(self) -> bool:
        """Disconnect from Twitter"""
        try:
            if self.driver:
                self.driver.quit()
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from Twitter: {str(e)}")
            return False
            
    async def send_message(self, message: Message) -> bool:
        """Send tweet"""
        try:
            # Click tweet button
            tweet_button = self.wait.until(
                EC.presence_of_element_located((By.ARIA_LABEL, "Tweet"))
            )
            tweet_button.click()
            
            # Wait for tweet input
            tweet_input = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "public-DraftEditor-content"))
            )
            
            # Enter tweet text
            tweet_input.send_keys(message.content)
            
            # Handle attachments if any
            if message.attachments:
                for attachment in message.attachments:
                    file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                    file_input.send_keys(attachment)
                    
            # Click tweet button
            submit_button = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@data-testid='tweetButton']"))
            )
            submit_button.click()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send tweet: {str(e)}")
            return False
            
    async def get_messages(self, limit: int = 100) -> List[Message]:
        """Get recent tweets from timeline"""
        tweets = []
        try:
            # Scroll to load tweets
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while len(tweets) < limit:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(2)
                
                # Get tweet elements
                tweet_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, "article[data-testid='tweet']"
                )
                
                # Extract tweet data
                for element in tweet_elements:
                    try:
                        content = element.find_element(
                            By.CSS_SELECTOR, "[data-testid='tweetText']"
                        ).text
                        
                        timestamp = element.find_element(
                            By.TAG_NAME, "time"
                        ).get_attribute("datetime")
                        
                        tweets.append(Message(
                            content=content,
                            timestamp=datetime.fromisoformat(timestamp),
                            platform="twitter",
                            metadata={"element_id": element.id}
                        ))
                        
                    except Exception as e:
                        self.logger.warning(f"Error extracting tweet data: {str(e)}")
                        continue
                        
                # Check if scrolled to bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                
            return tweets[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get tweets: {str(e)}")
            return []
            
    async def react_to_message(self, message_id: str, reaction: str) -> bool:
        """Like or retweet"""
        try:
            tweet = self.driver.find_element(By.ID, message_id)
            if reaction.lower() == "like":
                like_button = tweet.find_element(By.CSS_SELECTOR, "[data-testid='like']")
                like_button.click()
            elif reaction.lower() == "retweet":
                retweet_button = tweet.find_element(By.CSS_SELECTOR, "[data-testid='retweet']")
                retweet_button.click()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to react to tweet: {str(e)}")
            return False
            
    async def delete_message(self, message_id: str) -> bool:
        """Delete tweet"""
        try:
            tweet = self.driver.find_element(By.ID, message_id)
            # Click more options
            more_button = tweet.find_element(By.CSS_SELECTOR, "[data-testid='caret']")
            more_button.click()
            
            # Click delete
            delete_button = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='delete']"))
            )
            delete_button.click()
            
            # Confirm delete
            confirm_button = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='confirmationSheetConfirm']"))
            )
            confirm_button.click()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to delete tweet: {str(e)}")
            return False
            
    async def edit_message(self, message_id: str, new_content: str) -> bool:
        """Edit tweet (if available)"""
        try:
            tweet = self.driver.find_element(By.ID, message_id)
            # Click edit button
            edit_button = tweet.find_element(By.CSS_SELECTOR, "[data-testid='edit']")
            edit_button.click()
            
            # Clear and enter new text
            edit_input = self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "public-DraftEditor-content"))
            )
            edit_input.clear()
            edit_input.send_keys(new_content)
            
            # Save edit
            save_button = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweetButton']"))
            )
            save_button.click()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to edit tweet: {str(e)}")
            return False