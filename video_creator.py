import os
from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip

def create_video(text, audio_path):
    os.makedirs("output", exist_ok=True)

    audio = AudioFileClip(audio_path)

    txt = TextClip(
        text,
        fontsize=60,
        color='white',
        size=(1000, None),
        method='caption'
    ).set_duration(audio.duration)

    video = CompositeVideoClip([txt.set_position("center")])
    video = video.set_audio(audio)

    output_path = "output/video.mp4"
    video.write_videofile(output_path, fps=24)

    return output_path
