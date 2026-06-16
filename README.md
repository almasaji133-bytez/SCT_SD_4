# Task 04 — Web Scraper

A Python-based web scraping program with a GUI that extracts product information (names, prices, and ratings) from an online e-commerce website and stores the data in a structured CSV file.

---

## 🌐 Website Scraped
**books.toscrape.com** — a sandbox e-commerce site specifically designed for web scraping practice.

> ⚠️ Real e-commerce sites like Amazon or Flipkart block scraping with CAPTCHAs and login walls. books.toscrape.com is the standard practice site used for internship and learning projects.

---

## ✨ Features

- Scrapes book **name**, **price**, **star rating**, and **availability**
- Choose how many pages to scrape (1–50 pages, 20 books per page)
- Real-time log showing scraping progress
- Progress bar tracking pages scraped
- Saves extracted data to a **CSV file**
- Browse button to choose save location
- Runs scraping in a background thread so GUI stays responsive
- Clean purple-themed Tkinter GUI

---

## 🚀 How to Run

### Step 1 — Install Python
Download from https://python.org if not already installed.

### Step 2 — Install required libraries
Open terminal and run:
```bash
pip install requests beautifulsoup4
```

### Step 3 — Run the program
```bash
python web_scraper.py
```

---

## 🖥️ How to Use

1. Set the number of pages to scrape (each page has 20 books)
2. Choose where to save the CSV file using the Browse button
3. Click **Start Scraping**
4. Watch the log and progress bar as data is collected
5. Click **Save CSV** when done

---

## 📁 File Structure

```
Task-04-Web-Scraper/
├── web_scraper.py    → Full program (scraper + Tkinter GUI)
└── README.md         → Project documentation
```

---

## 📊 CSV Output Format

| Name | Price (£) | Rating (1-5) | Availability |
|------|-----------|--------------|--------------|
| A Light in the Attic | 51.77 | 3 | In stock |
| Tipping the Velvet | 53.74 | 1 | In stock |
| ... | ... | ... | ... |

---

## ⚙️ How It Works

```
1. Send an HTTP GET request to books.toscrape.com
2. Parse the HTML response using BeautifulSoup
3. Find all book elements on the page
4. Extract name, price, rating, and availability
5. Move to the next page and repeat
6. Save all collected data to a CSV file
```

---

## 🛠️ Technologies Used

- **Python 3** — Core language
- **requests** — Fetches web pages
- **BeautifulSoup4** — Parses and extracts HTML data
- **csv** — Saves data in structured CSV format
- **tkinter** — GUI (built into Python, no install needed)
- **threading** — Keeps GUI responsive during scraping

---

## 👨‍💻 Internship

**Organization:** SkillCraft Technology
**Task:** 04 — Web Scraper
**Intern:** [Your Name]
