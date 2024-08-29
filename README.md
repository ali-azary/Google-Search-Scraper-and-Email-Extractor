# Google-Search-Scraper-and-Email-Extractor

Building a Google Search Scraper with PyQt5 and Selenium
Introduction
In the world of data extraction, scraping web data has become increasingly important for various applications, from market research to personal data collection. This article outlines the development of a Google Search Scraper application using PyQt5, Selenium, and BeautifulSoup. The application facilitates the extraction of search results and email addresses from web pages.
Overview of the Application
The application is a desktop tool built using Python's PyQt5 library for the graphical user interface (GUI) and Selenium for automating web browser interactions. The core functionality includes querying Google Search, scraping URLs from the search results, and extracting email addresses from the collected URLs.
Key Components
1.	PyQt5 for GUI:
o	The graphical interface is built using PyQt5, featuring input fields for search queries and result count, along with text areas to display search results and extracted emails.
2.	Selenium for Web Interaction:
o	Selenium WebDriver automates Google searches and retrieves the HTML of the search results page. This approach leverages Chrome's headless mode to perform searches invisibly.
3.	BeautifulSoup for HTML Parsing:
o	BeautifulSoup is used to parse the HTML content and extract URLs from the search results page.
4.	Threading for Asynchronous Tasks:
o	PyQt5’s QThread is utilized to handle long-running operations such as web scraping and email extraction, ensuring the GUI remains responsive.
Implementation Details
GUI Development with PyQt5
The GUI of the application includes:
•	Search Query Input: A text field where users enter their search queries.
•	Number of Results Input: A text field to specify the number of search results to retrieve.
•	Output Text Areas: Two read-only text areas for displaying search results and extracted emails.
•	Action Button: A button to initiate the scraping process.
Web Scraping with Selenium
The WorkerThread class handles the Google search automation:
•	Initialization: The WebDriver is configured to operate in headless mode for efficiency.
•	Search Execution: Constructs the search URL and retrieves the HTML content.
•	URL Extraction: Uses BeautifulSoup to parse and extract URLs from the search result page.
Email Extraction
The EmailWorkerThread class processes the URLs:
•	Content Retrieval: Fetches the content of each URL.
•	Email Extraction: Uses regex to find email addresses, filtering out those associated with common file types to avoid false positives.
Code Snippets
1. WorkerThread for Google Search:
class WorkerThread(QThread):
    resultReady = pyqtSignal(str)
    def __init__(self, search_query, num_results, parent=None):
        super(WorkerThread, self).__init__(parent)
        self.search_query = search_query
        self.num_results = num_results

    def run(self):
        try:
            search_url = f"https://www.google.com/search?q={self.search_query}&num={self.num_results}#ip=1"
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(executable_path='path/to/chromedriver', options=chrome_options)
            driver.get(search_url)
            time.sleep(5)
            page_source = driver.page_source
            driver.quit()
            soup = BeautifulSoup(page_source, "html.parser")
            links = [link.get("href") for link in soup.find_all("a") if link.get("href").startswith('http')]
            self.resultReady.emit('\n'.join(links))
        except Exception as e:
            print("An error occurred:", e)
2. EmailWorkerThread for Email Extraction:
class EmailWorkerThread(QThread):
    emailsReady = pyqtSignal(str)
    def __init__(self, urls, parent=None):
        super(EmailWorkerThread, self).__init__(parent)
        self.urls = urls

    def run(self):
        all_emails = []
        for url in self.urls:
            emails = self.extract_content_and_emails(url)
            all_emails.extend(emails)
        self.emailsReady.emit(','.join(all_emails))

    def extract_content_and_emails(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', response.text)
                return emails
        except Exception as e:
            print('error trying to get emails: ' + str(e))
        return []

 
![image](https://github.com/user-attachments/assets/69fa8af0-7156-4092-a91f-3170d02da5a2)


Conclusion
The Google Search Scraper application is a practical tool for automating the extraction of URLs and emails from search results. By integrating PyQt5 for the user interface, Selenium for web interactions, and BeautifulSoup for HTML parsing, this application provides a streamlined approach to web data extraction. The use of threading ensures a responsive user experience, making it an effective solution for anyone looking to automate web scraping tasks.

