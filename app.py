from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import ImageClip, concatenate_videoclips
import aiofiles

app = FastAPI()

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if file.content_type not in ["audio/mpeg", "audio/wav"]:
        raise HTTPException(status_code=400, detail="Invalid file type. Only MP3 and WAV files are allowed.")
    
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    process_file(file_path, file.filename)
    return {"filename": file.filename}

def process_file(filepath, filename):
    y, sr = librosa.load(filepath)
    S, phase = librosa.magphase(librosa.stft(y))
    rms = librosa.feature.rms(S=S)
    frames = range(len(rms[0]))
    times = librosa.frames_to_time(frames, sr=sr)
    colors = [plt.cm.viridis(x) for x in rms[0] / max(rms[0])]
    
    fig, ax = plt.subplots(figsize=(10, 2))
    for i, color in enumerate(colors):
        ax.set_facecolor(color)
        plt.title(f'Time: {times[i]:.2f}s')
        plt.axis('off')
        plt.savefig(f'{PROCESSED_FOLDER}/frame_{i:04d}.png')
    
    image_clips = [ImageClip(f'{PROCESSED_FOLDER}/frame_{i:04d}.png').set_duration(times[1] - times[0]) for i in range(len(colors))]
    video = concatenate_videoclips(image_clips, method="compose")
    video.write_videofile(f'{PROCESSED_FOLDER}/{filename}.mp4', fps=24)

@app.get("/processed/{filename}")
async def processed_file(filename: str):
    file_path = os.path.join(PROCESSED_FOLDER, filename + ".mp4")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
