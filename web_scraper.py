import requests
from bs4 import BeautifulSoup
import csv
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os

# ──────────────────────────────────────────────
#  Scraper Logic
# ──────────────────────────────────────────────

BASE_URL = "https://books.toscrape.com/catalogue/"
START_URL = "https://books.toscrape.com/catalogue/page-1.html"

# Rating words on the site are written as words, not numbers
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def scrape_books(max_pages=5, progress_callback=None, log_callback=None):
    """
    Scrapes book data from books.toscrape.com
    Returns a list of dicts with name, price, rating, availability
    """
    books = []
    url = START_URL
    page = 1

    while url and page <= max_pages:
        if log_callback:
            log_callback(f"Scraping page {page}...")

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            if log_callback:
                log_callback(f"Error fetching page {page}: {e}")
            break

        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("article", class_="product_pod")

        for article in articles:
            # Extract book name
            name = article.find("h3").find("a")["title"]

            # Extract price
            price = article.find("p", class_="price_color").text.strip()
            # Remove currency symbol and convert to float
            price_clean = float(price.replace("£", "").replace("Â", "").strip())

            # Extract star rating (stored as a word class e.g. "Three")
            rating_class = article.find("p", class_="star-rating")["class"][1]
            rating = RATING_MAP.get(rating_class, 0)

            # Extract availability
            availability = article.find("p", class_="instock availability").text.strip()

            books.append({
                "Name":         name,
                "Price (£)":    price_clean,
                "Rating (1-5)": rating,
                "Availability": availability
            })

        if progress_callback:
            progress_callback(page, max_pages)

        # Find next page link
        next_btn = soup.find("li", class_="next")
        if next_btn:
            next_href = next_btn.find("a")["href"]
            url = BASE_URL + next_href
        else:
            url = None

        page += 1
        time.sleep(0.5)  # be polite — don't hammer the server

    if log_callback:
        log_callback(f"Done! Scraped {len(books)} books.")

    return books


def save_to_csv(books, filepath):
    """Saves list of book dicts to a CSV file."""
    if not books:
        return False
    fieldnames = ["Name", "Price (£)", "Rating (1-5)", "Availability"]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(books)
    return True


# ──────────────────────────────────────────────
#  Tkinter GUI
# ──────────────────────────────────────────────

BG       = "#08000f"
CARD_BG  = "#1a0030"
BORDER   = "#6633aa"
TEXT     = "#e8d5ff"
TEXT_DIM = "#9966cc"
ACCENT   = "#d4aaff"
BTN_BG   = "#3a0070"
BTN_FG   = "#dd99ff"
GREEN    = "#88ddaa"
RED      = "#ff6688"


class ScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Scraper — Books Data Extractor")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.books = []
        self._build_ui()

    def _build_ui(self):
        # ── Title ───────────────────────────────
        tk.Label(self.root, text="🌐  Web Scraper",
                 bg=BG, fg="#d4aaff",
                 font=("Segoe UI", 18, "bold")).pack(pady=(20, 2))
        tk.Label(self.root, text="Extracts book names, prices & ratings from books.toscrape.com",
                 bg=BG, fg=TEXT_DIM,
                 font=("Segoe UI", 9)).pack(pady=(0, 16))

        # ── Settings card ───────────────────────
        card = tk.Frame(self.root, bg=CARD_BG,
                        highlightbackground=BORDER, highlightthickness=1)
        card.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(card, text="Settings",
                 bg=CARD_BG, fg=TEXT_DIM,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=(12, 4))

        # Pages selector
        row1 = tk.Frame(card, bg=CARD_BG)
        row1.pack(fill="x", padx=16, pady=(0, 8))
        tk.Label(row1, text="Pages to scrape (1–50):",
                 bg=CARD_BG, fg=TEXT,
                 font=("Segoe UI", 10)).pack(side="left")
        self.pages_var = tk.IntVar(value=5)
        tk.Spinbox(row1, from_=1, to=50, textvariable=self.pages_var,
                   width=5, bg=CARD_BG, fg=ACCENT,
                   buttonbackground=CARD_BG,
                   font=("Segoe UI", 10)).pack(side="left", padx=(10, 0))
        tk.Label(row1, text="(20 books per page)",
                 bg=CARD_BG, fg=TEXT_DIM,
                 font=("Segoe UI", 8)).pack(side="left", padx=(8, 0))

        # Save path
        row2 = tk.Frame(card, bg=CARD_BG)
        row2.pack(fill="x", padx=16, pady=(0, 12))
        tk.Label(row2, text="Save CSV to:",
                 bg=CARD_BG, fg=TEXT,
                 font=("Segoe UI", 10)).pack(side="left")
        self.path_var = tk.StringVar(value=os.path.join(os.getcwd(), "books.csv"))
        tk.Entry(row2, textvariable=self.path_var,
                 bg="#120020", fg=ACCENT,
                 insertbackground=ACCENT,
                 relief="flat", width=30,
                 font=("Segoe UI", 9)).pack(side="left", padx=(8, 6), ipady=4)
        tk.Button(row2, text="Browse",
                  bg=BTN_BG, fg=BTN_FG,
                  activebackground="#4a0090",
                  relief="flat", padx=8, pady=3,
                  font=("Segoe UI", 9),
                  cursor="hand2",
                  command=self._browse).pack(side="left")

        # ── Progress ────────────────────────────
        prog_frame = tk.Frame(self.root, bg=BG)
        prog_frame.pack(fill="x", padx=20, pady=(0, 6))

        self.progress = ttk.Progressbar(prog_frame, orient="horizontal",
                                        length=400, mode="determinate")
        self.progress.pack(fill="x")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", troughcolor="#1a0030",
                         background="#8844cc", thickness=8)

        # ── Log box ─────────────────────────────
        log_frame = tk.Frame(self.root, bg=CARD_BG,
                             highlightbackground=BORDER, highlightthickness=1)
        log_frame.pack(fill="both", padx=20, pady=(0, 10), expand=True)

        tk.Label(log_frame, text="Log",
                 bg=CARD_BG, fg=TEXT_DIM,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=10, pady=(8, 2))

        self.log_box = tk.Text(log_frame, height=8,
                               bg="#120020", fg=TEXT,
                               insertbackground=ACCENT,
                               relief="flat",
                               font=("Consolas", 9),
                               state="disabled")
        self.log_box.pack(fill="both", padx=10, pady=(0, 10))

        # ── Buttons ─────────────────────────────
        btn_row = tk.Frame(self.root, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=(0, 8))

        self.scrape_btn = tk.Button(btn_row, text="🚀  Start Scraping",
                                    bg=BTN_BG, fg=BTN_FG,
                                    activebackground="#4a0090",
                                    activeforeground=BTN_FG,
                                    relief="flat", padx=16, pady=8,
                                    font=("Segoe UI", 11, "bold"),
                                    cursor="hand2",
                                    command=self._start_scraping)
        self.scrape_btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.save_btn = tk.Button(btn_row, text="💾  Save CSV",
                                  bg="#1a0030", fg=ACCENT,
                                  activebackground="#2a0050",
                                  activeforeground=ACCENT,
                                  relief="flat", padx=16, pady=8,
                                  font=("Segoe UI", 11),
                                  cursor="hand2",
                                  state="disabled",
                                  command=self._save_csv)
        self.save_btn.pack(side="left", expand=True, fill="x")

        # ── Status label ────────────────────────
        self.status_var = tk.StringVar(value="Ready to scrape.")
        tk.Label(self.root, textvariable=self.status_var,
                 bg=BG, fg=TEXT_DIM,
                 font=("Segoe UI", 9)).pack(pady=(0, 4))

        # ── Footer ──────────────────────────────
        tk.Label(self.root,
                 text="SkillCraft Technology — Task 04  |  Python · requests · BeautifulSoup · csv",
                 bg=BG, fg="#4a2a6a",
                 font=("Segoe UI", 7)).pack(pady=(0, 14))

    def _browse(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="books.csv"
        )
        if path:
            self.path_var.set(path)

    def _log(self, msg):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _set_progress(self, current, total):
        self.progress["value"] = (current / total) * 100
        self.root.update_idletasks()

    def _start_scraping(self):
        self.scrape_btn.config(state="disabled")
        self.save_btn.config(state="disabled")
        self.progress["value"] = 0
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.config(state="disabled")
        self.status_var.set("Scraping in progress...")
        self.books = []

        pages = self.pages_var.get()

        # Run scraping in a background thread so GUI doesn't freeze
        def run():
            self.books = scrape_books(
                max_pages=pages,
                progress_callback=lambda c, t: self.root.after(0, self._set_progress, c, t),
                log_callback=lambda msg: self.root.after(0, self._log, msg)
            )
            self.root.after(0, self._on_done)

        threading.Thread(target=run, daemon=True).start()

    def _on_done(self):
        self.scrape_btn.config(state="normal")
        if self.books:
            self.save_btn.config(state="normal")
            self.status_var.set(f"✓ Scraped {len(self.books)} books. Click 'Save CSV' to export.")
            self._log(f"\n✓ Total books scraped: {len(self.books)}")
        else:
            self.status_var.set("No data scraped. Check your internet connection.")

    def _save_csv(self):
        path = self.path_var.get()
        if not path:
            messagebox.showerror("Error", "Please select a save path first.")
            return
        if save_to_csv(self.books, path):
            messagebox.showinfo("Saved!", f"CSV saved successfully to:\n{path}")
            self._log(f"CSV saved to: {path}")
            self.status_var.set(f"✓ CSV saved to {path}")
        else:
            messagebox.showerror("Error", "Failed to save CSV.")


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("560x560")
    app = ScraperApp(root)
    root.mainloop()
