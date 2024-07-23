from tiktok_uploader.upload import upload_video

def UploadInstance(file):
	upload_video(file, 'Follow for more scary stories', 'accounts/Cookies.txt', headless=True)
