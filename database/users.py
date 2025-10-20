from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI, DATABASE_NAME
import logging
import time

logger = logging.getLogger(__name__)

class UserDB:
    def __init__(self):
        self.client = AsyncIOMotorClient(DATABASE_URI)
        self.db = self.client[DATABASE_NAME]
        self.col = self.db['users']

    async def add_user(self, user_id, name):
        """Add user to database"""
        try:
            user = await self.col.find_one({'user_id': user_id})
            if not user:
                await self.col.insert_one({
                    'user_id': user_id,
                    'name': name,
                    'is_premium': False,
                    'premium_expire': 0,
                    'points': 0,
                    'referred_by': None
                })
                return True
            return False
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False

    async def get_user(self, user_id):
        """Get user by ID"""
        return await self.col.find_one({'user_id': user_id})

    async def total_users_count(self):
        """Count total users"""
        return await self.col.count_documents({})

    async def get_all_users(self):
        """Get all users"""
        cursor = self.col.find({})
        return await cursor.to_list(length=None)

    async def delete_user(self, user_id):
        """Delete user"""
        await self.col.delete_one({'user_id': user_id})

    # Premium methods
    async def make_premium(self, user_id, expire_time):
        """Make user premium"""
        await self.col.update_one(
            {'user_id': user_id},
            {'$set': {'is_premium': True, 'premium_expire': expire_time}}
        )

    async def is_premium(self, user_id):
        """Check if user is premium"""
        user = await self.get_user(user_id)
        
        if not user:
            return False
        
        if user.get('is_premium'):
            if user.get('premium_expire') > time.time():
                return True
            else:
                await self.col.update_one(
                    {'user_id': user_id},
                    {'$set': {'is_premium': False}}
                )
        return False

    # Points system
    async def add_points(self, user_id, points):
        """Add points to user"""
        await self.col.update_one(
            {'user_id': user_id},
            {'$inc': {'points': points}}
        )

    async def get_points(self, user_id):
        """Get user points"""
        user = await self.get_user(user_id)
        return user.get('points', 0) if user else 0

    async def deduct_points(self, user_id, points):
        """Deduct points from user"""
        await self.col.update_one(
            {'user_id': user_id},
            {'$inc': {'points': -points}}
        )

    async def update_referral(self, user_id, referred_by):
        """Update user's referral info"""
        await self.col.update_one(
            {'user_id': user_id},
            {'$set': {'referred_by': referred_by}}
        )
