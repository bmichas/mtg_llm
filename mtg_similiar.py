import numpy as np
from collections import OrderedDict
import pickle
import os
from itertools import islice


MTG_DATA_PATH = "data_download/MyDataMTGv2.json"
MTG_DATA_JSON_ENCODING_PATH = "cards_and_encoding.pickle"

CARD_NAME = 'Sol Ring'
CARD_NAME = CARD_NAME.lower()

CARDS_NUMBER = 0
NUMBER_OF_SIMILAR_CARDS = 5
SIMILARITY_THRESHOLD = 0.8


class MtgSimiliar:
    def __init__(self,
                 similiar_cards=NUMBER_OF_SIMILAR_CARDS,
                 similarity_threshold=SIMILARITY_THRESHOLD):

        self.similiar_cards = similiar_cards
        self.similarity_threshold = similarity_threshold

    def __get_data(self, data_path):
        with open(data_path, 'rb') as f:
            return pickle.load(f)

    def __get_cards_with_same_type(self, mtg_data, card_name):
        list_of_card_types = mtg_data[card_name]["types"]
        cards = []
        for card in mtg_data:
            is_card_type_in_types = True
            for type in list_of_card_types:
                if type not in mtg_data[card]["types"]:
                    is_card_type_in_types = False

            if is_card_type_in_types:
                cards.append(card)

        return cards

    def find_similar_cards(self,
                           card_name,
                           mtg_data_path):

        mtg_data = self.__get_data(mtg_data_path)
        same_type_mtg_cards = self.__get_cards_with_same_type(mtg_data,
                                                              card_name)
        encoding1 = mtg_data[card_name]["encoding"]
        similiar_cards = {}
        for card in same_type_mtg_cards:
            encoding2 = mtg_data[card]["encoding"]
            similarity = np.dot(encoding1, encoding2) \
                / (np.linalg.norm(encoding1) * np.linalg.norm(encoding2))

            if similarity > self.similarity_threshold:
                similiar_cards[card] = similarity

            ordered_similarity = OrderedDict(reversed(sorted(similiar_cards.items())))

        if CARD_NAME in ordered_similarity:
            ordered_similarity.pop(CARD_NAME)

        for card in islice(ordered_similarity, self.similiar_cards):
            print(f"Card:{card}, similarity:{ordered_similarity[card]}")    


def main():
    directory_path = "data/"
    files = [f for f in os.listdir(directory_path)
             if os.path.isfile(os.path.join(directory_path, f))]

    mtg_similar = MtgSimiliar()
    for file in files:
        directory_path = "data/" + file
        print("Model:", file)
        mtg_similar.find_similar_cards(CARD_NAME, directory_path)
        print("="*40)


if __name__ == "__main__":
    main()
