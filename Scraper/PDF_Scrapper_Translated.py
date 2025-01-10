import requests
from bs4 import BeautifulSoup

def TranslatedLaws(base_url, output_file="laws_translated_pdfs.txt"):
    """
    Extracts all valid PDF links from the given URL and saves them to a text file.

    Args:
        base_url (str): The URL of the page to scrape.
        output_file (str): The name of the file to save the extracted PDF links.

    Returns:
        list: A list of extracted PDF links.
    """
    pdf_base_url = "https://www.gesetze-im-internet.de/"
    
    # Fetch the page
    response = requests.get(base_url)
    if response.status_code != 200:
        print(f"Failed to fetch the page: {base_url}. Status code: {response.status_code}")
        return []
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links for translated laws
    pdf_links = []
    for link in soup.find_all("a", href=True):
        href = link.get('href')
        if href and "index.html" in href:  # Look for 'index.html' links
            # Generate the PDF link
            pdf_link = href.replace("index.html", href.split('/')[0] + ".pdf")
            full_pdf_url = pdf_base_url + pdf_link.lstrip('./')
            
            # Ensure the URL ends with '.pdf'
            if full_pdf_url.endswith('.pdf'):
                pdf_links.append(full_pdf_url)
    
    # Deduplicate the list
    pdf_links = list(set(pdf_links))
    
    # Save the PDF links to a file
    with open(output_file, "w", encoding="utf-8") as file:
        file.write("\n".join(pdf_links))
    
    print(f"Extracted {len(pdf_links)} PDF links. Saved to {output_file}.")
    
    return pdf_links

# Example Usage
if __name__ == "__main__":
    base_url = "https://www.gesetze-im-internet.de/Teilliste_translations.html"
    TranslatedLaws(base_url)
