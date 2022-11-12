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
    
