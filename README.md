
# Welcome to Reach.IO

Reach.IO is an open source social media content engine. It scrapes data from Reddit, and other forums with popular threads.

Scraped data are then converted to audio with TTS and re-subtitled using OpenAI whisper. Once a VTT file is generated, Python syncs the VTT file with a random video from YouTube.

All outputs are placed at ```files/output``` folder.

Documentation to be added soon.


## Usage

```bash
python main.py
```


## Installation

Clone the project

```bash
  git clone https://github.com/vonuyvicoo/Reach.IO.git
  cd Reach.IO
  pip install -r requirements.txt
```
    
