# from typing import List
# from fastapi import APIRouter, Depends, File, Form, UploadFile, status
# from src.Shared.base.APIResponse import APIResponse
# from src.Shared.base import get_logger
# from src.Features.RealTimeAPI.Storage.CloudinaryService import CloudinaryService

# logger = get_logger(__name__)

# router = APIRouter(
#     tags=["Cloudinary"]
# )

# prefix="/api/v1/storage"

# @router.post(f"{prefix}/upload")
# async def upload_file(
#     file: UploadFile = File(...),
#     folder: str = Form(default="uploads"),
#     resource_type: str = Form(default="auto"),
#     service: CloudinaryService = Depends()
# ):
#     logger.info(f"Uploading file: {file.filename} to folder: {folder}")

#     file_content = await file.read()

#     result = service.upload_file(
#         file_content, 
#         folder=folder, 
#         resource_type=resource_type
#     )

#     return APIResponse(
#         message="Conversation retrieved successfully",
#         status_code=status.HTTP_200_OK,
#         data=result
#     )

# @router.post(f"{prefix}/upload/multiple")
# async def upload_multiple_files(
#     files: List[UploadFile] = File(...),
#     service: CloudinaryService = Depends()
# ):
#     list_result = []
#     for file in files:
#         file_content = await file.read()
#         result = service.upload_file(
#             file_content,
#             folder="uploads",
#             resource_type="auto"
#         )
#         list_result.append(result)

#     return APIResponse(
#         message="Files uploaded successfully",
#         status_code=status.HTTP_200_OK,
#         data=list_result
#     )