#!/usr/bin/env python3
"""
Kinva Master Bot - Quality Manager
Author: @funnytamilan
"""

import logging
from typing import Dict, List, Tuple, Optional
import cv2
import numpy as np

logger = logging.getLogger(__name__)


class QualityManager:
    """Manage video and image quality settings"""
    
    # Quality presets for videos
    VIDEO_QUALITIES = {
        '144p': {
            'width': 256,
            'height': 144,
            'bitrate': '100k',
            'fps': 30,
            'label': '144p',
            'icon': '📱',
            'premium': False
        },
        '240p': {
            'width': 426,
            'height': 240,
            'bitrate': '300k',
            'fps': 30,
            'label': '240p',
            'icon': '📱',
            'premium': False
        },
        '360p': {
            'width': 640,
            'height': 360,
            'bitrate': '500k',
            'fps': 30,
            'label': '360p',
            'icon': '📱',
            'premium': False
        },
        '480p': {
            'width': 854,
            'height': 480,
            'bitrate': '1000k',
            'fps': 30,
            'label': '480p',
            'icon': '📺',
            'premium': False
        },
        '720p': {
            'width': 1280,
            'height': 720,
            'bitrate': '2500k',
            'fps': 30,
            'label': '720p HD',
            'icon': '📺',
            'premium': False
        },
        '1080p': {
            'width': 1920,
            'height': 1080,
            'bitrate': '5000k',
            'fps': 30,
            'label': '1080p Full HD',
            'icon': '🎬',
            'premium': False
        },
        '2K': {
            'width': 2560,
            'height': 1440,
            'bitrate': '8000k',
            'fps': 30,
            'label': '2K Quad HD',
            'icon': '🌟',
            'premium': True
        },
        '4K': {
            'width': 3840,
            'height': 2160,
            'bitrate': '15000k',
            'fps': 30,
            'label': '4K Ultra HD',
            'icon': '💎',
            'premium': True
        }
    }
    
    # Quality presets for images
    IMAGE_QUALITIES = {
        'low': {
            'quality': 30,
            'size_reduction': 0.3,
            'label': 'Low',
            'icon': '📱',
            'premium': False
        },
        'medium': {
            'quality': 60,
            'size_reduction': 0.5,
            'label': 'Medium',
            'icon': '📱',
            'premium': False
        },
        'high': {
            'quality': 85,
            'size_reduction': 0.8,
            'label': 'High',
            'icon': '📺',
            'premium': False
        },
        'ultra': {
            'quality': 100,
            'size_reduction': 1.0,
            'label': 'Ultra',
            'icon': '💎',
            'premium': True
        }
    }
    
    # Compression presets
    COMPRESSION_PRESETS = {
        'small': {
            'target_size_mb': 5,
            'label': 'Small (5MB)',
            'icon': '📱'
        },
        'medium': {
            'target_size_mb': 10,
            'label': 'Medium (10MB)',
            'icon': '📺'
        },
        'large': {
            'target_size_mb': 20,
            'label': 'Large (20MB)',
            'icon': '🎬'
        },
        'original': {
            'target_size_mb': None,
            'label': 'Original',
            'icon': '💎'
        }
    }
    
    def __init__(self):
        self.current_video_quality = '720p'
        self.current_image_quality = 'high'
    
    def get_video_quality_config(self, quality: str) -> Dict:
        """Get video quality configuration"""
        return self.VIDEO_QUALITIES.get(quality, self.VIDEO_QUALITIES['720p'])
    
    def get_image_quality_config(self, quality: str) -> Dict:
        """Get image quality configuration"""
        return self.IMAGE_QUALITIES.get(quality, self.IMAGE_QUALITIES['high'])
    
    def is_premium_quality(self, quality: str, file_type: str = 'video') -> bool:
        """Check if quality requires premium"""
        if file_type == 'video':
            config = self.VIDEO_QUALITIES.get(quality, {})
        else:
            config = self.IMAGE_QUALITIES.get(quality, {})
        
        return config.get('premium', False)
    
    def get_available_qualities(self, is_premium: bool, file_type: str = 'video') -> List[Dict]:
        """Get available qualities based on premium status"""
        if file_type == 'video':
            qualities = self.VIDEO_QUALITIES
        else:
            qualities = self.IMAGE_QUALITIES
        
        available = []
        for key, config in qualities.items():
            if not config.get('premium', False) or is_premium:
                available.append({
                    'id': key,
                    'label': config['label'],
                    'icon': config['icon'],
                    'premium': config.get('premium', False),
                    'width': config.get('width'),
                    'height': config.get('height'),
                    'bitrate': config.get('bitrate'),
                    'quality': config.get('quality')
                })
        
        return available
    
    def get_quality_options_text(self, is_premium: bool, file_type: str = 'video') -> str:
        """Get formatted quality options text"""
        qualities = self.get_available_qualities(is_premium, file_type)
        
        text = f"*🎬 {file_type.upper()} QUALITY OPTIONS*\n\n"
        
        for q in qualities:
            premium_badge = " 💎" if q['premium'] else ""
            text += f"{q['icon']} *{q['label']}{premium_badge}*\n"
            if q.get('width') and q.get('height'):
                text += f"   • Resolution: {q['width']}x{q['height']}\n"
            if q.get('bitrate'):
                text += f"   • Bitrate: {q['bitrate']}\n"
            if q.get('quality'):
                text += f"   • Quality: {q['quality']}%\n"
            text += "\n"
        
        return text
    
    def get_compression_options_text(self) -> str:
        """Get formatted compression options text"""
        text = "*📦 COMPRESSION OPTIONS*\n\n"
        
        for key, preset in self.COMPRESSION_PRESETS.items():
            text += f"{preset['icon']} *{preset['label']}*\n"
            if preset['target_size_mb']:
                text += f"   • Target size: {preset['target_size_mb']}MB\n"
            else:
                text += f"   • No compression\n"
            text += "\n"
        
        return text
    
    def calculate_video_bitrate(self, quality: str, duration: float, target_size_mb: float = None) -> int:
        """Calculate video bitrate based on quality and duration"""
        if target_size_mb:
            # Calculate bitrate for target size
            return int((target_size_mb * 8 * 1024) / duration)
        
        # Use preset bitrate
        config = self.get_video_quality_config(quality)
        bitrate_str = config['bitrate']
        return int(bitrate_str.replace('k', '')) * 1000
    
    def get_recommended_quality(self, file_size_mb: float, duration: float = None) -> str:
        """Get recommended quality based on file size"""
        if duration:
            # For videos, consider duration
            bitrate = (file_size_mb * 8 * 1024) / duration
            
            if bitrate < 500:
                return '360p'
            elif bitrate < 1000:
                return '480p'
            elif bitrate < 2500:
                return '720p'
            elif bitrate < 5000:
                return '1080p'
            else:
                return '4K'
        else:
            # For images
            if file_size_mb < 0.5:
                return 'ultra'
            elif file_size_mb < 2:
                return 'high'
            elif file_size_mb < 5:
                return 'medium'
            else:
                return 'low'
    
    def get_quality_stats(self, quality: str, file_type: str = 'video') -> Dict:
        """Get statistics for a quality setting"""
        if file_type == 'video':
            config = self.get_video_quality_config(quality)
            return {
                'resolution': f"{config['width']}x{config['height']}",
                'bitrate': config['bitrate'],
                'fps': config['fps'],
                'premium': config['premium']
            }
        else:
            config = self.get_image_quality_config(quality)
            return {
                'quality_percent': config['quality'],
                'size_reduction': f"{config['size_reduction']*100}%",
                'premium': config['premium']
            }
    
    def validate_quality(self, quality: str, is_premium: bool, file_type: str = 'video') -> Tuple[bool, str]:
        """Validate if quality is available for user"""
        if file_type == 'video':
            config = self.VIDEO_QUALITIES.get(quality)
        else:
            config = self.IMAGE_QUALITIES.get(quality)
        
        if not config:
            return False, f"Invalid quality: {quality}"
        
        if config.get('premium', False) and not is_premium:
            return False, f"{quality} requires premium membership. Upgrade to unlock!"
        
        return True, "OK"
    
    def get_quality_upgrade_message(self, quality: str) -> str:
        """Get message for premium quality upgrade"""
        return f"""💎 *Premium Quality: {quality}* 💎

This quality requires premium membership.

*Premium Benefits:*
• 4K Ultra HD Export
• Unlimited Daily Edits
• 50+ Premium Effects
• Priority Processing
• Batch Processing
• No Watermarks

*Upgrade now:* /premium

*Contact:* @funnytamilan for support! 🚀"""
    
    def calculate_output_size(self, input_size_mb: float, quality: str, file_type: str = 'video') -> float:
        """Calculate estimated output file size"""
        if file_type == 'video':
            config = self.get_video_quality_config(quality)
            bitrate = int(config['bitrate'].replace('k', ''))
            # Rough estimate: 1 minute of video at given bitrate
            estimated_mb_per_minute = (bitrate * 60) / (8 * 1024)
            return estimated_mb_per_minute
        else:
            config = self.get_image_quality_config(quality)
            reduction = config['size_reduction']
            return input_size_mb * reduction
    
    def get_quality_matrix(self) -> Dict:
        """Get complete quality matrix for display"""
        return {
            'video': [
                {
                    'name': q['label'],
                    'resolution': f"{q['width']}x{q['height']}",
                    'bitrate': q['bitrate'],
                    'premium': q['premium']
                }
                for q in self.VIDEO_QUALITIES.values()
            ],
            'image': [
                {
                    'name': q['label'],
                    'quality': f"{q['quality']}%",
                    'premium': q['premium']
                }
                for q in self.IMAGE_QUALITIES.values()
            ]
        }
    
    def get_quality_recommendation(self, purpose: str = 'social_media') -> str:
        """Get quality recommendation based on purpose"""
        recommendations = {
            'social_media': '720p',
            'youtube': '1080p',
            'professional': '4K',
            'quick_share': '480p',
            'archive': '4K',
            'mobile': '360p'
        }
        return recommendations.get(purpose, '720p')
    
    def optimize_for_platform(self, platform: str, quality: str) -> Dict:
        """Optimize quality settings for specific platform"""
        platform_settings = {
            'instagram': {
                'max_width': 1080,
                'max_height': 1920,
                'max_duration': 60,
                'recommended': '720p'
            },
            'youtube': {
                'max_width': 3840,
                'max_height': 2160,
                'max_duration': 7200,
                'recommended': '1080p'
            },
            'tiktok': {
                'max_width': 1080,
                'max_height': 1920,
                'max_duration': 180,
                'recommended': '720p'
            },
            'twitter': {
                'max_width': 1920,
                'max_height': 1080,
                'max_duration': 140,
                'recommended': '720p'
            },
            'whatsapp': {
                'max_width': 1280,
                'max_height': 720,
                'max_duration': 300,
                'recommended': '480p'
            }
        }
        
        return platform_settings.get(platform, {
            'max_width': 3840,
            'max_height': 2160,
            'max_duration': 3600,
            'recommended': quality
        })
