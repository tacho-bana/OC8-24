from flask import Flask, render_template, request
import librosa
import numpy as np

app = Flask(__name__)

def analyze_audio(file_path):
    y, sr = librosa.load(file_path)
    # Calculate the root-mean-square (RMS) energy for each frame
    rms = librosa.feature.rms(y=y)[0]
    # Normalize the RMS values to [0, 1]
    rms_normalized = (rms - np.min(rms)) / (np.max(rms) - np.min(rms))
    return rms_normalized.tolist()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        file_path = 'uploaded_audio.wav'
        file.save(file_path)
        rms_data = analyze_audio(file_path)
        return {'rms_data': rms_data}

if __name__ == '__main__':
    app.run(debug=True)
