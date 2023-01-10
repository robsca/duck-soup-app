import datetime
from transformers import pipeline
class NLP:
    '''
    This class should be indipendent from the GUI
    '''
    def __init__(self): # works
        '''
        Initialize the NLP class
        '''
        print(f"Initalizing NLP_Processor class")
        start = datetime.datetime.now()
        # print("NLP class: Creating instance")
        self.summarizer = pipeline("summarization")
        #self.fill_mask = pipeline("fill-mask")
        self.qa = pipeline("question-answering")
        #self.classifier = pipeline("sentiment-analysis")
        #self.ner = pipeline("ner")
        self.text_generator = pipeline("text-generation")
        # set pad token id to eos token id
        self.text_generator.tokenizer.pad_token_id = self.text_generator.tokenizer.eos_token_id
        #self.conversational = pipeline("conversational")
        end = datetime.datetime.now()
        # time in seconds
        time = (end - start).total_seconds()
        print(f"Initialization NLP_Processor completed: {time} seconds")

    def summarize(self, prompt, max_length=100, min_length=30, delete_prompt=True): # works
        '''
        param: 
            prompt: string
            max_length: int
            min_length: int
            delete_prompt: bool
        return:
            summary: string
        '''
        print("Generating summary") 
        # delete last word from prompt
        last_word = prompt.split()[-1]
        prompt = prompt.replace(last_word, "")
        summary = self.summarizer(prompt, max_length=max_length, min_length=min_length, truncation=True)
        summary = summary[0]['summary_text']
        return summary
    
    def generate_text(self, prompt, num = 100): # works
        '''
        param:
            prompt: string
            num: int (number of words to generate)
        return:
            generated: string (generated text)
        '''
        print(f"Generating {num} words")
        len_prompt = len(prompt.split())
        last_word = prompt.split()[-1]
        # delete last word from prompt
        prompt = prompt.replace(last_word, "")
        # generate text
        generated = self.text_generator(prompt, max_length=len_prompt+num, do_sample=True, top_k=50, top_p=0.95, num_return_sequences=1)
        generated = generated[0]['generated_text']
        return generated

    def answer_question(self, prompt, question):
        '''
        param:
            prompt: string
            question: string
        return:
            answer: string
        '''
        print("Answering question")
        answer = self.qa(question=question, context=prompt)
        return answer['answer']