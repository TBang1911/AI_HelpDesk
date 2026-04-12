import os
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url
from dotenv import load_dotenv

load_dotenv()

class CloudinaryConfig:
    def __init__(self):
        self.cloudinary_url = os.getenv("CLOUDINARY_URL")

        if not self.cloudinary_url:
            raise ValueError("Thiếu cấu hình Cloudinary. Vui lòng cung cấp CLOUDINARY_URL")

        self.config = cloudinary.config(
            cloudinary_url=self.cloudinary_url, 
            secure=True
        )

    def cloudinary(self):
        return cloudinary