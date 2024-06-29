from flask import Flask, request, render_template, redirect, url_for
import librosa
import os

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
        try:
            file.save(file_path)
        except FileNotFoundError:
            return 'File not found. Please try again.'

        try:
            # Librosaを使ってBPMとダイナミクスを解析
            y, sr = librosa.load(file_path)
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

            # ダイナミクスの解析
            rms = librosa.feature.rms(y=y)[0]

            # ダイナミクスに基づいて背景色を決定するロジック
            def get_background_color(rms_value):
                if rms_value > 0.1:  # 適切な閾値に調整してください
                    return 'lightcoral'
                elif rms_value < 0.05:  # 適切な閾値に調整してください
                    return 'lightblue'
                else:
                    return 'white'

            background_colors = [get_background_color(value) for value in rms]

            # 結果を表示（簡単な例として背景色リストを表示）
            return f'BPM: {tempo}, Background Colors: {background_colors}'
        except FileNotFoundError:
            return 'File not found during processing. Please check the file path and try again.'

if __name__ == '__main__':
    app.run(debug=True)
