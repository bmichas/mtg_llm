import json
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import pickle


MTG_DATA_PATH = "data_download/MyDataMTGv2.json"
MODELS = ["distilbert-base-nli-mean-tokens",
          "all-MiniLM-L6-v2",
          "all-mpnet-base-v2",
          "paraphrase-multilingual-MiniLM-L12-v2",
          "paraphrase-multilingual-mpnet-base-v2",
          "LaBSE",
          "distiluse-base-multilingual-cased-v2"]

CARDS_NUMBER = 0


def print_card_info(mtg_data):
    for card in mtg_data:
        print("card_name=", card)


def get_text_to_encoding(cards, mtg_data, model_name):
    cards_and_encoding = {}
    model = SentenceTransformer(model_name)
    for card in tqdm(cards):
        text_if_none = str(mtg_data[card].get("manaValue"))\
            + str(mtg_data[card].get("toughness"))\
            + str(mtg_data[card].get("power"))\
            + str(mtg_data[card].get("type"))

        cards_and_encoding[card] = model.encode((
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


def save_cards_and_encoding(cards_and_encoding, file_name):
    with open(file_name, "wb") as outfile:
        pickle.dump(cards_and_encoding, outfile)


def marge_encoding_and_mtg_json(cards, cards_and_encoding, mtg_data):
    mtg_data = {k.lower(): v for k, v in mtg_data.items()}
    cards_and_encoding = {k.lower(): v for k, v in cards_and_encoding.items()}
    cards = [card.lower() for card in cards]

    for card in cards:
        mtg_data[card]['encoding'] = cards_and_encoding[card]

    return mtg_data


def main():
    cards_name, mtg_data = load_mtg_json(MTG_DATA_PATH)
    for model in MODELS:
        print("MODEL:", model)
        cards_and_encoding = get_text_to_encoding(cards_name, mtg_data, model)
        encoding_mtg_json = marge_encoding_and_mtg_json(cards_name,
                                                        cards_and_encoding,
                                                        mtg_data)

        file_name = "data/mtg_" + model + ".pickle"
        save_cards_and_encoding(encoding_mtg_json, file_name)


if __name__ == "__main__":
    main()
