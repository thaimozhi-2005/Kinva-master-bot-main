#!/usr/bin/env python3
"""
Kinva Master Bot - Premium Manager
Author: @funnytamilan
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
import secrets
import hashlib

logger = logging.getLogger(__name__)


class PremiumManager:
    """Manage premium features, subscriptions, and payments"""
    
    def __init__(self, db=None):
        self.db = db
        self.premium_features = {
            '4k_export': {
                'name': '4K Ultra HD Export',
                'description': 'Export videos in 4K quality',
                'icon': '🌟'
            },
            'unlimited_edits': {
                'name': 'Unlimited Edits',
                'description': 'No daily limits on edits',
                'icon': '∞'
            },
            'premium_effects': {
                'name': 'Premium Effects',
                'description': 'Access to 50+ exclusive effects',
                'icon': '✨',
                'count': 50
            },
            'priority_processing': {
                'name': 'Priority Processing',
                'description': '3x faster processing speed',
                'icon': '⚡'
            },
            'batch_processing': {
                'name': 'Batch Processing',
                'description': 'Process up to 10 files at once',
                'icon': '📦',
                'max_files': 10
            },
            'cloud_storage': {
                'name': 'Cloud Storage',
                'description': '100GB cloud storage',
                'icon': '☁️',
                'storage_gb': 100
            },
            'live_stream': {
                'name': 'Live Stream Editing',
                'description': 'Real-time editing with streaming',
                'icon': '🎬'
            },
            'no_watermark': {
                'name': 'No Watermarks',
                'description': 'Export without watermarks',
                'icon': '💎'
            },
            'priority_support': {
                'name': 'Priority Support',
                'description': '24/7 priority customer support',
                'icon': '🎯'
            }
        }
        
        self.premium_plans = {
            'monthly': {
                'name': 'Monthly',
                'days': 30,
                'price': 9.99,
                'price_inr': 499,
                'icon': '📅'
            },
            'quarterly': {
                'name': 'Quarterly',
                'days': 90,
                'price': 24.99,
                'price_inr': 1249,
                'icon': '📆',
                'discount': '15%'
            },
            'half_yearly': {
                'name': 'Half Yearly',
                'days': 180,
                'price': 44.99,
                'price_inr': 2249,
                'icon': '🎯',
                'discount': '25%'
            },
            'yearly': {
                'name': 'Yearly',
                'days': 365,
                'price': 79.99,
                'price_inr': 3999,
                'icon': '🎉',
                'discount': '33%'
            },
            'lifetime': {
                'name': 'Lifetime',
                'days': 3650,
                'price': 199.99,
                'price_inr': 9999,
                'icon': '👑',
                'discount': '50%'
            }
        }
        
        self.payment_methods = {
            'upi': {
                'name': 'UPI',
                'id': 'funnytamilan@okhdfcbank',
                'icon': '🇮🇳'
            },
            'crypto': {
                'name': 'Cryptocurrency',
                'address': '0x...',
                'icon': '₿',
                'currencies': ['USDT', 'BTC', 'ETH']
            },
            'card': {
                'name': 'Credit/Debit Card',
                'icon': '💳'
            },
            'bank_transfer': {
                'name': 'Bank Transfer',
                'icon': '🏦'
            }
        }
    
    def check_premium_status(self, user_id: int) -> bool:
        """Check if user has premium access"""
        if not self.db:
            return False
        
        user = self.db.get_user(user_id)
        if not user:
            return False
        
        # Check if user is premium
        if user.get('is_premium', False):
            expiry = user.get('premium_expiry')
            if expiry and expiry > datetime.now():
                return True
            elif not expiry:
                return True
        
        # Check trial period
        trial_end = user.get('trial_end')
        if trial_end and trial_end > datetime.now():
            return True
        
        return False
    
    def get_premium_features(self, user_id: int) -> Dict:
        """Get premium features for user"""
        is_premium = self.check_premium_status(user_id)
        
        if is_premium:
            return self.premium_features
        else:
            return {
                '4k_export': {
                    'name': '4K Ultra HD Export',
                    'description': 'Premium feature',
                    'icon': '🔒'
                },
                'unlimited_edits': {
                    'name': 'Unlimited Edits',
                    'description': 'Premium feature',
                    'icon': '🔒'
                },
                'premium_effects': {
                    'name': 'Premium Effects',
                    'description': 'Premium feature',
                    'icon': '🔒',
                    'count': 10
                },
                'priority_processing': {
                    'name': 'Priority Processing',
                    'description': 'Premium feature',
                    'icon': '🔒'
                },
                'batch_processing': {
                    'name': 'Batch Processing',
                    'description': 'Premium feature',
                    'icon': '🔒',
                    'max_files': 1
                },
                'cloud_storage': {
                    'name': 'Cloud Storage',
                    'description': 'Premium feature',
                    'icon': '🔒',
                    'storage_gb': 0
                },
                'live_stream': {
                    'name': 'Live Stream Editing',
                    'description': 'Premium feature',
                    'icon': '🔒'
                },
                'no_watermark': {
                    'name': 'No Watermarks',
                    'description': 'Premium feature',
                    'icon': '🔒'
                },
                'priority_support': {
                    'name': 'Priority Support',
                    'description': 'Premium feature',
                    'icon': '🔒'
                }
            }
    
    def can_use_feature(self, user_id: int, feature: str) -> bool:
        """Check if user can use specific premium feature"""
        if feature in ['basic_effects', 'basic_export']:
            return True
        
        features = self.get_premium_features(user_id)
        return feature in features and '🔒' not in features.get(feature, {}).get('icon', '')
    
    def get_premium_benefits_text(self, is_premium: bool = False) -> str:
        """Get formatted premium benefits text"""
        if is_premium:
            return """
