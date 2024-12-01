import pandas as pd
import pickle
import os
import tensorflow as tf
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.preprocessing.sequence import pad_sequences


MTG_DATA_SET_PATH = 'data_download/MyDataMTGv2.json'
TOKENIZER_PATH = "./models/tokenizer.pkl"
MODELS_PATH = "./models"
OUTPUT_FILENAME = 'mtg_similar.csv'
MODELS_NAMES = ["lstm"]
QUERY_DESCRIPTIONS = ['Sol Ring', 'Structural Assault', 'Crossbow Ambush', 'Mephitic Draught', 'Sangromancer', 'Propaganda', 'Rhystic Study']
MAX_LEN_NAME = 10 
MAX_LEN_DESCRIPTION = 50
EMBEDDING_DIM = 512
CARDS_TO_PREDICT = 50
TOP_CARDS = 5
SAME_TYPE = True


def compute_embeddings(descriptions, tokenizer, encoder):
    sequences = tokenizer.texts_to_sequences(descriptions)
    padded_seqs = pad_sequences(sequences, maxlen=MAX_LEN_DESCRIPTION, padding='post')
    return encoder.predict(padded_seqs)


def get_card_description(querry, card_names, card_descriptions):
    index = np.where(card_names == querry)[0]
    if index.size > 0:
        return card_descriptions[index][0]
    
    return querry


def get_card_name(querry, card_names, card_descriptions):
    card_index = np.where(card_descriptions == querry)[0][0]
    return card_names[card_index]


def find_similar_cards(tokenizer, encoder, querry, card_name, card_descriptions, card_embeddings, top_n=3):
    card_description = get_card_description(querry, card_name, card_descriptions)
    query_embedding = compute_embeddings([card_description], tokenizer, encoder)[0]
    similarities = cosine_similarity([query_embedding], card_embeddings)[0]
    similar_indices = similarities.argsort()[-top_n:][::-1]
    return [(card_descriptions[i], similarities[i]) for i in similar_indices]


def load_model(name, path=MODELS_PATH):
    return tf.keras.models.load_model(os.path.join(path, f"{name}.keras"))


def load_tokenizer(path='./models/tokenizer.pkl'):
    with open(path, 'rb') as f:
        tokenizer = pickle.load(f)
    return tokenizer


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


def load_json(path):
    with open(path) as json_file:
        return json.load(json_file)


def main():
    card_names, card_descriptions = load_dataset(MTG_DATA_SET_PATH)
    tokenizer = load_tokenizer(TOKENIZER_PATH)
    mtg_json = load_json(MTG_DATA_SET_PATH)
    model_predictions = []
    for i in range(len(MODELS_NAMES)):
        autoencoder_name = MODELS_NAMES[i] + "_autoencoder"
        encoder_name = MODELS_NAMES[i] + "_encoder"
        autoencoder = load_model(autoencoder_name)
        encoder = load_model(encoder_name)
        # print(autoencoder.summary(), encoder.summary())
        card_embeddings = compute_embeddings(card_descriptions, tokenizer, encoder)
        for query_description in QUERY_DESCRIPTIONS:
            card_predictions = [MODELS_NAMES[i], query_description, mtg_json[query_description]["text"]]
            similar_cards = set(find_similar_cards(tokenizer, encoder, query_description, card_names, card_descriptions, card_embeddings, CARDS_TO_PREDICT))
            card_counter = 0
            for desc, score in similar_cards:        
                card_name = get_card_name(desc, card_names, card_descriptions)
                if card_name == query_description and (mtg_json[query_description]["types"][0] == mtg_json[card_name]["types"][0]):
                    continue
                
                if mtg_json[query_description]["types"][0] == mtg_json[card_name]["types"][0] or not(SAME_TYPE):
                    if card_counter == TOP_CARDS:
                        break
                    
                    card = card_name + ": " + mtg_json[card_name]["text"]
                    card_predictions.append(card)
                    card_counter += 1

            model_predictions.append(card_predictions)

    columns = ['Model Name', 'Card Name', 'Card Description'] + [f'Similar Card {i+1}' for i in range(TOP_CARDS)]
    df = pd.DataFrame(model_predictions, columns=columns)
    df.to_csv(OUTPUT_FILENAME, index=False)
    print("DONE")


if __name__ == "__main__":
    main()