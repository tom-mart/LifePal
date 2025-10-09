"""
Celery tasks for tool execution (async operations like YouTube downloads).
"""
from celery import shared_task
from django.contrib.auth import get_user_model
import logging
import tempfile
import os
from pathlib import Path
import json

logger = logging.getLogger(__name__)
User = get_user_model()


@shared_task
def download_youtube_audio_async(user_id: int, url: str, query: str = None):
    """
    Asynchronously download YouTube audio and convert to MP3.
    
    Args:
        user_id: User ID
        url: YouTube URL to download
        query: Optional search query (if URL was found via search)
    
    Returns:
        dict: Result with file information or error
    """
    try:
        import yt_dlp
        from files.utils import ToolFileHelper
        
        user = User.objects.get(id=user_id)
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Configure yt-dlp options for audio extraction
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'noprogress': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            
            # Download and extract audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Get the downloaded file path (will be .mp3 after post-processing)
                base_filename = ydl.prepare_filename(info)
                filename = os.path.splitext(base_filename)[0] + '.mp3'
                
                if not os.path.exists(filename):
                    raise Exception("Downloaded MP3 file not found")
                
                # Use ToolFileHelper to save to user's storage
                file_helper = ToolFileHelper(
                    user=user,
                    tool_name='download_youtube_audio',
                    tool_execution_id=None
                )
                
                # Save file
                user_file = file_helper.save_file(
                    file_path=Path(filename),
                    category='audio',
                    description=f"Audio from YouTube: {info.get('title', 'Unknown')}",
                    metadata={
                        'source': 'youtube',
                        'url': url,
                        'title': info.get('title'),
                        'duration': info.get('duration'),
                        'artist': info.get('artist') or info.get('uploader'),
                        'album': info.get('album'),
                        'uploader': info.get('uploader'),
                        'upload_date': info.get('upload_date'),
                        'view_count': info.get('view_count'),
                        'like_count': info.get('like_count'),
                        'format': 'mp3',
                        'bitrate': '192kbps',
                        'search_query': query
                    }
                )
                
                return {
                    'success': True,
                    'file_id': str(user_file.id),
                    'filename': user_file.original_filename,
                    'file_size': user_file.file_size,
                    'title': info.get('title'),
                    'artist': info.get('artist') or info.get('uploader'),
                    'duration': info.get('duration'),
                    'download_url': user_file.download_url,
                    'message': f"Successfully downloaded audio: {info.get('title')}"
                }
                
        finally:
            # Cleanup temp directory
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass
                
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {
            'success': False,
            'error': 'User not found',
            'message': 'User account not found'
        }
    except Exception as e:
        logger.error(f"Error downloading YouTube audio: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to download audio: {str(e)}"
        }


@shared_task
def download_youtube_video_async(user_id: int, url: str, query: str = None):
    """
    Asynchronously download YouTube video.
    
    Args:
        user_id: User ID
        url: YouTube URL to download
        query: Optional search query (if URL was found via search)
    
    Returns:
        dict: Result with file information or error
    """
    try:
        import yt_dlp
        from files.utils import ToolFileHelper
        
        user = User.objects.get(id=user_id)
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'noprogress': True,
                'merge_output_format': 'mp4',
            }
            
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Get the downloaded file path
                filename = ydl.prepare_filename(info)
                
                # If merged, the file might have .mp4 extension
                if not os.path.exists(filename):
                    base = os.path.splitext(filename)[0]
                    filename = f"{base}.mp4"
                
                if not os.path.exists(filename):
                    raise Exception("Downloaded file not found")
                
                # Use ToolFileHelper to save to user's storage
                file_helper = ToolFileHelper(
                    user=user,
                    tool_name='download_youtube_video',
                    tool_execution_id=None
                )
                
                # Save file
                user_file = file_helper.save_file(
                    file_path=Path(filename),
                    category='video',
                    description=f"YouTube video: {info.get('title', 'Unknown')}",
                    metadata={
                        'source': 'youtube',
                        'url': url,
                        'title': info.get('title'),
                        'duration': info.get('duration'),
                        'uploader': info.get('uploader'),
                        'upload_date': info.get('upload_date'),
                        'view_count': info.get('view_count'),
                        'like_count': info.get('like_count'),
                        'search_query': query
                    }
                )
                
                return {
                    'success': True,
                    'file_id': str(user_file.id),
                    'filename': user_file.original_filename,
                    'file_size': user_file.file_size,
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'download_url': user_file.download_url,
                    'message': f"Successfully downloaded: {info.get('title')}"
                }
                
        finally:
            # Cleanup temp directory
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except:
                pass
                
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {
            'success': False,
            'error': 'User not found',
            'message': 'User account not found'
        }
    except Exception as e:
        logger.error(f"Error downloading YouTube video: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'message': f"Failed to download video: {str(e)}"
        }


@shared_task
def search_youtube(query: str):
    """
    Search YouTube and return the best match.
    
    Args:
        query: Search query
    
    Returns:
        dict: Video information or None
    """
    try:
        import yt_dlp
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_results = ydl.extract_info(f"ytsearch1:{query}", download=False)
            
            if search_results and 'entries' in search_results and len(search_results['entries']) > 0:
                video = search_results['entries'][0]
                return {
                    'success': True,
                    'url': f"https://www.youtube.com/watch?v={video['id']}",
                    'title': video.get('title', 'Unknown'),
                    'duration': video.get('duration', 0),
                    'uploader': video.get('uploader', 'Unknown')
                }
        
        return {
            'success': False,
            'error': 'No results found',
            'message': f"Could not find any videos for: {query}"
        }
        
    except Exception as e:
        logger.error(f"Error searching YouTube: {str(e)}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'message': f"Search failed: {str(e)}"
        }
