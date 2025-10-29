"""
Movie Filter Bot - Verification Database Module
Updated with proper verification flow
"""

import os
import logging
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict

logger = logging.getLogger(__name__)

# MongoDB setup
MONGODB_URL = os.getenv("DATABASE_URI")
if not MONGODB_URL:
    logger.error("❌ DATABASE_URI not found in environment variables!")
    raise ValueError("DATABASE_URI is required")

client = AsyncIOMotorClient(MONGODB_URL)
DATABASE_NAME = os.getenv("DATABASE_NAME", "MovieFilterBot")
db = client[DATABASE_NAME]
users_collection = db["users"]

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Import config values
try:
    from info import VERIFY_EXPIRE, PREMIUM_POINT, REFER_POINT, FREE_FILE_LIMIT
    VERIFY_TOKEN_TIMEOUT = VERIFY_EXPIRE
except ImportError as e:
    logger.error(f"❌ Error importing config: {e}")
    FREE_FILE_LIMIT = 5
    VERIFY_TOKEN_TIMEOUT = 21600  # 6 hours


class VerifyDB:
    """Database operations for verification system"""
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user from database"""
        try:
            return await users_collection.find_one({"user_id": user_id})
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
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
                verify_time = user.get("verify_time", 0)
                current_time = int(datetime.now(IST).timestamp())
                time_diff = current_time - verify_time
                
                logger.info(f"🔍 is_verified({user_id}): verify_time={verify_time}, current={current_time}, diff={time_diff}s")
                
                if time_diff < VERIFY_TOKEN_TIMEOUT:
                    logger.info(f"🔍 is_verified({user_id}): Valid verification → True")
                    return True
                else:
                    logger.info(f"🔍 is_verified({user_id}): Verification expired → False")
                    return False
            
            logger.info(f"🔍 is_verified({user_id}): Not verified → False")
            return False
            
        except Exception as e:
            logger.error(f"Error checking verification: {e}")
            return False
    
    async def update_verification(self, user_id: int) -> bool:
        """Mark user as verified with timestamp"""
        try:
            current_time = int(datetime.now(IST).timestamp())
            
            result = await users_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "is_verified": True,
                        "verify_time": current_time,
                        "files_sent": 0  # Reset file counter
                    }
                },
                upsert=True
            )
            
            logger.info(f"✅ User {user_id} verification updated at {current_time}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating verification: {e}")
            return False
    
    async def set_verify_token(self, user_id: int, token: str, expire_seconds: int = 600) -> bool:
        """Store verification token with expiry"""
        try:
            expire_time = int(datetime.now(IST).timestamp()) + expire_seconds
            
            result = await users_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "verify_token": token,
                        "token_expire": expire_time
                    }
                },
                upsert=True
            )
            
            logger.info(f"🔑 Token set for user {user_id}: {token[:20]}... (expires in {expire_seconds}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error setting verify token: {e}")
            return False
    
    async def verify_token(self, user_id: int, token: str) -> bool:
        """Verify if token is valid and not expired"""
        try:
            user = await self.get_user(user_id)
            if not user:
                logger.warning(f"❌ verify_token({user_id}): User not found")
                return False
            
            stored_token = user.get("verify_token")
            token_expire = user.get("token_expire", 0)
            current_time = int(datetime.now(IST).timestamp())
            
            logger.info(f"🔍 verify_token({user_id}): stored={stored_token}, provided={token}")
            logger.info(f"🔍 Token expire: {token_expire}, current: {current_time}")
            
            if stored_token == token and current_time < token_expire:
                logger.info(f"✅ Token valid for user {user_id}")
                return True
            else:
                logger.warning(f"❌ Token invalid or expired for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying token: {e}")
            return False
    
    async def increment_files_sent(self, user_id: int) -> bool:
        """Increment files sent counter for user"""
        try:
            result = await users_collection.update_one(
                {"user_id": user_id},
                {"$inc": {"files_sent": 1}},
                upsert=True
            )
            
            # Get updated count
            user = await self.get_user(user_id)
            new_count = user.get('files_sent', 0) if user else 0
            
            logger.info(f"📈 User {user_id} files_sent incremented to {new_count}")
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing files sent: {e}")
            return False
    
    async def clear_verification(self, user_id: int) -> bool:
        """Clear user verification status"""
        try:
            result = await users_collection.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "is_verified": False,
                        "verify_time": 0,
                        "files_sent": 0,
                        "verify_token": None,
                        "token_expire": 0
                    }
                }
            )
            
            logger.info(f"🗑️ Verification cleared for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error clearing verification: {e}")
            return False
    
    async def get_verification_info(self, user_id: int) -> Dict:
        """Get detailed verification info for user"""
        try:
            user = await self.get_user(user_id)
            if not user:
                return {
                    "verified": False,
                    "files_sent": 0,
                    "time_remaining": 0
                }
            
            is_verified = await self.is_verified(user_id)
            verify_time = user.get("verify_time", 0)
            current_time = int(datetime.now(IST).timestamp())
            time_remaining = max(0, VERIFY_TOKEN_TIMEOUT - (current_time - verify_time))
            
            return {
                "verified": is_verified,
                "files_sent": user.get("files_sent", 0),
                "verify_time": verify_time,
                "time_remaining": time_remaining,
                "is_premium": user.get("is_premium", False)
            }
            
        except Exception as e:
            logger.error(f"Error getting verification info: {e}")
            return {"verified": False, "files_sent": 0, "time_remaining": 0}
    
