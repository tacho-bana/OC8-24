from flask import Flask, request, redirect, url_for, send_from_directory, render_template
import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
from moviepy.editor import ImageClip, concatenate_videoclips

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

# フォルダの作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        process_file(filepath, file.filename)
        return redirect(url_for('processed_file', filename=file.filename))
    return redirect(request.url)

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
        plt.savefig(f'{app.config["PROCESSED_FOLDER"]}/frame_{i:04d}.png')
    
    image_clips = [ImageClip(f'{app.config["PROCESSED_FOLDER"]}/frame_{i:04d}.png').set_duration(times[1] - times[0]) for i in range(len(colors))]
    video = concatenate_videoclips(image_clips, method="compose")
    video.write_videofile(f'{app.config["PROCESSED_FOLDER"]}/{filename}.mp4', fps=24)

@app.route('/processed/<filename>')
def processed_file(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename + '.mp4')

if __name__ == '__main__':
    app.run(debug=True)
