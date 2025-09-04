"""
Hook Analyzer for TikTok Content
Processes and categorizes hooks for training dataset generation.
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from collections import Counter
from datetime import datetime
from loguru import logger


class HookAnalyzer:
    def __init__(self):
        self.hook_patterns = {
            "question": {
                "patterns": [r"^(what|why|how|when|where|who|which|can|do|does|did|is|are|will|would|should)", r"\?"],
                "examples": ["How to...", "Why does...", "What if..."],
                "weight": 1.5
            },
            "statement": {
                "patterns": [r"^(i|you|we|they|this|that|here)", r"^[A-Z]"],
                "examples": ["I found...", "This is...", "You won't believe..."],
                "weight": 1.0
            },
            "story": {
                "patterns": [r"^(once|yesterday|today|last|when i|story time|pov|imagine)", r"story", r"time"],
                "examples": ["POV:", "Story time:", "When I..."],
                "weight": 1.3
            },
            "list": {
                "patterns": [r"^(\d+|top|best|worst)", r"reasons?", r"ways?", r"things?", r"tips?"],
                "examples": ["5 ways to...", "Top 3...", "Best tips for..."],
                "weight": 1.4
            },
            "challenge": {
                "patterns": [r"challenge", r"try", r"can you", r"bet you", r"dare"],
                "examples": ["Try this...", "Challenge:", "Bet you can't..."],
                "weight": 1.2
            },
            "emotional": {
                "patterns": [r"(never|always|everyone|no one|must|need)", r"!+$", r"😱|😭|🤯|💀|🔥"],
                "examples": ["You NEED this!", "NEVER do this...", "Everyone should..."],
                "weight": 1.6
            },
            "educational": {
                "patterns": [r"learn", r"teach", r"explain", r"guide", r"tutorial", r"how to"],
                "examples": ["Learn how to...", "Tutorial:", "Quick guide..."],
                "weight": 1.3
            },
            "controversial": {
                "patterns": [r"unpopular opinion", r"hot take", r"controversial", r"nobody talks about"],
                "examples": ["Unpopular opinion:", "Hot take:", "Nobody talks about..."],
                "weight": 1.7
            }
        }
        
    def categorize_hook(self, hook: str) -> Dict[str, float]:
        """Categorize a hook by type with confidence scores"""
        if not hook:
            return {"unknown": 1.0}
        
        hook_lower = hook.lower().strip()
        scores = {}
        
        for category, config in self.hook_patterns.items():
            score = 0.0
            patterns = config["patterns"]
            
            for pattern in patterns:
                if re.search(pattern, hook_lower, re.IGNORECASE):
                    score += config["weight"]
            
            if score > 0:
                scores[category] = min(score, 1.0)  # Cap at 1.0
        
        # Normalize scores
        if scores:
            total = sum(scores.values())
            scores = {k: v/total for k, v in scores.items()}
        else:
            scores = {"general": 1.0}
        
        return scores
    
    def analyze_hook_quality(self, hook: str) -> Dict[str, any]:
        """Analyze the quality and characteristics of a hook"""
        analysis = {
            "length": len(hook),
            "word_count": len(hook.split()),
            "has_emoji": bool(re.search(r'[😀-🙏🌀-🗿🚀-🛿🏀-🏿]', hook)),
            "has_caps": bool(re.search(r'[A-Z]{2,}', hook)),
            "has_punctuation": bool(re.search(r'[!?]+', hook)),
            "has_numbers": bool(re.search(r'\d+', hook)),
            "urgency_words": 0,
            "curiosity_score": 0,
            "clarity_score": 0
        }
        
        # Check for urgency words
        urgency_words = ["now", "today", "quick", "fast", "immediately", "urgent", "limited", "hurry"]
        for word in urgency_words:
            if word in hook.lower():
                analysis["urgency_words"] += 1
        
        # Calculate curiosity score (0-1)
        curiosity_triggers = ["secret", "reveal", "discover", "hidden", "truth", "nobody", "everyone", "shocking"]
        curiosity_count = sum(1 for trigger in curiosity_triggers if trigger in hook.lower())
        analysis["curiosity_score"] = min(curiosity_count / 3, 1.0)
        
        # Calculate clarity score (0-1)
        # Simple clarity: shorter sentences with common words score higher
        if analysis["word_count"] > 0:
            analysis["clarity_score"] = min(1.0, 10 / analysis["word_count"])
        
        return analysis
    
    def extract_hook_components(self, hook: str) -> Dict[str, str]:
        """Extract components of a hook for detailed analysis"""
        components = {
            "opening": "",
            "body": "",
            "call_to_action": "",
            "hashtags": [],
            "mentions": []
        }
        
        # Extract hashtags and mentions
        components["hashtags"] = re.findall(r'#(\w+)', hook)
        components["mentions"] = re.findall(r'@(\w+)', hook)
        
        # Clean hook for component extraction
        clean_hook = re.sub(r'[#@]\w+', '', hook).strip()
        
        # Split into components (simple heuristic)
        words = clean_hook.split()
        if len(words) > 0:
            # First 1-3 words as opening
            components["opening"] = ' '.join(words[:min(3, len(words))])
            
            # Middle as body
            if len(words) > 3:
                components["body"] = ' '.join(words[3:min(-2, len(words)-2)] if len(words) > 5 else words[3:])
            
            # Last part as call to action (if exists)
            if len(words) > 5:
                potential_cta = ' '.join(words[-2:])
                cta_indicators = ["follow", "like", "share", "comment", "watch", "swipe", "tap", "click"]
                if any(indicator in potential_cta.lower() for indicator in cta_indicators):
                    components["call_to_action"] = potential_cta
        
        return components
    
    def generate_training_data(self, posts: List[Dict]) -> Dict:
        """Generate training dataset from posts"""
        training_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_posts": len(posts),
                "total_hooks": 0,
                "categories": {},
                "quality_metrics": {}
            },
            "hooks": [],
            "patterns": {},
            "statistics": {}
        }
        
        all_hooks = []
        category_counts = Counter()
        quality_scores = []
        
        for post in posts:
            if not post or not post.get("hook"):
                continue
            
            hook = post["hook"]
            
            # Analyze hook
            categories = self.categorize_hook(hook)
            quality = self.analyze_hook_quality(hook)
            components = self.extract_hook_components(hook)
            
            # Get primary category
            primary_category = max(categories.items(), key=lambda x: x[1])[0] if categories else "unknown"
            category_counts[primary_category] += 1
            
            # Calculate overall quality score
            quality_score = (
                quality["curiosity_score"] * 0.3 +
                quality["clarity_score"] * 0.3 +
                (1.0 if quality["has_emoji"] else 0.5) * 0.1 +
                (1.0 if quality["has_caps"] else 0.5) * 0.1 +
                (min(quality["urgency_words"] / 2, 1.0)) * 0.2
            )
            quality_scores.append(quality_score)
            
            # Create training entry
            training_entry = {
                "hook": hook,
                "categories": categories,
                "primary_category": primary_category,
                "quality_analysis": quality,
                "quality_score": quality_score,
                "components": components,
                "metadata": {
                    "post_id": post.get("id"),
                    "author": post.get("author", {}).get("username"),
                    "stats": post.get("stats", {}),
                    "is_slideshow": post.get("is_slideshow", False)
                }
            }
            
            training_data["hooks"].append(training_entry)
            all_hooks.append(hook)
        
        # Update metadata
        training_data["metadata"]["total_hooks"] = len(all_hooks)
        training_data["metadata"]["categories"] = dict(category_counts)
        
        # Calculate statistics
        if quality_scores:
            training_data["statistics"] = {
                "avg_quality_score": sum(quality_scores) / len(quality_scores),
                "max_quality_score": max(quality_scores),
                "min_quality_score": min(quality_scores),
                "avg_hook_length": sum(len(h) for h in all_hooks) / len(all_hooks) if all_hooks else 0,
                "avg_word_count": sum(len(h.split()) for h in all_hooks) / len(all_hooks) if all_hooks else 0
            }
        
        # Extract patterns
        training_data["patterns"] = self.extract_patterns(all_hooks)
        
        return training_data
    
    def extract_patterns(self, hooks: List[str]) -> Dict:
        """Extract common patterns from hooks"""
        patterns = {
            "common_openings": [],
            "common_endings": [],
            "frequent_words": [],
            "emoji_usage": {},
            "length_distribution": {}
        }
        
        if not hooks:
            return patterns
        
        # Extract openings and endings
        openings = []
        endings = []
        all_words = []
        emojis = []
        
        for hook in hooks:
            words = hook.split()
            if words:
                # First 2 words as opening
                opening = ' '.join(words[:min(2, len(words))]).lower()
                openings.append(opening)
                
                # Last 2 words as ending
                if len(words) > 2:
                    ending = ' '.join(words[-2:]).lower()
                    endings.append(ending)
                
                # All words for frequency
                all_words.extend([w.lower() for w in words])
                
                # Extract emojis
                hook_emojis = re.findall(r'[😀-🙏🌀-🗿🚀-🛿🏀-🏿]', hook)
                emojis.extend(hook_emojis)
        
        # Get most common patterns
        patterns["common_openings"] = [
            {"pattern": opening, "count": count}
            for opening, count in Counter(openings).most_common(10)
        ]
        
        patterns["common_endings"] = [
            {"pattern": ending, "count": count}
            for ending, count in Counter(endings).most_common(10)
        ]
        
        # Filter out common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were"}
        filtered_words = [w for w in all_words if w not in stop_words and len(w) > 2]
        patterns["frequent_words"] = [
            {"word": word, "count": count}
            for word, count in Counter(filtered_words).most_common(20)
        ]
        
        # Emoji statistics
        if emojis:
            patterns["emoji_usage"] = dict(Counter(emojis).most_common(10))
        
        # Length distribution
        length_buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81+": 0}
        for hook in hooks:
            length = len(hook)
            if length <= 20:
                length_buckets["0-20"] += 1
            elif length <= 40:
                length_buckets["21-40"] += 1
            elif length <= 60:
                length_buckets["41-60"] += 1
            elif length <= 80:
                length_buckets["61-80"] += 1
            else:
                length_buckets["81+"] += 1
        
        patterns["length_distribution"] = length_buckets
        
        return patterns
    
    def save_training_data(self, training_data: Dict, output_path: str = "training_dataset.json"):
        """Save training data to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(training_data, f, indent=2, ensure_ascii=False)
            logger.success(f"Training data saved to {output_path}")
            
            # Also save a simplified version for easier ML processing
            simplified_path = output_path.replace('.json', '_simplified.json')
            simplified_data = [
                {
                    "text": entry["hook"],
                    "category": entry["primary_category"],
                    "quality": entry["quality_score"],
                    "is_slideshow": entry["metadata"]["is_slideshow"]
                }
                for entry in training_data["hooks"]
            ]
            
            with open(simplified_path, 'w', encoding='utf-8') as f:
                json.dump(simplified_data, f, indent=2, ensure_ascii=False)
            logger.success(f"Simplified training data saved to {simplified_path}")
            
        except Exception as e:
            logger.error(f"Error saving training data: {e}")
    
    def process_scraped_data(self, data_dir: str = "scraped_data") -> Dict:
        """Process all scraped data from multiple profiles"""
        all_posts = []
        data_path = Path(data_dir)
        
        # Collect all posts from all profiles
        for profile_dir in data_path.iterdir():
            if profile_dir.is_dir():
                slideshows_file = profile_dir / "slideshows.json"
                if slideshows_file.exists():
                    try:
                        with open(slideshows_file, 'r', encoding='utf-8') as f:
                            posts = json.load(f)
                            all_posts.extend(posts)
                            logger.info(f"Loaded {len(posts)} posts from {profile_dir.name}")
                    except Exception as e:
                        logger.error(f"Error loading posts from {profile_dir.name}: {e}")
        
        logger.info(f"Total posts collected: {len(all_posts)}")
        
        # Generate training data
        training_data = self.generate_training_data(all_posts)
        
        return training_data


if __name__ == "__main__":
    # Test the HookAnalyzer
    analyzer = HookAnalyzer()
    
    # Test hook categorization
    test_hooks = [
        "How to make your photos look professional",
        "POV: You're a photographer in NYC",
        "5 tips for better Instagram photos",
        "You NEED to try this hack!",
        "Unpopular opinion: Film is better than digital"
    ]
    
    print("Hook Analysis Examples:\n")
    for hook in test_hooks:
        categories = analyzer.categorize_hook(hook)
        quality = analyzer.analyze_hook_quality(hook)
        print(f"Hook: {hook}")
        print(f"  Categories: {categories}")
        print(f"  Quality Score: {quality}")
        print()