import os

BASE_DIR = os.getcwd()
BIN_PATH = os.path.join(BASE_DIR, "_ai_utils", "bin")
os.environ["PATH"] += os.pathsep + BIN_PATH

import requests
import speech_recognition as sr
import time
import random
from datetime import datetime
from pydub import AudioSegment
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager

class WeBDataExractor:
    def __init__(self, url, query):
        self.url = url
        self.query = query
        self.options = webdriver.ChromeOptions()
        self.driver = None
        self.wait = None
        self.download_path = None

    def _log_error(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_entry = f"[{timestamp}] [ERROR] {message}\n"
        print(f"[ERROR] {message}")
        with open("Error_logs.txt", "a", encoding="utf-8") as f:
            f.write(error_entry)

    def _fucntWebConfiguration(self):
        try:
            self.download_path = os.path.abspath(r"_init_\captcha_downloads")
            if not os.path.exists(self.download_path):
                os.makedirs(self.download_path)
            self.options.add_argument("--headless=new")
            self.options.add_argument("--window-size=1920,1080")
            self.options.add_argument("--disable-blink-features=AutomationControlled")
            self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
            self.options.add_experimental_option('useAutomationExtension', False)
            self.options.add_argument("--no-sandbox")
            self.options.add_argument("--disable-dev-shm-usage")
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=self.options)
            self.wait = WebDriverWait(self.driver, 20)
            self.driver.execute_cdp_cmd("Page.setDownloadBehavior", {
                "behavior": "allow", 
                "downloadPath": self.download_path
            })
            return True
        except Exception as e:
            self._log_error(f"Config failed: {e}")
            return False

    def _clickCaptchaBox(self):
        try:
            self.driver.get(self.url)
            time.sleep(random.uniform(2, 4)) 
            recaptcha_frame = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[title*="reCAPTCHA"]')))
            self.driver.switch_to.frame(recaptcha_frame)
            button = self.wait.until(EC.element_to_be_clickable((By.ID, "recaptcha-anchor")))
            ActionChains(self.driver).move_to_element(button).pause(random.uniform(0.5, 1.0)).click().perform()
            time.sleep(2)
            status = button.get_attribute("aria-checked")
            if status == "true": 
                print("[SUCCESS]: Captcha bypass")
                return "SOLVED"
            return "CHALLENGE"
        except Exception as e:
            self._log_error(f"Captcha box click failed: {e}")
            return False
        finally:
            self.driver.switch_to.default_content()

    def _click_audio_button(self):
        try:
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[contains(@src, 'bframe')]")))
            audio_button = self.wait.until(EC.element_to_be_clickable((By.ID, "recaptcha-audio-button")))
            time.sleep(random.uniform(2, 3))
            ActionChains(self.driver).move_to_element(audio_button).pause(random.uniform(0.5, 1.0)).click().perform()
            return True
        except Exception as e:
            self._log_error(f"Audio button click failed: {e}")
            return False

    def _get_audio_url(self):
        try:
            download_link = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.rc-audiochallenge-tdownload-link')))
            return download_link.get_attribute('href')
        except Exception as e:
            if "automated queries" in self.driver.page_source:
                self._log_error("BLOCKED: Google detected the bot.")
            else:
                self._log_error(f"URL retrieval failed: {e}")
            return None

    def _force_download_(self, audio_url):
        try:
            path_to_mp3 = os.path.join(self.download_path, "captcha_audio.mp3")
            if os.path.exists(path_to_mp3): os.remove(path_to_mp3)
            session = requests.Session()
            for cookie in self.driver.get_cookies(): session.cookies.set(cookie['name'], cookie['value'])
            headers = {"User-Agent": self.driver.execute_script("return navigator.userAgent;")}
            response = session.get(audio_url, headers=headers, timeout=10)
            if response.status_code == 200:
                with open(path_to_mp3, 'wb') as f: f.write(response.content)
                if os.path.exists(path_to_mp3) and os.path.getsize(path_to_mp3) > 500: return True
            self._log_error(f"Download failed status: {response.status_code}")
            return False
        except Exception as e:
            self._log_error(f"Direct download error: {e}")
            return False

    def _transcribe_audio(self, mp3_filename):
        path_to_mp3 = os.path.join(self.download_path, mp3_filename)
        path_to_wav = os.path.join(self.download_path, "transformed.wav")
        try:
            timeout = 15
            while timeout > 0:
                if os.path.exists(path_to_mp3) and os.path.getsize(path_to_mp3) > 1000: break
                time.sleep(1); timeout -= 1
            if timeout == 0:
                self._log_error(f"File not found after 15s at {path_to_mp3}")
                return None
            audio = AudioSegment.from_mp3(path_to_mp3)
            audio.export(path_to_wav, format="wav")
            recognizer = sr.Recognizer()
            with sr.AudioFile(path_to_wav) as source:
                return recognizer.recognize_google(recognizer.record(source))
        except Exception as e:
            self._log_error(f"System error during processing: {e}")
            raise e
        finally:
            if os.path.exists(path_to_mp3): os.remove(path_to_mp3)
            if os.path.exists(path_to_wav): os.remove(path_to_wav)

    def _submit_solution(self, text):
        try:
            self.driver.switch_to.default_content()
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[contains(@src, 'bframe')]")))
            input_field = self.wait.until(EC.element_to_be_clickable((By.ID, "audio-response")))
            input_field.click()
            print("[INIT]: Auto Captcha execute....")
            for char in text:
                input_field.send_keys(char)
       
                time.sleep(random.uniform(0.1, 0.3))
            verify_button = self.driver.find_element(By.ID, "recaptcha-verify-button")
            ActionChains(self.driver).move_to_element(verify_button).click().perform()
            time.sleep(4)
            print("[SUCCESS]: Challenge passed!")
            return True
        except Exception as e:
            self._log_error(f"Submit solution failed: {e}")
            return False
        finally:
            self.driver.switch_to.default_content()

    def perform_search(self):
        try:
            search_input = self.wait.until(EC.element_to_be_clickable((By.ID, "q")))
            search_input.clear()
            for char in self.query:
                search_input.send_keys(char)
                time.sleep(random.uniform(0.1, 0.2))
            btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn")))
            ActionChains(self.driver).move_to_element(btn).click().perform()
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))
            return True
        except Exception as e:
            self._log_error(f"Search failed: {e}")
            return False