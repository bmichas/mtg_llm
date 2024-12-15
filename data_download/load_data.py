import pickle
with open("azorius/decks.pkl", "rb") as fp:   # Unpickling
    b = pickle.load(fp)

print(len(b))