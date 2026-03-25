#!/usr/bin/env python3
"""
Kinva Master Bot - Configuration File
Author: @funnytamilan
"""

import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

class Config:
    """Main configuration class for Kinva Master Bot"""
    
    # ============= BOT CONFIGURATION =============
    BOT_TOKEN = os.getenv('BOT_TOKEN', '8776043562:AAHLiV5VKyUXvhscNJ6FZZ2YLlqYiag_tHc')
    ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '8525952693').split(',')]
    
    # ============= WEB APP CONFIGURATION =============
    WEB_APP_URL = os.getenv('WEB_APP_URL', 'https://kinva-master-bot.onrender.com')
    WEB_APP_PORT = int(os.getenv('PORT', 5000))
    WEB_APP_HOST = os.getenv('HOST', '0.0.0.0')
    SECRET_KEY = os.getenv('SECRET_KEY', 'kinva-master-secret-key-2024')
    
    # ============= DATABASE CONFIGURATION =============
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://Bosshub:JMaff0WvazwNxKky@cluster0.l0xcoc1.mongodb.net/?appName=Cluster0')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'kinva_master')
    REDIS_URL = os.getenv('REDIS_URL', 'kinva-master-bot.onrender.com')
    
    # ============= PREMIUM SETTINGS =============
    TRIAL_DAYS = 60  # 2 months free trial
    PREMIUM_PRICE = 9.99  # USD
    PREMIUM_CURRENCY = 'USD'
    PREMIUM_CONTACT = '@funnytamilan'
    
    # Premium duration options
    PREMIUM_DURATIONS = {
        'monthly': 30,
        'quarterly': 90,
        'half_yearly': 180,
        'yearly': 365,
        'lifetime': 3650  # 10 years
    }
    
    # ============= QUALITY PRESETS =============
    VIDEO_QUALITIES = {
        '144p': {'width': 256, 'height': 144, 'bitrate': '100k', 'fps': 30},
        '240p': {'width': 426, 'height': 240, 'bitrate': '300k', 'fps': 30},
        '360p': {'width': 640, 'height': 360, 'bitrate': '500k', 'fps': 30},
        '480p': {'width': 854, 'height': 480, 'bitrate': '1000k', 'fps': 30},
        '720p': {'width': 1280, 'height': 720, 'bitrate': '2500k', 'fps': 30},
        '1080p': {'width': 1920, 'height': 1080, 'bitrate': '5000k', 'fps': 30},
        '2K': {'width': 2560, 'height': 1440, 'bitrate': '8000k', 'fps': 30},
        '4K': {'width': 3840, 'height': 2160, 'bitrate': '15000k', 'fps': 30}
    }
    
    IMAGE_QUALITIES = {
        'low': {'quality': 30, 'size_reduction': 0.3},
        'medium': {'quality': 60, 'size_reduction': 0.5},
        'high': {'quality': 85, 'size_reduction': 0.8},
        'ultra': {'quality': 100, 'size_reduction': 1.0}
    }
    
    # ============= FILE SETTINGS =============
    MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
    MAX_VIDEO_DURATION = 600  # 10 minutes
    MAX_IMAGES_PER_COLLAGE = 10
    
    # Directory paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TEMP_DIR = os.path.join(BASE_DIR, 'temp')
    OUTPUT_DIR = os.path.join(BASE_DIR, 'outputs')
    UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
    
    # ============= SUPPORTED FORMATS =============
    SUPPORTED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'heic', 'tiff']
    SUPPORTED_VIDEO_FORMATS = ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'm4v', '3gp']
    SUPPORTED_AUDIO_FORMATS = ['mp3', 'wav', 'aac', 'ogg', 'm4a']
    
    # ============= EFFECTS LIST =============
    IMAGE_EFFECTS = {
        'basic': ['vintage', 'cinematic', 'black_white', 'sepia', 'blur', 'sharpen'],
        'artistic': ['watercolor', 'oil_painting', 'sketch', 'cartoon', 'neon'],
        'modern': ['glitch', 'pixelate', 'mosaic', 'emboss', 'edge_detect'],
        'premium': ['3d_effect', 'cinematic_pro', 'ai_enhance', 'style_transfer']
    }
    
    VIDEO_EFFECTS = {
        'basic': ['vhs', 'retro', 'black_white', 'sepia', 'blur'],
        'motion': ['slow_motion', 'timelapse', 'reverse', 'zoom_in', 'zoom_out'],
        'effects': ['glitch', 'shake', 'fade_in', 'fade_out', 'glow'],
        'premium': ['4k_upscale', 'motion_tracking', 'green_screen', 'face_swap']
    }
    
    # ============= LIMITS =============
    DAILY_FREE_LIMIT = 100  # Free users daily edit limit
    DAILY_PREMIUM_LIMIT = 10000  # Premium users daily limit
    MAX_CONCURRENT_JOBS = 5
    JOB_TIMEOUT = 300  # 5 minutes
    
    # ============= CLOUD STORAGE =============
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME', '')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY', '')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET', '')
    
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY', '')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY', '')
    AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME', '')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # ============= PAYMENT SETTINGS =============
    PAYMENT_METHODS = ['UPI', 'CRYPTO', 'CARD', 'BANK_TRANSFER']
    UPI_ID = os.getenv('UPI_ID', 'funnytamilan@okhdfcbank')
    CRYPTO_ADDRESS = os.getenv('CRYPTO_ADDRESS', '')
    STRIPE_API_KEY = os.getenv('STRIPE_API_KEY', '')
    
    # ============= API KEYS =============
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    REPLICATE_API_KEY = os.getenv('REPLICATE_API_KEY', '')
    
    # ============= SOCIAL MEDIA =============
    SUPPORT_CHANNEL = 'https://t.me/funnytamilan'
    UPDATE_CHANNEL = 'https://t.me/kinvamaster'
    WEBSITE_URL = 'https://kinvamaster.com'
    
    # ============= BOT MESSAGES =============
    WELCOME_MESSAGE = """
🎨 *WELCOME TO KINVA MASTER BOT!* 🚀

Hello {first_name}! I'm your professional video and image editing assistant.

✨ *FEATURES:*
• 🖼️ Advanced Image Editing
• 🎬 Professional Video Editing
• 🌟 50+ Effects & Filters
• 🎨 AI Background Removal
• 📱 Web Editor with Live Streaming
• 💎 Quality Export: 144p → 4K

💎 *YOUR STATUS:* {status}

🎯 *GET STARTED:* Send me any photo or video!
"""
    
    HELP_MESSAGE = """
📚 *KINVA MASTER - HELP GUIDE*

*🎨 IMAGE EDITING:*
• Send image + apply filters
• /removebg - AI background removal
• /collage - Create photo collage
• /text [text] - Add text overlay
• /resize [width] [height] - Resize image

*🎬 VIDEO EDITING:*
• /trim [start] [end] - Trim video
• /speed [0.5-3.0] - Change speed
• /compress - Compress video
• /music - Add background music
• /quality - Set export quality

*✨ EFFECTS:*
vintage, cinematic, black_white, sepia
glitch, neon, watercolor, sketch
vhs, retro, slow_motion, timelapse

*💎 PREMIUM FEATURES:*
• 4K Ultra HD Export
• Unlimited Edits
• 50+ Premium Effects
• Priority Processing
• Batch Processing (10 files)
• 100GB Cloud Storage

*Commands:* /start, /help, /profile, /premium, /webapp
"""
    
    PREMIUM_MESSAGE = """
💎 *PREMIUM MEMBERSHIP* 💎

*BENEFITS:*
🌟 4K ULTRA HD EXPORT
🚀 3x FASTER PROCESSING
🎨 50+ EXCLUSIVE EFFECTS
📦 BATCH PROCESS (10 files)
☁️ 100GB CLOUD STORAGE
🎬 LIVE STREAM EDITING
💎 NO WATERMARKS
🎯 PRIORITY SUPPORT

*PRICE:* ${price}/month

*UPGRADE:* Contact {contact}
"""
    
    # ============= HELPER METHODS =============
    
    @classmethod
    def get_quality_config(cls, quality: str) -> dict:
        """Get video quality configuration"""
        return cls.VIDEO_QUALITIES.get(quality, cls.VIDEO_QUALITIES['720p'])
    
    @classmethod
    def get_image_quality(cls, quality: str) -> dict:
        """Get image quality configuration"""
        return cls.IMAGE_QUALITIES.get(quality, cls.IMAGE_QUALITIES['high'])
    
    @classmethod
    def is_premium_quality(cls, quality: str) -> bool:
        """Check if quality requires premium"""
        premium_qualities = ['2K', '4K']
        return quality in premium_qualities
    
    @classmethod
    def is_premium_effect(cls, effect: str) -> bool:
        """Check if effect requires premium"""
        premium_effects = cls.IMAGE_EFFECTS['premium'] + cls.VIDEO_EFFECTS['premium']
        return effect in premium_effects
    
    @classmethod
    def create_directories(cls):
        """Create all required directories"""
        directories = [
            cls.TEMP_DIR,
            cls.OUTPUT_DIR,
            cls.UPLOAD_DIR,
            cls.LOGS_DIR,
            cls.STATIC_DIR,
            cls.TEMPLATES_DIR
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
        
        # Create subdirectories
        os.makedirs(os.path.join(cls.STATIC_DIR, 'css'), exist_ok=True)
        os.makedirs(os.path.join(cls.STATIC_DIR, 'js'), exist_ok=True)
        os.makedirs(os.path.join(cls.STATIC_DIR, 'img'), exist_ok=True)
    
    @classmethod
    def validate_config(cls) -> list:
        """Validate configuration and return errors"""
        errors = []
        
        if not cls.BOT_TOKEN or cls.BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
            errors.append("BOT_TOKEN is not set in environment variables")
        
        if not cls.MONGODB_URI:
            errors.append("MONGODB_URI is not set in environment variables")
        
        if not cls.WEB_APP_URL or cls.WEB_APP_URL == 'https://your-domain.com':
            errors.append("WEB_APP_URL is not set in environment variables")
        
        return errors
    
    @classmethod
    def get_stats(cls) -> dict:
        """Get configuration statistics"""
        return {
            'bot_token_set': bool(cls.BOT_TOKEN and cls.BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE'),
            'web_app_url_set': bool(cls.WEB_APP_URL and cls.WEB_APP_URL != 'https://your-domain.com'),
            'mongodb_uri_set': bool(cls.MONGODB_URI),
            'admin_count': len(cls.ADMIN_IDS),
            'video_qualities': len(cls.VIDEO_QUALITIES),
            'image_effects': sum(len(v) for v in cls.IMAGE_EFFECTS.values()),
            'video_effects': sum(len(v) for v in cls.VIDEO_EFFECTS.values()),
            'trial_days': cls.TRIAL_DAYS,
            'max_file_size_mb': cls.MAX_FILE_SIZE / (1024 * 1024)
        }

# Create directories on import
Config.create_directories()

# Validate configuration on import
errors = Config.validate_config()
if errors:
    import logging
    logging.warning(f"Configuration warnings: {errors}")
