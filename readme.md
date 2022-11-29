PS:
Everytime the databsae is being modified, reset the database to the an empty state, otherwise it would be impossible to test the code.

Setup
```
virtualenv env_main -p python3
source env_main/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
---
# TextEditor
With this editor open source you can scrape data, you can dictate.

Features:
---
    1. Add paraphrasing feature.
    - https://huggingface.co/tuner007/pegasus_paraphrase?text=Legislation+and+a+budget+are+some+of+the+responsibilities+of+the+executive+branch.
    2. Work on plotter.



---
Issues:
---
    - When scraping text from wikipedia, the old text it's been deleted
    
---
