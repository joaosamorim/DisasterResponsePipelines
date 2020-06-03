# DisasterResponsePipelines

This an open source project to make an ETL pipeline and a Machine Learning pipeline of a model to categorize disasters messages.
Furthermore it will be implemented a browser interface to use this model.

The preparation of the data can be found in the notebooks in the preparation folder.
The cleaning process is explained throughout the notebooks but they were mainly NLP processes, such as:
1- Normalize, tokenize, removing stop words and lemmatize the messages.
2- CountVectorizer and TF-IDF transformer for the document term matrix.

The dataframes are merged into a SQL database.
The files to prepare the data and train the model can be found in the respective folders and were developed with python.
Finally the web app is design using flask, html and CSS.


Intructions:

First run the process_data.py in the data folder to clean the data.
process_data should be run like this:
process_data.py messages_dataframe_filepath categories_data_filepath database_filepath
example: python process_data.py '/data/messages.csv' '/data/categories.csv' 'data/disasters.db'
 
Second run the train_classifer.py in the models folder to train and save to a pickle file the predictive model:
train_classifer shoud be run like this:
train_classifer database_filepath model_filepath
example: python train_classfier.py 'data/disasters.db' 'model/trained_model.pkl'

Third and last run the run.py in the app folder to launch the website:
To visit the website simply type localhost:3001 in your browser of choice.
