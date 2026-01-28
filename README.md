Web Scraper & Captcha Bypass
Overview
A Selenium-based web scraper designed to extract table data and bypass audio-based captchas using AI-powered speech recognition.

🛠️ Prerequisites
Python 3.10+

FFmpeg: Required by pydub for audio manipulation.

Note: Ensure ffmpeg is placed in _ai_utils/bin or added to your system PATH.

Link : https://github.com/GyanD/codexffmpeg/releases/download/2026-01-26-git-fe0813d6e2/ffmpeg-2026-01-26-git-fe0813d6e2-full_build.7z

Chrome Browser: The scraper uses webdriver-manager to automatically handle driver compatibility.

Questions and Answers

Q1 : How to install dependencies ?

A1 : just type in terminal "pip install requirements.txt"

Q2 : How to run the script ?
Q2 : just run the "run.py"

Q3 : Libraries Used & Why:
    ------------------------------------ A3 -----------------------------------

    Selenium: To automate browser actions and handle dynamic website content.
    Webdriver-manager: To automatically manage Chrome driver updates.
    Pandas: To clean the scraped data and save it into CSV/Excel files.
    SpeechRecognition: To convert audio captchas into text using Google’s API.
    Pydub: To convert captcha audio files (MP3 to WAV) so the AI can read them.
    Requests: To download audio files quickly from the web.

    ------------------------------------ A3 -----------------------------------
Q4 : Assumptions and Limitations:

    ------------------------------------ A4 ----------------------------------------

                                Assumptions
    The computer has Python 3.10+ and Google Chrome installed.
    FFmpeg binaries are located in the "_ai_utils/bin" folder for audio processing.
    An internet connection is active to reach the Speech-to-Text API.
    The website provides an "audio" option for its captchas.

                                Limitations
    If the website changes its design (HTML IDs or Classes), the scraper will stop working until updated.
    Extremely distorted audio captchas might fail to transcribe correctly.
    The script could be blocked if the website detects too many requests from the same IP address.
    It only handles audio-based captchas; it cannot solve "click the image" captchas.
    ------------------------------------ A4 ---------------------------------------



CAPTCHA ACCURACY

NON HEADLESS : 80%

HEADLESS : 96%

# Data-Scraping-Engineer-Trial-Test
