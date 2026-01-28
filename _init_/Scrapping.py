from .byPass import WeBDataExractor
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from concurrent.futures import ThreadPoolExecutor
from selenium.common.exceptions import WebDriverException, TimeoutException
import re
import time 
import pandas as pd 
import random

class TableScraper(WeBDataExractor):
    def __init__(self, url, query):
        super().__init__(url, query)
        self.all_data = []

    def start_process(self):
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            try:
                if self.driver:
                    self.driver.quit()
                
                if not self._fucntWebConfiguration():
                    continue

                status = self._clickCaptchaBox()
                if not status: 
                    continue

                if status == "CHALLENGE":
                    if not self._click_audio_button():
                        continue
                    
                    audio_url = self._get_audio_url()
                    if not (audio_url and self._force_download_(audio_url)):
                        continue

                    text = self._transcribe_audio("captcha_audio.mp3")
                    if not text or not self._submit_solution(text):
                        continue
                    
                    time.sleep(2)

                if self.perform_search():
                    return True
                
            except Exception as e:
                self._log_error(f"System error on attempt {attempt}: {e}")
                
            if attempt < max_attempts:
                self._log_error(f"Restarting from beginning (Attempt {attempt+1}/{max_attempts})...")
                time.sleep(random.uniform(3, 6))
            else:
                self._log_error("Max attempts reached. Failed to bypass.")
                if self.driver: self.driver.quit()
                return False
        return False

    def get_total_pages(self):
        try:
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tbody tr")))
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1) 
            xpath = "/html/body/div[1]/main/div/div[2]/div[1]/div[2]"
            element = self.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
            inner_text = element.text.strip()
            numbers = re.findall(r'\d+', inner_text)
            return int(numbers[-1]) if numbers else 1
        except WebDriverException:
            self._log_error("Browser crashed during pagination. Attempting to recover...")
            return 1
    
    def scrape_table(self):
        try:
            table = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 4:
                    row_data = {
                        "business_name": cells[0].text.strip(),
                        "registration_id": cells[1].text.strip(),
                        "status": cells[2].text.strip(),
                        "filing_date": cells[3].text.strip()
                    }
                    try:
                        row_data["source_url"] = row.find_element(By.TAG_NAME, "a").get_attribute("href")
                    except:
                        row_data["source_url"] = None
                    self.all_data.append(row_data)
            return True
        except Exception as e:
            self._log_error(f"Error scraping table: {e}")
            return False

    def next_page(self):
        try:
            xpath = "/html/body/div[1]/main/div/div[2]/div[3]/button[2]"
            next_btn = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            if next_btn.get_attribute("disabled"):
                return False
            old_data = self.driver.find_element(By.XPATH, "//table/tbody/tr[1]").text
            time.sleep(random.uniform(1, 2))
            self.driver.execute_script("arguments[0].scrollIntoView();", next_btn)
            next_btn.click()
            timeout = 10
            start = time.time()
            while time.time() - start < timeout:
                try:
                    new_data = self.driver.find_element(By.XPATH, "//table/tbody/tr[1]").text
                    if new_data != old_data:
                        time.sleep(1)
                        return True
                except:
                    pass
                time.sleep(0.5)
            return False
        except Exception as e:
            self._log_error(f"Pagination error: {e}")
            return False

    def _scrape_link_chunk(self, chunk):
        temp_bot = WeBDataExractor(self.url, self.query)
        if not temp_bot._fucntWebConfiguration():
            return
        try:
            for row in chunk:
                url = row.get("source_url")
                if not url: continue
                try:
                    temp_bot.driver.get(url)
                    temp_bot.wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div/div[6]/div[2]")))
                    row["agent_name"] = temp_bot.driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div[6]/div[2]").text.strip()
                    row["agent_address"] = temp_bot.driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div[4]/div[2]").text.strip()
                    row["agent_email"] = temp_bot.driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div[6]/div[4]/code").text.strip()
                except Exception as e:
                    self._log_error(f"Failed to collect inner data for {row['business_name']}: {e}")
                    row["agent_name"] = "N/A"
                    row["agent_address"] = "N/A"
                    row["agent_email"] = "N/A"
        finally:
            temp_bot.driver.quit()

    def parallel_scrape_details(self, thread_count=4):
        if not self.all_data:
            self._log_error("No data available for deep scraping.")
            return
        chunk_size = (len(self.all_data) + thread_count - 1) // thread_count
        chunks = [self.all_data[i:i + chunk_size] for i in range(0, len(self.all_data), chunk_size)]
        with ThreadPoolExecutor(max_workers=thread_count) as executor:
            executor.map(self._scrape_link_chunk, chunks)

    def save_final_data(self, filename="final_business_audit.csv"):
        if not self.all_data:
            self._log_error("No data to save.")
            return
        df = pd.DataFrame(self.all_data)
        column_order = ["business_name", "registration_id", "status", "filing_date", "agent_name", "agent_address", "agent_email"]
        for col in column_order:
            if col not in df.columns: df[col] = "N/A"
        df[column_order].to_csv(filename, index=False, quoting=1, encoding='utf-8')

    save_to_csv = save_final_data

def DataScrapper(test_url, text):
    bot = TableScraper(test_url, text)
    if bot.start_process():
        print("[INIT]: Collecting Data....")
        total_pages = bot.get_total_pages()
        for p in range(1, total_pages + 1):
            bot.scrape_table()
            if p < total_pages:
                if not bot.next_page(): break
        bot.parallel_scrape_details(thread_count=5)
        print("[INIT]: Saving Data....")
        bot.save_to_csv("Output.csv")
        return "[FINISHED]: Scrapping Success!"
    else:
        
        print("[ERROR] Initialization failed.")