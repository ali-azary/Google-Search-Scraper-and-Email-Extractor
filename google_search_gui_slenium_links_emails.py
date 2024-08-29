import sys
import re
import requests
from readability import Document
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QTextEdit, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from tqdm import tqdm

FILE_EXTENSIONS = ['.jpg', '.png', '.gif', '.bmp', '.tiff', '.ico', '.jfif',
                   '.webp', '.mp3', '.wav', '.ogg', '.flac', '.aac', '.wma',
                   '.mp4', '.avi', '.wmv', '.mov', '.flv', '.mkv', '.pdf', '.doc',
                   '.docx', '.xls', '.xlsx', '.ppt', '.pptx']

class EmailWorkerThread(QThread):
    emailsReady = pyqtSignal(str)

    def __init__(self, urls, parent=None):
        super(EmailWorkerThread, self).__init__(parent)
        self.urls = urls

    def run(self):
        all_emails = []
        for url in tqdm(self.urls):
            emails = self.extract_content_and_emails(url)
            all_emails.extend(emails)
        all_emails = set(all_emails)
        self.emailsReady.emit(','.join(''.join(email) for email in all_emails))

    def extract_content_and_emails(self, url):
        try:
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                doc = Document(response.text)
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', response.text)
                filtered_emails = [email for email in emails if not any(email.lower().endswith(ext) for ext in FILE_EXTENSIONS)]
                return filtered_emails
        except Exception as e:
            print('error trying to get emails: ' + str(e))
            pass
        return []

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
            chrome_driver_path = "C:\projects\marketing\chromedriver-win64\chromedriver.exe"
            driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)
            driver.get(search_url)
            time.sleep(5)
            page_source = driver.page_source
            with open("google_search_results.html", "w", encoding="utf-8") as file:
                file.write(page_source)
            driver.quit()

            with open("google_search_results.html", "r", encoding="utf-8") as file:
                html_content = file.read()
            
            soup = BeautifulSoup(html_content, "html.parser")
            links = soup.find_all("a")
            urls = []

            for link in links:
                href = link.get("href")
                if href and href.startswith('http'):
                    urls.append(href)

            self.resultReady.emit('\n'.join(urls))
        except Exception as e:
            print("An error occurred:", e)

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Google Search Scraper')
        self.resize(800, 800)

        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Enter search query")

        self.num_results_input = QLineEdit(self)
        self.num_results_input.setPlaceholderText("Number of search results")

        self.output_textbox = QTextEdit(self)
        self.output_textbox.setPlaceholderText("Search results will appear here")
        self.output_textbox.setReadOnly(True)

        self.emails_textbox = QTextEdit(self)
        self.emails_textbox.setPlaceholderText("Emails will appear here")
        self.emails_textbox.setReadOnly(True)

        self.button = QPushButton('Scrape Google Search', self)
        self.button.clicked.connect(self.startScraping)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Search Query:"))
        layout.addWidget(self.search_input)
        layout.addWidget(QLabel("Number of Results:"))
        layout.addWidget(self.num_results_input)
        layout.addWidget(self.button)
        layout.addWidget(self.output_textbox)
        layout.addWidget(QLabel("Scraped Emails:"))
        layout.addWidget(self.emails_textbox)

        self.setLayout(layout)

    def startScraping(self):
        search_query = self.search_input.text()
        num_results = self.num_results_input.text()
        self.worker = WorkerThread(search_query, num_results)
        self.worker.resultReady.connect(self.displayResults)
        self.worker.start()

    def displayResults(self, links_text):
        self.output_textbox.setPlainText(links_text)
        urls = links_text.split('\n')
        self.emailWorker = EmailWorkerThread(urls)
        self.emailWorker.emailsReady.connect(self.displayEmails)
        self.emailWorker.start()

    def displayEmails(self, emails_text):
        self.emails_textbox.setPlainText(emails_text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    ex.show()
    sys.exit(app.exec_())
