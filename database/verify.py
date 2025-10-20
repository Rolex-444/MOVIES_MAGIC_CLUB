from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI, DATABASE_NAME
import time
import logging

logger = logging.getLogger(__name__)

class VerifyDB:
    def __init__(self):
        self.client = AsyncIOMotorClient(DATABASE_URI)
        self.db = self.client[DATABASE_NAME]
        self.col = self.db['verify_users']

    async def add_user(self, user_id: int, verify_time: int):
        """Add verified user with expiry time"""
        expire_at = int(time.time()) + verify_time
        await self.col.update_one(
            {'user_id': user_id},
            {'$set': {'user_id': user_id, 'expire_at': expire_at}},
            upsert=True
        )
        logger.info(f"User {user_id} verified until {expire_at}")

    async def is_verified(self, user_id: int) -> bool:
        """Check if user is verified"""
        user = await self.col.find_one({'user_id': user_id})
        if not user:
            return False
        
        if user['expire_at'] < int(time.time()):
            await self.col.delete_one({'user_id': user_id})
            return False
        
        return True

    async def get_verify_status(self, user_id: int):
        """Get verification status"""
        user = await self.col.find_one({'user_id': user_id})
        if not user:
            return None
        return user

    async def delete_user(self, user_id: int):
        """Delete verified user"""
        await self.col.delete_one({'user_id': user_id})
