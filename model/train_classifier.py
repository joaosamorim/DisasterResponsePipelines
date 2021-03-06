import re
import sqlite3
import statistics
import sys
import pandas as pd
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.ensemble import RandomForestClassifier
import joblib
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV



def load_data(database_filepath, table_name):
    '''loading the messages database'''

    #opening the connect and reading the database
    conn = sqlite3.connect(database_filepath)
    query = 'SELECT * FROM '+table_name
    df = pd.read_sql(query, conn)
    df = df.drop(columns=['index'])

    #storing the database into X,y
    X = df['message'].values#first scenario will ignore the genre feature
    y= df[df.columns.difference(['message', 'genre', 'genre_news', 'genre_social'])]

    #closing connection
    conn.close()
    return X,y;


def tokenize(text):
    stop_words = stopwords.words("english")
    lemmatizer = WordNetLemmatizer()
    # normalize case, remove punctuation and numbers
    text = re.sub(r"[^a-zA-Z]", " ", text.lower())

    # tokenize text
    tokens = word_tokenize(text)

    # lemmatize and remove stop words
    tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]

    #lemmatize verbs
    tokens = [lemmatizer.lemmatize(word, pos='v') for word in tokens]

    #lemmatize adjectives
    tokens = [lemmatizer.lemmatize(word, pos='a') for word in tokens]

    #lemmatize adverbs
    tokens = [lemmatizer.lemmatize(word, pos='r') for word in tokens]



    return tokens


def build_model(X,y):
    '''Pipeline for a model with the following parameters
    These parameters were chosen by running GridSearchCV, for further details on these parameters take a look at the
        ML-pipeline and ML-tuning notebooks in the preparation folder in the repository
    '''

    pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer=tokenize)),
        ('tfidf', TfidfTransformer()),
        ('clf', MultiOutputClassifier(estimator=RandomForestClassifier()))
    ])

    # specify parameters for grid search
    parameters = {
        # 'vect__ngram_range': ((1, 1), (1, 2)),
        # 'vect__max_df': (0.5, 0.75, 1.0),
        # 'vect__max_features': (None, 5000, 10000),
        # 'tfidf__use_idf': (True, False),
        'clf__estimator__n_estimators': [100],
        #'clf__estimator__max_depth': [200],
        'clf__estimator__random_state': [42]

    }

    # create grid search object
    cv = GridSearchCV(pipeline, param_grid=parameters, verbose=1)

    return cv


def model_scores(y_test, y_pred):
    '''Calculates the area under the ROC curve,f1_score, accuracy, precision and recall scores for every label
    and displays the mean, maximum and minimum values of each score.'''

    auc = []
    for i in range(0, y_test.shape[1]):
        auc.append(roc_auc_score(y_test.iloc[:, i], y_pred[:, i]))
    print('Mean AUC:', "%.2f" % statistics.mean(auc), ' Max AUC:', "%.2f" % max(auc), ' Min AUC:', "%.2f" % min(auc))

    f1_score_model = []
    for i in range(0, y_test.shape[1]):
        f1_score_column = f1_score(y_test.iloc[:, i], y_pred[:, i])
        f1_score_model.append(f1_score_column)
    print('Mean f1 score:', "%.2f" % statistics.mean(f1_score_model), ' Max f1 score:', "%.2f" % max(f1_score_model),
          ' Min f1 score:', "%.2f" % min(f1_score_model))

    precision_score_model = []
    for i in range(0, y_test.shape[1]):
        precision_score_column = precision_score(y_test.iloc[:, i], y_pred[:, i])
        precision_score_model.append(precision_score_column)
    print('Mean precision score:', "%.2f" % statistics.mean(precision_score_model), ' Max precision score:',
          "%.2f" % max(precision_score_model), ' Min precision score:', "%.2f" % min(precision_score_model))

    accuracy_score_model = []
    for i in range(0, y_test.shape[1]):
        accuracy_score_column = accuracy_score(y_test.iloc[:, i], y_pred[:, i])
        accuracy_score_model.append(accuracy_score_column)
    print('Mean accuracy score:', "%.2f" % statistics.mean(accuracy_score_model), ' Max accuracy score:',
          "%.2f" % max(accuracy_score_model), ' Min accuracy score:', "%.2f" % min(accuracy_score_model))

    recall_score_model = []
    for i in range(0, y_test.shape[1]):
        recall_score_column = recall_score(y_test.iloc[:, i], y_pred[:, i])
        recall_score_model.append(recall_score_column)
    print('Mean recall score:', "%.2f" % statistics.mean(recall_score_model), ' Max recall score:',
          "%.2f" % max(recall_score_model), ' Min recall score:', "%.2f" % min(recall_score_model))


def AUC_ROC(y_test, y_pred):
    '''Calculates the area under the ROC curve for every label and displays the value.
    '''

    auc = []
    for i in range(0, y_test.shape[1]):
        auc_score_column = roc_auc_score(y_test.iloc[:, i], y_pred[:, i])
        auc.append(auc_score_column)
        print('The AUC for', y_test.columns[i], ' was: ', "%.2f" % auc_score_column, '.')

    # return auc; remove the comment if you want to return the list


