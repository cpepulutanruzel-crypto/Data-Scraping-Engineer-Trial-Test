from _init_.Scrapping import DataScrapper

def main():
    # https://www.google.com/recaptcha/api2/demo
    # "https://scraping-trial-test.vercel.app/search"
    test_url = "https://scraping-trial-test.vercel.app/search"
    text = "silver"
     
    print("[START]: Starting the process...")
    # 1. Initialize the bot
    app = DataScrapper(test_url, text)
    print(app)
   
    
if __name__ == "__main__":
    main()



    