import json
import pandas as pd
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow.keras.layers import Embedding, LSTM, Bidirectional, Dense, Input, TimeDistributed, Add
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam

def load_dataset(path):
    df = pd.read_json(path).T
    df['text'] = df['text'].astype(str).fillna('text')
    df['manaValue'] = df['manaValue'].astype(str).fillna('manaValue')
    df['toughness'] = df['toughness'].astype(str).fillna('toughness')
    df['power'] = df['power'].astype(str).fillna('power')
    df['type'] = df['type'].astype(str).fillna('type')
    df['description'] = df['text'] + '' + df['manaValue'] + '' + df['toughness'] + '' + df['power'] + '' + df['type']
    df_filtered = df[['description']].reset_index()
    df_filtered.rename(columns={'index': 'card_name'}, inplace=True)
    return df_filtered['card_name'].values, df_filtered['description'].values

def prepare_tokenizer(descriptions):
    tokenizer = Tokenizer(char_level=True,
                          lower=True,
                          filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n')
    tokenizer.fit_on_texts(descriptions)
    return tokenizer

def encode_data(tokenizer, descriptions, cardnames):
    encoded_descriptions = tokenizer.texts_to_sequences(descriptions)
    encoded_descriptions = pad_sequences(encoded_descriptions, padding='post')

    label_encoder = LabelEncoder()
    encoded_cardnames = label_encoder.fit_transform(cardnames)

    return encoded_descriptions, encoded_cardnames, tokenizer, label_encoder

def prepare_mtg_data(filepath):
    cardnames, descriptions = load_dataset(filepath)
    tokenizer = prepare_tokenizer(descriptions)
    encoded_descriptions, encoded_cardnames, tokenizer, label_encoder = encode_data(
        tokenizer, descriptions, cardnames
    )
    sequence_length = max(len(seq) for seq in encoded_descriptions)
    return encoded_descriptions, encoded_cardnames, tokenizer, label_encoder, sequence_length

filepath = 'data_download/MyDataMTGv2.json'
encoded_descriptions, encoded_cardnames, tokenizer, label_encoder, sequence_length = prepare_mtg_data(filepath)
vocab_size = len(tokenizer.word_index) + 1

print(f'Word count in tokenizer: {vocab_size}')
print(f'Sequence len: {sequence_length}')
print(f'Encoded descriptions shape: {encoded_descriptions.shape}')
print(f'Encoded card names shape: {encoded_cardnames.shape}')

################################################################
#MODEL CREATION
################################################################

class CharacterEmbeddingLayer(tf.keras.layers.Layer):
    def __init__(self, vocab_size, embedding_dim, **kwargs):
        super(CharacterEmbeddingLayer, self).__init__(**kwargs)
        self.embedding_dim = embedding_dim
        self.vocab_size = vocab_size

    def build(self, input_shape):
        self.embedding = self.add_weight(
            shape=(self.vocab_size, self.embedding_dim),
            initializer='uniform',
            trainable=True,
            name='character_embedding'
        )
        super(CharacterEmbeddingLayer, self).build(input_shape)

    def call(self, inputs):
        return tf.nn.embedding_lookup(self.embedding, inputs)

class BiLSTMLayer(tf.keras.layers.Layer):
    def __init__(self, lstm_units, **kwargs):
        super(BiLSTMLayer, self).__init__(**kwargs)
        self.lstm_units = lstm_units

    def build(self, input_shape):
        self.bilstm = Bidirectional(LSTM(self.lstm_units, return_sequences=True))
        super(BiLSTMLayer, self).build(input_shape)

    def call(self, inputs):
        return self.bilstm(inputs)

    def compute_output_shape(self, input_shape):
        return (input_shape[0], input_shape[1], self.lstm_units * 2)

class ELMoModelWithSkip(tf.keras.Model):
    def __init__(self, vocab_size, char_embedding_dim, lstm_units, num_classes, **kwargs):
        super(ELMoModelWithSkip, self).__init__(**kwargs)
        self.char_embedding_layer = CharacterEmbeddingLayer(vocab_size, char_embedding_dim)
        self.bilstm_layer = BiLSTMLayer(lstm_units)
        self.dense_projection = Dense(char_embedding_dim)
        self.output_layer = TimeDistributed(Dense(num_classes, activation='softmax'))

    def build(self, input_shape):
        self.char_embedding_layer.build(input_shape)
        self.bilstm_layer.build(input_shape)
        self.dense_projection.build(self.bilstm_layer.compute_output_shape(input_shape))
        sample_input = tf.keras.layers.Input(shape=input_shape[1:])
        self.output_layer.build(sample_input.shape)
        super(ELMoModelWithSkip, self).build(input_shape)

    def call(self, inputs):
        x = self.char_embedding_layer(inputs)
        lstm_output = self.bilstm_layer(x)
        lstm_output_projected = self.dense_projection(lstm_output)
        x = Add()([x, lstm_output_projected])
        x = self.output_layer(x)
        return x

    def get_embeddings(self, inputs):
        x = self.char_embedding_layer(inputs)
        lstm_output = self.bilstm_layer(x)
        lstm_output_projected = self.dense_projection(lstm_output)
        x = Add()([x, lstm_output_projected])
        return x

elmo_model = ELMoModelWithSkip(vocab_size=vocab_size,
                               char_embedding_dim=50,
                               lstm_units=256,
                               num_classes=vocab_size)

elmo_model.compile(optimizer=Adam(), loss='categorical_crossentropy')

# Model summary
elmo_model.build(input_shape=(None, None, sequence_length))
elmo_model.summary()

################################################################
#TRAINING DATA
################################################################

def generate_training_data(encoded_descriptions, vocab_size):
    X_train = encoded_descriptions[:, :-1]
    Y_train = encoded_descriptions[:, 1:]
    Y_train = np.expand_dims(Y_train, -1)
    return X_train, Y_train

X_train, Y_train = generate_training_data(encoded_descriptions, vocab_size)
print(f'X_train shape {X_train.shape}')
print(f'Y_train shape {Y_train.shape}')

################################################################
#MODEL TRAINING
################################################################

batch_size = 32
epochs = 10
elmo_model.fit(X_train, Y_train, batch_size=batch_size, epochs=epochs)
