# main.py
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from tensorflow.keras.preprocessing import image
from keras.models import load_model
import numpy as np
import shutil
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static") 
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
templates = Jinja2Templates(directory="templates")

# Load your trained model
model = load_model("Model.h5")
labels = ['Daisy', 'Dandelion', 'Rose', 'Sunflower', 'Tulip']  # แก้ตามคลาสจริงของคุณ

@app.get("/", response_class=HTMLResponse)
def form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, file: UploadFile = File(...)):
    filepath = f"uploads/{file.filename}"
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    img = image.load_img(filepath, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0

    prediction = model.predict(img_array)[0]
    predicted_index = np.argmax(prediction)
    predicted_class = labels[predicted_index]
    confidence = prediction[predicted_index] * 100
    result_text = f"{predicted_class} ({confidence:.2f}%)"

    return templates.TemplateResponse("index.html", {
        "request": request,
        "result": result_text,
        "image_path": f"/uploads/{file.filename}"
    })
