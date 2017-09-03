word_class_xtagpenn_dict = {"A": ['JJ', 'JJR', 'JJS'], "Adv": ['RB', 'RBR', 'RBS', 'WRB'], "Conj": ['CC'],
                            "Det": ['DT', 'PDT', 'WDT', 'IN/that'],
                            "N": ['NN', 'NNS', 'NP', 'NVVC'], "Pron": ['PP', 'PP$', 'WP', 'WP$', 'NVVC'],
                            "Prep": ['IN'], "PropN": ['NP', 'NPS'], "I": ['UH'], "Part": ['RP'],
                            "V": ['MD', 'TO', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VH', 'VHD', 'VHG', 'VHN',
                                  'VHP', 'VHZ', 'VV', 'VVD', 'VVG', 'VVN', 'VVP', 'VVZ'],
                            'NVC': ['NVVC'], 'VVC': ['NVVC'], "Punct": ['SENT']}

new_dict = {}

for k, val in word_class_xtagpenn_dict.items():
    for v in val:
        if v in new_dict:
            new_dict[v].append(k)
        else:
            new_dict[v] = [k]

print(new_dict)

