"""
import pyttsx3
engine = pyttsx3.init()
engine.say("I will speak this text")
engine.runAndWait()

"""
from gtts import gTTS
from audiostretchy.stretch import stretch_audio



class TTSEngine: 
	def textToSpeech(TextInput, FileName):
		tts = gTTS(TextInput, lang='en', tld='com.au')
		tts.save(FileName)

		TTSEngine.SpeedUp(FileName)
	def SpeedUp(file):
		stretch_audio(file, file, ratio=0.95)


