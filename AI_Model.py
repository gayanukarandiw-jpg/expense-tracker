from sklearn.metrics import confusion_matrix # To predict Error detection
import pandas as pd # For data handle
from sklearn.feature_extraction.text import CountVectorizer # covert text to numbers
from sklearn.model_selection import train_test_split # to split data, first 70% for training and other 30% for testing
from sklearn.preprocessing import LabelEncoder 
#   from scipy.sparse import hstack
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import pickle
import glob # To combine multiple csv

le = LabelEncoder()
vectorizer = CountVectorizer() # For turn text to numbers for training
all_files = glob.glob('datasets/*.csv')
dfs = []
for files in all_files:
    df = pd.read_csv(files)
    df = df[['Description', 'Category']]
    dfs.append(df)
df = pd.concat(dfs, ignore_index=True)
df.dropna(subset=['Description', 'Category'], inplace=True)
   #df = pd.read_csv('expenses.csv') # Read .csv Data

#   df['Transaction Type'] = le.fit_transform(df['Transaction Type'])  # 0-credit 1-debit

TrainData = vectorizer.fit_transform(df['Description'])
Labels = (df['Category']).values

MODEL = LogisticRegression(max_iter=1000)
train, test, train_labels, test_labels = train_test_split(TrainData, Labels, test_size = 0.30, random_state = 0) # Split data into train/test

NB_Classifier = MODEL.fit(train, train_labels) # Train the Model using train and train_labels

predictions = NB_Classifier.predict(test) # Ai try to predict answers from unseen data
print(predictions)
cm_NBClassifier = confusion_matrix(test_labels, predictions) # Show prediction mistakes(Compare with actual answers[test_labels]
print('Confusion Matrix:', cm_NBClassifier)
print(f'Accuracy:, {(accuracy_score(test_labels, predictions))*100}%') # Calculate Accuracy

# save trained AI model and vectorizer
with open("expense_model.pkl", "wb") as f:
    pickle.dump(MODEL, f)

with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)