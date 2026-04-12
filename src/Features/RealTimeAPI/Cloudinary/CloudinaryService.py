# from typing import Optional
# from src.Features.RealTimeAPI.Storage.CloudinaryConfig import CloudinaryConfig
# from src.Shared.base import get_logger

# logger = get_logger(__name__)

# class CloudinaryService:
#     def __init__(self):
#         self.cloudinary_config = CloudinaryConfig()
#         self.cloudinary = self.cloudinary_config.cloudinary()
#         logger.info("CloudinaryService initialized successfully")

#     def upload_file(
#         self, 
#         file_path: str, 
#         folder: str = "uploads", 
#         resource_type: str = "auto"
#     ):
#         try:
#             result = self.cloudinary.uploader.upload(
#                 file_path, 
#                 folder=folder, 
#                 resource_type=resource_type
#             )

#             return {
#                 "url": result["secure_url"],
#                 "public_id": result["public_id"]
#             }
#         except Exception as e:
#             logger.error(f"Error uploading file from URL: {str(e)}")
#         pass

#     # def delete_file(
#     #     self,
#     #     public_id: str, 
#     #     resource_type: str = "auto",
#     #     invalidate: bool = True
#     # ):
#     #     pass