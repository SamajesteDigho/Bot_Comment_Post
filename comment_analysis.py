# -*- coding: utf-8 -*-
"""
Created on Thu Jun  2 12:15:01 2022

@author: DIGHO D. T. Jordan
"""

try:
    import os
    import pandas as pd
    import numpy as np
    import tensorflow as tf
    import tensorflow.keras as keras
    from sklearn.model_selection import train_test_split
except:
    pass

def data_upload():
    imdb_review = pd.read_csv('Dataset/imdb_reviews.csv')
    test_review = pd.read_csv('Dataset/test_reviews.csv')
    
    dataset = pd.concat([imdb_review, test_review], axis=0, ignore_index=True)
    
    return dataset

def word_index():
    word_index = pd.read_csv('Dataset/word_indexes.csv')
    
    # Word index preparation
    word_index = dict(zip(word_index.Words, word_index.Indexes))
    word_index['<PAD>']=0
    word_index['<START']=1
    word_index['<UNK>']=0
    word_index['<UNUSED>']=0
    
    return word_index

def data_preprocessing(dataset):
    
    # Function to encode words to number indexed
    def review_encoder(text):
        arr = [wi[word] for word in text]
        return arr
    
    
    # Preparing the dataset
    # Upload Word Index
    wi = word_index()
    
    # Convert positive to 1 and negatives to 0
    dataset['Sentiment'] = dataset['Sentiment'].apply(lambda x: 1 if x == 'positive' else 0)
    
    # Split comments into list of words
    dataset['Reviews'] = dataset['Reviews'].apply(lambda review: review.split())

    # Convert the list of words to list of numbers for each review
    dataset['Reviews'] = dataset['Reviews'].apply(review_encoder)
    
    X_train, X_test, y_train, y_test = train_test_split(dataset['Reviews'], dataset['Sentiment'], random_state=42, test_size=0.3)
    
    # Last preprocess
    X_train = keras.preprocessing.sequence.pad_sequences(X_train, value=wi["<PAD>"], padding="post", maxlen=500)
    X_test = keras.preprocessing.sequence.pad_sequences(X_test, value=wi["<PAD>"], padding="post", maxlen=500)
    
    return X_train, X_test, y_train, y_test


def Model():
    model = keras.Sequential([keras.layers.Embedding(10000, 16, input_length=500),
                        keras.layers.GlobalAveragePooling1D(),
                        keras.layers.Dense(16, activation='relu'),
                        keras.layers.Dense(1, activation='sigmoid')])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    
    return model

def train_model(model, X_train, y_train, X_test, y_test):
    model.fit(X_train, y_train,
                    epochs=30, batch_size=512,
                    validation_data=(X_test, y_test)
                   )
    loss, accuracy = model.evaluate(X_test, y_test)
    return loss, accuracy

def save_model(model):
    model.save('Model/Sentiment')

def load_model(name='Sentiment'):
    return keras.models.load_model(''.join(['Model/',name]))

def all_process_training():
    data = data_upload();
    X_train, X_test, y_train, y_test = data_preprocessing(data)
    model = Model()
    loss, accuracy = train_model(model, X_train, y_train, X_test, y_test)
    save_model(model)
    
    print("==================================================")
    print('Loss : ', loss)
    print('Accuracy : ', accuracy)

def predict(sentiment=None):
    if check_if_model_exist():
        pass
    else:
        print('Model was not found...')
        print('Now the model is training...')
        all_process_training()
    
    def review_encoder(text):
        arr = []
        for word in text:
            try:
                arr.append(wi[word])
            except:
                pass
        return arr
    
    if sentiment == None or len(sentiment) == 0:
        return False
    
    wi = word_index()
    data = pd.DataFrame([{'Reviews': sentiment}])
    data['Reviews'] = data['Reviews'].apply(lambda review: review.split())
    data['Reviews'] = data['Reviews'].apply(review_encoder)
    """for word in vector:
        try:
            data.append(wi[word])
        except:
            pass"""
    
    print("Vectorizing")
    data = keras.preprocessing.sequence.pad_sequences(data['Reviews'], value=wi["<PAD>"], padding="post", maxlen=500)
    
    """print('Numparize')
    data = np.array([data])
    data = tf.reshape(data, [500,0])
    print("Shape is : ", data.shape)"""
    
    print("Predict")
    # Model loading
    model = load_model()
    if int(model.predict(data) > 0.65):
        return 1
    else:
        return 0    


def check_if_model_exist():
    path = 'Model/Sentiment'
    if os.path.isdir(path):
        return True
    else:
        return False

"""
    Prediction using nltk simply
"""
def simple_predict(text):
    from nltk.sentiment import SentimentIntensityAnalyzer
    sia = SentimentIntensityAnalyzer()
    res = sia.polarity_scores(text)
    
    print(res)
    if res['pos'] >= 0.65:
        return True
    else:
        return False

"""
if __name__ == '__main__':
    predict('<START Bonjour mes amis')
    
"""
13.7.islower()
    