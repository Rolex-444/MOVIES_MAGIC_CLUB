from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI, DATABASE_NAME
import logging
import time

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = AsyncIOMotorClient(DATABASE_URI)
        self.db = self.client[DATABASE_NAME]
        self.col = self.db['files']
        self.grp = self.db['groups']
        self.usr = self.db['users']

    async def create_index(self):
        """Create database indexes"""
        try:
            await self.col.create_index([('file_name', 'text')])
            await self.usr.create_index([('user_id', 1)])
            await self.grp.create_index([('group_id', 1)])
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")

    # ============ FILE METHODS ============
    
    async def add_file(self, file_data):
        """Add file to database"""
        try:
            await self.col.insert_one(file_data)
            return True
        except Exception as e:
            logger.error(f"Error adding file: {e}")
            return False

    async def get_file(self, file_id):
        """Get file by ID"""
        return await self.col.find_one({'_id': file_id})

    async def search_files(self, query, offset=0, limit=10):
        """Search files by query"""
        try:
            cursor = self.col.find(
                {'$text': {'$search': query}}
            ).skip(offset).limit(limit)
            files = await cursor.to_list(length=limit)
            total = await self.col.count_documents({'$text': {'$search': query}})
            return files, total
        except Exception as e:
            logger.error(f"Search error: {e}")
            return [], 0

    async def delete_file(self, file_id):
        """Delete file from database"""
        await self.col.delete_one({'_id': file_id})

    async def get_all_files(self):
        """Get all files"""
        cursor = self.col.find({})
        return await cursor.to_list(length=None)

    async def delete_all_files(self):
        """Delete all files"""
        result = await self.col.delete_many({})
        return result

    async def total_files_count(self):
        """Count total files"""
        return await self.col.count_documents({})

    async def get_file_by_file_id(self, file_id):
        """Get file data by Telegram file_id"""
        try:
            file_data = await self.col.find_one({'file_id': file_id})
            return file_data
        except Exception as e:
            logger.error(f"Error getting file by file_id: {e}")
            return None

    async def delete_file_by_file_id(self, file_id):
        """Delete file from database by Telegram file_id"""
        try:
            result = await self.col.delete_one({'file_id': file_id})
            logger.info(f"Deleted file by file_id: {file_id}, count: {result.deleted_count}")
            return result
        except Exception as e:
            logger.error(f"Error deleting file by file_id: {e}")
            return None

    async def delete_file_by_id(self, mongo_id):
        """Delete file from database by MongoDB _id"""
        try:
            result = await self.col.delete_one({'_id': mongo_id})
            logger.info(f"Deleted file by ID: {mongo_id}, count: {result.deleted_count}")
            return result
        except Exception as e:
            logger.error(f"Error deleting file by ID: {e}")
            return None

    # ============ 🆕 DUPLICATE DETECTION METHODS ============
    
    async def find_duplicate_files(self, file_name, file_size):
        """
        🆕 Find files with same name and size
        Returns list of matching files
        """
        try:
            duplicates = self.col.find({
                'file_name': file_name,
                'file_size': file_size
            })
            
            result = await duplicates.to_list(length=None)
            return result
            
        except Exception as e:
            logger.error(f"Error finding duplicates: {e}")
            return []

    async def get_duplicate_count(self):
        """
        🆕 Get total number of duplicate files in database
        Returns: (total_duplicate_files, number_of_duplicate_groups)
        """
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": {"name": "$file_name", "size": "$file_size"},
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$match": {
                        "count": {"$gt": 1}
                    }
                }
            ]
            
            duplicates = await self.col.aggregate(pipeline).to_list(length=None)
            
            total_duplicates = sum(item['count'] - 1 for item in duplicates)
            
            return total_duplicates, len(duplicates)
            
        except Exception as e:
            logger.error(f"Error counting duplicates: {e}")
            return 0, 0

    async def delete_duplicate_files(self, keep_latest=True):
        """
        🆕 Delete all duplicate files
        If keep_latest=True, keeps the newest file for each duplicate group
        Returns number of files deleted
        """
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": {"name": "$file_name", "size": "$file_size"},
                        "files": {"$push": {"id": "$_id", "time": "$_id"}},
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$match": {
                        "count": {"$gt": 1}
                    }
                }
            ]
            
            duplicate_groups = await self.col.aggregate(pipeline).to_list(length=None)
            
            deleted_count = 0
            
            for group in duplicate_groups:
                files = group['files']
                
                if keep_latest:
                    # Sort by ID (newer files have larger ObjectId)
                    files.sort(key=lambda x: x['id'], reverse=True)
                    # Keep first (newest), delete rest
                    to_delete = files[1:]
                else:
                    # Delete all
                    to_delete = files
                
                for file in to_delete:
                    await self.col.delete_one({'_id': file['id']})
                    deleted_count += 1
            
            logger.info(f"✅ Deleted {deleted_count} duplicate files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting duplicates: {e}")
            return 0

    # ============ GROUP METHODS ============
    
    async def add_group(self, group_id, group_name):
        """Add group to database"""
        await self.grp.update_one(
            {'group_id': group_id},
            {'$set': {'group_name': group_name}},
            upsert=True
        )

    async def get_group(self, group_id):
        """Get group by ID"""
        return await self.grp.find_one({'group_id': group_id})

    async def get_all_groups(self):
        """Get all groups"""
        cursor = self.grp.find({})
        return await cursor.to_list(length=None)

    async def delete_group(self, group_id):
        """Delete group"""
        await self.grp.delete_one({'group_id': group_id})

    async def total_groups_count(self):
        """Count total groups"""
        return await self.grp.count_documents({})

    # ============ USER METHODS ============
    
    async def add_user(self, user_id):
        """Add user to database"""
        try:
            user_data = {
                'user_id': user_id,
                'points': 0,
                'referral_count': 0,
                'premium_expire': 0,
                'joined_at': int(time.time())
            }
            
            await self.usr.update_one(
                {'user_id': user_id},
                {'$setOnInsert': user_data},
                upsert=True
            )
            
            return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False

    async def get_user(self, user_id):
        """Get user data"""
        return await self.usr.find_one({'user_id': user_id})
    
    async def update_user(self, user_id, update_data):
        """🆕 Update user data with custom fields"""
        try:
            await self.usr.update_one(
                {'user_id': user_id},
                {'$set': update_data},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return False

    async def total_users_count(self):
        """Count total users"""
        return await self.usr.count_documents({})

    # ============ PREMIUM METHODS ============
    
    async def is_premium_user(self, user_id):
        """Check if user is premium"""
        try:
            user = await self.usr.find_one({'user_id': user_id})
            if user and user.get('premium_expire', 0) > int(time.time()):
                return True
            return False
        except Exception as e:
            logger.error(f"Error checking premium: {e}")
            return False

    async def get_premium_expire(self, user_id):
        """Get premium expiry time"""
        try:
            user = await self.usr.find_one({'user_id': user_id})
            return user.get('premium_expire', 0) if user else 0
        except Exception as e:
            logger.error(f"Error getting premium expire: {e}")
            return 0

    async def make_premium(self, user_id, expire_time):
        """Make user premium"""
        try:
            await self.usr.update_one(
                {'user_id': user_id},
                {'$set': {'premium_expire': expire_time}},
                upsert=True
            )
            
            return True
        except Exception as e:
            logger.error(f"Error making premium: {e}")
            return False

    # ============ REFERRAL/POINTS METHODS ============
    
    async def get_points(self, user_id):
        """Get user points"""
        try:
            user = await self.usr.find_one({'user_id': user_id})
            return user.get('points', 0) if user else 0
        except Exception as e:
            logger.error(f"Error getting points: {e}")
            return 0

    async def add_points(self, user_id, points):
        """Add points to user"""
        try:
            await self.usr.update_one(
                {'user_id': user_id},
                {'$inc': {'points': points}},
                upsert=True
            )
            
            return True
        except Exception as e:
            logger.error(f"Error adding points: {e}")
            return False

    async def deduct_points(self, user_id, points):
        """Deduct points from user"""
        try:
            await self.usr.update_one(
                {'user_id': user_id},
                {'$inc': {'points': -points}}
            )
            
            return True
        except Exception as e:
            logger.error(f"Error deducting points: {e}")
            return False

    async def get_referral_count(self, user_id):
        """Get user referral count"""
        try:
            user = await self.usr.find_one({'user_id': user_id})
            return user.get('referral_count', 0) if user else 0
        except Exception as e:
            logger.error(f"Error getting referral count: {e}")
            return 0

    async def increment_referral(self, user_id):
        """Increment user referral count"""
        try:
            await self.usr.update_one(
                {'user_id': user_id},
                {'$inc': {'referral_count': 1}},
                upsert=True
            )
            
            return True
        except Exception as e:
            logger.error(f"Error incrementing referral: {e}")
            return False
                        
