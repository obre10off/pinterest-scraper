"""
Data Extractor for TikTok Content
Parses JSON data from TikTok pages and extracts relevant information.
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from loguru import logger
from bs4 import BeautifulSoup


class DataExtractor:
    def __init__(self):
        self.slideshow_indicators = [
            "photo", "slideshow", "carousel", "swipe", "album",
            "ImagePost", "multi", "gallery"
        ]
        
    def extract_universal_data(self, html_content: str) -> Optional[Dict]:
        """Extract __UNIVERSAL_DATA_FOR_REHYDRATION__ from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find the script tag containing universal data
            script_tags = soup.find_all('script', id='__UNIVERSAL_DATA_FOR_REHYDRATION__')
            
            if not script_tags:
                # Try alternative ID patterns
                script_tags = soup.find_all('script', id=re.compile(r'__UNIVERSAL.*DATA.*'))
            
            if script_tags:
                script_content = script_tags[0].string
                if script_content:
                    # Clean and parse JSON
                    json_data = json.loads(script_content)
                    return json_data
            
            # Fallback: Look for SIGI_STATE or other data containers
            for script in soup.find_all('script'):
                if script.string and 'window.SIGI_STATE' in script.string:
                    match = re.search(r'window\.SIGI_STATE\s*=\s*({.*?});', script.string, re.DOTALL)
                    if match:
                        return json.loads(match.group(1))
                        
            logger.warning("No universal data found in HTML")
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON data: {e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting universal data: {e}")
            return None
    
    def is_slideshow_post(self, post_data: Dict) -> bool:
        """Determine if a post is a slideshow/carousel"""
        try:
            # Check various indicators for slideshow content
            post_str = json.dumps(post_data).lower()
            
            # Check for slideshow keywords
            for indicator in self.slideshow_indicators:
                if indicator.lower() in post_str:
                    return True
            
            # Check for multiple images
            if "imageurls" in post_str or "imageurl" in post_str:
                # Count image URLs
                image_count = post_str.count("imageurl")
                if image_count > 1:
                    return True
            
            # Check post type field
            if "type" in post_data:
                post_type = str(post_data.get("type", "")).lower()
                if any(ind in post_type for ind in self.slideshow_indicators):
                    return True
            
            # Check for image array
            if isinstance(post_data.get("images"), list) and len(post_data.get("images", [])) > 1:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking slideshow status: {e}")
            return False
    
    def extract_post_data(self, post: Dict) -> Optional[Dict]:
        """Extract relevant data from a TikTok post"""
        try:
            extracted = {
                "id": None,
                "type": "unknown",
                "is_slideshow": False,
                "caption": "",
                "hook": "",
                "hashtags": [],
                "mentions": [],
                "stats": {},
                "media": {},
                "author": {},
                "created_at": None,
                "url": None
            }
            
            # Extract post ID
            extracted["id"] = post.get("id") or post.get("itemId") or post.get("video_id")
            
            # Determine if slideshow
            extracted["is_slideshow"] = self.is_slideshow_post(post)
            
            # Extract caption and hook
            caption = self.extract_caption(post)
            extracted["caption"] = caption
            extracted["hook"] = self.extract_hook(caption)
            
            # Extract hashtags and mentions
            extracted["hashtags"] = self.extract_hashtags(caption)
            extracted["mentions"] = self.extract_mentions(caption)
            
            # Extract statistics
            extracted["stats"] = self.extract_statistics(post)
            
            # Extract media URLs
            extracted["media"] = self.extract_media_urls(post)
            
            # Extract author info
            extracted["author"] = self.extract_author_info(post)
            
            # Extract timestamp
            extracted["created_at"] = self.extract_timestamp(post)
            
            # Generate post URL
            if extracted["id"] and extracted["author"].get("username"):
                extracted["url"] = f"https://www.tiktok.com/@{extracted['author']['username']}/video/{extracted['id']}"
            
            return extracted
            
        except Exception as e:
            logger.error(f"Error extracting post data: {e}")
            return None
    
    def extract_caption(self, post: Dict) -> str:
        """Extract caption/description from post"""
        caption_fields = ["desc", "description", "caption", "text", "title"]
        
        for field in caption_fields:
            if field in post and post[field]:
                return str(post[field])
        
        # Deep search for caption
        if "video" in post and isinstance(post["video"], dict):
            for field in caption_fields:
                if field in post["video"]:
                    return str(post["video"][field])
        
        return ""
    
    def extract_hook(self, caption: str, max_length: int = 50) -> str:
        """Extract the hook (first compelling part) of the caption"""
        if not caption:
            return ""
        
        # Clean caption
        clean_caption = caption.strip()
        
        # Find natural break points
        break_points = [
            clean_caption.find('\n'),
            clean_caption.find('!'),
            clean_caption.find('?'),
            clean_caption.find('...'),
            clean_caption.find('#')
        ]
        
        # Filter valid break points
        valid_breaks = [bp for bp in break_points if 0 < bp < max_length]
        
        if valid_breaks:
            # Use the earliest break point
            hook_end = min(valid_breaks) + 1
            return clean_caption[:hook_end].strip()
        
        # No natural break, use max_length
        if len(clean_caption) <= max_length:
            return clean_caption
        
        # Find word boundary near max_length
        space_before = clean_caption.rfind(' ', 0, max_length)
        if space_before > 0:
            return clean_caption[:space_before].strip() + "..."
        
        return clean_caption[:max_length].strip() + "..."
    
    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        hashtags = re.findall(r'#(\w+)', text)
        return list(set(hashtags))  # Remove duplicates
    
    def extract_mentions(self, text: str) -> List[str]:
        """Extract mentions from text"""
        mentions = re.findall(r'@(\w+)', text)
        return list(set(mentions))  # Remove duplicates
    
    def extract_statistics(self, post: Dict) -> Dict:
        """Extract engagement statistics"""
        stats = {
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "bookmarks": 0
        }
        
        # Common field mappings
        stat_mappings = {
            "views": ["playCount", "play_count", "views", "video_play_count"],
            "likes": ["diggCount", "digg_count", "likes", "heart_count"],
            "comments": ["commentCount", "comment_count", "comments"],
            "shares": ["shareCount", "share_count", "shares"],
            "bookmarks": ["collectCount", "collect_count", "bookmarks", "save_count"]
        }
        
        # Search for statistics in post data
        for stat_key, field_names in stat_mappings.items():
            for field in field_names:
                if field in post:
                    stats[stat_key] = int(post.get(field, 0))
                    break
                # Check nested stats object
                if "stats" in post and field in post["stats"]:
                    stats[stat_key] = int(post["stats"].get(field, 0))
                    break
                if "statistics" in post and field in post["statistics"]:
                    stats[stat_key] = int(post["statistics"].get(field, 0))
                    break
        
        return stats
    
    def extract_media_urls(self, post: Dict) -> Dict:
        """Extract media URLs (images for slideshows, video for regular posts)"""
        media = {
            "type": "unknown",
            "images": [],
            "video_url": None,
            "cover_url": None,
            "music_url": None
        }
        
        if self.is_slideshow_post(post):
            media["type"] = "slideshow"
            # Extract image URLs
            media["images"] = self.extract_slideshow_images(post)
        else:
            media["type"] = "video"
            # Extract video URL
            media["video_url"] = self.extract_video_url(post)
        
        # Extract cover image
        cover_fields = ["cover", "coverUrl", "cover_url", "thumbnail"]
        for field in cover_fields:
            if field in post and post[field]:
                media["cover_url"] = post[field]
                break
        
        # Extract music/audio
        if "music" in post and isinstance(post["music"], dict):
            media["music_url"] = post["music"].get("playUrl") or post["music"].get("play_url")
        
        return media
    
    def extract_slideshow_images(self, post: Dict) -> List[str]:
        """Extract image URLs from slideshow post"""
        images = []
        
        # Check for images array
        if "images" in post and isinstance(post["images"], list):
            for img in post["images"]:
                if isinstance(img, dict):
                    url = img.get("url") or img.get("imageUrl") or img.get("imageURL")
                    if url:
                        images.append(url)
                elif isinstance(img, str):
                    images.append(img)
        
        # Check for imagePost structure
        if "imagePost" in post and isinstance(post["imagePost"], dict):
            if "images" in post["imagePost"]:
                for img in post["imagePost"]["images"]:
                    if isinstance(img, dict):
                        url = img.get("url") or img.get("imageUrl")
                        if url:
                            images.append(url)
        
        # Search for image URLs in string representation
        if not images:
            post_str = json.dumps(post)
            # Find URLs that look like image URLs
            url_pattern = r'https?://[^\s"]+\.(?:jpg|jpeg|png|gif|webp)'
            found_urls = re.findall(url_pattern, post_str, re.IGNORECASE)
            images.extend(found_urls)
        
        return list(set(images))  # Remove duplicates
    
    def extract_video_url(self, post: Dict) -> Optional[str]:
        """Extract video URL from post"""
        # Check video object
        if "video" in post and isinstance(post["video"], dict):
            video = post["video"]
            # Try different URL fields
            url_fields = ["downloadAddr", "download_addr", "playAddr", "play_addr", "url"]
            for field in url_fields:
                if field in video and video[field]:
                    return video[field]
        
        # Check direct URL fields
        url_fields = ["videoUrl", "video_url", "downloadUrl", "download_url"]
        for field in url_fields:
            if field in post and post[field]:
                return post[field]
        
        return None
    
    def extract_author_info(self, post: Dict) -> Dict:
        """Extract author/creator information"""
        author = {
            "username": None,
            "nickname": None,
            "user_id": None,
            "avatar_url": None,
            "verified": False
        }
        
        # Check for author/creator object
        author_obj = post.get("author") or post.get("creator") or post.get("user")
        
        if author_obj and isinstance(author_obj, dict):
            author["username"] = author_obj.get("uniqueId") or author_obj.get("unique_id") or author_obj.get("username")
            author["nickname"] = author_obj.get("nickname") or author_obj.get("nick_name")
            author["user_id"] = author_obj.get("id") or author_obj.get("uid") or author_obj.get("user_id")
            author["avatar_url"] = author_obj.get("avatarThumb") or author_obj.get("avatar_thumb") or author_obj.get("avatar")
            author["verified"] = author_obj.get("verified", False)
        
        return author
    
    def extract_timestamp(self, post: Dict) -> Optional[str]:
        """Extract post creation timestamp"""
        timestamp_fields = ["createTime", "create_time", "createdAt", "created_at", "timestamp"]
        
        for field in timestamp_fields:
            if field in post:
                timestamp = post[field]
                # Convert to ISO format if it's a Unix timestamp
                if isinstance(timestamp, (int, float)):
                    return datetime.fromtimestamp(timestamp).isoformat()
                return str(timestamp)
        
        return None
    
    def extract_profile_posts(self, universal_data: Dict) -> List[Dict]:
        """Extract all posts from profile page data"""
        posts = []
        
        try:
            # Navigate through possible data structures
            # Check for default scope
            if "__DEFAULT_SCOPE__" in universal_data:
                scope = universal_data["__DEFAULT_SCOPE__"]
                
                # Look for webapp user detail (main location for profile posts)
                if "webapp.user-detail" in scope:
                    user_detail = scope["webapp.user-detail"]
                    # Check userInfo.itemList (the main post list)
                    if isinstance(user_detail, dict) and "userInfo" in user_detail:
                        user_info = user_detail["userInfo"]
                        if isinstance(user_info, dict) and "itemList" in user_info:
                            item_list = user_info["itemList"]
                            if isinstance(item_list, list):
                                posts.extend(item_list)
                                logger.info(f"Found {len(item_list)} posts in userInfo.itemList")
                    
                    # Also check direct itemList
                    if isinstance(user_detail, dict) and "itemList" in user_detail:
                        item_list = user_detail["itemList"]
                        if isinstance(item_list, list):
                            posts.extend(item_list)
                            logger.info(f"Found {len(item_list)} posts in direct itemList")
                
                # Look for video list
                if "webapp.video-list" in scope:
                    video_list = scope["webapp.video-list"]
                    if isinstance(video_list, dict) and "itemList" in video_list:
                        item_list = video_list["itemList"]
                        if isinstance(item_list, list):
                            posts.extend(item_list)
                            logger.info(f"Found {len(item_list)} posts in video-list")
                
                # Look for any other webapp sections with itemList
                for key, value in scope.items():
                    if key.startswith("webapp.") and isinstance(value, dict):
                        if "itemList" in value and isinstance(value["itemList"], list):
                            posts.extend(value["itemList"])
                            logger.info(f"Found {len(value['itemList'])} posts in {key}")
            
            # Check for ItemModule
            if "ItemModule" in universal_data:
                item_module = universal_data["ItemModule"]
                if isinstance(item_module, dict):
                    posts.extend(item_module.values())
                    logger.info(f"Found {len(item_module)} posts in ItemModule")
            
            # Check for items directly
            if "items" in universal_data:
                items = universal_data["items"]
                if isinstance(items, list):
                    posts.extend(items)
                    logger.info(f"Found {len(items)} posts in direct items")
            
            logger.success(f"Total extracted: {len(posts)} posts from profile data")
            
        except Exception as e:
            logger.error(f"Error extracting profile posts: {e}")
        
        return posts
    
    def filter_slideshow_posts(self, posts: List[Dict]) -> List[Dict]:
        """Filter posts to only include slideshows"""
        slideshow_posts = []
        
        for post in posts:
            if self.is_slideshow_post(post):
                extracted = self.extract_post_data(post)
                if extracted:
                    slideshow_posts.append(extracted)
        
        logger.info(f"Filtered {len(slideshow_posts)} slideshow posts from {len(posts)} total posts")
        return slideshow_posts


if __name__ == "__main__":
    # Test the DataExtractor
    extractor = DataExtractor()
    
    # Test hook extraction
    test_caption = "This is an amazing hook! Follow for more content #viral #tiktok"
    hook = extractor.extract_hook(test_caption)
    print(f"Hook: {hook}")
    
    # Test hashtag extraction
    hashtags = extractor.extract_hashtags(test_caption)
    print(f"Hashtags: {hashtags}")