import shutil
from importlib.resources import read_binary

from fastapi import FastAPI, File, UploadFile
from pathlib import Path
import uvicorn
import uuid
from PIL import Image, UnidentifiedImageError
from python_multipart import multipart
import os
from pydantic import BaseModel

app = FastAPI()

MAX_IMAGE_SIZE = 5*1024*1024
BASE_DIR = Path(__file__).parent.parent.parent.parent
SUPPORTED_FORMATS = {'.jpg', '.png', '.gif'}
if not os.path.exists(os.path.join(BASE_DIR,'images\\')):
    os.mkdir(os.path.join(BASE_DIR,'images\\'))
IMAGE_DIR = os.path.join(BASE_DIR,'images\\')

class Post(BaseModel):
    image:str


@app.get('/home')
async def get_home():
    return "hello world"

@app.get('/upload/images')
async def get_home():
    image_list = []
    for path in Path.iterdir(Path(IMAGE_DIR)):
        image_list.append(path)
    return image_list

@app.post('/upload')
async def create_upload_image(file: UploadFile = File(...)):
    if file.size > MAX_IMAGE_SIZE:
        return {"error": "Image must be less than 1MB"}
    image_full_name = file.filename if file.filename else "uploaded_image"
    image_name = os.path.splitext(image_full_name)[0].lower()
    image_extension = os.path.splitext(image_full_name)[1].lower()
    if image_extension not in SUPPORTED_FORMATS:
        return {"error": f"Invalid image type, gpj, png, gif supported only"}
    image_db_name = f"{image_name}_{uuid.uuid4()}{image_extension}"
    try:
        img_file = Image.open(file.file,"r")
        img_file.verify()
    except UnidentifiedImageError:
        return f"bad image file"
    with open(f"{IMAGE_DIR}{image_db_name}","wb") as img:
        file.file.seek(0)
        img.write(file.file.read())
    return f"{IMAGE_DIR}/{image_db_name}"

@app.delete('/upload/{img_url}')
async def delete_uploaded_image(img_url):
    image_path = os.path.join(IMAGE_DIR,img_url)
    if Path(image_path) in Path.iterdir(Path(IMAGE_DIR)):
        try:
            os.remove(Path(image_path))
        except FileNotFoundError:
            return {f"Image not found"}
    else:
        return {f"Image not found"}
    return {"Image successfully deleted"}