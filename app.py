from flask import Flask, request, render_template, send_from_directory
import librosa
import os
import numpy as np

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ディレクトリが存在しない場合は作成する
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def upload_file():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Librosaを使ってBPMとダイナミクスを解析
        y, sr = librosa.load(file_path)
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)

        # ダイナミクスの解析
        rms = librosa.feature.rms(y=y)[0]

        # 背景色の変化ポイントを計算
        color_changes = [get_background_color(value) for value in rms]

        # リアルタイムのタイムスタンプを生成
        duration = librosa.get_duration(y=y, sr=sr)
        timestamps = np.linspace(0, duration, len(color_changes))

        return render_template('player.html', file_path=file_path, color_changes=color_changes, timestamps=timestamps)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def get_background_color(rms_value):
    if rms_value > 0.1:  # 適切な閾値に調整してください
        return 'lightcoral'
    elif rms_value < 0.05:  # 適切な閾値に調整してください
        return 'lightblue'
    else:
        return 'white'

if __name__ == '__main__':
    app.run(debug=True)
