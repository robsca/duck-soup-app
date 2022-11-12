PS:
Everytime the databsae is being modified, reset the database to the an empty state, otherwise it would be impossible to test the code.

Setup
```
virtualenv env_main -p python3
source env_main/bin/activate
pip install -r requirements.txt
```

# create a home page for the project
1. New Note - Done
2. Edit Note - Done
3. Delete Note - Done
4. Clean up UI - To do
    1. Size main window 10% less
    2. Create a nav bar with the buttons on the top of the page
5. Every word that is been written,
    the title date and title the date entries change position. - Done 
    Fixed ~
6. Add a new column in database, now every note has a tag field.

------------------------
4. Add Analysis for Note 
    # word count - dictionary with word,count as key, value.
    # add tag to database, so I can use a structure like: Source   -  Target,   - Value
    #                                                     Element1 -  Element2  - Weight_of_connection
    #                                                     Tag      -  Words in note - How many time appears in Tag    

    Tag -> Word(after cleaning useless words) -> number of times
    ------------------------------------------------------------
    This can became our training data for the classification, so Once you start writing your note, it will suggest
    what's the computation thinks is the right tag.
    ------------------------------------------------------------
      
5. Use pyvis or networkx for network graph visual
6. Perform summarization and question answering 
7. Create a webscraper with beautifulsoup
8. Create a database for video and their text to speech editable 
