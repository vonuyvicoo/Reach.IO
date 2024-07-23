import warnings
warnings.simplefilter(action='ignore')

import praw
import pandas as pd
import tts
import random
from pytubefix import YouTube
from pytubefix.cli import on_progress
import uuid
from mutagen.mp3 import MP3
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import moviepy.editor as mpy
from moviepy.video.fx.all import crop
import os
from moviepy.editor import *
import autocap
import captionsBurn
from tiktok_uploader.upload import upload_video
import upload
reddit_read_only = praw.Reddit(client_id="5Im5FyaAFyIPpldPQhW8KQ",         # your client id
                               client_secret="DIVVNKdd1M3Zj9PNa8XktsDHHPFXxg",      # your client secret
                               user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")        # your user agent
 
 
subreddit = reddit_read_only.subreddit("scarystories")
 
# Display the name of the Subreddit
"""
print("Display Name:", subreddit.display_name)
 
# Display the title of the Subreddit
print("Title:", subreddit.title)
 
# Display the description of the Subreddit
print("Description:", subreddit.description)
"""
class MainEngine:
	def InitEngine():
		for submission in subreddit.top(time_filter="day", limit=20): #timefilter all
			wordcount = len(submission.selftext.split(" "))
			story = submission.selftext.upper()
			print(wordcount)
			if(wordcount > 600):
				continue
				#story = ' '.join(story.split(" ")[0:300])
				
			#generate filenames and ID
			id = "files/videos/" + str(uuid.uuid4()) + ".mp4"
			audio_fn = id.replace(".mp4", ".mp3").replace("videos", "audio")

			tts.TTSEngine.textToSpeech(story, audio_fn)
			VideoDownload = MainEngine.GetVideo(id)

			audio = MP3(audio_fn)
			print("TRIMMING VIDEO")

		

			##TRIM VIDEO--------------------------------------------------->
			trimVideoFN = id.replace("videos", "proc_videos")
			duration = audio.info.length
			ffmpeg_extract_subclip(id, 0, duration, targetname=trimVideoFN)
			#-------------------------------------------------------------->
			# delete original video after trim, before crop
			os.remove(id)

			##CROP VIDEO--------------------------------------------------->
			cropVideoFN = id.replace("videos", "crop_videos")
			# add audio
			audioclip = mpy.AudioFileClip(audio_fn)
			
			


			clip = mpy.VideoFileClip(trimVideoFN)
			(w, h) = clip.size

			crop_width = h * 9/16

			x1, x2 = (w - crop_width)//2, (w+crop_width)//2
			y1, y2 = 0, h
			cropped_clip = crop(clip, x1=x1, y1=y1, x2=x2, y2=y2)

			new_audioclip = mpy.CompositeAudioClip([audioclip])
			cropped_clip.audio = new_audioclip
			cropped_clip.write_videofile(cropVideoFN, codec='mpeg4', audio_codec='aac')
			#-------------------------------------------------------------->
			#print(VideoDownload)
			autocap.AutoCap(cropVideoFN, id.replace("mp4", "vtt").replace("videos", "vtt"))

			vttFile = id.replace("mp4", "vtt").replace("videos", "vtt")
			captionsBurn.InitBurnCap(vttFile, cropVideoFN, cropVideoFN.replace("crop_videos", "output"))

			#upload to TIKTOK
			outputFN = cropVideoFN.replace("crop_videos", "output")
			#upload.UploadInstance(outputFN)

	def GetVideo(id):
		with open("videos.txt", "r") as video:
			lineArr = video.readlines()
			ArrIndex = random.randint(0,len(lineArr)-1)

			url = lineArr[ArrIndex]

 
			yt = YouTube(url)
			print(yt.title)
			
			ys = yt.streams.filter(res="1080p").first()
			ys.download(filename=id)

			return id
