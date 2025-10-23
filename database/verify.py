"""
Movie Filter Bot - Verification Database Module
WITH EXTENSIVE DEBUGGING - Find verification issues
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
    logger.error(f"❌ Error importing config: {e}")
    FREE_FILE_LIMIT = 5
    VERIFY_TOKEN_TIMEOUT = 86400
    PREMIUM_POINT = 1000
    REFER_POINT = 50

# Log the limit on startup
logger.info(f"🔧 FREE_FILE_LIMIT set to: {FREE_FILE_LIMIT}")


class VerifyDB:
    def __init__(self):
        """Initialize VerifyDB with MongoDB collection"""
        self.collection = users_collection
        logger.info("✅ VerifyDB initialized")

    # ============ USER METHODS ============
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user data"""
        try:
            user = self.collection.find_one({"user_id": user_id})
            if not user:
                default_user = {
                    "user_id": user_id,
                    "is_verified": False,
                    "verify_expire": 0,
                    "is_premium": False,
                    "premium_expire": 0,
                    "points": 0,
                    "referred_by": None,
                    "file_attempts": 0,
                    "last_reset": datetime.now(IST),
                    "created_at": datetime.now(IST)
                }
                self.collection.insert_one(default_user)
                logger.info(f"🆕 Created new user: {user_id}")
                return default_user
            return user
        except Exception as e:
            logger.error(f"❌ Error getting user {user_id}: {e}")
            return None

    async def add_user(self, user_id: int, referred_by: Optional[int] = None):
        """Add new user to database"""
        try:
            existing = self.collection.find_one({"user_id": user_id})
            if existing:
                return True
            
            user_data = {
                "user_id": user_id,
                "is_verified": False,
                "verify_expire": 0,
                "is_premium": False,
                "premium_expire": 0,
                "points": 0,
                "referred_by": referred_by,
                "file_attempts": 0,
                "last_reset": datetime.now(IST),
                "created_at": datetime.now(IST)
            }
            
            self.collection.insert_one(user_data)
            logger.info(f"✅ New user added: {user_id}")
            
            if referred_by:
                await self.add_points(referred_by, REFER_POINT)
                logger.info(f"✅ Referral reward given to {referred_by}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Error adding user {user_id}: {e}")
            return False

    # ============ VERIFICATION METHODS ============
    
    async def is_verified(self, user_id: int) -> bool:
        """Check if user is verified and not expired"""
        try:
            user = await self.get_user(user_id)
            if not user:
                logger.info(f"🔍 is_verified({user_id}): No user data → False")
                return False
            
            # Premium users are always verified
            if user.get("is_premium", False):
                premium_expire = user.get("premium_expire", 0)
                current_time = int(datetime.now(IST).timestamp())
                if premium_expire > current_time:
                    logger.info(f"🔍 is_verified({user_id}): Premium user → True")
                    return True
            
            # Check verification status with expiry validation
            if user.get("is_verified", False):
                verify_expire = user.get("verify_expire", 0)
                current_time = int(datetime.now(IST).timestamp())
                
                logger.info(f"🔍 is_verified({user_id}): verify_expire={verify_expire}, current={current_time}")
                
                if verify_expire > current_time:
                    logger.info(f"🔍 is_verified({user_id}): Valid verification → True")
                    return True
                else:
                    # Expired, automatically reset verification
                    await self.reset_verification(user_id)
                    logger.info(f"⏰ Verification expired for user {user_id} → False")
                    return False
            
            logger.info(f"🔍 is_verified({user_id}): Not verified → False")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking verification for {user_id}: {e}")
            return False

    async def can_access_file(self, user_id: int) -> bool:
        """Check if user can access file - WITH EXTENSIVE DEBUGGING"""
        try:
            logger.info(f"")
            logger.info(f"{'='*60}")
            logger.info(f"🔍 CHECKING FILE ACCESS FOR USER: {user_id}")
            logger.info(f"{'='*60}")
            
            # Step 1: Check premium
            is_premium = await self.is_premium(user_id)
            logger.info(f"📌 Step 1 - Is Premium? {is_premium}")
            if is_premium:
                logger.info(f"✅ RESULT: Premium user - ACCESS GRANTED")
                logger.info(f"{'='*60}")
                return True
            
            # Step 2: Check verified
            is_verified = await self.is_verified(user_id)
            logger.info(f"📌 Step 2 - Is Verified? {is_verified}")
            if is_verified:
                logger.info(f"✅ RESULT: Verified user - ACCESS GRANTED")
                logger.info(f"{'='*60}")
                return True
            
            # Step 3: Get user data and check free limit
            logger.info(f"📌 Step 3 - Checking free file limit...")
            user = await self.get_user(user_id)
            if not user:
                logger.error(f"❌ RESULT: No user data - ACCESS DENIED")
                logger.info(f"{'='*60}")
                return False
            
            # Get file attempts
            file_attempts = user.get("file_attempts", 0)
            logger.info(f"📊 Current file_attempts: {file_attempts}")
            logger.info(f"📊 FREE_FILE_LIMIT: {FREE_FILE_LIMIT}")
            logger.info(f"📊 Comparison: {file_attempts} >= {FREE_FILE_LIMIT} = {file_attempts >= FREE_FILE_LIMIT}")
            
            if file_attempts >= FREE_FILE_LIMIT:
                logger.info(f"❌ RESULT: Limit reached ({file_attempts}/{FREE_FILE_LIMIT}) - ACCESS DENIED")
                logger.info(f"{'='*60}")
                return False
            
            logger.info(f"✅ RESULT: Free file allowed ({file_attempts}/{FREE_FILE_LIMIT}) - ACCESS GRANTED")
            logger.info(f"{'='*60}")
            return True
            
        except Exception as e:
            logger.error(f"❌ ERROR in can_access_file: {e}")
            logger.info(f"{'='*60}")
            return False

    async def get_verify_status(self, user_id: int) -> Dict:
        """Get verification status with expiry info"""
        try:
            user = await self.get_user(user_id)
            if not user:
                return {"verified": False, "expire_at": 0}
            
            verify_expire = user.get("verify_expire", 0)
            current_time = int(datetime.now(IST).timestamp())
            
            if user.get("is_verified", False) and verify_expire <= current_time:
                await self.reset_verification(user_id)
                return {"verified": False, "expire_at": 0}
            
            return {
                "verified": user.get("is_verified", False),
                "expire_at": verify_expire
            }
        except Exception as e:
            logger.error(f"❌ Error getting verify status for {user_id}: {e}")
            return {"verified": False, "expire_at": 0}

    async def add_verification(self, user_id: int, expire_seconds: int):
        """Add verification to user with expiry time"""
        try:
            current_time = int(datetime.now(IST).timestamp())
            expire_time = current_time + expire_seconds
            
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "is_verified": True,
                    "verify_expire": expire_time
                }},
                upsert=True
            )
            logger.info(f"✅ Verification added for user {user_id}, expires at {expire_time} ({expire_seconds}s)")
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
                    "verify_expire": 0,
                    "file_attempts": 0
                }},
                upsert=True
            )
            logger.info(f"✅ Verification reset for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error resetting verification for {user_id}: {e}")
            return False

    # ============ VERIFICATION TOKEN METHODS ============
    
    async def set_verify_token(self, user_id: int, token: str, expire_seconds: int = 600):
        """Store verification token (for shortlink verification)"""
        try:
            expire_at = int(datetime.now(IST).timestamp()) + expire_seconds
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "verify_token": token,
                    "token_expire": expire_at
                }},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error setting verify token for {user_id}: {e}")
            return False

    async def verify_token(self, token: str) -> Optional[int]:
        """Verify token and return user_id if valid"""
        try:
            user = self.collection.find_one({"verify_token": token})
            if not user:
                return None
            
            current_time = int(datetime.now(IST).timestamp())
            token_expire = user.get("token_expire", 0)
            
            if token_expire <= current_time:
                logger.info(f"⏰ Token expired for user {user.get('user_id')}")
                return None
            
            return user.get("user_id")
        except Exception as e:
            logger.error(f"❌ Error verifying token: {e}")
            return None

    # ============ FILE ATTEMPTS METHODS ============
    
    async def increment_file_attempts(self, user_id: int):
        """Increment file access attempts - WITH EXTENSIVE DEBUGGING"""
        try:
            # Get current count BEFORE increment
            user_before = self.collection.find_one({"user_id": user_id})
            before_count = user_before.get("file_attempts", 0) if user_before else 0
            
            # Perform increment
            result = self.collection.update_one(
                {"user_id": user_id},
                {"$inc": {"file_attempts": 1}},
                upsert=True
            )
            
            # Get count AFTER increment
            user_after = self.collection.find_one({"user_id": user_id})
            after_count = user_after.get("file_attempts", 0) if user_after else 0
            
            logger.info(f"")
            logger.info(f"📈 FILE ATTEMPT INCREMENT:")
            logger.info(f"   User: {user_id}")
            logger.info(f"   Before: {before_count}")
            logger.info(f"   After: {after_count}")
            logger.info(f"   Limit: {FREE_FILE_LIMIT}")
            logger.info(f"   Modified: {result.modified_count}")
            logger.info(f"   Next file will be: {after_count + 1}/{FREE_FILE_LIMIT}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Error incrementing attempts for {user_id}: {e}")
            return False

    async def reset_file_attempts(self, user_id: int):
        """Reset file attempts to 0"""
        try:
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"file_attempts": 0}},
                upsert=True
            )
            logger.info(f"✅ File attempts reset to 0 for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error resetting file attempts for {user_id}: {e}")
            return False

    # ============ DAILY RESET METHODS ============
    
    async def check_and_reset_daily(self, user_id: int):
        """Check if daily reset is needed - NOT CALLED AUTOMATICALLY"""
        try:
            user = await self.get_user(user_id)
            if not user:
                return
            
            now = datetime.now(IST)
            last_reset = user.get("last_reset")
            
            if last_reset is None:
                self.collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"last_reset": now}},
                    upsert=True
                )
                return
            
            if isinstance(last_reset, datetime):
                last_reset_date = last_reset.date()
            else:
                last_reset_date = now.date()
            
            current_date = now.date()
            
            if current_date > last_reset_date:
                await self.reset_daily_limits(user_id)
                logger.info(f"📅 Daily reset performed for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error checking daily reset for {user_id}: {e}")

    async def reset_daily_limits(self, user_id: int):
        """Reset daily file limits"""
        try:
            now = datetime.now(IST)
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "file_attempts": 0,
                    "last_reset": now
                }},
                upsert=True
            )
            logger.info(f"✅ Daily limits reset for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error resetting daily limits for {user_id}: {e}")
            return False

    # ============ PREMIUM METHODS ============
    
    async def is_premium(self, user_id: int) -> bool:
        """Check if user has active premium"""
        try:
            user = await self.get_user(user_id)
            if not user:
                return False
            
            if user.get("is_premium", False):
                premium_expire = user.get("premium_expire", 0)
                current_time = int(datetime.now(IST).timestamp())
                
                if premium_expire > current_time:
                    return True
                else:
                    self.collection.update_one(
                        {"user_id": user_id},
                        {"$set": {"is_premium": False}}
                    )
            
            return False
        except Exception as e:
            logger.error(f"❌ Error checking premium for {user_id}: {e}")
            return False

    async def add_premium(self, user_id: int, duration_seconds: int):
        """Add premium to user"""
        try:
            current_time = int(datetime.now(IST).timestamp())
            user = await self.get_user(user_id)
            current_expire = user.get("premium_expire", 0) if user else 0
            
            if current_expire > current_time:
                new_expire = current_expire + duration_seconds
            else:
                new_expire = current_time + duration_seconds
            
            self.collection.update_one(
                {"user_id": user_id},
                {"$set": {
                    "is_premium": True,
                    "premium_expire": new_expire
                }},
                upsert=True
            )
            logger.info(f"✅ Premium added for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error adding premium for {user_id}: {e}")
            return False

    # ============ POINTS METHODS ============
    
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
                {"$inc": {"points": points}},
                upsert=True
            )
            logger.info(f"✅ Added {points} points to user {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error adding points to {user_id}: {e}")
            return False

    async def deduct_points(self, user_id: int, points: int) -> bool:
        """Deduct points from user"""
        try:
            user = await self.get_user(user_id)
            current_points = user.get("points", 0) if user else 0
            
            if current_points < points:
                return False
            
            self.collection.update_one(
                {"user_id": user_id},
                {"$inc": {"points": -points}}
            )
            logger.info(f"✅ Deducted {points} points from user {user_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error deducting points from {user_id}: {e}")
            return False

    # ============ STATS METHODS ============
    
    async def total_users(self) -> int:
        """Get total number of users"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            logger.error(f"❌ Error getting total users: {e}")
            return 0

    async def total_verified_users(self) -> int:
        """Get total verified users"""
        try:
            current_time = int(datetime.now(IST).timestamp())
            return self.collection.count_documents({
                "is_verified": True,
                "verify_expire": {"$gt": current_time}
            })
        except Exception as e:
            logger.error(f"❌ Error getting verified users: {e}")
            return 0

    async def total_premium_users(self) -> int:
        """Get total premium users"""
        try:
            current_time = int(datetime.now(IST).timestamp())
            return self.collection.count_documents({
                "is_premium": True,
                "premium_expire": {"$gt": current_time}
            })
        except Exception as e:
            logger.error(f"❌ Error getting premium users: {e}")
            return 0
    
