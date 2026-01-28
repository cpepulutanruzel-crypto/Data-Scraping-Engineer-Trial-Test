from _init_.Scrapping import DataScrapper
from ScrapperLogger import setup_logging


def main():
    log = setup_logging()
    test_url = "https://scraping-trial-test.vercel.app/search"
    text = "silver"
    log.info("Starting the process...")
    try:
        app = DataScrapper(test_url, text)
        print(app)
    except Exception as e:
        log.error(f"Main execution failed: {e}")
if __name__ == "__main__":
    main()


    