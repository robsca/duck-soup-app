import pyttsx3

def text_to_speech(text):
    # create a new instance of the engine
    engine = pyttsx3.init()
    # set the rate of the speech
    engine.setProperty('rate', 170)
    # say the text
    engine.say(text)
    # run and wait
    engine.runAndWait()
    engine.stop()
    
def web_scrape_webpage(url):
    # import the libraries
    import requests
    from bs4 import BeautifulSoup
    # get the webpage
    page = requests.get(url)
    # create a BeautifulSoup object
    soup = BeautifulSoup(page.content, 'html.parser')
    # find the text
    text = soup.find_all('p')
    # clean the text
    text = [t.get_text() for t in text]
    # join the text
    text = ' '.join(text)
    return text

def get_wiki_text(url, chapter=None):
    # import the libraries
    import requests
    from bs4 import BeautifulSoup
    # get the webpage
    page = requests.get(url)
    # create a BeautifulSoup object
    soup = BeautifulSoup(page.content, 'html.parser')
    # get all the chapters
    chapters = soup.find_all('h2')
    # get the text of the chapters
    chapters = [c.get_text() for c in chapters]
    print(chapters)
    # show the chapters
    if chapter in chapters:
        print(f"Getting chapter {chapter}")
        # iterate over the text if find p or h2
        text = []
        for t in soup.find_all(['p', 'h2']):
            if t.name == 'h2': # if the tag is h2
                if t.get_text() == chapter: # if the text is the chapter
                    print("Found chapter")
                    text.append(t.get_text()) # append the text
                    print(t.get_text()) 
                    next_p = t.find_next('p') # find the next p
                    text.append(next_p.get_text()) # append the text
                    print(next_p.get_text()) 
                    # get the next h2
                    next_h2 = t.find_next('h2')
                    # all the text until the next_2
                    for t in t.find_next_siblings():
                        if t == next_h2:
                            break
                        else:
                            text.append(t.get_text())

                else:
                    print(f"Not found {t.get_text()} != {chapter}")

        # join the text
        text = ' '.join(text)
        return text, chapters
    else:
        # find the text
        text = soup.find_all('p')
        # clean the text
        text = [t.get_text() for t in text]
        # join the text
        text = ' '.join(text)
        return text, chapters

def get_text_from_url(url):
    # import the libraries
    import requests
    from bs4 import BeautifulSoup
    # get the webpage
    page = requests.get(url)
    # create a BeautifulSoup object
    soup = BeautifulSoup(page.content, 'html.parser')
    # find everything that contains the text
    text = soup.find_all('p')
    # clean the text
    text = [t.get_text() for t in text]
    # join the text
    text = ' '.join(text)
    return text

# run
if __name__ == '__main__':
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    # get the text
    wikipedia_url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
    text = web_scrape_webpage(wikipedia_url)
    print(text)    