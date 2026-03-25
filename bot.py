#!/usr/bin/env python3
"""
Kinva Master Telegram Bot - Complete Production Bot with Advanced UI
Author: @funnytamilan
Version: 3.0
"""

import os
import asyncio
import logging
import uuid
import shutil
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import json
import re
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, InputFile, InputMediaPhoto
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes, ConversationHandler
)
from telegram.constants import ParseMode
from telegram.error import TelegramError

from config import Config
from database import Database
from admin import AdminPanel
from utils.image_editor import ImageEditor
from utils.video_editor import VideoEditor
from utils.effects import AdvancedEffects
from utils.error_handler import auto_fix_error, ErrorRecovery
from utils.quality_manager import QualityManager
from utils.premium_manager import PremiumManager
from utils.streaming import StreamManager

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create logs directory
os.makedirs('logs', exist_ok=True)

# Conversation states
(WAITING_FOR_TEXT, WAITING_FOR_TRIM_START, WAITING_FOR_TRIM_END, 
 WAITING_FOR_SPEED, WAITING_FOR_QUALITY, WAITING_FOR_MUSIC,
 WAITING_FOR_PREMIUM_USER, WAITING_FOR_PREMIUM_DAYS) = range(8)

class KinvaMasterBot:
    """Main bot class for Kinva Master"""
    
    def __init__(self):
        """Initialize bot with all managers"""
        self.config = Config()
        self.db = Database()
        self.admin_panel = AdminPanel()
        self.image_editor = ImageEditor()
        self.video_editor = VideoEditor()
        self.effects = AdvancedEffects()
        self.quality_manager = QualityManager()
        self.premium_manager = PremiumManager()
        self.stream_manager = StreamManager()
        self.user_sessions = {}
        
        # Create necessary directories
        os.makedirs(self.config.TEMP_DIR, exist_ok=True)
        os.makedirs(self.config.OUTPUT_DIR, exist_ok=True)
        os.makedirs(self.config.UPLOAD_DIR, exist_ok=True)
        
        logger.info("Kinva Master Bot initialized successfully")
    
    async def create_welcome_image(self, user_first_name: str, is_premium: bool, trial_days: int, total_edits: int) -> BytesIO:
        """Create a beautiful welcome image with custom design"""
        try:
            # Create image with gradient background
            img = Image.new('RGB', (1200, 800), color='#1a1a2e')
            draw = ImageDraw.Draw(img)
            
            # Add gradient effect
            for i in range(800):
                color_value = int(30 + (i / 800) * 50)
                draw.rectangle([(0, i), (1200, i+1)], fill=(color_value, color_value, color_value+20))
            
            # Try to load custom fonts, fallback to default
            try:
                title_font = ImageFont.truetype("fonts/Poppins-Bold.ttf", 72)
                subtitle_font = ImageFont.truetype("fonts/Poppins-Regular.ttf", 36)
                button_font = ImageFont.truetype("fonts/Poppins-Medium.ttf", 28)
                status_font = ImageFont.truetype("fonts/Poppins-SemiBold.ttf", 24)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                button_font = ImageFont.load_default()
                status_font = ImageFont.load_default()
            
            # Draw decorative elements
            # Top gradient line
            for i in range(1200):
                draw.point((i, 0), fill=(255, 100, 100))
            
            # Draw circles for decoration
            draw.ellipse([(950, 50), (1150, 250)], outline=(255, 100, 100), width=3)
            draw.ellipse([(50, 600), (250, 800)], outline=(100, 150, 255), width=3)
            
            # Main title with gradient effect
            title_text = "✨ KINVA MASTER ✨"
            title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (1200 - title_width) // 2
            
            # Add shadow effect
            draw.text((title_x + 4, 104), title_text, fill=(0, 0, 0), font=title_font)
            draw.text((title_x, 100), title_text, fill=(255, 215, 0), font=title_font)
            
            # Welcome message with user name
            welcome_text = f"Welcome, {user_first_name}! 🎉"
            welcome_bbox = draw.textbbox((0, 0), welcome_text, font=subtitle_font)
            welcome_width = welcome_bbox[2] - welcome_bbox[0]
            welcome_x = (1200 - welcome_width) // 2
            draw.text((welcome_x, 220), welcome_text, fill=(255, 255, 255), font=subtitle_font)
            
            # Status card background
            card_y = 320
            draw.rectangle([(100, card_y), (1100, card_y + 180)], fill=(30, 30, 60), outline=(255, 100, 100), width=2)
            
            # Premium status with emojis
            if is_premium:
                status_icon = "💎"
                status_text = "PREMIUM MEMBER"
                status_color = (255, 215, 0)
                days_text = f"✨ Active until: {self.db.get_user_stats(user_first_name)['premium_expiry']}"
            else:
                status_icon = "🎁"
                status_text = "TRIAL ACTIVE"
                status_color = (100, 200, 255)
                days_text = f"⏰ {trial_days} days remaining"
            
            # Draw status
            status_full = f"{status_icon} {status_text}"
            status_bbox = draw.textbbox((0, 0), status_full, font=status_font)
            status_width = status_bbox[2] - status_bbox[0]
            draw.text(((1200 - status_width) // 2, card_y + 30), status_full, fill=status_color, font=status_font)
            
            # Draw trial days and edits
            stats_text = f"📊 {days_text}    🎬 {total_edits} total edits"
            stats_bbox = draw.textbbox((0, 0), stats_text, font=status_font)
            stats_width = stats_bbox[2] - stats_bbox[0]
            draw.text(((1200 - stats_width) // 2, card_y + 80), stats_text, fill=(200, 200, 200), font=status_font)
            
            # Features section
            features_y = 540
            features_title = "🚀 FEATURES"
            title_bbox = draw.textbbox((0, 0), features_title, font=subtitle_font)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text(((1200 - title_width) // 2, features_y), features_title, fill=(255, 215, 0), font=subtitle_font)
            
            # Feature boxes
            features = [
                ("🎨", "50+ Effects", "Professional filters"),
                ("🎬", "Video Editor", "Trim, merge, music"),
                ("💎", "4K Export", "Ultra HD quality"),
                ("🌐", "Web Editor", "Live streaming")
            ]
            
            box_width = 250
            box_height = 100
            start_x = (1200 - (box_width * 4 + 60)) // 2
            
            for i, (icon, title, desc) in enumerate(features):
                x = start_x + i * (box_width + 20)
                # Draw box
                draw.rectangle([(x, features_y + 50), (x + box_width, features_y + 50 + box_height)], 
                             fill=(40, 40, 70), outline=(100, 100, 150), width=1)
                # Icon
                draw.text((x + 15, features_y + 65), icon, fill=(255, 215, 0), font=subtitle_font)
                # Title
                draw.text((x + 60, features_y + 65), title, fill=(255, 255, 255), font=status_font)
                # Description
                desc_font = ImageFont.load_default()
                draw.text((x + 15, features_y + 95), desc, fill=(180, 180, 200), font=desc_font)
            
            # Footer
            footer_text = "💡 Send a photo or video to start editing! | @funnytamilan"
            footer_bbox = draw.textbbox((0, 0), footer_text, font=status_font)
            footer_width = footer_bbox[2] - footer_bbox[0]
            draw.text(((1200 - footer_width) // 2, 750), footer_text, fill=(150, 150, 180), font=status_font)
            
            # Convert to BytesIO
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG', quality=95)
            img_buffer.seek(0)
            
            return img_buffer
            
        except Exception as e:
            logger.error(f"Error creating welcome image: {e}")
            return None
    
    @auto_fix_error
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command with advanced welcome UI"""
        user = update.effective_user
        user_id = user.id
        
        # Add user to database
        is_new = self.db.add_user(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Check premium status
        is_premium = self.db.check_premium_status(user_id)
        stats = self.db.get_user_stats(user_id)
        
        # Get trial days left
        trial_days = stats.get('trial_days_left', 60) if not is_premium else 0
        total_edits = stats.get('total_edits', 0)
        
        # Create welcome image
        welcome_image = await self.create_welcome_image(
            user.first_name,
            is_premium,
            trial_days,
            total_edits
        )
        
        # Create inline keyboard with premium emojis
        keyboard = [
            [
                InlineKeyboardButton("🎨 OPEN WEB EDITOR", web_app=WebAppInfo(url=f"{self.config.WEB_APP_URL}/editor")),
                InlineKeyboardButton("📊 MY PROFILE", callback_data="profile")
            ],
            [
                InlineKeyboardButton("✨ 50+ EFFECTS", callback_data="show_effects"),
                InlineKeyboardButton("💎 UPGRADE NOW", callback_data="premium_info")
            ],
            [
                InlineKeyboardButton("🎬 VIDEO EDITING", callback_data="video_guide"),
                InlineKeyboardButton("🖼️ IMAGE EDITING", callback_data="image_guide")
            ],
            [
                InlineKeyboardButton("📖 HELP & GUIDE", callback_data="help_menu"),
                InlineKeyboardButton("⭐ RATE 5★", url="https://t.me/tlgrmcbot?start=rate")
            ]
        ]
        
        # Add admin button if user is admin
        if user_id in self.config.ADMIN_IDS:
            keyboard.append([InlineKeyboardButton("🔐 ADMIN PANEL 👑", callback_data="admin_panel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send welcome image with caption
        if welcome_image:
            await update.message.reply_photo(
                photo=InputFile(welcome_image, filename="welcome.png"),
                caption=f"🎉 *WELCOME TO KINVA MASTER* 🎉\n\n"
                       f"Hello *{user.first_name}*! Your professional editing suite is ready.\n\n"
                       f"{'💎 *PREMIUM MEMBER*' if is_premium else f'🎁 *FREE TRIAL*: {trial_days} days remaining'}\n\n"
                       f"✨ *Quick Stats:*\n"
                       f"• Total Edits: `{total_edits}`\n"
                       f"• Available Quality: `{'4K Ultra HD' if is_premium else '1080p Full HD'}`\n\n"
                       f"🚀 *Get Started:* Send me any photo or video to begin!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
        else:
            # Fallback text welcome
            welcome_text = f"""
🎨✨ *KINVA MASTER PRO* ✨🎨

*Welcome, {user.first_name}!* 🚀

{'💎 PREMIUM MEMBER • UNLIMITED ACCESS 💎' if is_premium else f'🎁 60-DAY FREE TRIAL • {trial_days} DAYS LEFT 🎁'}

━━━━━━━━━━━━━━━━━━━━━━━

✨ *PRO FEATURES:* ✨
┌─────────────────────────┐
│ 🎨 50+ AI Effects       │
│ 🎬 Professional Editor  │
│ 💎 4K Ultra HD Export   │
│ 🌐 Live Web Editor      │
│ 🚀 Lightning Fast       │
│ 📱 All Formats Support  │
└─────────────────────────┘

📊 *YOUR STATS:*
• Total Edits: `{total_edits}`
• Premium Status: `{'ACTIVE ✅' if is_premium else 'TRIAL 🔄'}`
• Max Quality: `{'4K' if is_premium else '1080p'}`

💡 *PRO TIP:* Send any photo or video to start editing!

*Need Help?* Use /help or contact @funnytamilan
"""
            await update.message.reply_text(
                welcome_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        
        # Send welcome GIF for new users
        if is_new:
            try:
                await update.message.reply_animation(
                    animation="https://media.giphy.com/media/26AHONQ79FdWZhAI0/giphy.gif",
                    caption="🎉 *Welcome to the creative community!* Start creating magic! 🎨✨",
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                pass
        
        logger.info(f"User {user_id} started the bot - Premium: {is_premium}")
    
    @auto_fix_error
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command with detailed guide"""
        user_id = update.effective_user.id
        is_premium = self.db.check_premium_status(user_id)
        
        help_text = f"""
📚 *KINVA MASTER - COMPLETE GUIDE* 📚

*🎨 IMAGE EDITING*
┌─────────────────────────────┐
│ • Send image + apply filters │
│ • /removebg - AI background  │
│ • /collage - Create collage  │
│ • /text [text] - Add text    │
│ • /resize - Resize image     │
└─────────────────────────────┘

*🎬 VIDEO EDITING*
┌─────────────────────────────┐
│ • /trim [start] [end]       │
│ • /speed [0.5-3.0]          │
│ • /compress - Compress      │
│ • /music - Add background   │
│ • /quality - Set resolution │
└─────────────────────────────┘

*✨ POPULAR EFFECTS*
┌─────────────────────────────┐
│ vintage | cinematic | vhs   │
│ glitch | neon | watercolor  │
│ sketch | oil_painting       │
│{' 3d | 4k_upscale | ai_enhance' if is_premium else ''}│
└─────────────────────────────┘

*💎 PREMIUM FEATURES*
{'✅ UNLOCKED - You have full access!' if is_premium else '''
┌─────────────────────────────┐
│ • 4K Ultra HD Export        │
│ • Unlimited Edits           │
│ • 50+ Premium Effects       │
│ • Priority Processing       │
│ • Batch Processing          │
│ • Cloud Storage (100GB)     │
└─────────────────────────────┘

💎 Upgrade: /premium
'''}

*📱 QUICK COMMANDS*
/start - Welcome
/webapp - Web editor
/profile - Your stats
/effects - All effects
/premium - Upgrade

*Support:* @funnytamilan
"""
        
        keyboard = [
            [InlineKeyboardButton("🎨 WEB EDITOR", web_app=WebAppInfo(url=f"{self.config.WEB_APP_URL}/editor"))],
            [InlineKeyboardButton("💎 UPGRADE NOW", callback_data="premium_info")],
            [InlineKeyboardButton("📞 SUPPORT", url="https://t.me/funnytamilan")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    
    @auto_fix_error
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /profile command with detailed stats"""
        user_id = update.effective_user.id
        user = update.effective_user
        
        is_premium = self.db.check_premium_status(user_id)
        stats = self.db.get_user_stats(user_id)
        
        # Get recent activity
        recent_edits = self.db.get_recent_edits(user_id, limit=5)
        
        profile_text = f"""
👤 *USER PROFILE* 👤
━━━━━━━━━━━━━━━━━━━━━

*Name:* {user.first_name} {user.last_name or ''}
*Username:* @{user.username or 'N/A'}
*User ID:* `{user_id}`

━━━━━━━━━━━━━━━━━━━━━
*STATUS* {'💎 PREMIUM' if is_premium else '🎁 TRIAL'}
━━━━━━━━━━━━━━━━━━━━━

{'✨ Premium Features: ACTIVE' if is_premium else f'⏰ Trial Days Left: {stats["trial_days_left"]}'}
📅 Joined: {stats['join_date']}
🎬 Total Edits: {stats['total_edits']}
📊 Today's Edits: {stats['today_usage']}
🎯 Daily Limit: {stats['daily_limit']}

━━━━━━━━━━━━━━━━━━━━━
*RECENT ACTIVITY*
━━━━━━━━━━━━━━━━━━━━━
{chr(10).join([f"• {edit['operation']} - {edit['date']}" for edit in recent_edits]) or 'No recent activity'}

━━━━━━━━━━━━━━━━━━━━━
*AVAILABLE FEATURES*
━━━━━━━━━━━━━━━━━━━━━
{'✅' if is_premium else '🔒'} 4K Ultra HD Export
{'✅' if is_premium else '🔒'} Unlimited Edits
{'✅' if is_premium else '✅'} 50+ Basic Effects
{'✅' if is_premium else '🔒'} AI Enhancement
{'✅' if is_premium else '🔒'} Batch Processing
{'✅' if is_premium else '✅'} Web Editor Access

*Need more features?* /premium
"""
        
        keyboard = [
            [InlineKeyboardButton("💎 UPGRADE NOW", callback_data="premium_info")],
            [InlineKeyboardButton("📊 FULL STATS", callback_data="detailed_stats")],
            [InlineKeyboardButton("🎨 OPEN EDITOR", web_app=WebAppInfo(url=f"{self.config.WEB_APP_URL}/editor"))]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            profile_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    @auto_fix_error
    async def premium_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /premium command with pricing and benefits"""
        user_id = update.effective_user.id
        is_premium = self.db.check_premium_status(user_id)
        
        if is_premium:
            premium_text = """
💎 *PREMIUM MEMBERSHIP ACTIVE* 💎
━━━━━━━━━━━━━━━━━━━━━

*Your Benefits:*
✅ 4K Ultra HD Export
✅ Unlimited Daily Edits
✅ 50+ Premium Effects
✅ Priority Processing (3x faster)
✅ Batch Processing (10 files)
✅ 100GB Cloud Storage
✅ Live Stream Editing
✅ Priority Support 24/7

*Total Savings:* $99/year
*Edits Made:* Unlimited

*Thank you for supporting Kinva Master!* 🙏

*Contact:* @funnytamilan for support
"""
            await update.message.reply_text(premium_text, parse_mode=ParseMode.MARKDOWN)
        else:
            stats = self.db.get_user_stats(user_id)
            premium_text = f"""
💎 *UNLOCK PREMIUM POWER* 💎
━━━━━━━━━━━━━━━━━━━━━

🎁 *FREE TRIAL:* {stats['trial_days_left']} days remaining

*PREMIUM BENEFITS:*
━━━━━━━━━━━━━━━━━━━━━
🌟 4K ULTRA HD EXPORT
🚀 3x FASTER PROCESSING
🎨 50+ EXCLUSIVE EFFECTS
📦 BATCH PROCESS (10 files)
☁️ 100GB CLOUD STORAGE
🎬 LIVE STREAM EDITING
💎 NO WATERMARKS
🎯 PRIORITY SUPPORT

*PRICING PLANS:*
━━━━━━━━━━━━━━━━━━━━━
📅 MONTHLY: ${self.config.PREMIUM_PRICE}/month
🎁 QUARTERLY: $25 (Save 15%)
🌟 YEARLY: $89 (Save 25%)

*HOW TO UPGRADE:*
━━━━━━━━━━━━━━━━━━━━━
1️⃣ Click "UPGRADE NOW"
2️⃣ Choose payment method
3️⃣ Complete payment
4️⃣ Get instant access!

*PAYMENT METHODS:*
• UPI: funnytamilan@okhdfcbank
• Crypto: USDT (TRC20)
• Card: Stripe
• Bank Transfer

*SPECIAL OFFER:* First 50 users get 30% OFF!
"""
            
            keyboard = [
                [InlineKeyboardButton("💎 UPGRADE NOW", callback_data="buy_premium")],
                [InlineKeyboardButton("📞 CONTACT SUPPORT", url="https://t.me/funnytamilan")],
                [InlineKeyboardButton("🎁 TRY FREE TRIAL", callback_data="trial_info")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                premium_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )
    
    @auto_fix_error
    async def webapp_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Open web app editor"""
        user_id = update.effective_user.id
        is_premium = self.db.check_premium_status(user_id)
        
        keyboard = [
            [
                InlineKeyboardButton(
                    "🎨 OPEN ADVANCED EDITOR", 
                    web_app=WebAppInfo(url=f"{self.config.WEB_APP_URL}/editor?user={user_id}")
                )
            ]
        ]
        
        if is_premium:
            keyboard.append([
                InlineKeyboardButton("🎬 LIVE STREAM EDITING", 
                                   web_app=WebAppInfo(url=f"{self.config.WEB_APP_URL}/stream"))
            ])
        
        keyboard.append([
            InlineKeyboardButton("📱 MOBILE EDITOR", 
                               web_app=WebAppInfo(url=f"{self.config.WEB_APP_URL}/mobile"))
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎨 *ADVANCED WEB EDITOR* 🎨\n\n"
            "✨ *Features:*\n"
            "• Real-time preview & streaming\n"
            "• Professional editing tools\n"
            "• Layer management system\n"
            f"• Export up to {'4K' if is_premium else '1080p'} quality\n"
            "• 50+ effects and filters\n"
            "• AI-powered background removal\n"
            "• Text & sticker overlay\n\n"
            f"{'💎 PREMIUM: 4K Export & Live Streaming Active' if is_premium else '🎁 FREE TRIAL: 60 days of 1080p export'}\n\n"
            "Click below to start editing! 🚀",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    @auto_fix_error
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages"""
        user_id = update.effective_user.id
        is_premium = self.db.check_premium_status(user_id)
        
        # Check usage limits
        if not is_premium and self.db.get_daily_usage(user_id) >= 100:
            await update.message.reply_text(
                "⚠️ *Daily limit reached!* ⚠️\n\n"
                "Free users can make 100 edits per day.\n"
                f"Upgrade to premium for unlimited edits!\n\n"
                f"💎 Contact: {self.config.PREMIUM_CONTACT}\n"
                f"🎁 /premium to upgrade now!",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Send processing message
        processing_msg = await update.message.reply_text(
            "🔄 *Processing your image...* 🔄\n\n"
            "Applying AI enhancements... Please wait ⏳",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Get photo
            photo = update.message.photo[-1]
            file = await context.bot.get_file(photo.file_id)
            
            # Generate unique filename
            filename = f"{user_id}_{uuid.uuid4()}.jpg"
            file_path = os.path.join(self.config.TEMP_DIR, filename)
            
            # Download file
            await file.download_to_drive(file_path)
            
            # Store in context
            context.user_data['current_file'] = file_path
            context.user_data['file_type'] = 'image'
            
            # Delete processing message
            await processing_msg.delete()
            
            # Get caption for direct effect application
            caption = update.message.caption or ""
            
            # Create editing keyboard with premium emojis
            keyboard = [
                [
                    InlineKeyboardButton("🎨 FILTERS", callback_data=f"image_filters_{file_path}"),
                    InlineKeyboardButton("✏️ ADD TEXT", callback_data=f"add_text_{file_path}")
                ],
                [
                    InlineKeyboardButton("🖼️ REMOVE BG", callback_data=f"remove_bg_{file_path}"),
                    InKeyboardButton("📐 RESIZE", callback_data=f"resize_image_{file_path}")
                ],
                [
                    InlineKeyboardButton("✨ EFFECTS", callback_data=f"image_effects_{file_path}"),
                    InlineKeyboardButton("💾 EXPORT", callback_data=f"export_image_{file_path}")
                ]
            ]
            
            if is_premium:
                keyboard.insert(2, [
                    InlineKeyboardButton("🤖 AI ENHANCE", callback_data=f"ai_enhance_{file_path}"),
                    InlineKeyboardButton("🎭 STYLE TRANSFER", callback_data=f"style_transfer_{file_path}")
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send preview
            with open(file_path, 'rb') as f:
                await update.message.reply_photo(
                    photo=f,
                    caption="✅ *Image loaded successfully!* ✅\n\n"
                           "✨ Choose an editing option below:\n"
                           f"{'💎 Premium features available!' if is_premium else '🎁 Upgrade to premium for AI enhancement!'}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            
            logger.info(f"User {user_id} uploaded image: {filename}")
            
        except Exception as e:
            await processing_msg.delete()
            await update.message.reply_text(
                "❌ *Error processing image!* ❌\n\n"
                "Please try again with a different image.\n"
                "If problem persists, contact @funnytamilan",
                parse_mode=ParseMode.MARKDOWN
            )
            logger.error(f"Error handling photo: {e}")
    
    @auto_fix_error
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle video messages"""
        user_id = update.effective_user.id
        is_premium = self.db.check_premium_status(user_id)
        
        # Check usage limits
        if not is_premium and self.db.get_daily_usage(user_id) >= 100:
            await update.message.reply_text(
                "⚠️ *Daily limit reached!* ⚠️\n\n"
                "Free users can make 100 edits per day.\n"
                f"Upgrade to premium for unlimited edits!\n\n"
                f"💎 /premium to upgrade now!",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Send processing message
        processing_msg = await update.message.reply_text(
            "🔄 *Processing your video...* 🔄\n\n"
            "This may take a few moments depending on file size ⏳",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Get video
            video = update.message.video
            file = await context.bot.get_file(video.file_id)
            
            # Check file size
            if file.file_size > self.config.MAX_FILE_SIZE:
                await processing_msg.delete()
                await update.message.reply_text(
                    "⚠️ *File too large!* ⚠️\n\n"
                    f"Maximum size: {self.config.MAX_FILE_SIZE / 1024 / 1024}MB\n"
                    f"Your file: {file.file_size / 1024 / 1024:.1f}MB\n\n"
                    "Try compressing your video first.",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Generate filename
            filename = f"{user_id}_{uuid.uuid4()}.mp4"
            file_path = os.path.join(self.config.TEMP_DIR, filename)
            
            # Download file
            await file.download_to_drive(file_path)
            
            # Store in context
            context.user_data['current_file'] = file_path
            context.user_data['file_type'] = 'video'
            
            # Delete processing message
            await processing_msg.delete()
            
            # Create video editing keyboard
            keyboard = [
                [
                    InlineKeyboardButton("✂️ TRIM", callback_data=f"trim_video_{file_path}"),
                    InlineKeyboardButton("⚡ SPEED", callback_data=f"speed_video_{file_path}")
                ],
                [
                    InlineKeyboardButton("🎵 ADD MUSIC", callback_data=f"add_music_{file_path}"),
                    InlineKeyboardButton("📦 COMPRESS", callback_data=f"compress_video_{file_path}")
                ],
                [
                    InlineKeyboardButton("🎨 EFFECTS", callback_data=f"video_effects_{file_path}"),
                    InlineKeyboardButton("💎 QUALITY", callback_data=f"quality_video_{file_path}")
                ],
                [
                    InlineKeyboardButton("🎬 MERGE", callback_data=f"merge_video_{file_path}"),
                    InlineKeyboardButton("💾 EXPORT", callback_data=f"export_video_{file_path}")
                ]
            ]
            
            if is_premium:
                keyboard.insert(3, [
                    InlineKeyboardButton("🌟 4K UPSCALE", callback_data=f"upscale_4k_{file_path}"),
                    InlineKeyboardButton("🎬 LIVE STREAM", callback_data=f"live_stream_{file_path}")
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send preview
            with open(file_path, 'rb') as f:
                await update.message.reply_video(
                    video=f,
                    caption="✅ *Video loaded successfully!* ✅\n\n"
                           "🎬 Choose an editing option below:\n"
                           f"{'💎 Premium: 4K export & live streaming available!' if is_premium else '🎁 Upgrade to premium for 4K export!'}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup
                )
            
            logger.info(f"User {user_id} uploaded video: {filename}")
            
        except Exception as e:
            await processing_msg.delete()
            await update.message.reply_text(
                "❌ *Error processing video!* ❌\n\n"
                "Please try again with a different video.\n"
                "If problem persists, contact @funnytamilan",
                parse_mode=ParseMode.MARKDOWN
            )
            logger.error(f"Error handling video: {e}")
    
    @auto_fix_error
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = update.effective_user.id
        
        try:
            # Admin panel
            if data == "admin_panel":
                if user_id in self.config.ADMIN_IDS:
                    await self.admin_panel.admin_command(update, context)
                else:
                    await query.edit_message_text("❌ You are not authorized!")
            
            # Profile
            elif data == "profile":
                await self.profile_command(update, context)
            
            # Premium info
            elif data == "premium_info":
                await self.premium_command(update, context)
            
            # Buy premium
            elif data == "buy_premium":
                await query.edit_message_text(
                    "💎 *PREMIUM UPGRADE* 💎\n\n"
                    "To upgrade to premium:\n\n"
                    "1️⃣ Send payment to:\n"
                    "   • UPI: funnytamilan@okhdfcbank\n"
                    "   • Crypto: USDT (TRC20)\n"
                    "   • Card: via Stripe\n\n"
                    "2️⃣ Amount: $9.99 USD\n\n"
                    "3️⃣ Take screenshot of payment\n\n"
                    "4️⃣ Send screenshot to @funnytamilan\n\n"
                    "5️⃣ Get instant premium access!\n\n"
                    "*Premium will be activated within 5 minutes.*\n\n"
                    "🎁 *Special Offer:* First 50 users get 30% OFF!",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("📞 CONTACT SUPPORT", url="https://t.me/funnytamilan")
                    ]])
                )
            
            # Show effects
            elif data == "show_effects":
                await self.effects_command(update, context)
            
            # Help menu
            elif data == "help_menu":
                await self.help_command(update, context)
            
            # Video guide
            elif data == "video_guide":
                await query.edit_message_text(
                    "🎬 *VIDEO EDITING GUIDE* 🎬\n\n"
                    "*Basic Editing:*\n"
                    "1. Send a video to the bot\n"
                    "2. Use buttons to trim/cut\n"
                    "3. Add music or effects\n"
                    "4. Export in desired quality\n\n"
                    "*Advanced Editing:*\n"
                    "• Use /webapp for professional tools\n"
                    "• Add subtitles with /subtitles\n"
                    "• Change speed with /speed\n"
                    "• Merge videos with /merge\n\n"
                    "*Quality Options:*\n"
                    f"{'144p → 4K' if self.db.check_premium_status(user_id) else '144p → 1080p'}\n\n"
                    "Try it now! Send a video to begin 🚀",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🎬 START EDITING", callback_data="start_video_edit")
                    ]])
                )
            
            # Image guide
            elif data == "image_guide":
                await query.edit_message_text(
                    "🖼️ *IMAGE EDITING GUIDE* 🖼️\n\n"
                    "*Basic Editing:*\n"
                    "1. Send an image to the bot\n"
                    "2. Choose from filters\n"
                    "3. Add text or stickers\n"
                    "4. Remove background with AI\n\n"
                    "*Advanced Editing:*\n"
                    "• Use /webapp for professional tools\n"
                    "• Create collages with /collage\n"
                    "• Apply artistic effects\n"
                    "• AI enhancement available\n\n"
                    "*Popular Effects:*\n"
                    "vintage, cinematic, watercolor\n"
                    "glitch, neon, oil_painting\n\n"
                    "Send an image now to get started! 🎨",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🎨 START EDITING", callback_data="start_image_edit")
                    ]])
                )
            
            # Handle other callbacks
            elif data.startswith("image_filters_"):
                file_path = data.replace("image_filters_", "")
                await self.show_image_filters(query, file_path)
            
            # Add more callback handlers as needed
            
        except Exception as e:
            logger.error(f"Error in button callback: {e}")
            await query.edit_message_text(
                "❌ *Error!* ❌\n\n"
                "Something went wrong. Please try again.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def show_image_filters(self, query, file_path):
        """Show available image filters"""
        filters_list = [
            ('vintage', '🎞️ Vintage'),
            ('cinematic', '🎬 Cinematic'),
            ('black_white', '⚫ Black & White'),
            ('blur', '🌀 Blur'),
            ('sharpen', '✨ Sharpen'),
            ('watercolor', '🎨 Watercolor'),
            ('oil_painting', '🖼️ Oil Painting'),
            ('glitch', '💫 Glitch')
        ]
        
        keyboard = []
        for filter_id, filter_name in filters_list:
            keyboard.append([InlineKeyboardButton(filter_name, callback_data=f"apply_filter_{filter_id}_{file_path}")])
        
        keyboard.append([InlineKeyboardButton("🔙 BACK", callback_data=f"back_to_image_{file_path}")])
        
        await query.edit_message_caption(
            caption="🎨 *Choose a filter to apply:*\n\n"
                   "Try different filters to transform your image!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    def run(self):
        """Run the bot"""
        # Create application
        application = Application.builder().token(self.config.BOT_TOKEN).build()
        
        # Add command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("webapp", self.webapp_command))
        application.add_handler(CommandHandler("premium", self.premium_command))
        application.add_handler(CommandHandler("profile", self.profile_command))
        
        # Add message handlers
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        application.add_handler(MessageHandler(filters.VIDEO, self.handle_video))
        
        # Add callback handler
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Start bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
        logger.info("Bot started successfully!")

if __name__ == "__main__":
    bot = KinvaMasterBot()
    bot.run()
