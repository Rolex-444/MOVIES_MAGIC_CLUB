from aiohttp import web
from pyrogram import Client
from info import BOT_TOKEN, API_ID, API_HASH, BIN_CHANNEL
from database.database import Database
import logging
import base64

logger = logging.getLogger(__name__)
db = Database()

class StreamServer:
    def __init__(self, client: Client):
        self.client = client
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Setup web server routes"""
        self.app.router.add_get('/download/{file_hash}', self.download_file)
        self.app.router.add_get('/watch/{file_hash}', self.watch_file)
        self.app.router.add_get('/health', self.health)
    
    async def download_file(self, request):
        """Download file endpoint"""
        file_hash = request.match_info['file_hash']
        logger.info(f"📥 Download request: {file_hash}")
        
        try:
            file_data = await db.get_stream_file(file_hash)
            
            if not file_data:
                return web.Response(text="File not found", status=404)
            
            message_id = file_data.get('message_id')
            
            # Get file from BIN_CHANNEL
            message = await self.client.get_messages(BIN_CHANNEL, message_id)
            
            if message.document:
                file = await self.client.download_media(message, in_memory=True)
                
                return web.Response(
                    body=file,
                    headers={
                        'Content-Disposition': 'attachment',
                        'Content-Type': 'application/octet-stream'
                    }
                )
            
            return web.Response(text="Invalid file type", status=400)
            
        except Exception as e:
            logger.error(f"Download error: {e}")
            return web.Response(text=f"Error: {str(e)}", status=500)
    
    async def watch_file(self, request):
        """Stream file endpoint"""
        file_hash = request.match_info['file_hash']
        logger.info(f"🎬 Watch request: {file_hash}")
        
        try:
            file_data = await db.get_stream_file(file_hash)
            
            if not file_data:
                return web.Response(text="File not found", status=404)
            
            message_id = file_data.get('message_id')
            
            # Get file from BIN_CHANNEL
            message = await self.client.get_messages(BIN_CHANNEL, message_id)
            
            if message.video:
                file = await self.client.download_media(message, in_memory=True)
                
                return web.Response(
                    body=file,
                    headers={
                        'Content-Type': 'video/mp4',
                        'Accept-Ranges': 'bytes',
                        'Content-Disposition': 'inline'
                    }
                )
            
            elif message.document:
                file = await self.client.download_media(message, in_memory=True)
                
                return web.Response(
                    body=file,
                    headers={
                        'Content-Type': 'application/octet-stream',
                        'Content-Disposition': 'inline'
                    }
                )
            
            return web.Response(text="Unsupported file type", status=400)
            
        except Exception as e:
            logger.error(f"Stream error: {e}")
            return web.Response(text=f"Error: {str(e)}", status=500)
    
    async def health(self, request):
        """Health check endpoint"""
        return web.Response(text="OK", status=200)
    
    async def start(self, host='0.0.0.0', port=8080):
        """Start web server"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        logger.info(f"✅ Stream server started on {host}:{port}")
        return runner
