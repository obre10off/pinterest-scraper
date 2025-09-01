"""
Profile Manager for TikTok Scraper
Manages target profiles, tracks progress, and handles profile-related operations.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from loguru import logger


class ProfileManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.profiles_file = "profiles.json"
        self.profiles_data = self.load_profiles()
        
    def load_config(self) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found. Using defaults.")
            return self.get_default_config()
    
    def get_default_config(self) -> dict:
        """Return default configuration"""
        return {
            "target_profiles": [],
            "output": {
                "base_directory": "scraped_data"
            }
        }
    
    def load_profiles(self) -> dict:
        """Load profiles data from file"""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading profiles: {e}")
                return {}
        return {}
    
    def save_profiles(self):
        """Save profiles data to file"""
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(self.profiles_data, f, indent=2)
            logger.info("Profiles saved successfully")
        except Exception as e:
            logger.error(f"Error saving profiles: {e}")
    
    def add_profile(self, username: str, url: Optional[str] = None) -> bool:
        """Add a new profile to track"""
        # Clean username (remove @ if present)
        username = username.strip().lstrip('@')
        
        if not url:
            url = f"https://www.tiktok.com/@{username}"
        
        if username in self.profiles_data:
            logger.info(f"Profile @{username} already exists")
            return False
        
        self.profiles_data[username] = {
            "url": url,
            "added_at": datetime.now().isoformat(),
            "last_scraped": None,
            "total_posts_scraped": 0,
            "slideshow_posts_scraped": 0,
            "status": "pending",
            "error_count": 0,
            "metadata": {}
        }
        
        # Also add to config
        if username not in self.config.get("target_profiles", []):
            self.config.setdefault("target_profiles", []).append(username)
            self.save_config()
        
        self.save_profiles()
        logger.success(f"Added profile @{username}")
        return True
    
    def remove_profile(self, username: str) -> bool:
        """Remove a profile from tracking"""
        username = username.strip().lstrip('@')
        
        if username not in self.profiles_data:
            logger.warning(f"Profile @{username} not found")
            return False
        
        del self.profiles_data[username]
        
        # Remove from config
        if username in self.config.get("target_profiles", []):
            self.config["target_profiles"].remove(username)
            self.save_config()
        
        self.save_profiles()
        logger.success(f"Removed profile @{username}")
        return True
    
    def update_profile_status(self, username: str, status: str, error: Optional[str] = None):
        """Update profile scraping status"""
        username = username.strip().lstrip('@')
        
        if username not in self.profiles_data:
            logger.warning(f"Profile @{username} not found")
            return
        
        self.profiles_data[username]["status"] = status
        
        if status == "completed":
            self.profiles_data[username]["last_scraped"] = datetime.now().isoformat()
        elif status == "error" and error:
            self.profiles_data[username]["error_count"] += 1
            self.profiles_data[username]["last_error"] = error
            self.profiles_data[username]["last_error_time"] = datetime.now().isoformat()
        
        self.save_profiles()
    
    def update_profile_stats(self, username: str, total_posts: int = 0, slideshow_posts: int = 0):
        """Update profile statistics"""
        username = username.strip().lstrip('@')
        
        if username not in self.profiles_data:
            return
        
        self.profiles_data[username]["total_posts_scraped"] += total_posts
        self.profiles_data[username]["slideshow_posts_scraped"] += slideshow_posts
        self.save_profiles()
    
    def get_pending_profiles(self) -> List[str]:
        """Get list of profiles that haven't been scraped yet"""
        return [
            username for username, data in self.profiles_data.items()
            if data["status"] == "pending" or data["status"] == "error"
        ]
    
    def get_profile_info(self, username: str) -> Optional[Dict]:
        """Get information about a specific profile"""
        username = username.strip().lstrip('@')
        return self.profiles_data.get(username)
    
    def list_profiles(self) -> List[Dict]:
        """List all profiles with their status"""
        profiles_list = []
        for username, data in self.profiles_data.items():
            profiles_list.append({
                "username": username,
                "url": data["url"],
                "status": data["status"],
                "last_scraped": data.get("last_scraped"),
                "total_posts": data.get("total_posts_scraped", 0),
                "slideshow_posts": data.get("slideshow_posts_scraped", 0),
                "errors": data.get("error_count", 0)
            })
        return profiles_list
    
    def save_config(self):
        """Save configuration back to file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def reset_profile(self, username: str):
        """Reset a profile's scraping status"""
        username = username.strip().lstrip('@')
        
        if username not in self.profiles_data:
            logger.warning(f"Profile @{username} not found")
            return
        
        self.profiles_data[username]["status"] = "pending"
        self.profiles_data[username]["error_count"] = 0
        self.save_profiles()
        logger.info(f"Reset profile @{username}")
    
    def get_profile_output_dir(self, username: str) -> Path:
        """Get the output directory for a specific profile"""
        username = username.strip().lstrip('@')
        base_dir = self.config.get("output", {}).get("base_directory", "scraped_data")
        profile_dir = Path(base_dir) / username
        profile_dir.mkdir(parents=True, exist_ok=True)
        return profile_dir


if __name__ == "__main__":
    # Test the ProfileManager
    manager = ProfileManager()
    
    # Add some test profiles
    manager.add_profile("@test_user1")
    manager.add_profile("@test_user2")
    
    # List profiles
    print("\nAll profiles:")
    for profile in manager.list_profiles():
        print(f"  @{profile['username']}: {profile['status']}")
    
    # Get pending profiles
    print("\nPending profiles:")
    for username in manager.get_pending_profiles():
        print(f"  @{username}")