#!/usr/bin/env python3
"""
Kinva Master Bot - Main Entry Point
Author: @funnytamilan
Version: 3.0
"""

import os
import sys
import logging
import asyncio
import signal
import argparse
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import configuration
from config import Config

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/run.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create logs directory
os.makedirs('logs', exist_ok=True)

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = ['BOT_TOKEN', 'MONGODB_URI']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please copy .env.example to .env and fill in the values")
        return False
    
    # Check if BOT_TOKEN is still default
    if os.getenv('BOT_TOKEN') == 'YOUR_BOT_TOKEN_HERE':
        logger.error("Please set your actual BOT_TOKEN in .env file")
        return False
    
    return True

def check_directories():
    """Check and create required directories"""
    directories = [
        Config.TEMP_DIR,
        Config.OUTPUT_DIR,
        Config.UPLOAD_DIR,
        Config.LOGS_DIR,
        Config.STATIC_DIR,
        Config.TEMPLATES_DIR
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Directory ready: {directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            return False
    
    return True

def check_database():
    """Check database connection"""
    try:
        from database import Database
        db = Database()
        # Test connection
        db.client.admin.command('ping')
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def run_bot():
    """Run the Telegram bot"""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        from bot import KinvaMasterBot
        logger.info("Starting Kinva Master Bot...")
        bot = KinvaMasterBot()
        bot.run()
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        # traceback
        import traceback
        logger.error(traceback.format_exc())
        raise

def run_web():
    """Run the Flask web application"""
    try:
        from web_app import app, socketio
        logger.info(f"Starting Web Server on {Config.WEB_APP_HOST}:{Config.WEB_APP_PORT}...")
        socketio.run(
            app,
            host=Config.WEB_APP_HOST,
            port=Config.WEB_APP_PORT,
            debug=False,
            # allow_unsafe_werkzeug removed - it's for dev
        )
    except Exception as e:
        logger.error(f"Web server crashed: {e}")
        raise

def run_both():
    """Run both bot and web server in parallel"""
    import threading
    
    logger.info("Starting both Bot and Web Server...")
    
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("Bot thread started")
    
    # Run web server in main thread
    run_web()

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Kinva Master Bot')
    parser.add_argument(
        '--mode',
        choices=['bot', 'web', 'both'],
        default='both',
        help='Run mode: bot only, web only, or both (default: both)'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check environment and dependencies'
    )
    
    args = parser.parse_args()
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Print banner
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     ██╗  ██╗██╗███╗   ██╗██╗   ██╗ █████╗                ║
║     ██║ ██╔╝██║████╗  ██║██║   ██║██╔══██╗               ║
║     █████╔╝ ██║██╔██╗ ██║██║   ██║███████║               ║
║     ██╔═██╗ ██║██║╚██╗██║╚██╗ ██╔╝██╔══██║               ║
║     ██║  ██╗██║██║ ╚████║ ╚████╔╝ ██║  ██║               ║
║     ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝  ╚═══╝  ╚═╝  ╚═╝               ║
║                                                           ║
║              ███╗   ███╗ █████╗ ███████╗████████╗███████╗ ║
║              ████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝ ║
║              ██╔████╔██║███████║███████╗   ██║   ███████╗ ║
║              ██║╚██╔╝██║██╔══██║╚════██║   ██║   ╚════██║ ║
║              ██║ ╚═╝ ██║██║  ██║███████║   ██║   ███████║ ║
║              ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝ ║
║                                                           ║
║           KINVA MASTER - Professional Editor              ║
║                   Version 3.0                             ║
║              Author: @funnytamilan                        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    logger.info(f"Starting Kinva Master Bot v3.0")
    logger.info(f"Mode: {args.mode}")
    
    # Check environment
    if args.check:
        logger.info("Running environment check...")
        
        # Check environment variables
        if check_environment():
            logger.info("✓ Environment variables OK")
        else:
            logger.error("✗ Environment variables check failed")
            sys.exit(1)
        
        # Check directories
        if check_directories():
            logger.info("✓ Directories OK")
        else:
            logger.error("✗ Directories check failed")
            sys.exit(1)
        
        # Check database
        if check_database():
            logger.info("✓ Database OK")
        else:
            logger.error("✗ Database check failed")
            sys.exit(1)
        
        # Check configuration
        errors = Config.validate_config()
        if errors:
            logger.warning(f"Configuration warnings: {errors}")
        else:
            logger.info("✓ Configuration OK")
        
        # Print stats
        stats = Config.get_stats()
        logger.info(f"Configuration Stats: {stats}")
        
        logger.info("Environment check completed successfully!")
        sys.exit(0)
    
    # Run based on mode
    try:
        if args.mode == 'bot':
            run_bot()
        elif args.mode == 'web':
            run_web()
        else:
            run_both()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
