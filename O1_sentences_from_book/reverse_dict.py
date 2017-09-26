
def reverse_dict():
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

def dict_table():
    word_class_dict = {'JJ': ['A'], 'VVZ': ['V'], 'VBP': ['V'], 'NPS': ['PropN'], 'VHG': ['V'], 'PP$': ['Pron'],
                       'RBR': ['Adv'], 'UH': ['I'], 'JJS': ['A'], 'VBD': ['V'], 'WP': ['Pron'], 'VVD': ['V'],
                       'VVN': ['V'],
                       'IN/that': ['Det'], 'IN': ['Prep'], 'VHD': ['V'], 'NN': ['N'], 'PP': ['Pron'], 'VBZ': ['V'],
                       'NP': ['PropN'], 'VV': ['V'], 'VBG': ['V'], 'VVG': ['V'], 'VVP': ['V'], 'VHP': ['V'],
                       'PDT': ['Det'], 'CC': ['Conj'], 'WP$': ['Pron'],
                       'JJR': ['A'], 'VHN': ['V'], 'RBS': ['Adv'], 'VB': ['V'], 'TO': ['V'], 'RB': ['Adv'],
                       'WDT': ['Det'], 'VH': ['V'], 'DT': ['Det'], 'MD': ['V'], 'RP': ['Part'], 'WRB': ['Adv'],
                       'VBN': ['V'], 'VHZ': ['V'], 'NNS': ['N'], 'SENT': ['Punct'], ',': ['Punct'], ':': ['Punct'],
                       'EX': ['Adv'], 'SYM': ['Punct'], '``': ['Punct'], "''": ['Punct'], 'FW': [''], ')': ['Punct'],
                       '(': ['Punct'], '$': ['Punct']}

    for k, val in word_class_dict.items():
        print(k , "&" , val[0] , "\\\\")

if __name__ == '__main__':
    dict_table()