def f1_score_labels(y_test, y_pred):
    '''Calculates the f1 score for every label and displays the value.
    '''

    f1_score_model = []
    for i in range(0, y_test.shape[1]):
        f1_score_column = f1_score(y_test.iloc[:, i], y_pred[:, i])
        f1_score_model.append(f1_score_column)
        print('The f1 score for', y_test.columns[i], ' was: ', "%.2f" % f1_score_column, '.')

    # return f1_score_model; remove the comment if you want to return the list


def precision_score_labels(y_test, y_pred):
    '''Calculates the precision score for every label and displays the value.
    '''

    precision_score_model = []
    for i in range(0, y_test.shape[1]):
        precision_score_column = precision_score(y_test.iloc[:, i], y_pred[:, i])
        precision_score_model.append(precision_score_column)
        print('The precision score for', y_test.columns[i], ' was: ', "%.2f" % precision_score_column, '.')

    # return precision_score_model; remove the comment if you want to return the list


def accuracy_score_labels(y_test, y_pred):
    '''Calculates the accuracy score for every label and displays the value.
    '''

    accuracy_score_model = []
    for i in range(0, y_test.shape[1]):
        accuracy_score_column = accuracy_score(y_test.iloc[:, i], y_pred[:, i])
        accuracy_score_model.append(accuracy_score_column)
        print('The accuracy score for', y_test.columns[i], ' was: ', "%.2f" % accuracy_score_column, '.')

    # return accuracy_score_model; remove the comment if you want to return the list


def recall_score_labels(y_test, y_pred):
    '''Calculates the accuracy score for every label and displays the value.
    '''

    recall_score_model = []
    for i in range(0, y_test.shape[1]):
        recall_score_column = recall_score(y_test.iloc[:, i], y_pred[:, i])
        recall_score_model.append(recall_score_column)
        print('The recall score for', y_test.columns[i], ' was: ', "%.2f" % recall_score_column, '.')

    # return recall_score_model; remove the comment if you want to return the list


# if you want the score values for just one label run the following functions,
# these functions don't run in the main code.
def AUC_ROC_column(y_test, y_pred, column):
    '''Calculates the area under the ROC curve for the column(label) and displays the value.
    '''
    index = y_test.columns.get_loc(column)
    auc_score_column = roc_auc_score(y_test.iloc[:, index], y_pred[:, index])
    print('The AUC for', column, 'was: ', "%.2f" % auc_score_column, '.')

    # return auc_score_column; remove the comment if you want to return the value


def f1_score_column(y_test, y_pred, column):
    '''Calculates the f1 score for the column(label) and displays the value.
    '''

    index = y_test.columns.get_loc(column)
    f1_score_column = f1_score(y_test.iloc[:, index], y_pred[:, index])
    print('The f1 score for', column, 'was: ', "%.2f" % f1_score_column, '.')

    # return f1_score_column; remove the comment if you want to return the value


def precision_score_column(y_test, y_pred, column):
    '''Calculates the precision score for the column(label) and displays the value.
    '''

    index = y_test.columns.get_loc(column)
    precision_score_column = precision_score(y_test.iloc[:, index], y_pred[:, index])
    print('The precision score for', column, 'was: ', "%.2f" % precision_score_column, '.')

    # return precision_score_column; remove the comment if you want to return the value


def accuracy_score_column(y_test, y_pred, column):
    '''Calculates the accuracy score for the column(label) and displays the value.
    '''

    index = y_test.columns.get_loc(column)
    accuracy_score_column = accuracy_score(y_test.iloc[:, index], y_pred[:, index])
    print('The accuracy score for', column, 'was: ', "%.2f" % accuracy_score_column, '.')

    # return accuracy_score_column; remove the comment if you want to return the value


def recall_score_column(y_test, y_pred, column):
    '''Calculates the accuracy score for the column(label) and displays the value.
    '''

    index = y_test.columns.get_loc(column)
    recall_score_column = recall_score(y_test.iloc[:, index], y_pred[:, index])
    print('The recall score for', column, 'was: ', "%.2f" % recall_score_column, '.')

    # return recall_score_column; remove the comment if you want to return the value

def evaluate_model(model, X_test, y_test):
    y_pred = model.predict(X_test)
    AUC_ROC(y_test,y_pred)
    f1_score_labels(y_test,y_pred)
    precision_score_labels(y_test,y_pred)
    accuracy_score_labels (y_test,y_pred)
    recall_score_labels (y_test,y_pred)
    model_scores(y_test, y_pred)


def save_model(model, model_filepath):
    joblib.dump(model, model_filepath)


def main():
    if len(sys.argv) == 4:
        database_filepath, table_name, model_filepath = sys.argv[1:]
        print('Loading data...\n    DATABASE: {}'.format(database_filepath))
        X, y = load_data(database_filepath, table_name)

        random_state=42
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,random_state=random_state)
        
        print('Building model...')
        model = build_model(X,y)
        
        print('Training model...')
        model.fit(X_train, y_train)
        
        print('Evaluating model...')
        evaluate_model(model, X_test, y_test)

        print('Saving model...\n    MODEL: {}'.format(model_filepath))
        save_model(model, model_filepath)

        print('Trained model saved!')

    else:
        print('Please provide the filepath of the disaster messages database '\
              'as the first argument and the filepath of the pickle file to '\
              'save the model to as the second argument. \n\nExample: python '\
              'train_classifier.py ../data/DisasterResponse.db classifier.pkl')


if __name__ == '__main__':
    main()