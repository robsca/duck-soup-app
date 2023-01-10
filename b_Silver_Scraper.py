import requests
from bs4 import BeautifulSoup

class Silver_Scraper:
    def __init__(self, url):
        self.url = url

    # 1. WIKI
    def get_wiki_text(self, chapter=None):
        '''
        param:
            chapter: string (chapter to get)
        return:
            text: string  (text of the chapter)
        '''
        page = requests.get(self.url) # get the page
        soup = BeautifulSoup(page.content, 'html.parser') # create a BeautifulSoup object
        chapters = soup.find_all('h2') # find all the chapters
        chapters = [c.get_text() for c in chapters] # get the text of the chapters

        # print(chapters)
        
        if chapter in chapters:
            print(f"Getting chapter {chapter}")
            # iterate over the text if find p or h2
            text = []
            for t in soup.find_all(['p', 'h2']):
                if t.name == 'h2': # if the tag is h2
                    if t.get_text() == chapter: # if the text is the chapter
                        print("Found chapter")
                        next_h2 = t.find_next('h2') # find the next h2
                        # all the text until the next_2
                        for t in t.find_next_siblings(): # iterate over the siblings
                            if t == next_h2:
                                break
                            else:
                                text.append(t.get_text())
                    else:
                        # handle the case where the chapter is not found
                        pass

            # join the text
            text = ' '.join(text)
            text = text.replace("/", "-")
            return text, chapters
        else:
            # find the text from p and h2
            text = [t.get_text() for t in soup.find_all(['p', 'h2'])]
            # join the text
            text = ' '.join(text)
            # replace the / with a space
            text = text.replace("/", "-")
            return text, chapters

    def scraping_wiki(self, last_word):
        '''
        param:
            last_word: string
        return:
            wiki_text: string
        '''
        print("Getting wikipedia summary")
        word = last_word[6:] # get the word to search
        if "+" in word:
            word_ = word.split("+")[0] 
            chapter_ = word.split("+")[1]
            print(f"Getting chapter {chapter_} of {word_}")
            url = f"https://en.wikipedia.org/wiki/{word_}"
            text, chapters = self.get_wiki_text(url, chapter_)
            # replace the / with a space
            wiki_text = text.replace("/", " ")
            return wiki_text
        else:
            chapter_ = None
            url = f"https://en.wikipedia.org/wiki/{word}"
            text, chapters = self.get_wiki_text(url)
            # replace the / with a space
            text = text.replace("/", " ")
            return text, chapters
    # 2. URL
    def get_text_from_url(self, chapter=None):
        page = requests.get(self.url) # get the page
        soup = BeautifulSoup(page.content, 'html.parser') # create a BeautifulSoup object
        chapters = soup.find_all('h2') # find all the chapters
        chapters = [c.get_text() for c in chapters] # get the text of the chapters

        # print(chapters)
        
        if chapter in chapters:
            print(f"Getting chapter {chapter}")
            # iterate over the text if find p or h2
            text = []
            for t in soup.find_all(['p', 'h2']):
                if t.name == 'h2': # if the tag is h2
                    if t.get_text() == chapter: # if the text is the chapter
                        print("Found chapter")
                        text.append(t.get_text()) # append the text
                        next_p = t.find_next('p') # find the next p
                        text.append(next_p.get_text()) # append the text
                        next_h2 = t.find_next('h2') # find the next h2
                        # all the text until the next_2
                        for t in t.find_next_siblings(): # iterate over the siblings
                            if t == next_h2:
                                break
                            else:
                                text.append(t.get_text())
                    else:
                        # handle the case where the chapter is not found
                        pass

            # join the text
            text = ' '.join(text)
            return text, chapters
        else:
            # find the text from p and h2
            text = [t.get_text() for t in soup.find_all(['p', 'h2'])]
            # join the text
            text = ' '.join(text)
            return text, chapters

    def scraping_url(self):
        print("Getting wikipedia summary")
        text, chapters = self.get_text_from_url()
        # replace the / with a space
        text = text.replace("/", " ")
        return text, chapters
            
if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
    scraper = Silver_Scraper(url)
    text, chapters = scraper.get_wiki_text("History")
    print(text)