import collections.abc
#hyper needs the four following aliases to be done manually.
collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping
import whisper
import ffmpeg
import os
import tempfile

def extract_audio_from_video(video_path):
    audio_path = tempfile.mktemp(suffix='.wav')
    try:
        ffmpeg.input(video_path).output(audio_path).run(overwrite_output=True)
    except ffmpeg.Error as e:
        print(f"An error occurred while extracting audio: {e}")
        raise
    return audio_path

def generate_vtt_captions(audio_path):
    model = whisper.load_model("base")  # or "small", "medium", "large" depending on your needs
    result = model.transcribe(audio_path, word_timestamps=True)

    vtt_captions = []
    for segment in result['segments']:
        for word_info in segment['words']:
            start_time = word_info['start']
            end_time = word_info['end']
            word = word_info['word'].upper()
            vtt_captions.append((start_time, end_time, word))
    
    return vtt_captions

def write_vtt_file(captions, output_vtt_path):
    with open(output_vtt_path, 'w') as file:
        file.write("WEBVTT\n\n")
        for start_time, end_time, word in captions:
            start_time_str = f"{int(start_time // 3600):02}:{int(start_time % 3600 // 60):02}:{int(start_time % 60):02}.{int(start_time * 1000 % 1000):03}"
            end_time_str = f"{int(end_time // 3600):02}:{int(end_time % 3600 // 60):02}:{int(end_time % 60):02}.{int(end_time * 1000 % 1000):03}"
            file.write(f"{start_time_str} --> {end_time_str}\n")
            file.write(f"{word}\n\n")

def AutoCap(video_path, output_vtt_path):
    audio_path = extract_audio_from_video(video_path)
    captions = generate_vtt_captions(audio_path)
    write_vtt_file(captions, output_vtt_path)
    os.remove(audio_path)
    print(f"Captions saved to {output_vtt_path}")


#video_path = "files/crop_videos/d5bb0676-15eb-428b-a697-5a865b2cce72.mp4"  # Replace with your video file path
#output_vtt_path = "captions.vtt"  # Replace with desired output file path
#AutoCap(video_path, output_vtt_path)
