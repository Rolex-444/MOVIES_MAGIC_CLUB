"""
Movie Filter Bot - Verification Database Module
WITH DAILY RESET SYSTEM (Resets at 12:00 AM IST)
Tracks user verification, free limits, premium, and points
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# MongoDB setup
MONGODB_URL = os.getenv("DATABASE_URI")
if not MONGODB_URL:
    logger.error("❌ DATABASE_URI not found in environment variables!")
    raise ValueError("DATABASE_URI is required")

client = MongoClient(MONGODB_URL)
DATABASE_NAME = os.getenv("DATABASE_NAME", "MovieFilterBot")
db = client[DATABASE_NAME]
users_collection = db["users"]

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Import config values
try:
    from info import (
        VERIFY_EXPIRE,
        PREMIUM_POINT,
        REFER_POINT
    )
    FREE_FILE_LIMIT = int(os.getenv("FREE_FILE_LIMIT", "5"))
    VERIFY_TOKEN_TIMEOUT = VERIFY_EXPIRE
except ImportError as e:
    logger.error(f"❌ Config import error: {e}")
    FREE_FILE_LIMIT = 5
    VERIFY_TOKEN_TIMEOUT = 86400  # 24 hours
    PREMIUM_POINT = 1500
    REFER_POINT = 50

# Create indexes
try:
    users_collection.create_index("user_id", unique=True)
    logger.info("✅ Database indexes created")
except Exception as e:
    logger.error(f"❌ Index creation error: {e}")


class VerifyDB:
    """Database class for verification and user management"""

    def __init__(self):
        self.collection = users_collection

    async def add_user(self, user_id: int, name: str = "User"):
        """Add or update user in database"""
        try:
            now = datetime.now(IST)
            user_data = {
                "user_id": user_id,
                "name": name,
                "joined_date": now,
                "is_verified": False,
                "verify_expire": 0,
                "verify_token": None,
                "token_expiry": 0,
                "file_attempts": 0,
                "last_reset": now,
                "is_premium": False,
                "premium_expire": 0,
                "points": 0,
                "referrals": 0
            }
            self.collection.update_one(
                {"user_id": user_id},
                {"$setOnInsert": user_data},
                upsert=True
            )
            logger.info(f"✅ User {user_id} added to database")
            return True
        except Exception as e:
            logger.error(f"❌ Error adding user {user_id}: {e}")
            return False

    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data"""
        try:
            user = self.collection.find_one({"user_id": user_id})
            return user
        except Exception as e:
            logger.error(f"❌ Error getting user {user_id}: {e}")
            return None

    async def is_verified(self, user_id: int) -> bool:
        """Check if user is verified"""
        try:
            user = await self.get_user(user_id)
            if not user:
                return False
            
            # Premium users are always verified
            if user.get("is_premium", False):
                if user.get("premium_expire", 0) > int(datetime.now(IST).timestamp()):
                    return True
            
            # Check verification status
            if user.get("is_verified", False):
                if user.get("verify_expire", 0) > int(datetime.now(IST).timestamp()):
                    return True
                else:
                    # Expired, reset verification
                    await self.reset_verification(user_id)
            
            return False
        except Exception as e:
            logger.error(f"❌ Error checking verification for {user_id}: {e}")
            return False

    async def is_premium(self, user_id: int) -> bool:
        """Check if user has active premium"""
        try:
            user = await self.get_user(user_id)
            if not user:
                return False
            
            if user.get("is_premium", False):
                if user.get("premium_expire", 0) > int(datetime.now(IST).timestamp()):
                    return True
                else:
                    # Premium expired
                    await self.remove_premium(user_id)
            
            return False
        except Exception as e:
            logger.error(f"❌ Error checking premium for {user_id}: {e}")
            return False

    async def reset_daily_limits(self, user_id: int):
        """Reset daily file attempt limits"""
        try:
            now = datetime.now(IST)
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "file_attempts": 0,
                    "last_reset": now
                }}
            )
            logger.info(f"✅ Daily limits reset for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error resetting limits for {user_id}: {e}")

    async def check_and_reset_daily(self, user_id: int):
        """Check if daily reset is needed and perform it"""
        try:
            user = await self.get_user(user_id)
            if not user:
                return
            
            now = datetime.now(IST)
            last_reset = user.get("last_reset")
            
            if isinstance(last_reset, datetime):
                last_reset_date = last_reset.date()
            else:
                last_reset_date = now.date()
            
            if now.date() > last_reset_date:
                await self.reset_daily_limits(user_id)
        except Exception as e:
            logger.error(f"❌ Error checking daily reset for {user_id}: {e}")

    async def can_access_file(self, user_id: int) -> bool:
        """Check if user can access file (verified or under free limit)"""
        try:
            # Check if verified or premium
            if await self.is_verified(user_id):
                return True
            
            # Check daily reset
            await self.check_and_reset_daily(user_id)
            
            # Check free limit
            user = await self.get_user(user_id)
            if not user:
                return False
            
            file_attempts = user.get("file_attempts", 0)
            return file_attempts < FREE_FILE_LIMIT
        except Exception as e:
            logger.error(f"❌ Error checking file access for {user_id}: {e}")
            return False

    async def increment_file_attempts(self, user_id: int):
        """Increment file access attempts"""
        try:
            self.collection.update_one(
                {"user_id": user_id},
                {"$inc": {"file_attempts": 1}}
            )
            logger.info(f"✅ File attempts incremented for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error incrementing attempts for {user_id}: {e}")

    async def get_verify_status(self, user_id: int) -> Dict:
        """Get verification status details"""
        try:
            user = await self.get_user(user_id)
            if not user:
                return {"verified": False, "expire_at": 0}
            
            return {
                "verified": user.get("is_verified", False),
                "expire_at": user.get("verify_expire", 0)
            }
        except Exception as e:
            logger.error(f"❌ Error getting verify status for {user_id}: {e}")
            return {"verified": False, "expire_at": 0}

    async def add_verification(self, user_id: int, expire_seconds: int):
        """Add verification to user"""
        try:
            expire_time = int(datetime.now(IST).timestamp()) + expire_seconds
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "is_verified": True,
                    "verify_expire": expire_time
                }}
            )
            logger.info(f"✅ Verification added for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error adding verification for {user_id}: {e}")
            return False

    async def reset_verification(self, user_id: int):
        """Reset verification status"""
        try:
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "is_verified": False,
                    "verify_expire": 0
                }}
            )
            logger.info(f"✅ Verification reset for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error resetting verification for {user_id}: {e}")

    async def set_verify_token(self, user_id: int, token: str, timeout: int):
        """Set verification token with expiry"""
        try:
            token_expiry = int(datetime.now(IST).timestamp()) + timeout
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "verify_token": token,
                    "token_expiry": token_expiry
                }}
            )
            logger.info(f"✅ Verify token set for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error setting token for {user_id}: {e}")
            return False

    async def verify_token(self, token: str) -> Optional[int]:
        """Verify token and return user_id if valid"""
        try:
            user = self.collection.find_one({"verify_token": token})
            if not user:
                return None
            
            # Check token expiry
            token_expiry = user.get("token_expiry", 0)
            if token_expiry < int(datetime.now(IST).timestamp()):
                return None
            
            # Token valid, mark user as verified
            user_id = user.get("user_id")
            await self.add_verification(user_id, VERIFY_TOKEN_TIMEOUT)
            
            # Clear token
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "verify_token": None,
                    "token_expiry": 0
                }}
            )
            
            return user_id
        except Exception as e:
            logger.error(f"❌ Error verifying token: {e}")
            return None

    async def get_points(self, user_id: int) -> int:
        """Get user points"""
        try:
            user = await self.get_user(user_id)
            return user.get("points", 0) if user else 0
        except Exception as e:
            logger.error(f"❌ Error getting points for {user_id}: {e}")
            return 0

    async def add_points(self, user_id: int, points: int):
        """Add points to user"""
        try:
            self.collection.update_one(
                {"user_id": user_id},
                {"$inc": {"points": points}}
            )
            logger.info(f"✅ Added {points} points to user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error adding points to {user_id}: {e}")

    async def deduct_points(self, user_id: int, points: int):
        """Deduct points from user"""
        try:
            self.collection.update_one(
                {"user_id": user_id},
                {"$inc": {"points": -points}}
            )
            logger.info(f"✅ Deducted {points} points from user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error deducting points from {user_id}: {e}")

    async def make_premium(self, user_id: int, expire_time: int):
        """Make user premium"""
        try:
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "is_premium": True,
                    "premium_expire": expire_time
                }}
            )
            logger.info(f"✅ Premium activated for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error making premium {user_id}: {e}")

    async def remove_premium(self, user_id: int):
        """Remove premium status"""
        try:
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "is_premium": False,
                    "premium_expire": 0
                }}
            )
            logger.info(f"✅ Premium removed for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error removing premium {user_id}: {e}")

    async def increment_referrals(self, user_id: int):
        """Increment referral count"""
        try:
            self.collection.update_one(
                {"user_id": user_id},
                {"$inc": {"referrals": 1}}
            )
            logger.info(f"✅ Referral count incremented for user {user_id}")
        except Exception as e:
            logger.error(f"❌ Error incrementing referrals for {user_id}: {e}")
    
