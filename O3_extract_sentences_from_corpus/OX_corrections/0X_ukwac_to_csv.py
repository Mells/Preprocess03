from lxml import etree as et
import csv

word_class_dict = {'JJ': 'A', 'VVZ': 'V', 'VBP': 'V', 'NPS': 'PropN', 'VHG': 'V', 'PP$': 'Pron',
                   'RBR': 'Adv', 'UH': 'I', 'JJS': 'A', 'VBD': 'V', 'WP': 'Pron', 'VVD': 'V', 'VVN': 'V',
                   'IN/that': 'Det', 'IN': 'Prep', 'VHD': 'V', 'NN': 'N', 'PP': 'Pron', 'VBZ': 'V',
                   'NP': 'PropN', 'VV': 'V', 'VBG': 'V', 'VVG': 'V', 'VVP': 'V', 'VHP': 'V',
                   'PDT': 'Det', 'CC': 'Conj', 'WP$': 'Pron',
                   'JJR': 'A', 'VHN': 'V', 'RBS': 'Adv', 'VB': 'V', 'TO': 'V', 'RB': 'Adv',
                   'WDT': 'Det', 'VH': 'V', 'DT': 'Det', 'MD': 'V', 'RP': 'Part', 'WRB': 'Adv',
                   'VBN': 'V', 'VHZ': 'V', 'NNS': 'N', 'SENT': 'Punct', ',': 'Punct', ':': 'Punct',
                   'EX': 'Adv', 'SYM': 'Punct', '``': 'Punct', "''": 'Punct', 'FW': '', ')': 'Punct',
                   '(': 'Punct', '$': 'Punct', '#': 'Punct', 'CD': 'CD', 'POS': 'G', 'LS': 'LS'}


def import_as_csv():

    sent_parser = et.XMLParser(encoding='iso-8859-5', recover=True)
    sent_tree = et.parse("ukwac1_fixed.xml", sent_parser)
    sent_root = sent_tree.getroot()

    max_text = len(sent_root.findall('text'))
    index = 1

    with open("ukwac_as_csv.csv", 'w', encoding='iso-8859-5') as s_writer:

        s_w = csv.writer(s_writer, delimiter=';')

        for txt in sent_root.findall('text'):
            print(index, ' - ', max_text)
            for sent in txt.findall('s'):
                # if index == 85087 or index == 85088:
                #    print(sent.text)
                new_row_string = ""
                simple_lemma_tag_tuple = []
                voc_lemma = {}
                # normal_lemma_tag_tuple = []
                word_list = []
                line = sent.text.split('\n')
                for word_arguments in line:
                    #print(word_arguments)
                    # used	use	VVD	8	5	PMOD
                    if isinstance(word_arguments, list):
                        continue
                    word_arguments = word_arguments.split('\t')
                    if word_arguments == [''] or word_arguments == ['        ']:
                        pass
                    else:
                        #print(word_arguments)
                        if len(word_arguments) == 6:
                            word = word_arguments[0].strip()
                            lemma = word_arguments[1].strip()
                            pos = word_class_dict[word_arguments[2]]

                            # simple tag
                            #if pos.startswith('V') or \
                            #        pos.startswith('J') or \
                            #        pos.startswith('RB') or \
                            #        pos.startswith('N'):
                            #    new_pos = pos[:2]
                            #    word_list.append(word)
                            #    simple_lemma_tag_tuple.append((lemma, new_pos))
                            #else:
                            #    word_list.append(word)
                            #    simple_lemma_tag_tuple.append((lemma, pos))
                            word_list.append(word)
                            simple_lemma_tag_tuple.append((lemma, pos))
                            # vocable-lemma dictionary

                            if lemma in voc_lemma:
                                if word not in voc_lemma[lemma]:
                                    voc_lemma[lemma].append(word)
                            else:
                                voc_lemma[lemma] = [word]

                            # normal_lemma_tag_tuple.append((lemma, pos))

                if len(word_list) < 21:
                    new_row_string += " ".join(word_list) + "\n"
                    new_row_string = new_row_string.replace(' ,', ',').replace(' \.', '\.').replace(' ;', ';')\
                        .replace(' ?', '?').replace(' !', '!').replace(' :', ':').strip()
                    new_row_string = new_row_string.replace(' \'s', '\'s').replace('\'ll', '\'ll').replace(' \'re', '\'re')\
                        .replace(' n\t', 'n\t').replace(' \'ve', '\'ve')
                    # s_w.writerow([new_row_string] + [str(normal_lemma_tag_tuple)] + [str(simple_lemma_tag_tuple)])
                    if not new_row_string.isupper():
                        # print(new_row_string, simple_lemma_tag_tuple, voc_lemma, "\n")
                        s_w.writerow([new_row_string] + [str(simple_lemma_tag_tuple)] + [str(voc_lemma)])
            index += 1


def delete_double_lines():
    uniqlines = set(open('ukwac_as_csv.csv', 'r', encoding='iso-8859-5').readlines())

    open('ukwac_as_csv_fixed.csv', 'w', encoding='iso-8859-5').writelines(set(uniqlines))


if __name__ == '__main__':
    import_as_csv()
    delete_double_lines()
