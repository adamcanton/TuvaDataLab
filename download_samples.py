import os
import requests
from bs4 import BeautifulSoup

# Base URL for the CMS DE-SynPUF page
main_url = "https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf"
base_download_url = "https://www.cms.gov"

# Specify the folder to download to
download_folder = "Data/Raw/DE_SynPUF_Downloaded"

# Create the folder if it doesn't exist
if not os.path.exists(download_folder):
    os.makedirs(download_folder)


# Function to download a file from a URL and save it locally
def download_file(url, folder):
    local_filename = os.path.join(folder, url.split("/")[-1])
    with requests.get(url, stream=True) as response:
        if response.status_code == 200:
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded: {local_filename}")
        else:
            print(f"Failed to download: {url}")


# Scrape a given sample page to find download links for ZIP files
def scrape_sample_page(sample_page_url):
    sample_response = requests.get(sample_page_url)
    sample_soup = BeautifulSoup(sample_response.text, "html.parser")

    # Find all links on the sample page that point to ZIP files
    links = []
    for link in sample_soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.zip'):
            # Ensure the correct base URL is appended if necessary
            if href.startswith("http"):
                full_url = href  # Full URL already present
            else:
                full_url = base_download_url + href  # Append base URL
            links.append(full_url)

    return links


# Scrape the main DE-SynPUF page for sample links
def scrape_main_page():
    response = requests.get(main_url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all sample links (e.g., DE1.0 Sample 1)
    sample_links = []
    for link in soup.find_all('a', href=True):
        href = link['href']
        if "/de10-sample-" in href:  # Identify links pointing to sample pages
            sample_page_url = base_download_url + href
            sample_links.append(sample_page_url)

    return sample_links


# Main process
sample_pages = scrape_main_page()

# For each sample page, scrape and download the ZIP files
for sample_page_url in sample_pages:
    print(f"Processing {sample_page_url}")
    zip_links = scrape_sample_page(sample_page_url)

    for zip_url in zip_links:
        download_file(zip_url, download_folder)

print("All files downloaded!")
