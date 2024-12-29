import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import csv

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def fetch_job_data(url, page_number):
    # Open the page
    driver.get(url)
    time.sleep(3)  # Wait for the page to load
    
    # Parse the page source
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Collect job data
    jobs = []
    job_cards = soup.find_all("div", class_="job_seen_beacon")
    
    for job_card in job_cards:
        title = job_card.find("h2", class_="jobTitle")
        title = title.text.strip() if title else "N/A"
        
        company = job_card.find("span", {'data-testid': 'company-name'})
        company = company.text.strip() if company else "N/A"
        
        location = job_card.find("div", {'data-testid': 'text-location'})
        location = location.text.strip() if location else "N/A"
        
        jobs.append({"Title": title, "Company": company, "Location": location})
    
    # Find the next page URL using `data-testid`
    next_button = soup.find("a", {'data-testid': f'pagination-page-{page_number}'})
    next_url = next_button.get("href") if next_button else None
    if next_url:
        next_url = "https://in.indeed.com" + next_url  # Append the domain to the relative URL
    
    return jobs, next_url

def scrape_all_pages(start_url, max_pages=5):
    current_url = start_url
    all_jobs = []
    page_count = 1  # Start with page 1
    
    while current_url and page_count <= max_pages:
        print(f"Scraping page {page_count}: {current_url}")
        try:
            jobs, next_url = fetch_job_data(current_url, page_count + 1)
        except Exception as e:
            print(f"An error occurred: {e}")
            break
        if not jobs:
            break
        all_jobs.extend(jobs)
        current_url = next_url
        page_count += 1
    
    return all_jobs

# Starting URL
start_url = "https://in.indeed.com/jobs?q=python+developer&l=Bengaluru%2C+Karnataka"

# Scrape all pages
jobs = scrape_all_pages(start_url, max_pages=5)

# Print jobs
for idx, job in enumerate(jobs, start=1):
    print(f"{idx}. {job['Title']} at {job['Company']} in {job['Location']}")

# Write data to CSV
try:
    with open("jobs_selenium.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["Title", "Company", "Location"])
        writer.writeheader()
        writer.writerows(jobs)
    print("Data has been written to jobs_selenium.csv successfully.")
except Exception as e:
    print(f"An error occurred while writing to the CSV file: {e}")

# Close the browser
driver.quit()
