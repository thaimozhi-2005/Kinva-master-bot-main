#!/usr/bin/env python3
"""
Kinva Master Bot - Error Handler Module
Author: @funnytamilan
"""

import functools
import traceback
import logging
import sys
import os
import time
from datetime import datetime
from typing import Callable, Any, Optional, Dict
import asyncio

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/error.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create logs directory
os.makedirs('logs', exist_ok=True)


def auto_fix_error(func: Callable) -> Callable:
    """Decorator to auto-fix common errors and provide graceful degradation"""
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            # Log the error
            logger.error(f"Error in {func.__name__}: {error_type} - {error_msg}")
            logger.error(traceback.format_exc())
            
            # Save to error log file
            save_error_log(func.__name__, error_type, error_msg, traceback.format_exc())
            
            # Try to get update object for reply
            try:
                update = args[0] if args else None
                if update and hasattr(update, 'message') and update.message:
                    # Auto-fix based on error type
                    fixed_message = get_fix_message(error_type, error_msg)
                    await update.message.reply_text(
                        fixed_message,
                        parse_mode='Markdown'
                    )
            except Exception as reply_error:
                logger.error(f"Failed to send error message: {reply_error}")
            
            return None
    
    return wrapper


def get_fix_message(error_type: str, error_msg: str) -> str:
    """Get appropriate fix message based on error type"""
    
    error_lower = error_msg.lower()
    
    # File related errors
    if "file too large" in error_lower or "max_file_size" in error_lower:
        return """⚠️ *File too large!*

Please send a file under 50MB.

*Tips:*
• Compress your video before uploading
• Use lower quality images
• Premium users can upload up to 200MB

Upgrade: /premium"""
    
    elif "unsupported format" in error_lower or "format" in error_lower:
        return """⚠️ *Unsupported file format!*

*Supported formats:*
• Images: JPG, PNG, GIF, WEBP, BMP
• Videos: MP4, AVI, MOV, MKV, WEBM

Please try again with a supported format."""
    
    elif "timeout" in error_lower or "timed out" in error_lower:
        return """⏰ *Processing timeout!*

The file took too long to process.

*Try:*
• Use a smaller file
• Try again later
• Upgrade to premium for priority processing

Upgrade: /premium"""
    
    elif "memory" in error_lower:
        return """💾 *Server memory limit reached!*

Please try again in a few minutes.

*Premium users get priority processing!*
Upgrade: /premium"""
    
    elif "connection" in error_lower or "connect" in error_lower:
        return """🌐 *Connection error!*

Please check your internet connection and try again.

If problem persists, contact @funnytamilan"""
    
    elif "permission" in error_lower or "denied" in error_lower:
        return """🔒 *Permission denied!*

Please try again or contact support @funnytamilan"""
    
    elif "invalid" in error_lower:
        return """❌ *Invalid input!*

Please check your command and try again.

Use /help for correct usage."""
    
    elif "not found" in error_lower:
        return """🔍 *File not found!*

Please upload a file first before editing.

Send me a photo or video to get started!"""
    
    elif "ban" in error_lower or "banned" in error_lower:
        return """🚫 *You have been banned!*

If you believe this is a mistake, contact @funnytamilan"""
    
    elif "premium" in error_lower:
        return """💎 *Premium feature!*

This feature requires premium membership.

*Premium Benefits:*
• 4K Ultra HD Export
• Unlimited Edits
• Priority Processing
• 50+ Exclusive Effects

Upgrade: /premium"""
    
    elif "network" in error_lower:
        return """📡 *Network error!*

Please check your connection and try again.

If problem persists, contact @funnytamilan"""
    
    elif "timeout" in error_lower:
        return """⏱️ *Request timeout!*

The server took too long to respond.

Please try again in a few moments."""
    
    else:
        return f"""❌ *Error occurred!*

Please try again or contact @funnytamilan for support.

*Error ID:* `{datetime.now().strftime('%Y%m%d%H%M%S')}`"""


