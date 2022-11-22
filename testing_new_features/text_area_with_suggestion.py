import tkinter as tk
from model_tgen import tokenizer, model

root = tk.Tk()
root.title("Text Generator")
root.geometry("800x600")
# text area
text = tk.Text(root, height=40, width=100)
text.pack()

def generate_text_from_prompt(text):
    prompt = text.get("1.0", "end-1c")
    # get last word of prompt
    last_word = prompt.split()[-1]
    # get length of prompt
    if last_word == "/gen200":
        print("Generating 200 words")
        # delete last word from prompt
        prompt = prompt.replace(last_word, "")
        # encode context the generation is conditioned on
        input_ids = tokenizer.encode(prompt, return_tensors='pt')
        sample_outputs = model.generate(input_ids, do_sample=True, max_length= 200)
        # print sample outputs
        generated_text = tokenizer.decode(sample_outputs[0], skip_special_tokens=True)
        # delete textarea
        text.delete(1.0, tk.END)
        return generated_text
    elif last_word == "/gen50":
        print("Generating 50 words")
        # delete last word from prompt
        prompt = prompt.replace(last_word, "")
        # encode context the generation is conditioned on
        input_ids = tokenizer.encode(prompt, return_tensors='pt')
        sample_outputs = model.generate(input_ids, do_sample=True, max_length=50)
        # print sample outputs
        generated_text = tokenizer.decode(sample_outputs[0], skip_special_tokens=True)
        # delete textarea
        text.delete(1.0, tk.END)
        return generated_text
    elif last_word == "/gen100":
        print("Generating 100 words")
        # delete last word from prompt
        prompt = prompt.replace(last_word, "")
        # encode context the generation is conditioned on
        input_ids = tokenizer.encode(prompt, return_tensors='pt')
        sample_outputs = model.generate(input_ids, do_sample=True, max_length=100)
        # print sample outputs
        generated_text = tokenizer.decode(sample_outputs[0], skip_special_tokens=True)
        # delete textarea
        text.delete(1.0, tk.END)
        return generated_text
    else:
        print('No generate command found')

root.bind('<Return>', lambda event: text.insert(tk.END, generate_text_from_prompt(text)))

root.mainloop()

# Path: model_tgen.py