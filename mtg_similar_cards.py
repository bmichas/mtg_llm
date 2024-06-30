import json
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import pickle
from collections import OrderedDict


MTG_DATA_PATH = "data_download/MyDataMTGv2.json"
MTG_DATA_JSON_ENCODING_PATH = "cards_and_encoding.pickle"
MODEL = SentenceTransformer('distilbert-base-nli-mean-tokens')

CARD_NAME = 'Sol Ring'
CARD_NAME = CARD_NAME.lower()

CARDS_NUMBER = 0
NUMBER_OF_SIMILAR_CARDS = 5
SIMILARITY_THRESHOLD = 0.9


class MtgSimiliar:
    def __init__(self,
                 mtg_data,
                 similiar_cards=NUMBER_OF_SIMILAR_CARDS,
                 similarity_threshold=SIMILARITY_THRESHOLD,
                 model=MODEL):

        self.mtg_data = mtg_data
        self.similiar_cards = similiar_cards
        self.similarity_threshold = similarity_threshold
        self.model = MODEL


def print_card_info(mtg_data):
    for card in mtg_data:
        print("card_name=", card)


def get_text_to_encoding(cards, mtg_data):
    cards_and_encoding = {}
    for card in tqdm(cards):
        text_if_none = str(mtg_data[card].get("manaValue"))\
            + str(mtg_data[card].get("toughness"))\
            + str(mtg_data[card].get("power"))\
            + str(mtg_data[card].get("type"))

        cards_and_encoding[card] = MODEL.encode((
                                    mtg_data[card].get(
                                        "text", "") + text_if_none))

    return cards_and_encoding


def load_mtg_json(path):
    with open(path, "r") as file:
        mtg_data = json.load(file)

    print("Cards_number = ", len(mtg_data.keys()))
    if CARDS_NUMBER == 0:
        cards_name = list(mtg_data.keys())
    else:
        cards_name = list(mtg_data.keys())[:CARDS_NUMBER]

    return cards_name, mtg_data


def save_cards_and_encoding(cards_and_encoding):
    with open('cards_and_encoding.pickle', 'wb') as handle:
        pickle.dump(cards_and_encoding,
                    handle,
                    protocol=pickle.HIGHEST_PROTOCOL)


def load_cards_and_encoding(path):
    with open(path, 'rb') as handle:
        cards_and_encoding = pickle.load(handle)

    return cards_and_encoding


def marge_encoding_and_mtg_json(cards, cards_and_encoding, mtg_data):
    mtg_data = {k.lower(): v for k, v in mtg_data.items()}
    cards_and_encoding = {k.lower(): v for k, v in cards_and_encoding.items()}
    cards = [card.lower() for card in cards]

    for card in cards:
        mtg_data[card]['encoding'] = cards_and_encoding[card]

    return mtg_data


def find_similar_cards(card_name,
                       cards_and_encoding,
                       number_of_similar_cards,
                       similarity_threshold):
    encoding1 = cards_and_encoding[card_name]['encoding']
    similiar_cards = {}
    for card in tqdm(cards_and_encoding):
        encoding2 = cards_and_encoding[card]['encoding']
        similarity = np.dot(encoding1, encoding2) \
            / (np.linalg.norm(encoding1) * np.linalg.norm(encoding2))

        if similarity > similarity_threshold:
            similiar_cards[card] = similarity

        ordered_similarity = OrderedDict(sorted(similiar_cards.items()))
        ordered_similiar_cards = list(ordered_similarity.keys())

    print("Card:", card_name)
    print("Similiar card:", ordered_similiar_cards[:number_of_similar_cards])


def main():
    # cards_name, mtg_data = load_mtg_json(MTG_DATA_PATH)
    # cards_and_encoding = get_text_to_encoding(cards_name, mtg_data)
    # encoding_mtg_json = marge_encoding_and_mtg_json(cards_name,
    #                                                 cards_and_encoding,
    #                                                 mtg_data)
    # save_cards_and_encoding(encoding_mtg_json)
    encoding_mtg_json = load_cards_and_encoding(MTG_DATA_JSON_ENCODING_PATH)
    find_similar_cards(CARD_NAME,
                       encoding_mtg_json,
                       NUMBER_OF_SIMILAR_CARDS,
                       SIMILARITY_THRESHOLD)


if __name__ == "__main__":
    main()