💎 *YOUR PREMIUM BENEFITS* 💎

✅ 4K Ultra HD Export
✅ Unlimited Daily Edits
✅ 50+ Premium Effects
✅ Priority Processing (3x faster)
✅ Batch Processing (10 files)
✅ 100GB Cloud Storage
✅ Live Stream Editing
✅ No Watermarks
✅ Priority Support 24/7

*Thank you for supporting Kinva Master!* 🙏
"""
        else:
            return """
💎 *PREMIUM BENEFITS* 💎

🌟 *4K Ultra HD Export* - Crystal clear quality
🚀 *Priority Processing* - 3x faster
🎨 *50+ Premium Effects* - Exclusive filters
📦 *Batch Processing* - 10 files at once
☁️ *100GB Cloud Storage* - Save your work
🎬 *Live Stream Editing* - Real-time edits
💎 *No Watermarks* - Clean exports
🎯 *Priority Support* - 24/7 assistance

*Upgrade now and unlock all features!* 🚀
"""
    
    def get_plans_text(self) -> str:
        """Get formatted plans text"""
        plans_text = "*💎 PREMIUM PLANS* 💎\n\n"
        
        for key, plan in self.premium_plans.items():
            plans_text += f"{plan['icon']} *{plan['name']}*\n"
            plans_text += f"   • {plan['days']} days access\n"
            plans_text += f"   • ${plan['price']} USD / ₹{plan['price_inr']}\n"
            if 'discount' in plan:
                plans_text += f"   • Save {plan['discount']}\n"
            plans_text += "\n"
        
        plans_text += "*Payment Methods:*\n"
        plans_text += "• UPI: funnytamilan@okhdfcbank\n"
        plans_text += "• Crypto: USDT (TRC20)\n"
        plans_text += "• Credit/Debit Card\n\n"
        plans_text += "*Contact:* @funnytamilan to upgrade! 🚀"
        
        return plans_text
    
    def get_trial_info(self, user_id: int) -> Dict:
        """Get trial information for user"""
        if not self.db:
            return {'has_trial': False, 'days_left': 0}
        
        user = self.db.get_user(user_id)
        if not user:
            return {'has_trial': False, 'days_left': 0}
        
        trial_end = user.get('trial_end')
        if trial_end and trial_end > datetime.now():
            days_left = (trial_end - datetime.now()).days
            return {
                'has_trial': True,
                'days_left': days_left,
                'ends_at': trial_end
            }
        
        return {'has_trial': False, 'days_left': 0}
    
    def get_user_premium_info(self, user_id: int) -> Dict:
        """Get complete premium information for user"""
        if not self.db:
            return {'is_premium': False, 'features': {}}
        
        user = self.db.get_user(user_id)
        is_premium = self.check_premium_status(user_id)
        
        info = {
            'is_premium': is_premium,
            'features': self.get_premium_features(user_id),
            'trial': self.get_trial_info(user_id)
        }
        
        if is_premium:
            info['premium_expiry'] = user.get('premium_expiry')
            info['premium_activated'] = user.get('premium_activated')
        
        return info
    
    def activate_premium(self, user_id: int, plan: str = 'monthly', 
                        transaction_id: str = None) -> bool:
        """Activate premium for user"""
        if not self.db:
            return False
        
        plan_config = self.premium_plans.get(plan, self.premium_plans['monthly'])
        days = plan_config['days']
        
        try:
            self.db.users.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'is_premium': True,
                        'premium_plan': plan,
                        'premium_expiry': datetime.now() + timedelta(days=days),
                        'premium_activated': datetime.now(),
                        'transaction_id': transaction_id
                    }
                }
            )
            
            # Record payment
            if transaction_id:
                self.db.add_payment(user_id, transaction_id, plan_config['price'])
            
            logger.info(f"Premium activated for user {user_id} with {plan} plan")
            return True
            
        except Exception as e:
            logger.error(f"Error activating premium for {user_id}: {e}")
            return False
    
    def deactivate_premium(self, user_id: int) -> bool:
        """Deactivate premium for user"""
        if not self.db:
            return False
        
        try:
            self.db.users.update_one(
                {'user_id': user_id},
                {
                    '$set': {
                        'is_premium': False,
                        'premium_expiry': None
                    }
                }
            )
            
            logger.info(f"Premium deactivated for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deactivating premium for {user_id}: {e}")
            return False
    
    def generate_license_key(self, user_id: int, days: int = 30) -> str:
        """Generate license key for manual activation"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        key_data = f"{user_id}_{timestamp}_{days}_{secrets.token_hex(8)}"
        license_key = hashlib.sha256(key_data.encode()).hexdigest()[:16].upper()
        
        # Add formatting
        license_key = '-'.join([license_key[i:i+4] for i in range(0, 16, 4)])
        
        return license_key
    
    def validate_license_key(self, license_key: str, user_id: int) -> Dict:
        """Validate license key and activate if valid"""
        # This would validate against a database of issued keys
        # Simplified version
        if len(license_key.replace('-', '')) == 16:
            return {
                'valid': True,
                'days': 30,
                'message': 'License key activated successfully!'
            }
        
        return {
            'valid': False,
            'message': 'Invalid license key. Please contact @funnytamilan'
        }
    
    def get_referral_link(self, user_id: int) -> str:
        """Generate referral link for user"""
        if not self.db:
            return ""
        
        user = self.db.get_user(user_id)
        if user and user.get('referral_code'):
            return f"https://t.me/kinvamasterbot?start=ref_{user['referral_code']}"
        
        return ""
    
    def process_referral(self, referrer_id: int, new_user_id: int) -> bool:
        """Process referral and give rewards"""
        if not self.db:
            return False
        
        try:
            # Give referrer reward (3 extra trial days)
            referrer = self.db.get_user(referrer_id)
            if referrer:
                trial_end = referrer.get('trial_end', datetime.now())
                new_trial_end = trial_end + timedelta(days=3)
                self.db.users.update_one(
                    {'user_id': referrer_id},
                    {'$set': {'trial_end': new_trial_end}}
                )
            
            # Record referral
            self.db.users.update_one(
                {'user_id': new_user_id},
                {'$set': {'referred_by': referrer_id}}
            )
            
            logger.info(f"Referral processed: {referrer_id} -> {new_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing referral: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get premium statistics"""
        if not self.db:
            return {
                'total_premium': 0,
                'active_premium': 0,
                'total_revenue': 0,
                'monthly_revenue': 0
            }
        
        try:
            total_premium = self.db.get_premium_users_count()
            active_premium = len([u for u in self.db.get_premium_users() 
                                 if u.get('premium_expiry', datetime.now()) > datetime.now()])
            total_revenue = self.db.get_total_revenue()
            monthly_revenue = self.db.get_monthly_revenue()
            
            return {
                'total_premium': total_premium,
                'active_premium': active_premium,
                'total_revenue': total_revenue,
                'monthly_revenue': monthly_revenue
            }
            
        except Exception as e:
            logger.error(f"Error getting premium statistics: {e}")
            return {
                'total_premium': 0,
                'active_premium': 0,
                'total_revenue': 0,
                'monthly_revenue': 0
}
