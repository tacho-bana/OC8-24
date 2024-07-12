import numpy as np
import librosa
import matplotlib.pyplot as plt
from moviepy.editor import VideoClip, AudioFileClip
from moviepy.video.io.bindings import mplfig_to_npimage

def analyze_audio(file_path):
    y, sr = librosa.load(file_path)
    rms = librosa.feature.rms(y=y)[0]
    rms_normalized = (rms - np.min(rms)) / (np.max(rms) - np.min(rms))
    return y, sr, rms_normalized

def get_background_color(intensity):
    red = int(255 * intensity)
    green = int(255 * (1 - intensity))
    return (red, green, 0)

def make_frame(t, y, sr, rms_normalized, fps):
    fig, ax = plt.subplots(figsize=(10, 2))
    start = int(t * sr)
    end = int((t + 1 / fps) * sr)
    ax.plot(y[start:end])
    ax.axis('off')
    intensity_index = int(t * fps / len(rms_normalized) * len(rms_normalized))
    color = get_background_color(rms_normalized[intensity_index])
    fig.patch.set_facecolor(np.array(color) / 255)
    frame = mplfig_to_npimage(fig)
    plt.close(fig)
    return frame

audio_path = '/Users/tachibananoyushou/OC8-24/mirai-demo-HardRock.mp3'
y, sr, rms_normalized = analyze_audio(audio_path)
fps = 24
duration = len(y) / sr

video = VideoClip(lambda t: make_frame(t, y, sr, rms_normalized, fps), duration=duration)
audio = AudioFileClip(audio_path)
video = video.set_audio(audio)
output_path = 'output_video.mp4'
video.write_videofile(output_path, fps=fps)
