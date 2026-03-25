#!/usr/bin/env python3
"""
Kinva Master Bot - Complete Admin Panel with Premium Management
Author: @funnytamilan
Version: 2.0
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import pandas as pd
import io
import json
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram.constants import ParseMode

from database import Database
from config import Config

logger = logging.getLogger(__name__)

# Conversation states for admin actions
(ADMIN_MAIN_MENU, ADMIN_PREMIUM_ADD, ADMIN_PREMIUM_REMOVE, ADMIN_BROADCAST, 
 ADMIN_BAN_USER, ADMIN_UNBAN_USER, ADMIN_RESET_TRIAL, ADMIN_SEARCH_USER,
 ADMIN_PREMIUM_DURATION) = range(9)

class AdminPanel:
    """Complete Admin Panel for Kinva Master Bot"""
    
    def __init__(self):
        self.db = Database()
        self.config = Config()
        self.admin_ids = self.config.ADMIN_IDS
        
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.admin_ids
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /admin command - Main admin panel"""
        user_id = update.effective_user.id
        
        if not self.is_admin(user_id):
            await update.message.reply_text(
                "🚫 *Access Denied!*\n\n"
                "You are not authorized to use admin commands.\n\n"
                "This incident has been logged.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Get admin stats for welcome
        total_users = self.db.get_total_users()
        premium_users = self.db.get_premium_users_count()
        today_edits = self.db.get_today_edits()
        
        admin_text = f"""
👑 *KINVA MASTER - ADMIN PANEL* 👑
━━━━━━━━━━━━━━━━━━━━━━━

*Welcome Admin!* Here's your control center:

📊 *QUICK STATS*
• Total Users: `{total_users}`
• Premium Users: `{premium_users}`
• Today's Edits: `{today_edits}`
• Conversion Rate: `{(premium_users/total_users*100 if total_users > 0 else 0):.1f}%`

━━━━━━━━━━━━━━━━━━━━━━━
*AVAILABLE ACTIONS*
━━━━━━━━━━━━━━━━━━━━━━━

Use the buttons below to manage your bot:
"""
        
        keyboard = [
            [InlineKeyboardButton("📊 STATISTICS", callback_data="admin_stats")],
            [InlineKeyboardButton("👥 USER MANAGEMENT", callback_data="admin_user_menu")],
            [InlineKeyboardButton("💎 PREMIUM MANAGEMENT", callback_data="admin_premium_menu")],
            [InlineKeyboardButton("📢 BROADCAST", callback_data="admin_broadcast")],
            [InlineKeyboardButton("⚙️ SYSTEM SETTINGS", callback_data="admin_settings")],
            [InlineKeyboardButton("📝 VIEW LOGS", callback_data="admin_logs")],
            [InlineKeyboardButton("💾 BACKUP DATABASE", callback_data="admin_backup")],
            [InlineKeyboardButton("🔄 RESTART BOT", callback_data="admin_restart")],
            [InlineKeyboardButton("🔙 CLOSE", callback_data="admin_close")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            admin_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show detailed bot statistics"""
        query = update.callback_query
        await query.answer()
        
        # Get comprehensive stats
        total_users = self.db.get_total_users()
        active_today = self.db.get_active_users_today()
        active_week = self.db.get_active_users_week()
        premium_users = self.db.get_premium_users_count()
        trial_users = self.db.get_trial_users_count()
        banned_users = self.db.get_banned_users_count()
        total_edits = self.db.get_total_edits()
        today_edits = self.db.get_today_edits()
        week_edits = self.db.get_week_edits()
        total_revenue = self.db.get_total_revenue()
        monthly_revenue = self.db.get_monthly_revenue()
        
        # Get recent admin actions
        recent_logs = list(self.db.logs.find().sort('timestamp', -1).limit(5))
        
        stats_text = f"""
📊 *BOT STATISTICS* 📊
━━━━━━━━━━━━━━━━━━━━━━━

*👥 USER STATISTICS*
• Total Users: `{total_users}`
• Active Today: `{active_today}`
• Active This Week: `{active_week}`
• Premium Users: `{premium_users}`
• Trial Users: `{trial_users}`
• Banned Users: `{banned_users}`
• Conversion Rate: `{(premium_users/total_users*100 if total_users > 0 else 0):.1f}%`

*🎬 EDIT STATISTICS*
• Total Edits: `{total_edits}`
• Today's Edits: `{today_edits}`
• This Week Edits: `{week_edits}`
• Avg Edits/Day: `{total_edits//30 if total_edits > 0 else 0}`

*💰 REVENUE STATISTICS*
• Total Revenue: `${total_revenue:.2f}`
• Monthly Revenue: `${monthly_revenue:.2f}`
• Avg Revenue/User: `${(total_revenue/total_users if total_users > 0 else 0):.2f}`

*📋 RECENT ADMIN ACTIONS*
{self._format_recent_logs(recent_logs)}

*🔄 LAST UPDATED:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        keyboard = [
            [InlineKeyboardButton("🔄 REFRESH", callback_data="admin_stats")],
            [InlineKeyboardButton("📥 EXPORT CSV", callback_data="admin_export_stats")],
            [InlineKeyboardButton("🔙 BACK TO MENU", callback_data="admin_back_to_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def premium_management_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show premium management menu"""
        query = update.callback_query
        await query.answer()
        
        premium_stats = self._get_premium_stats()
        
        menu_text = f"""
💎 *PREMIUM MANAGEMENT* 💎
━━━━━━━━━━━━━━━━━━━━━━━

*PREMIUM STATISTICS*
• Total Premium Users: `{premium_stats['total']}`
• Active Premium: `{premium_stats['active']}`
• Expired Premium: `{premium_stats['expired']}`
• Monthly Revenue: `${premium_stats['monthly_revenue']:.2f}`

*QUICK ACTIONS*
Choose an action below:
"""
        
        keyboard = [
            [InlineKeyboardButton("➕ ADD PREMIUM", callback_data="admin_premium_add")],
            [InlineKeyboardButton("➖ REMOVE PREMIUM", callback_data="admin_premium_remove")],
            [InlineKeyboardButton("📋 LIST PREMIUM USERS", callback_data="admin_premium_list")],
            [InlineKeyboardButton("🔄 RESET TRIAL", callback_data="admin_reset_trial")],
            [InlineKeyboardButton("📊 PREMIUM ANALYTICS", callback_data="admin_premium_analytics")],
            [InlineKeyboardButton("🔙 BACK", callback_data="admin_back_to_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            menu_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def add_premium_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start add premium conversation"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "➕ *ADD PREMIUM USER* ➕\n\n"
            "Please send me the Telegram User ID of the user you want to add premium to.\n\n"
            "*How to find User ID:*\n"
            "1. Forward a message from the user to @userinfobot\n"
            "2. Or use /id command in chat with the user\n\n"
            "Send the User ID now (numeric only):\n"
            "Type /cancel to cancel.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ADMIN_PREMIUM_ADD
    
    async def handle_premium_user_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle premium user ID input"""
        user_id_input = update.message.text.strip()
        
        # Check for cancel
        if user_id_input.lower() == '/cancel':
            await update.message.reply_text("❌ Operation cancelled.")
            return ConversationHandler.END
        
        # Validate user ID
        try:
            target_user_id = int(user_id_input)
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid User ID! Please send a numeric User ID.\n\n"
                "Try again or type /cancel to cancel."
            )
            return ADMIN_PREMIUM_ADD
        
        # Check if user exists
        user = self.db.get_user(target_user_id)
        if not user:
            await update.message.reply_text(
                f"❌ User `{target_user_id}` not found in database!\n\n"
                "The user needs to start the bot first.\n\n"
                "Try another User ID or type /cancel to cancel.",
                parse_mode=ParseMode.MARKDOWN
            )
            return ADMIN_PREMIUM_ADD
        
        # Store user ID in context
        context.user_data['premium_target_user'] = target_user_id
        context.user_data['premium_target_name'] = user.get('first_name', 'Unknown')
        
        # Ask for duration
        keyboard = [
            [InlineKeyboardButton("📅 30 DAYS", callback_data="premium_duration_30")],
            [InlineKeyboardButton("📅 90 DAYS (3 months)", callback_data="premium_duration_90")],
            [InlineKeyboardButton("📅 180 DAYS (6 months)", callback_data="premium_duration_180")],
            [InlineKeyboardButton("📅 365 DAYS (1 year)", callback_data="premium_duration_365")],
            [InlineKeyboardButton("🎁 LIFETIME", callback_data="premium_duration_lifetime")],
            [InlineKeyboardButton("🔙 CANCEL", callback_data="premium_duration_cancel")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"✅ User found: *{user.get('first_name')}* (ID: `{target_user_id}`)\n\n"
            f"Current status: {'💎 PREMIUM' if user.get('is_premium') else '🎁 TRIAL'}\n\n"
            "Select premium duration:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
        return ADMIN_PREMIUM_DURATION
    
    async def handle_premium_duration(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle premium duration selection"""
        query = update.callback_query
        await query.answer()
        
        duration_data = query.data
        target_user_id = context.user_data.get('premium_target_user')
        target_name = context.user_data.get('premium_target_name')
        
        # Parse duration
        if duration_data == "premium_duration_cancel":
            await query.edit_message_text("❌ Premium addition cancelled.")
            return ConversationHandler.END
        
        duration_map = {
            "premium_duration_30": 30,
            "premium_duration_90": 90,
            "premium_duration_180": 180,
            "premium_duration_365": 365,
            "premium_duration_lifetime": 3650  # 10 years as lifetime
        }
        
        days = duration_map.get(duration_data, 30)
        
        # Add premium to user
        success = self.db.add_premium_by_admin(
            user_id=target_user_id,
            days=days,
            admin_id=update.effective_user.id
        )
        
        if success:
            # Send confirmation
            user = self.db.get_user(target_user_id)
            expiry = user.get('premium_expiry', datetime.now() + timedelta(days=days))
            
            await query.edit_message_text(
                f"✅ *Premium Added Successfully!*\n\n"
                f"User: *{target_name}* (ID: `{target_user_id}`)\n"
                f"Duration: *{days} days*{' (LIFETIME)' if days >= 3650 else ''}\n"
                f"Expires: *{expiry.strftime('%Y-%m-%d')}*\n\n"
                f"User can now enjoy all premium features! 🎉",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Notify user
            try:
                await update.get_bot().send_message(
                    chat_id=target_user_id,
                    text=f"🎉 *Congratulations!* 🎉\n\n"
                         f"Admin has granted you *PREMIUM ACCESS* for {days} days!\n\n"
                         f"✨ *New Features Unlocked:*\n"
                         f"• 4K Ultra HD Export\n"
                         f"• Unlimited Edits\n"
                         f"• 50+ Premium Effects\n"
                         f"• Priority Processing\n"
                         f"• Live Stream Editing\n\n"
                         f"Thank you for using Kinva Master! 🚀",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Could not notify user {target_user_id}: {e}")
        else:
            await query.edit_message_text(
                f"❌ *Failed to add premium!*\n\n"
                f"User: {target_name} (ID: `{target_user_id}`)\n\n"
                "Please check logs for more details.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        return ConversationHandler.END
    
    async def remove_premium_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start remove premium conversation"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "➖ *REMOVE PREMIUM USER* ➖\n\n"
            "Please send me the Telegram User ID of the user you want to remove premium from.\n\n"
            "Send the User ID now (numeric only):\n"
            "Type /cancel to cancel.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ADMIN_PREMIUM_REMOVE
    
    async def handle_remove_premium(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle remove premium"""
        user_id_input = update.message.text.strip()
        
        # Check for cancel
        if user_id_input.lower() == '/cancel':
            await update.message.reply_text("❌ Operation cancelled.")
            return ConversationHandler.END
        
        # Validate user ID
        try:
            target_user_id = int(user_id_input)
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid User ID! Please send a numeric User ID.\n\n"
                "Try again or type /cancel to cancel."
            )
            return ADMIN_PREMIUM_REMOVE
        
        # Check if user exists
        user = self.db.get_user(target_user_id)
        if not user:
            await update.message.reply_text(
                f"❌ User `{target_user_id}` not found in database!",
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END
        
        # Check if user has premium
        if not user.get('is_premium', False):
            await update.message.reply_text(
                f"❌ User *{user.get('first_name')}* does not have premium!",
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END
        
        # Remove premium
        success = self.db.remove_premium_by_admin(
            user_id=target_user_id,
            admin_id=update.effective_user.id
        )
        
        if success:
            await update.message.reply_text(
                f"✅ *Premium Removed Successfully!*\n\n"
                f"User: *{user.get('first_name')}* (ID: `{target_user_id}`)\n\n"
                f"User has been downgraded to trial/free status.",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Notify user
            try:
                await update.get_bot().send_message(
                    chat_id=target_user_id,
                    text=f"⚠️ *Premium Access Removed* ⚠️\n\n"
                         f"Your premium access has been removed by admin.\n\n"
                         f"You are now on free trial. To upgrade again, contact @funnytamilan.",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Could not notify user {target_user_id}: {e}")
        else:
            await update.message.reply_text(
                f"❌ *Failed to remove premium!*\n\n"
                f"Please check logs.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        return ConversationHandler.END
    
    async def list_premium_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List all premium users"""
        query = update.callback_query
        await query.answer()
        
        premium_users = self.db.get_premium_users(limit=50)
        
        if not premium_users:
            await query.edit_message_text(
                "📋 *PREMIUM USERS*\n\n"
                "No premium users found.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Format premium users list
        user_list = []
        for user in premium_users:
            expiry = user.get('premium_expiry', datetime.now())
            days_left = (expiry - datetime.now()).days if expiry else 0
            status = "🟢 Active" if days_left > 0 else "🔴 Expired"
            
            user_list.append(
                f"• *{user.get('first_name', 'Unknown')}* (ID: `{user['user_id']}`)\n"
                f"  Expires: {expiry.strftime('%Y-%m-%d') if expiry else 'Lifetime'} | {status} | Days Left: {max(0, days_left)}\n"
            )
        
        # Split into chunks if too long
        all_users = "\n".join(user_list)
        
        # Send as file if too long
        if len(all_users) > 4000:
            # Create text file
            file_content = f"PREMIUM USERS LIST\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{all_users}"
            file_io = io.BytesIO(file_content.encode())
            file_io.name = "premium_users.txt"
            
            await query.edit_message_text(
                "📋 *PREMIUM USERS LIST*\n\n"
                f"Total: {len(premium_users)} premium users\n"
                "Downloading full list...",
                parse_mode=ParseMode.MARKDOWN
            )
            
            await update.callback_query.message.reply_document(
                document=InputFile(file_io, filename="premium_users.txt"),
                caption=f"Premium Users List - {len(premium_users)} users"
            )
        else:
            await query.edit_message_text(
                f"📋 *PREMIUM USERS LIST*\n\n"
                f"Total: {len(premium_users)} premium users\n\n"
                f"{all_users}\n\n"
                f"Use /premium_list to see more.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def reset_user_trial_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start reset trial conversation"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🔄 *RESET USER TRIAL* 🔄\n\n"
            "Please send me the Telegram User ID of the user whose trial you want to reset.\n\n"
            "Send the User ID now (numeric only):\n"
            "Type /cancel to cancel.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ADMIN_RESET_TRIAL
    
    async def handle_reset_trial(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle reset trial"""
        user_id_input = update.message.text.strip()
        
        # Check for cancel
        if user_id_input.lower() == '/cancel':
            await update.message.reply_text("❌ Operation cancelled.")
            return ConversationHandler.END
        
        # Validate user ID
        try:
            target_user_id = int(user_id_input)
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid User ID! Please send a numeric User ID.\n\n"
                "Try again or type /cancel to cancel."
            )
            return ADMIN_RESET_TRIAL
        
        # Check if user exists
        user = self.db.get_user(target_user_id)
        if not user:
            await update.message.reply_text(
                f"❌ User `{target_user_id}` not found in database!",
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END
        
        # Reset trial
        success = self.db.reset_user_trial(
            user_id=target_user_id,
            admin_id=update.effective_user.id
        )
        
        if success:
            await update.message.reply_text(
                f"✅ *Trial Reset Successfully!*\n\n"
                f"User: *{user.get('first_name')}* (ID: `{target_user_id}`)\n"
                f"New trial period: *{self.config.TRIAL_DAYS} days*\n\n"
                f"User now has fresh trial access! 🎁",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Notify user
            try:
                await update.get_bot().send_message(
                    chat_id=target_user_id,
                    text=f"🎁 *Trial Period Reset!* 🎁\n\n"
                         f"Admin has reset your trial period.\n"
                         f"You now have *{self.config.TRIAL_DAYS} days* of trial access!\n\n"
                         f"Enjoy editing with Kinva Master! 🚀",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Could not notify user {target_user_id}: {e}")
        else:
            await update.message.reply_text(
                f"❌ *Failed to reset trial!*\n\n"
                f"Please check logs.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        return ConversationHandler.END
    
    async def user_management_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Show user management menu"""
        query = update.callback_query
        await query.answer()
        
        menu_text = """
👥 *USER MANAGEMENT* 👥
━━━━━━━━━━━━━━━━━━━━━━━

*Available Actions:*
• View all users
• Search users
• Ban/Unban users
• View user details
• Reset user trial

Choose an action below:
"""
        
        keyboard = [
            [InlineKeyboardButton("📋 LIST ALL USERS", callback_data="admin_list_users")],
            [InlineKeyboardButton("🔍 SEARCH USER", callback_data="admin_search_user")],
            [InlineKeyboardButton("🚫 BAN USER", callback_data="admin_ban_user")],
            [InlineKeyboardButton("✅ UNBAN USER", callback_data="admin_unban_user")],
            [InlineKeyboardButton("📊 TOP USERS", callback_data="admin_top_users")],
            [InlineKeyboardButton("🔙 BACK", callback_data="admin_back_to_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            menu_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def ban_user_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start ban user conversation"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "🚫 *BAN USER* 🚫\n\n"
            "Please send me the Telegram User ID of the user you want to ban.\n\n"
            "Optional: You can also include a reason after the ID.\n"
            "Example: `123456789 Spamming`\n\n"
            "Send the User ID now:\n"
            "Type /cancel to cancel.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ADMIN_BAN_USER
    
    async def handle_ban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle ban user"""
        input_text = update.message.text.strip()
        
        # Check for cancel
        if input_text.lower() == '/cancel':
            await update.message.reply_text("❌ Operation cancelled.")
            return ConversationHandler.END
        
        # Parse user ID and reason
        parts = input_text.split(maxsplit=1)
        try:
            target_user_id = int(parts[0])
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid User ID! Please send a numeric User ID.\n\n"
                "Try again or type /cancel to cancel."
            )
            return ADMIN_BAN_USER
        
        reason = parts[1] if len(parts) > 1 else "No reason provided"
        
        # Check if user exists
        user = self.db.get_user(target_user_id)
        if not user:
            await update.message.reply_text(
                f"❌ User `{target_user_id}` not found in database!",
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END
        
        # Ban user
        success = self.db.ban_user(
            user_id=target_user_id,
            admin_id=update.effective_user.id,
            reason=reason
        )
        
        if success:
            await update.message.reply_text(
                f"✅ *User Banned Successfully!*\n\n"
                f"User: *{user.get('first_name')}* (ID: `{target_user_id}`)\n"
                f"Reason: `{reason}`\n\n"
                f"User can no longer use the bot.",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Notify user
            try:
                await update.get_bot().send_message(
                    chat_id=target_user_id,
                    text=f"🚫 *You have been banned from Kinva Master* 🚫\n\n"
                         f"Reason: `{reason}`\n\n"
                         f"If you believe this is a mistake, contact @funnytamilan",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Could not notify user {target_user_id}: {e}")
        else:
            await update.message.reply_text(
                f"❌ *Failed to ban user!*\n\n"
                f"Please check logs.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        return ConversationHandler.END
    
    async def unban_user_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start unban user conversation"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "✅ *UNBAN USER* ✅\n\n"
            "Please send me the Telegram User ID of the user you want to unban.\n\n"
            "Send the User ID now:\n"
            "Type /cancel to cancel.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ADMIN_UNBAN_USER
    
    async def handle_unban_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle unban user"""
        user_id_input = update.message.text.strip()
        
        # Check for cancel
        if user_id_input.lower() == '/cancel':
            await update.message.reply_text("❌ Operation cancelled.")
            return ConversationHandler.END
        
        # Validate user ID
        try:
            target_user_id = int(user_id_input)
        except ValueError:
            await update.message.reply_text(
                "❌ Invalid User ID! Please send a numeric User ID.\n\n"
                "Try again or type /cancel to cancel."
            )
            return ADMIN_UNBAN_USER
        
        # Check if user exists
        user = self.db.get_user(target_user_id)
        if not user:
            await update.message.reply_text(
                f"❌ User `{target_user_id}` not found in database!",
                parse_mode=ParseMode.MARKDOWN
            )
            return ConversationHandler.END
        
        # Unban user
        success = self.db.unban_user(
            user_id=target_user_id,
            admin_id=update.effective_user.id
        )
        
        if success:
            await update.message.reply_text(
                f"✅ *User Unbanned Successfully!*\n\n"
                f"User: *{user.get('first_name')}* (ID: `{target_user_id}`)\n\n"
                f"User can now use the bot again.",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Notify user
            try:
                await update.get_bot().send_message(
                    chat_id=target_user_id,
                    text=f"✅ *You have been unbanned from Kinva Master* ✅\n\n"
                         f"You can now use the bot again!\n\n"
                         f"Welcome back! 🎉",
                    parse_mode=ParseMode.MARKDOWN
                )
            except Exception as e:
                logger.error(f"Could not notify user {target_user_id}: {e}")
        else:
            await update.message.reply_text(
                f"❌ *Failed to unban user!*\n\n"
                f"Please check logs.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        return ConversationHandler.END
    
    async def list_all_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List all users"""
        query = update.callback_query
        await query.answer()
        
        # Get page from callback data
        data = query.data
        page = 0
        if "_page_" in data:
            page = int(data.split("_page_")[1])
        
        users = self.db.get_all_users(limit=20, skip=page * 20)
        total_users = self.db.get_total_users()
        
        if not users:
            await query.edit_message_text(
                "📋 *USERS LIST*\n\n"
                "No users found.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Format users list
        user_list = []
        for user in users:
            premium_status = "💎" if user.get('is_premium') else "🎁"
            banned_status = "🚫" if user.get('is_banned') else ""
            user_list.append(
                f"{premium_status} *{user.get('first_name', 'Unknown')}* {banned_status}\n"
                f"  ID: `{user['user_id']}` | Edits: {user.get('total_edits', 0)}\n"
            )
        
        all_users = "\n".join(user_list)
        total_pages = (total_users + 19) // 20
        
        # Create navigation buttons
        keyboard = []
        nav_buttons = []
        
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ PREV", callback_data=f"admin_list_users_page_{page-1}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("NEXT ▶️", callback_data=f"admin_list_users_page_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.append([InlineKeyboardButton("🔙 BACK", callback_data="admin_user_menu")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"📋 *USERS LIST* (Page {page + 1}/{total_pages})\n"
            f"Total Users: {total_users}\n\n"
            f"{all_users}",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Start broadcast conversation"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "📢 *BROADCAST MESSAGE* 📢\n\n"
            "Send me the message you want to broadcast to ALL users.\n\n"
            "*Supported formats:*\n"
            "• Text with formatting\n"
            "• Photo with caption\n"
            "• Video with caption\n"
            "• Document\n\n"
            "Type /cancel to cancel broadcast.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        return ADMIN_BROADCAST
    
    async def handle_broadcast(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle broadcast message"""
        message = update.message
        admin_id = update.effective_user.id
        
        # Send progress message
        progress_msg = await message.reply_text(
            "📢 *Starting broadcast...*\n\n"
            "Getting user list...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Get all users
        all_users = self.db.get_all_users()
        total_users = len(all_users)
        success_count = 0
        failed_count = 0
        
        await progress_msg.edit_text(
            f"📢 *Broadcasting to {total_users} users...*\n\n"
            f"Progress: 0/{total_users}\n"
            f"✅ Success: 0\n"
            f"❌ Failed: 0",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Broadcast to each user
        for i, user in enumerate(all_users):
            try:
                user_id = user['user_id']
                
                # Skip banned users
                if user.get('is_banned', False):
                    failed_count += 1
                    continue
                
                if message.text:
                    await update.get_bot().send_message(
                        chat_id=user_id,
                        text=message.text,
                        parse_mode=ParseMode.MARKDOWN
                    )
                elif message.photo:
                    await update.get_bot().send_photo(
                        chat_id=user_id,
                        photo=message.photo[-1].file_id,
                        caption=message.caption,
                        parse_mode=ParseMode.MARKDOWN
                    )
                elif message.video:
                    await update.get_bot().send_video(
                        chat_id=user_id,
                        video=message.video.file_id,
                        caption=message.caption,
                        parse_mode=ParseMode.MARKDOWN
                    )
                elif message.document:
                    await update.get_bot().send_document(
                        chat_id=user_id,
                        document=message.document.file_id,
                        caption=message.caption,
                        parse_mode=ParseMode.MARKDOWN
                    )
                
                success_count += 1
                
                # Update progress every 10 users
                if (i + 1) % 10 == 0:
                    await progress_msg.edit_text(
                        f"📢 *Broadcasting to {total_users} users...*\n\n"
                        f"Progress: {i + 1}/{total_users}\n"
                        f"✅ Success: {success_count}\n"
                        f"❌ Failed: {failed_count}",
                        parse_mode=ParseMode.MARKDOWN
                    )
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to broadcast to {user_id}: {e}")
        
        # Final update
        await progress_msg.edit_text(
            f"✅ *Broadcast Completed!*\n\n"
            f"📊 *Statistics:*\n"
            f"• Total Users: {total_users}\n"
            f"• Successfully Sent: {success_count}\n"
            f"• Failed: {failed_count}\n"
            f"• Success Rate: {(success_count/total_users*100 if total_users > 0 else 0):.1f}%\n\n"
            f"Broadcast finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Log broadcast
        self.db.add_admin_log(admin_id, f"Broadcast sent to {success_count} users")
        
        return ConversationHandler.END
    
    async def export_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Export statistics as CSV"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "📥 *Exporting statistics...*\n\n"
            "Please wait...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Get all users data
            users = self.db.get_all_users(limit=10000)
            
            # Create DataFrame
            data = []
            for user in users:
                data.append({
                    'User ID': user['user_id'],
                    'Username': user.get('username', ''),
                    'First Name': user.get('first_name', ''),
                    'Premium': user.get('is_premium', False),
                    'Banned': user.get('is_banned', False),
                    'Total Edits': user.get('total_edits', 0),
                    'Created At': user.get('created_at', datetime.now()).strftime('%Y-%m-%d %H:%M:%S'),
                    'Last Seen': user.get('last_seen', datetime.now()).strftime('%Y-%m-%d %H:%M:%S') if user.get('last_seen') else 'Never'
                })
            
            df = pd.DataFrame(data)
            
            # Create CSV file
            csv_buffer = io.BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            
            # Send file
            await update.callback_query.message.reply_document(
                document=InputFile(csv_buffer, filename=f"kinva_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"),
                caption=f"📊 *Statistics Export*\n\n"
                       f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                       f"Total Users: {len(data)}\n"
                       f"Premium Users: {len([u for u in data if u['Premium']])}",
                parse_mode=ParseMode.MARKDOWN
            )
            
            await query.delete_message()
            
        except Exception as e:
            logger.error(f"Error exporting stats: {e}")
            await query.edit_message_text(
                f"❌ *Error exporting statistics!*\n\n"
                f"Error: {str(e)}",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def view_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """View recent admin logs"""
        query = update.callback_query
        await query.answer()
        
        # Get recent logs
        logs = list(self.db.logs.find().sort('timestamp', -1).limit(50))
        
        if not logs:
            await query.edit_message_text(
                "📝 *ADMIN LOGS*\n\n"
                "No logs found.",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Format logs
        log_lines = []
        for log in logs:
            timestamp = log.get('timestamp', datetime.now()).strftime('%Y-%m-%d %H:%M')
            admin_id = log.get('admin_id', 'Unknown')
            action = log.get('action', 'Unknown')
            log_lines.append(f"`{timestamp}` | Admin `{admin_id}` | {action}")
        
        logs_text = "\n".join(log_lines[:20])  # Show only last 20
        
        keyboard = [
            [InlineKeyboardButton("🔄 REFRESH", callback_data="admin_logs")],
            [InlineKeyboardButton("🔙 BACK", callback_data="admin_back_to_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"📝 *RECENT ADMIN LOGS*\n\n"
            f"{logs_text}\n\n"
            f"*Total:* {len(logs)} logs in last 50",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def backup_database(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Backup database"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "💾 *Creating database backup...*\n\n"
            "Please wait...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Get all collections data
            backup_data = {
                'users': list(self.db.users.find({}, {'_id': 0})),
                'payments': list(self.db.payments.find({}, {'_id': 0})),
                'settings': list(self.db.settings.find({}, {'_id': 0})),
                'backup_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Create JSON file
            json_data = json.dumps(backup_data, default=str, indent=2)
            json_buffer = io.BytesIO(json_data.encode())
            json_buffer.name = f"kinva_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # Send file
            await update.callback_query.message.reply_document(
                document=InputFile(json_buffer, filename=json_buffer.name),
                caption=f"💾 *Database Backup*\n\n"
                       f"Date: {backup_data['backup_date']}\n"
                       f"Users: {len(backup_data['users'])}\n"
                       f"Payments: {len(backup_data['payments'])}",
                parse_mode=ParseMode.MARKDOWN
            )
            
            await query.delete_message()
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            await query.edit_message_text(
                f"❌ *Error creating backup!*\n\n"
                f"Error: {str(e)}",
                parse_mode=ParseMode.MARKDOWN
            )
    
    def _get_premium_stats(self) -> Dict:
        """Get premium statistics"""
        try:
            total_premium = self.db.get_premium_users_count()
            all_users = self.db.get_all_users()
            
            active = 0
            expired = 0
            
            for user in all_users:
                if user.get('is_premium'):
                    expiry = user.get('premium_expiry')
                    if expiry and expiry > datetime.now():
                        active += 1
                    else:
                        expired += 1
            
            monthly_revenue = self.db.get_monthly_revenue()
            
            return {
                'total': total_premium,
                'active': active,
                'expired': expired,
                'monthly_revenue': monthly_revenue
            }
        except Exception as e:
            logger.error(f"Error getting premium stats: {e}")
            return {'total': 0, 'active': 0, 'expired': 0, 'monthly_revenue': 0}
    
    def _format_recent_logs(self, logs: List[Dict]) -> str:
        """Format recent logs for display"""
        if not logs:
            return "No recent actions"
        
        lines = []
        for log in logs:
            timestamp = log.get('timestamp', datetime.now()).strftime('%H:%M')
            action = log.get('action', 'Unknown')[:50]
            lines.append(f"• `{timestamp}` - {action}")
        
        return "\n".join(lines[:5])
    
    def get_conversation_handler(self) -> ConversationHandler:
        """Get conversation handler for admin actions"""
        return ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.add_premium_menu, pattern="^admin_premium_add$"),
                CallbackQueryHandler(self.remove_premium_menu, pattern="^admin_premium_remove$"),
                CallbackQueryHandler(self.reset_user_trial_menu, pattern="^admin_reset_trial$"),
                CallbackQueryHandler(self.ban_user_menu, pattern="^admin_ban_user$"),
                CallbackQueryHandler(self.unban_user_menu, pattern="^admin_unban_user$"),
                CallbackQueryHandler(self.broadcast_message, pattern="^admin_broadcast$"),
            ],
            states={
                ADMIN_PREMIUM_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_premium_user_id)],
                ADMIN_PREMIUM_DURATION: [CallbackQueryHandler(self.handle_premium_duration, pattern="^premium_duration_")],
                ADMIN_PREMIUM_REMOVE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_remove_premium)],
                ADMIN_RESET_TRIAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_reset_trial)],
                ADMIN_BAN_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_ban_user)],
                ADMIN_UNBAN_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_unban_user)],
                ADMIN_BROADCAST: [MessageHandler(filters.ALL & ~filters.COMMAND, self.handle_broadcast)],
            },
            fallbacks=[
                CommandHandler("cancel", self.cancel_conversation),
                CallbackQueryHandler(self.cancel_conversation, pattern="^cancel$")
            ]
        )
    
    async def cancel_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancel current conversation"""
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text("❌ Operation cancelled.")
        else:
            await update.message.reply_text("❌ Operation cancelled.")
        
        return ConversationHandler.END
    
    async def admin_callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle all admin callback queries"""
        query = update.callback_query
        data = query.data
        
        if data == "admin_stats":
            await self.show_stats(update, context)
        elif data == "admin_premium_menu":
            await self.premium_management_menu(update, context)
        elif data == "admin_premium_list":
            await self.list_premium_users(update, context)
        elif data == "admin_user_menu":
            await self.user_management_menu(update, context)
        elif data == "admin_list_users":
            await self.list_all_users(update, context)
        elif data.startswith("admin_list_users_page_"):
            await self.list_all_users(update, context)
        elif data == "admin_export_stats":
            await self.export_stats(update, context)
        elif data == "admin_logs":
            await self.view_logs(update, context)
        elif data == "admin_backup":
            await self.backup_database(update, context)
        elif data == "admin_back_to_menu":
            await self.admin_command(update, context)
        elif data == "admin_close":
            await query.edit_message_text("👑 Admin panel closed.")
