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
    if intensity < 0.1:
        # No sound: Blue color
        return (0, 0, 255)
    else:
        # Interpolated color between green and red based on intensity
        red = int(255 * (intensity - 0.1) / 0.9)
        green = int(255 * (1 - (intensity - 0.1) / 0.9))
        return (red, green, 0)

def make_frame(t, y, sr, rms_normalized, fps):
    fig, ax = plt.subplots(figsize=(10, 2))
    start = int(t * sr)
    end = int((t + 1 / fps) * sr)
    ax.plot(y[start:end])
    ax.axis('off')
    intensity_index = int(t * len(rms_normalized) / duration)
    intensity_index = min(intensity_index, len(rms_normalized) - 1)
    color = get_background_color(rms_normalized[intensity_index])
    fig.patch.set_facecolor(np.array(color) / 255)
    frame = mplfig_to_npimage(fig)
    plt.close(fig)
    return frame

audio_path = 'y2mate.com - Mrs GREEN APPLEナハトムジークOfficial Music Video.mp3'
y, sr, rms_normalized = analyze_audio(audio_path)
fps = 24
duration = len(y) / sr

video = VideoClip(lambda t: make_frame(t, y, sr, rms_normalized, fps), duration=duration)
audio = AudioFileClip(audio_path).subclip(0, duration)
video = video.set_audio(audio)
output_path = 'output_video.mp4'
video.write_videofile(output_path, fps=fps)