def save_error_log(function_name: str, error_type: str, error_msg: str, traceback_str: str):
    """Save error to log file"""
    try:
        with open('logs/error.log', 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Time: {datetime.now().isoformat()}\n")
            f.write(f"Function: {function_name}\n")
            f.write(f"Error Type: {error_type}\n")
            f.write(f"Error Message: {error_msg}\n")
            f.write(f"Traceback:\n{traceback_str}\n")
            f.write(f"{'='*60}\n")
    except Exception as e:
        logger.error(f"Failed to save error log: {e}")


class ErrorRecovery:
    """Error recovery utilities"""
    
    @staticmethod
    def safe_file_operation(func: Callable) -> Callable:
        """Safely handle file operations with retry logic"""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            max_retries = 3
            retry_delay = 1
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except FileNotFoundError as e:
                    logger.error(f"File not found in {func.__name__}: {e}")
                    if attempt == max_retries - 1:
                        return None
                    time.sleep(retry_delay)
                except PermissionError as e:
                    logger.error(f"Permission denied in {func.__name__}: {e}")
                    return None
                except OSError as e:
                    logger.error(f"OS error in {func.__name__}: {e}")
                    if attempt == max_retries - 1:
                        return None
                    time.sleep(retry_delay)
                except Exception as e:
                    logger.error(f"File operation failed in {func.__name__}: {e}")
                    if attempt == max_retries - 1:
                        return None
                    time.sleep(retry_delay)
            
            return None
        
        return wrapper
    
    @staticmethod
    def safe_database_operation(func: Callable) -> Callable:
        """Safely handle database operations"""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Database operation failed in {func.__name__}: {e}")
                return None
        
        return wrapper
    
    @staticmethod
    def safe_network_operation(func: Callable) -> Callable:
        """Safely handle network operations with retry"""
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except asyncio.TimeoutError:
                    logger.error(f"Network timeout in {func.__name__}")
                    if attempt == max_retries - 1:
                        return None
                    await asyncio.sleep(retry_delay * (attempt + 1))
                except Exception as e:
                    logger.error(f"Network operation failed in {func.__name__}: {e}")
                    if attempt == max_retries - 1:
                        return None
                    await asyncio.sleep(retry_delay)
            
            return None
        
        return wrapper
    
    @staticmethod
    def safe_api_call(func: Callable) -> Callable:
        """Safely handle API calls with rate limiting"""
        
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"API call failed in {func.__name__}: {e}")
                return None
        
        return wrapper


class ErrorContext:
    """Context manager for error handling and performance tracking"""
    
    def __init__(self, operation_name: str, user_id: Optional[int] = None):
        self.operation_name = operation_name
        self.user_id = user_id
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        logger.info(f"Starting operation: {self.operation_name} (User: {self.user_id})")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        
        if exc_type:
            logger.error(f"Operation failed: {self.operation_name} - {exc_type.__name__}: {exc_val}")
            logger.error(traceback.format_exc())
            save_error_log(self.operation_name, exc_type.__name__, str(exc_val), traceback.format_exc())
            return False  # Re-raise the exception
        
        logger.info(f"Operation completed: {self.operation_name} in {duration:.2f}s")
        return True
    
    def get_duration(self) -> float:
        """Get operation duration in seconds"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return time.time() - self.start_time
        return 0


class RateLimiter:
    """Rate limiter for API calls and user actions"""
    
    def __init__(self, max_calls: int = 10, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.user_limits = {}
    
    def can_call(self, user_id: Optional[int] = None) -> bool:
        """Check if call is allowed"""
        now = time.time()
        # Remove old calls
        self.calls = [call for call in self.calls if call > now - self.time_window]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
    
    def can_user_call(self, user_id: int, limit: int = 5, window: int = 60) -> bool:
        """Check if specific user can call"""
        now = time.time()
        
        if user_id not in self.user_limits:
            self.user_limits[user_id] = []
        
        # Remove old calls
        self.user_limits[user_id] = [call for call in self.user_limits[user_id] if call > now - window]
        
        if len(self.user_limits[user_id]) < limit:
            self.user_limits[user_id].append(now)
            return True
        return False
    
    def wait_time(self, user_id: Optional[int] = None) -> float:
        """Get wait time until next call"""
        calls = self.user_limits.get(user_id, []) if user_id else self.calls
        
        if not calls:
            return 0
        
        oldest = min(calls)
        now = time.time()
        return max(0, (oldest + self.time_window) - now)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry on failure with exponential backoff"""
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    wait_time = delay * (backoff ** attempt)
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {e}")
                    logger.warning(f"Retrying in {wait_time:.2f}s...")
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(wait_time)
            
            logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            raise last_error
        
        return wrapper
    
    return decorator


def handle_async_errors(func: Callable) -> Callable:
    """Handle async function errors gracefully"""
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncio.CancelledError:
            logger.warning(f"Task cancelled: {func.__name__}")
            raise
        except Exception as e:
            logger.error(f"Unhandled error in {func.__name__}: {e}")
            logger.error(traceback.format_exc())
            return None
    
    return wrapper


class HealthChecker:
    """Health checker for services"""
    
    def __init__(self):
        self.checks = {}
        self.status = {}
    
    def register_check(self, name: str, check_func: Callable):
        """Register a health check function"""
        self.checks[name] = check_func
    
    async def check_all(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
                results[name] = {
                    'status': 'healthy',
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
                self.status[name] = 'healthy'
            except Exception as e:
                results[name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                self.status[name] = 'unhealthy'
                logger.error(f"Health check failed for {name}: {e}")
        
        return results
    
    def get_status(self, name: str = None) -> Dict:
        """Get health status"""
        if name:
            return {name: self.status.get(name, 'unknown')}
        return self.status


# Global instances
error_recovery = ErrorRecovery()
rate_limiter = RateLimiter()
health_checker = HealthChecker()
