from curses import window
import tkinter as tk
from model_tgen import tokenizer, model
from helper_functions import *
from transformers import pipeline


# WINDOW
root = tk.Tk()
root.title("Text Generator")
root.geometry("800x600")
# text area
text_entry = tk.Text(root, height=40, width=100)
text_entry.grid(row=0, column=0, columnspan=2, rowspan=2, sticky="nsew", padx=5, pady=5)

# FUNCTIONS NLP
def generate_text(num, prompt):
    print(f"Generating {num} words")
    len_prompt = len(prompt.split())
    last_word = prompt.split()[-1]
    # delete last word from prompt
    prompt = prompt.replace(last_word, "")
    
    input_ids = tokenizer.encode(prompt, return_tensors='pt')
    sample_outputs = model.generate(input_ids, do_sample=True, max_length= len_prompt + num)
    
    # print sample outputs
    generated_text = tokenizer.decode(sample_outputs[0], skip_special_tokens=True)
    # delete textarea
    text_entry.delete(1.0, tk.END)
    # insert generated text
    text_entry.insert(tk.END, generated_text)

def create_summary(prompt, max_length=100, min_length=30, delete_prompt=True):
        # delete last word from prompt
        last_word = prompt.split()[-1]
        prompt = prompt.replace(last_word, "")
        print("Generating summary") 
        summarizer = pipeline("summarization")

        summary = summarizer(prompt, max_length=max_length, min_length=min_length, truncation=True)
        summary = summary[0]['summary_text']
        # add summary to textarea
        text_entry.insert(tk.END, summary)

def get_wiki_summary(prompt,last_word):
    # make a request to wikipedia
    print("Getting wikipedia summary")
    # get the word to search
    word = last_word[6:]
    # if + is in the word
    if "+" in word:
        word_ = word.split("+")[0]
        chapter_ = word.split("+")[1]
        print(f"Getting chapter {chapter_} of {word_}")
        url = f"https://en.wikipedia.org/wiki/{word_}"
        text, chapters = get_wiki_text(url, chapter_)
        # replace the / with a space
        text = text.replace("/", " ")
        prompt = prompt.replace(last_word, text)
        # delete textarea
        text_entry.delete(1.0, tk.END)
        # insert generated text
        text_entry.insert(tk.END, prompt)

    else:
        chapter_ = None
        url = f"https://en.wikipedia.org/wiki/{word}"
        text, chapters = get_wiki_text(url)
        # replace the / with a space
        text = text.replace("/", " ")
        print(text)
        print(chapters)
        # create a new window
        wiki_window = tk.Toplevel(root)
        wiki_window.title("Wikipedia")
        wiki_window.geometry("350x350")
        # add text to textarea
        text_entry.insert(tk.END, text)
        # add chapters to listbox
        listbox = tk.Listbox(wiki_window, height=10, width=40)
        listbox.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        for chapter in chapters:
            listbox.insert(tk.END, chapter)
        
        # if chapter is selected
        def select_chapter(event):
            # get selected chapter
            chapter = listbox.get(listbox.curselection())
            # get text from wikipedia
            text, chapters = get_wiki_text(url, chapter)
            # replace the / with a space
            text = text.replace("/", " ")
            # delete textarea
            text_entry.delete(1.0, tk.END)
            # insert generated text
            text_entry.insert(tk.END, text)
            # destroy window
            wiki_window.destroy()
        # bind event to listbox
        listbox.bind("<<ListboxSelect>>", select_chapter)

def question_answering(prompt):
    def answer_question(prompt):
        model = pipeline("question-answering")
        question = question_entry.get("1.0", "end-1c")
        answer = model(question=question, context=prompt)
        answer_entry.insert(tk.END, answer['answer'])

    # create a new window
    qa_window = tk.Toplevel(root)
    qa_window.title("Question Answering")
    qa_window.geometry("350x350")
    # question entry
    question_entry = tk.Text(qa_window, height=10, width=40)
    question_entry.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
    # answer entry
    answer_entry = tk.Text(qa_window, height=10, width=40)
    answer_entry.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
    # answer button
    answer_button = tk.Button(qa_window, text="Answer", command=lambda: answer_question(prompt))
    answer_button.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)
    # close button
    def close_window():
        # delete /qa from prompt
        # get text from text_entry
        text = text_entry.get("1.0", "end-1c")
        # delete last word from prompt
        last_word = text.split()[-1]
        text = text.replace(last_word, "")
        # delete textarea
        text_entry.delete(1.0, tk.END)
        # insert generated text
        text_entry.insert(tk.END, text)

        qa_window.destroy()
    close_button = tk.Button(qa_window, text="Close", command=close_window)
    close_button.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

