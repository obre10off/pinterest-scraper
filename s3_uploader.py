"""
S3 Uploader for Pinterest Scraper
Handles uploading 9x16 images to AWS S3 bucket with organized structure.
"""

import os
import boto3
import hashlib
from pathlib import Path
from typing import List, Dict, Optional
from botocore.exceptions import ClientError, NoCredentialsError
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()


class S3Uploader:
    def __init__(self):
        """Initialize S3 client with credentials from environment variables"""
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        self.bucket_name = os.getenv('AWS_S3_BUCKET_NAME', 'tryfaceless')
        
        try:
            self.s3_client = boto3.client(
                's3',
                region_name=self.region,
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
            logger.info(f"Initialized S3 client for bucket: {self.bucket_name}")
        except NoCredentialsError:
            logger.error("AWS credentials not found. Please check your .env file.")
            raise
        except Exception as e:
            logger.error(f"Error initializing S3 client: {e}")
            raise
    
    def file_exists_in_s3(self, s3_key: str) -> bool:
        """Check if a file already exists in S3"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                logger.error(f"Error checking if file exists: {e}")
                return False
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def upload_file(self, local_file_path: Path, s3_key: str, skip_existing: bool = True) -> bool:
        """Upload a single file to S3"""
        try:
            # Check if file exists and skip if requested
            if skip_existing and self.file_exists_in_s3(s3_key):
                logger.info(f"Skipping {s3_key} - already exists in S3")
                return True
            
            # Upload file
            self.s3_client.upload_file(
                str(local_file_path),
                self.bucket_name,
                s3_key,
                ExtraArgs={'ContentType': 'image/jpeg'}
            )
            
            logger.success(f"Uploaded: {local_file_path.name} -> s3://{self.bucket_name}/{s3_key}")
            return True
            
        except FileNotFoundError:
            logger.error(f"File not found: {local_file_path}")
            return False
        except ClientError as e:
            logger.error(f"Error uploading {local_file_path.name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error uploading {local_file_path.name}: {e}")
            return False
    
    def upload_category_images(self, category_name: str, findings_dir: Path = Path("findings")) -> Dict[str, int]:
        """Upload all 9x16 images for a specific category"""
        category_dir = findings_dir / category_name
        images_dir = category_dir / "images_9x16"
        
        if not category_dir.exists():
            logger.error(f"Category directory not found: {category_dir}")
            return {"uploaded": 0, "skipped": 0, "errors": 0}
        
        if not images_dir.exists():
            logger.error(f"Images directory not found: {images_dir}")
            return {"uploaded": 0, "skipped": 0, "errors": 0}
        
        # Get all image files
        image_files = list(images_dir.glob("*.jpg"))
        if not image_files:
            logger.warning(f"No .jpg files found in {images_dir}")
            return {"uploaded": 0, "skipped": 0, "errors": 0}
        
        logger.info(f"Found {len(image_files)} images in {category_name}")
        
        # Upload statistics
        stats = {"uploaded": 0, "skipped": 0, "errors": 0}
        
        for image_file in image_files:
            # Create S3 key: library/category-name/filename
            s3_key = f"library/{category_name}/{image_file.name}"
            
            # Check if file exists
            if self.file_exists_in_s3(s3_key):
                logger.info(f"Skipping {image_file.name} - already exists")
                stats["skipped"] += 1
                continue
            
            # Upload file
            success = self.upload_file(image_file, s3_key, skip_existing=True)
            if success:
                stats["uploaded"] += 1
            else:
                stats["errors"] += 1
        
        return stats
    
    def list_available_categories(self, findings_dir: Path = Path("findings")) -> List[str]:
        """List all available categories that have 9x16 images"""
        categories = []
        
        if not findings_dir.exists():
            logger.error(f"Findings directory not found: {findings_dir}")
            return categories
        
        for category_dir in findings_dir.iterdir():
            if category_dir.is_dir():
                images_dir = category_dir / "images_9x16"
                if images_dir.exists() and any(images_dir.glob("*.jpg")):
                    categories.append(category_dir.name)
        
        return sorted(categories)
    
    def get_category_stats(self, category_name: str, findings_dir: Path = Path("findings")) -> Dict[str, int]:
        """Get statistics for a category (local files count)"""
        category_dir = findings_dir / category_name
        images_dir = category_dir / "images_9x16"
        
        if not images_dir.exists():
            return {"local_files": 0}
        
        image_files = list(images_dir.glob("*.jpg"))
        return {"local_files": len(image_files)}
    
    def test_connection(self) -> bool:
        """Test S3 connection and permissions"""
        try:
            # Try to list objects in the bucket
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=1
            )
            logger.success(f"Successfully connected to S3 bucket: {self.bucket_name}")
            return True
        except ClientError as e:
            logger.error(f"Error connecting to S3: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error testing S3 connection: {e}")
            return False


def main():
    """Test the S3 uploader"""
    uploader = S3Uploader()
    
    # Test connection
    if not uploader.test_connection():
        return
    
    # List available categories
    categories = uploader.list_available_categories()
    print(f"Available categories: {categories}")
    
    # Test with first category
    if categories:
        test_category = categories[0]
        print(f"\nTesting upload with category: {test_category}")
        
        stats = uploader.upload_category_images(test_category)
        print(f"Upload results: {stats}")


if __name__ == "__main__":
    main()
