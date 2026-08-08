"""
uploader.py - رفع الفيديو النهائي لـ YouTube كـ long-form video (ماشي
Short)، عبر OAuth refresh token (نفس منطق المشروع الأصلي).
"""
import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from src.config import Config
from src.logger import Logger

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


class YouTubeUploader:
    def __init__(self):
        self.service = None

    def get_authenticated_service(self):
        creds = Credentials(
            token=None,
            refresh_token=Config.YOUTUBE_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=Config.YOUTUBE_CLIENT_ID,
            client_secret=Config.YOUTUBE_CLIENT_SECRET,
            scopes=SCOPES,
        )
        self.service = build("youtube", "v3", credentials=creds)
        return self.service

    def upload_video(self, video_path, title, description, tags=None, category_id="27"):
        """
        category_id=27 -> "Education" (الأنسب لتوتوريالات البرمجة).
        يرجّع video_id أو None.
        """
        if not self.service:
            self.get_authenticated_service()

        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tags or ["programming", "coding", "tutorial"],
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": Config.UPLOAD_PRIVACY,
                "selfDeclaredMadeForKids": False,
            },
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")

        try:
            request = self.service.videos().insert(
                part="snippet,status", body=body, media_body=media
            )
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    Logger.info(f"Upload progress: {int(status.progress() * 100)}%")

            video_id = response.get("id")
            return video_id

        except Exception as e:
            Logger.error(f"YouTube upload failed: {e}")
            return None