# EVENTS
def interpreter(event):
    prompt = text_entry.get("1.0", "end-1c")
    # get last word of prompt
    last_word = prompt.split()[-1]


    # text generation
    if last_word == "/gen200":
        generate_text(200, prompt)
    elif last_word == "/gen50":
        generate_text(50, prompt)
    elif last_word == "/gen100":
        generate_text(100, prompt)
    # summary
    elif last_word == "/summary":
        create_summary(prompt)
    # wikipedia scraping
    elif last_word[:6] == "/wiki-":
        get_wiki_summary(prompt, last_word)
    # question answering
    elif last_word == "/qa":
        question_answering(prompt)
    else:
        print('No generate command found')

    return None

# if text is highlighted, delete it when pressed command + s
def summary_highlighted_text(event):
    '''
    This function is called when the user presses command + s
    It creates a summary of the highlighted text and replaces it with the summary
    '''
    # get selected text
    prompt = text_entry.selection_get()
    
    # delete last word from prompt
    print("Generating summary") 
    summarizer = pipeline("summarization")

    summary = summarizer(prompt, max_length=100, min_length=30, truncation=True)
    summary = summary[0]['summary_text']

    # put instead of selected text
    text_entry.delete(tk.SEL_FIRST, tk.SEL_LAST)
    text_entry.insert(tk.INSERT, summary)    

# every new char excecute a function thtat if is a /
def is_command(event):
    '''
    This function is called every time a new character is inserted in the text area
    It handles the styling of the text if it is a command
    '''
    # check if '/' is in text
    prompt = text_entry.get("1.0", "end-1c")
    if '/' in prompt:
        print("Command found")
        # get index of '/'
        index = prompt.index('/')
        # change the color of the text until the end
        text_entry.tag_add("command", "1.0 + " + str(index) + "c", "end")
        text_entry.tag_config("command", foreground="grey")
        # make it bold
        text_entry.tag_add("bold", "1.0 + " + str(index) + "c", "end")
        text_entry.tag_config("bold", font="bold")
        # make it bigger
        text_entry.tag_add("big", "1.0 + " + str(index) + "c", "end")
        text_entry.tag_config("big", font=("Helvetica", 20))
    else:
        #print("No command found")
        text_entry.tag_delete("command")
        text_entry.tag_delete("bold")
        text_entry.tag_delete("big")

    text = text_entry.get(index1="1.0", index2="end")
    words = text.split()
    word_count = len(words)
    word_count_label = tk.Label(root, text=f"Word count: {word_count}")
    word_count_label.grid(row=2, column=0, columnspan=3)

    # analyze the text
    def analyze_text():
        from nltk.corpus import stopwords
        no_words = stopwords.words("english")
        from collections import Counter

        words = text.split() # split the text into words
        words = [word.strip(".,!?:;") for word in words] # strip the words from the symbols
        words = [word for word in words if word not in no_words]  # take out the no words
        word_count = Counter(words)
        # get the most common words
        most_common_words = word_count.most_common(5)
        most_common_words_label = tk.Label(root, text=f"Most common words: {most_common_words}")
        most_common_words_label.grid(row=3, column=0, columnspan=4)
    
    analyze_text()

# BINDINGS
text_entry.bind('<KeyRelease>', is_command)

text_entry.bind('<Return>', lambda event: text_entry.insert(tk.END, interpreter(text_entry)))
text_entry.bind('<Control-s>', summary_highlighted_text)
root.mainloop()

# Path: model_tgen.py # contains the model and tokenizer