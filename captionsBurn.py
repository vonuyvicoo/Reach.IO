import re
import os
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont



def grpbin(arr, ind):
    index = 0
    masterArr = []
    currentArr = []
    for i in arr:
        if 0 <= index < len(arr):
            currentArr.append(arr[index])
        for x in range(1, ind):
            if 0 <= index + x < len(arr):
                currentArr.append(arr[index + x])
        index += ind
        if currentArr:
            masterArr.append(currentArr)
        currentArr = []
    return masterArr

# Parse VTT file to get words and their timestamps
def parse_vtt(file):
    with open(file, 'r') as f:
        content = f.read()

    pattern = r'(\d{2}:\d{2}:\d{02}\.\d{3}) --> (\d{2}:\d{2}:\d{02}\.\d{3})\n(.*)'
    matches = re.findall(pattern, content)

    captions = []
    for start, end, text in matches:
        captions.append({
            'start': start,
            'end': end,
            'text': text
        })

    return captions

# Function to convert timestamp to seconds
def timestamp_to_seconds(timestamp):
    h, m, s = map(float, timestamp.split(':'))
    return h * 3600 + m * 60 + s

# Function to create an image with highlighted text using PIL
def create_text_image(text, highlight_word, font_path, font_size, image_size):
    img = Image.new('RGBA', image_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, font_size)
    border_color = 'black'
    border_width = 2  # Thin border width

    # Wrap text to fit within image width
    def wrap_text(text, font, max_width):
        lines = []
        words = text.split()
        while words:
            line = ''
            while words and draw.textbbox((0, 0), line + words[0], font=font)[2] <= max_width:
                line += (words.pop(0) + ' ')
            lines.append(line.strip())
        return lines

    wrapped_lines = wrap_text(text, font, image_size[0] - 80)  # 20 pixels padding

    # Calculate text height and Y position
    text_height = sum(draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in wrapped_lines)
    y = ((image_size[1] - text_height) // 2) - 80

    # Draw text with line wrapping and border
    for line in wrapped_lines:
        # Calculate text width and position to center horizontally
        text_width = draw.textbbox((0, 0), line, font=font)[2] - draw.textbbox((0, 0), line, font=font)[0]
        x = (image_size[0] - text_width) // 2

        # Function to draw text with border
        def draw_text_with_border(position, text, font, text_color, border_color, border_width):
            x, y = position
            # Draw border by drawing text multiple times with a slight offset
            for dx in range(-border_width, border_width + 1):
                for dy in range(-border_width, border_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), text, font=font, fill=border_color)
            # Draw the actual text on top
            draw.text((x, y), text, font=font, fill=text_color)

        # Highlight the word if it is in the line
        if highlight_word:
            highlight_start = line.find(highlight_word)
            if highlight_start != -1:
                pre_highlight = line[:highlight_start]
                highlight = line[highlight_start:highlight_start + len(highlight_word)]
                post_highlight = line[highlight_start + len(highlight_word):]

                # Draw pre-highlight text with border
                draw_text_with_border((x, y), pre_highlight, font, 'white', border_color, border_width)
                highlight_x = x + draw.textbbox((0, 0), pre_highlight, font=font)[2] - draw.textbbox((0, 0), pre_highlight, font=font)[0]

                # Draw highlighted text with border
                draw_text_with_border((highlight_x, y), highlight, font, 'yellow', border_color, border_width)
                highlight_x += draw.textbbox((0, 0), highlight, font=font)[2] - draw.textbbox((0, 0), highlight, font=font)[0]

                # Draw post-highlight text with border
                draw_text_with_border((highlight_x, y), post_highlight, font, 'white', border_color, border_width)
            else:
                # Draw text with border
                draw_text_with_border((x, y), line, font, 'white', border_color, border_width)
        else:
            # Draw text with border
            draw_text_with_border((x, y), line, font, 'white', border_color, border_width)

        y += draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1]

    return img
# Create caption clips with highlighted word
def create_caption_clips(captions, font_path, video_width, video_height):
    clips = []
    words = [caption['text'] for caption in captions]
    chunkArr = grpbin(words, 4)

    contRepeater = 0
    temp_dir = 'temp'
    os.makedirs(temp_dir, exist_ok=True)

    for chunk in chunkArr:
        for word in chunk:
            contRepeater += 1
            try:
                highlight_word = captions[contRepeater - 1]['text'].replace(" ", "")
            except IndexError:
                highlight_word = ""
            display_text = ' '.join(chunk)

            # Create text image
            img = create_text_image(display_text, highlight_word, font_path, 60, (video_width, video_height))
            img_path = os.path.join(temp_dir, f'temp_caption_{contRepeater}.png')
            img.save(img_path)

            try:
                start_time = timestamp_to_seconds(captions[contRepeater - 1]['start'])
                end_time = timestamp_to_seconds(captions[contRepeater - 1]['end'])
            except IndexError:
                start_time = timestamp_to_seconds(captions[-1]['start'])
                end_time = timestamp_to_seconds(captions[-1]['end'])

            if start_time is None or end_time is None:
                continue  # Skip this iteration if timestamps are invalid

            # Ensure end_time is not less than start_time
            if end_time <= start_time:
                end_time = start_time + 1

            # Create ImageClip from the saved image
            text_clip = ImageClip(img_path).set_position(('center', 'center')).set_duration(end_time - start_time)
            clips.append(text_clip.set_start(start_time))

    return clips

# Main function to overlay captions onto video
def add_captions_to_video(video_file, output_file, captions, font_path, video_width, video_height):
    video = VideoFileClip(video_file)
    caption_clips = create_caption_clips(captions, font_path, video_width, video_height)

    final = CompositeVideoClip([video] + caption_clips)
    final.write_videofile(output_file, codec='mpeg4', audio_codec='aac')





# Add captions to video



def InitBurnCap(vtt, vid, out):
     # Define file paths and settings
    vtt_file = vtt #input
    video_file = vid #input
    output_file = out #output
    font_path = 'Poppins-ExtraBold.ttf'
    video_width = 607
    video_height = 1080
    # Parse VTT file

    captions = parse_vtt(vtt_file)
    add_captions_to_video(video_file, output_file, captions, font_path, video_width, video_height)