# AgenticRAG


Agentic RAG for German Laws for English and German languages. The switching logic is based on language detection to switch between respective language agents.

It comes with scraping module as well. Just run:

PDF_Scrapper_German.py and 
PDF_Scrapper_Translated to get all the pdf links from openly available German Government website link: https://www.gesetze-im-internet.de 

The above codes generates two text files that contains all the links laws_german_pdfs.txt and laws_translated_pdfs.txt

I didn't created the embeddings for all the pdf links and used sample of those links.
For German agent: BNatSchg and BImSchG  
For English Agent:  englisch_urhdag and Immigration laws 

Change the file name in the Scraper Directory, If you want to create RAG on all laws.
