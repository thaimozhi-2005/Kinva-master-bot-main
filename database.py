#!/usr/bin/env python3
"""
Kinva Master Bot - Database Management
Author: @funnytamilan
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from bson.objectid import ObjectId

from config import Config

logger = logging.getLogger(__name__)

class Database:
    """Database management class for Kinva Master Bot"""
    
    def __init__(self):
        """Initialize database connection"""
        self.config = Config()
        try:
            self.client = MongoClient(self.config.MONGODB_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.config.DATABASE_NAME]
            
            # Collections
            self.users = self.db.users
            self.processing = self.db.processing
            self.payments = self.db.payments
            self.edits = self.db.edits
            self.banned_users = self.db.banned_users
            self.settings = self.db.settings
            self.logs = self.db.logs
            
            # Create indexes for better performance
            self._create_indexes()
            
            logger.info("Database connected successfully")
            
        except ConnectionFailure as e:
            logger.error(f"Database connection failed: {e}")
            raise
    
    def _create_indexes(self):
        """Create database indexes for optimization"""
        try:
            # Users collection indexes
            self.users.create_index('user_id', unique=True)
            self.users.create_index('username')
            self.users.create_index('created_at')
            self.users.create_index('is_premium')
            
            # Processing collection indexes
            self.processing.create_index('user_id')
            self.processing.create_index('status')
            self.processing.create_index('created_at')
            
            # Payments collection indexes
            self.payments.create_index('user_id')
            self.payments.create_index('transaction_id', unique=True)
            self.payments.create_index('date')
            
            # Edits collection indexes
            self.edits.create_index('user_id')
            self.edits.create_index('date')
            self.edits.create_index('file_type')
            
            # Banned users indexes
            self.banned_users.create_index('user_id', unique=True)
            self.banned_users.create_index('banned_at')
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
    
    # ============= USER MANAGEMENT =============
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> bool:
        """Add new user to database"""
        try:
            # Check if user exists
            existing = self.users.find_one({'user_id': user_id})
            if existing:
                # Update last seen
                self.users.update_one(
                    {'user_id': user_id},
                    {'$set': {'last_seen': datetime.now(), 'username': username, 'first_name': first_name}}
                )
                return False
            
            # Create new user
            user_data = {
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'is_premium': False,
                'is_banned': False,
                'trial_start': datetime.now(),
                'trial_end': datetime.now() + timedelta(days=self.config.TRIAL_DAYS),
                'created_at': datetime.now(),
                'last_seen': datetime.now(),
                'usage_count': 0,
                'total_edits': 0,
                'daily_usage': {},
                'premium_features_used': 0,
                'referral_code': self._generate_referral_code(user_id),
                'referred_by': None
            }
            
            self.users.insert_one(user_data)
            logger.info(f"New user added: {user_id} ({username})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False
    
    def _generate_referral_code(self, user_id: int) -> str:
        """Generate unique referral code"""
        import random
        import string
        code = f"KINVA{user_id}{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"
        return code[:12]
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data"""
        try:
            return self.users.find_one({'user_id': user_id})
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def check_premium_status(self, user_id: int) -> bool:
        """Check if user has premium access"""
        try:
            user = self.users.find_one({'user_id': user_id})
            if not user:
                return False
            
            # Check if user is banned
            if user.get('is_banned', False):
                return False
            
            # Check if premium is active
            if user.get('is_premium', False):
                # Check expiry if set
                expiry = user.get('premium_expiry')
                if expiry and expiry < datetime.now():
                    # Premium expired
                    self.users.update_one(
                        {'user_id': user_id},
                        {'$set': {'is_premium': False}}
                    )
                    return False
                return True
            
            # Check trial
            trial_end = user.get('trial_end')
            if trial_end and trial_end > datetime.now():
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking premium status for {user_id}: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> Dict:
        """Get user statistics"""
        try:
            user = self.get_user(user_id)
            if not user:
                return {
                    'is_premium': False,
                    'trial_days_left': 0,
                    'total_edits': 0,
                    'today_usage': 0,
                    'daily_limit': 100,
                    'join_date': 'N/A',
                    'premium_expiry': None,
                    'premium_features_used': 0
                }
            
            # Calculate trial days left
            trial_days_left = 0
            if not user.get('is_premium', False):
                trial_end = user.get('trial_end')
                if trial_end:
                    trial_days_left = max(0, (trial_end - datetime.now()).days)
            
            # Get today's usage
            today = datetime.now().strftime('%Y-%m-%d')
            daily_usage = user.get('daily_usage', {})
            today_usage = daily_usage.get(today, 0)
            
            # Get daily limit based on premium status
            daily_limit = 1000 if user.get('is_premium', False) else 100
            
            return {
                'is_premium': user.get('is_premium', False),
                'trial_days_left': trial_days_left,
                'total_edits': user.get('total_edits', 0),
                'today_usage': today_usage,
                'daily_limit': daily_limit,
                'join_date': user.get('created_at', datetime.now()).strftime('%Y-%m-%d'),
                'premium_expiry': user.get('premium_expiry'),
                'premium_features_used': user.get('premium_features_used', 0),
                'referral_code': user.get('referral_code'),
                'referred_by': user.get('referred_by')
            }
            
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return {}
    
    def get_daily_usage(self, user_id: int) -> int:
        """Get user's daily usage count"""
        try:
            user = self.get_user(user_id)
            if not user:
                return 0
            
            today = datetime.now().strftime('%Y-%m-%d')
            daily_usage = user.get('daily_usage', {})
            return daily_usage.get(today, 0)
            
        except Exception as e:
            logger.error(f"Error getting daily usage for {user_id}: {e}")
            return 0
    
    def increment_usage(self, user_id: int, operation: str = None, file_type: str = None) -> bool:
        """Increment user usage count"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Update user
            self.users.update_one(
                {'user_id': user_id},
                {
                    '$inc': {
                        'total_edits': 1,
                        f'daily_usage.{today}': 1,
                        'usage_count': 1
                    },
                    '$set': {'last_seen': datetime.now()}
                }
            )
            
            # Log edit
            if operation:
                self.add_edit_log(user_id, operation, file_type)
            
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing usage for {user_id}: {e}")
            return False
    
    def add_edit_log(self, user_id: int, operation: str, file_type: str = None):
        """Add edit log entry"""
        try:
            edit_data = {
                'user_id': user_id,
                'operation': operation,
                'file_type': file_type,
                'date': datetime.now(),
                'status': 'completed'
            }
            self.edits.insert_one(edit_data)
        except Exception as e:
            logger.error(f"Error adding edit log: {e}")
    
    def get_recent_edits(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get user's recent edits"""
        try:
            edits = self.edits.find(
                {'user_id': user_id}
            ).sort('date', -1).limit(limit)
            
            return [{
                'operation': e.get('operation', 'Unknown'),
                'date': e.get('date', datetime.now()).strftime('%Y-%m-%d %H:%M'),
                'file_type': e.get('file_type', 'N/A')
            } for e in edits]
            
        except Exception as e:
            logger.error(f"Error getting recent edits: {e}")
            return []
    
    # ============= PREMIUM MANAGEMENT =============
    
    def activate_premium(self, user_id: int, transaction_id: str, duration_days: int = 30) -> bool:
        """Activate premium for user"""
        try:
            self.users.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'is_premium': True,
                        'premium_activated': datetime.now(),
                        'premium_expiry': datetime.now() + timedelta(days=duration_days),
                        'transaction_id': transaction_id
                    }
                }
            )
            
            # Record payment
            self.add_payment(user_id, transaction_id, self.config.PREMIUM_PRICE)
            
            logger.info(f"Premium activated for user {user_id} for {duration_days} days")
            return True
            
        except Exception as e:
            logger.error(f"Error activating premium for {user_id}: {e}")
            return False
    
    def remove_premium(self, user_id: int) -> bool:
        """Remove premium from user"""
        try:
            self.users.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'is_premium': False,
                        'premium_expiry': None
                    }
                }
            )
            logger.info(f"Premium removed for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing premium for {user_id}: {e}")
            return False
    
    def add_premium_by_admin(self, user_id: int, days: int, admin_id: int) -> bool:
        """Add premium by admin"""
        try:
            self.users.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'is_premium': True,
                        'premium_activated': datetime.now(),
                        'premium_expiry': datetime.now() + timedelta(days=days),
                        'premium_added_by': admin_id,
                        'premium_added_at': datetime.now()
                    }
                }
            )
            
            # Add admin log
            self.add_admin_log(admin_id, f"Added premium to user {user_id} for {days} days")
            
            logger.info(f"Admin {admin_id} added premium to user {user_id} for {days} days")
            return True
            
        except Exception as e:
            logger.error(f"Error adding premium by admin: {e}")
            return False
    
    def remove_premium_by_admin(self, user_id: int, admin_id: int) -> bool:
        """Remove premium by admin"""
        try:
            self.users.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'is_premium': False,
                        'premium_expiry': None
                    }
                }
            )
            
            # Add admin log
            self.add_admin_log(admin_id, f"Removed premium from user {user_id}")
            
            logger.info(f"Admin {admin_id} removed premium from user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing premium by admin: {e}")
            return False
    
    def reset_user_trial(self, user_id: int, admin_id: int) -> bool:
        """Reset user trial period"""
        try:
            self.users.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'trial_start': datetime.now(),
                        'trial_end': datetime.now() + timedelta(days=self.config.TRIAL_DAYS),
                        'is_premium': False,
                        'premium_expiry': None
                    }
                }
            )
            
            self.add_admin_log(admin_id, f"Reset trial for user {user_id}")
            logger.info(f"Admin {admin_id} reset trial for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error resetting trial: {e}")
            return False
    
    # ============= PAYMENT MANAGEMENT =============
    
    def add_payment(self, user_id: int, transaction_id: str, amount: float) -> bool:
        """Add payment record"""
        try:
            payment_data = {
                'user_id': user_id,
                'transaction_id': transaction_id,
                'amount': amount,
                'date': datetime.now(),
                'status': 'completed',
                'currency': self.config.PREMIUM_CURRENCY
            }
            self.payments.insert_one(payment_data)
            return True
            
        except Exception as e:
            logger.error(f"Error adding payment: {e}")
            return False
    
    def get_total_revenue(self) -> float:
        """Get total revenue"""
        try:
            pipeline = [
                {'$match': {'status': 'completed'}},
                {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
            ]
            result = list(self.payments.aggregate(pipeline))
            return result[0]['total'] if result else 0.0
            
        except Exception as e:
            logger.error(f"Error getting total revenue: {e}")
            return 0.0
    
    def get_monthly_revenue(self) -> float:
        """Get current month revenue"""
        try:
            start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0)
            pipeline = [
                {
                    '$match': {
                        'status': 'completed',
                        'date': {'$gte': start_of_month}
                    }
                },
                {'$group': {'_id': None, 'total': {'$sum': '$amount'}}}
            ]
            result = list(self.payments.aggregate(pipeline))
            return result[0]['total'] if result else 0.0
            
        except Exception as e:
            logger.error(f"Error getting monthly revenue: {e}")
            return 0.0
    
    # ============= BAN MANAGEMENT =============
    
    def ban_user(self, user_id: int, admin_id: int, reason: str = None) -> bool:
        """Ban user"""
        try:
            self.users.update_one(
                {'user_id': user_id},
                {'$set': {'is_banned': True, 'banned_at': datetime.now(), 'banned_by': admin_id, 'ban_reason': reason}}
            )
            
            ban_data = {
                'user_id': user_id,
                'banned_by': admin_id,
                'reason': reason,
                'banned_at': datetime.now()
            }
            self.banned_users.insert_one(ban_data)
            
            self.add_admin_log(admin_id, f"Banned user {user_id} - Reason: {reason}")
            logger.info(f"Admin {admin_id} banned user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error banning user: {e}")
            return False
    
    def unban_user(self, user_id: int, admin_id: int) -> bool:
        """Unban user"""
        try:
            self.users.update_one(
                {'user_id': user_id},
                {'$set': {'is_banned': False}, '$unset': {'banned_at': '', 'banned_by': '', 'ban_reason': ''}}
            )
            
            self.banned_users.update_one(
                {'user_id': user_id},
                {'$set': {'unbanned_at': datetime.now(), 'unbanned_by': admin_id}}
            )
            
            self.add_admin_log(admin_id, f"Unbanned user {user_id}")
            logger.info(f"Admin {admin_id} unbanned user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unbanning user: {e}")
            return False
    
    def is_user_banned(self, user_id: int) -> bool:
        """Check if user is banned"""
        try:
            user = self.get_user(user_id)
            return user.get('is_banned', False) if user else False
        except Exception as e:
            logger.error(f"Error checking ban status: {e}")
            return False
    
    # ============= ADMIN FUNCTIONS =============
    
    def add_admin_log(self, admin_id: int, action: str):
        """Add admin action log"""
        try:
            log_data = {
                'admin_id': admin_id,
                'action': action,
                'timestamp': datetime.now()
            }
            self.logs.insert_one(log_data)
        except Exception as e:
            logger.error(f"Error adding admin log: {e}")
    
    def get_total_users(self) -> int:
        """Get total number of users"""
        try:
            return self.users.count_documents({})
        except Exception as e:
            logger.error(f"Error getting total users: {e}")
            return 0
    
    def get_active_users_today(self) -> int:
        """Get active users today"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            query = {f'daily_usage.{today}': {'$exists': True, '$gt': 0}}
            return self.users.count_documents(query)
        except Exception as e:
            logger.error(f"Error getting active users today: {e}")
            return 0
    
    def get_active_users_week(self) -> int:
        """Get active users this week"""
        try:
            # Get last 7 days
            active_users = set()
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                query = {f'daily_usage.{date}': {'$exists': True, '$gt': 0}}
                users = self.users.find(query, {'user_id': 1})
                for user in users:
                    active_users.add(user['user_id'])
            return len(active_users)
        except Exception as e:
            logger.error(f"Error getting active users week: {e}")
            return 0
    
    def get_premium_users_count(self) -> int:
        """Get number of premium users"""
        try:
            return self.users.count_documents({'is_premium': True})
        except Exception as e:
            logger.error(f"Error getting premium users count: {e}")
            return 0
    
    def get_trial_users_count(self) -> int:
        """Get number of trial users"""
        try:
            return self.users.count_documents({'is_premium': False})
        except Exception as e:
            logger.error(f"Error getting trial users count: {e}")
            return 0
    
    def get_banned_users_count(self) -> int:
        """Get number of banned users"""
        try:
            return self.users.count_documents({'is_banned': True})
        except Exception as e:
            logger.error(f"Error getting banned users count: {e}")
            return 0
    
    def get_total_edits(self) -> int:
        """Get total number of edits"""
        try:
            result = self.users.aggregate([
                {'$group': {'_id': None, 'total': {'$sum': '$total_edits'}}}
            ])
            result_list = list(result)
            return result_list[0]['total'] if result_list else 0
        except Exception as e:
            logger.error(f"Error getting total edits: {e}")
            return 0
    
    def get_today_edits(self) -> int:
        """Get today's total edits"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            result = self.users.aggregate([
                {'$group': {'_id': None, 'total': {'$sum': f'$daily_usage.{today}'}}}
            ])
            result_list = list(result)
            return result_list[0]['total'] if result_list else 0
        except Exception as e:
            logger.error(f"Error getting today's edits: {e}")
            return 0
    
    def get_week_edits(self) -> int:
        """Get this week's total edits"""
        try:
            total = 0
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                result = self.users.aggregate([
                    {'$group': {'_id': None, 'total': {'$sum': f'$daily_usage.{date}'}}}
                ])
                result_list = list(result)
                total += result_list[0]['total'] if result_list else 0
            return total
        except Exception as e:
            logger.error(f"Error getting week edits: {e}")
            return 0
    
    def get_all_users(self, limit: int = 100, skip: int = 0) -> List[Dict]:
        """Get all users with pagination"""
        try:
            return list(self.users.find({}, {'_id': 0}).sort('created_at', -1).skip(skip).limit(limit))
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def get_premium_users(self, limit: int = 100) -> List[Dict]:
        """Get all premium users"""
        try:
            return list(self.users.find({'is_premium': True}, {'_id': 0}).sort('premium_activated', -1).limit(limit))
        except Exception as e:
            logger.error(f"Error getting premium users: {e}")
            return []
    
    def search_users(self, query: str) -> List[Dict]:
        """Search users by username or user_id"""
        try:
            search_query = {
                '$or': [
                    {'username': {'$regex': query, '$options': 'i'}},
                    {'first_name': {'$regex': query, '$options': 'i'}},
                    {'user_id': int(query) if query.isdigit() else None}
                ]
            }
            return list(self.users.find(search_query, {'_id': 0}).limit(50))
        except Exception as e:
            logger.error(f"Error searching users: {e}")
            return []
    
    def get_db_size(self) -> float:
        """Get database size in MB"""
        try:
            stats = self.db.command('dbstats')
            return stats.get('dataSize', 0) / (1024 * 1024)
        except Exception as e:
            logger.error(f"Error getting DB size: {e}")
            return 0.0
    
    # ============= PROCESSING JOBS =============
    
    def add_processing_job(self, user_id: int, file_id: str, file_type: str, operation: str) -> str:
        """Add processing job to queue"""
        try:
            job_data = {
                'user_id': user_id,
                'file_id': file_id,
                'file_type': file_type,
                'operation': operation,
                'status': 'pending',
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            result = self.processing.insert_one(job_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error adding processing job: {e}")
            return None
    
    def update_job_status(self, job_id: str, status: str, result_path: str = None, error: str = None):
        """Update processing job status"""
        try:
            update_data = {
                'status': status,
                'updated_at': datetime.now()
            }
            if result_path:
                update_data['result_path'] = result_path
                update_data['completed_at'] = datetime.now()
            if error:
                update_data['error'] = error
            
            self.processing.update_one({'_id': ObjectId(job_id)}, {'$set': update_data})
        except Exception as e:
            logger.error(f"Error updating job status: {e}")
    
    def get_pending_jobs(self) -> List[Dict]:
        """Get all pending jobs"""
        try:
            return list(self.processing.find({'status': 'pending'}).sort('created_at', 1))
        except Exception as e:
            logger.error(f"Error getting pending jobs: {e}")
            return []
    
    # ============= SETTINGS =============
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get bot setting"""
        try:
            setting = self.settings.find_one({'key': key})
            return setting.get('value', default) if setting else default
        except Exception as e:
            logger.error(f"Error getting setting: {e}")
            return default
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set bot setting"""
        try:
            self.settings.update_one(
                {'key': key},
                {'$set': {'value': value, 'updated_at': datetime.now()}},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error setting setting: {e}")
            return False
