import json
from tqdm import tqdm


keys_to_remove = ['artist', 'artistIds', 'boosterTypes', 'borderColor', 'finishes', 'flavorText', 'foreignData', 'frameVersion', 'hasFoil', 'hasNonFoil', 'identifiers', 'isReprint', 'language', 'layout', 'legalities', 'number', 'originalText', 'originalType', 'printings', 'purchaseUrls', 'rulings', 'setCode', 'sourceProducts', 'uuid', 'availability']

with open('AllIdentifiers.json','r',encoding='UTF-8') as f:
    data = json.loads(f.read())

counter = 0
error_counter = 0
breaker = float('inf')

card_dictionary = {}
list_name = []
for card in data['data']:
    if counter == breaker:
        break
    
    try:
        card_language = data['data'][card]['language']
        card_legality = data['data'][card]['legalities']['commander']
        if card_language == 'English' and card_legality == 'Legal':
            clear_card = data['data'][card]
            for key in keys_to_remove:
                if key in clear_card:
                    del clear_card[key]

            card_dictionary[card]= clear_card
            card_name = data['data'][card]['name']
            list_name.append(card_name)
    
    except KeyError:
        pass
            
    counter += 1
                
print(len(card_dictionary))
print(len(set(list_name)))


clear_card_dictionary = {}
for name in tqdm(set(list_name)):
    for card in card_dictionary:
        if name == card_dictionary[card]['name']:
            clear_card_dictionary[name] = card_dictionary[card]
            clear_card_dictionary[name]['name'] = card
            break

print(len(clear_card_dictionary))
json_object = json.dumps(clear_card_dictionary, indent=4)
with open('MyDataMTGv2.json', 'w') as outfile:
    outfile.write(json_object)