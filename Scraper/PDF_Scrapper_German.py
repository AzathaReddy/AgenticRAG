import urllib3
from bs4 import BeautifulSoup
from urllib3.util import Retry

def ScrapePDFLinks(main_url, output_file="laws_german_pdfs.txt"):
    """
    Scrapes all valid PDF links from the specified URL and saves them to a text file.

    Args:
        main_url (str): The URL of the main page to scrape.
        output_file (str): The name of the file to save the extracted PDF links.
    """
    # Configure retries for HTTP requests
    retries = Retry(connect=5, read=2, redirect=5)
    http = urllib3.PoolManager(retries=retries)
    
    url_domain = "https://www.gesetze-im-internet.de/"
    
    # Fetch alphabetical subdirectories
    html = http.request('GET', main_url).data
    soup = BeautifulSoup(html, features="lxml")
    lista_pagine_alfab = []
    section = soup.find(id="container")
    
    # Collect links to Teilliste pages
    for link in section.find_all("a"):
        href = link.get('href')
        if href and "Teilliste_" in href:
            url_clean_coll = url_domain + href.lstrip('./')
            lista_pagine_alfab.append(url_clean_coll)
    
    # Collect URLs for all laws
    URL_laws = []
    for x in lista_pagine_alfab:
        html = http.request('GET', x).data
        soup = BeautifulSoup(html, features="lxml")
        section = soup.find(id="container")
    
        for link in section.find_all("a"):
            href = link.get('href')
            if href and "index.html" in href:
                law_url = url_domain + href.lstrip('./')
                URL_laws.append(law_url)
    
    # Collect valid PDF links
    PDF_list = []
    counter = 0
    
    for law_url in URL_laws:
        html = http.request('GET', law_url).data
        soup = BeautifulSoup(html, features="lxml")
        section = soup.find(id="container")
        
        # Get base directory name from the law URL
        base_directory = law_url.split('/')[-2]
        
        # Search for PDF links in the law's index page
        for link in section.find_all("a"):
            href = link.get('href')
            if href and href.endswith('.pdf'):  # Ensure the link points to a PDF
                pdf_url = f"{url_domain}{base_directory}/{href.lstrip('./')}"  # Build full PDF URL
                PDF_list.append(pdf_url)
                counter += 1
                print("\r", f"{counter} PDF URLs scraped", end="")
    
    # Deduplicate the list
    PDF_list = list(set(PDF_list))
    
    # Write the PDF links to a file
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(PDF_list))
    
    print(f"\nDone. Extracted {len(PDF_list)} PDF links. Saved to {output_file}.")

# Example Usage
if __name__ == "__main__":
    ScrapePDFLinks("https://www.gesetze-im-internet.de/aktuell.html", "laws_german_pdfs.txt")

