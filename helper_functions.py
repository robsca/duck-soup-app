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

# run
if __name__ == '__main__':
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context

    # get the text
    wikipedia_url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
    text = web_scrape_webpage(wikipedia_url)
    print(text)    