import pickle
import random


COLORS = [
        "mono-white",
        "mono-blue",
        "mono-black",
        "mono-red",
        "mono-green",
        "azorius",
        "dimir",
        "rakdos",
        "gruul",
        "selesnya",
        "orzhov",
        "izzet",
        "golgari",
        "boros",
        "simic",
        "grixis",
        "esper",
        "jund",
        "naya",
        "bant",
        "abzan",
        "jeskai",
        "sultai",
        "mardu",
        "temur"
    ]

TIMES = 50

def load_data(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)

    return data

def save_data(list, name):
    with open(name, 'wb') as f:
        pickle.dump(list, f)

def scramble_and_make_it_bigger(lst_to_scrample, times):
    sublist = lst_to_scrample[1:]
    scrambled_decks = []
    for _ in range(times):
        random.shuffle(sublist)
        scrambled = [lst_to_scrample[0]] + sublist
        scrambled_decks.append(scrambled)

    return scrambled_decks


def main():
    all_decks = []
    for color in COLORS:
        path = "25deck/" + color + "/decks.pkl"
        decks_from_color = load_data(path)
        for deck in decks_from_color:
            scrambled = scramble_and_make_it_bigger(deck, TIMES)
            all_decks += scrambled

    save_data(all_decks, "mtg_decks.pkl")


if __name__ == "__main__":
    main()
