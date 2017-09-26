import xml.etree.ElementTree as ET
import treetaggerwrapper
import csv
import nltk
import re

tree_b1 = ET.parse('book_1_edit_wo_delete.xml')
root_b1 = tree_b1.getroot()

tree_b2 = ET.parse('book_2_edit_wo_delete.xml')
root_b2 = tree_b2.getroot()

tree_b3 = ET.parse('book_3_edit_wo_delete.xml')
root_b3 = tree_b3.getroot()

sent_id = 1

tagger = treetaggerwrapper.TreeTagger(TAGLANG='en')

# 'NVVC': ['Pron', 'N', 'NVC', 'VVC'],
word_class_dict = {'JJ': ['A'], 'VVZ': ['V'], 'VBP': ['V'], 'NPS': ['PropN'], 'VHG': ['V'], 'PP$': ['Pron'],
                   'RBR': ['Adv'], 'UH': ['I'], 'JJS': ['A'], 'VBD': ['V'], 'WP': ['Pron'], 'VVD': ['V'], 'VVN': ['V'],
                   'IN/that': ['Det'], 'IN': ['Prep'], 'VHD': ['V'], 'NN': ['N'], 'PP': ['Pron'], 'VBZ': ['V'],
                   'NP': ['PropN'], 'VV': ['V'], 'VBG': ['V'], 'VVG': ['V'], 'VVP': ['V'], 'VHP': ['V'],
                   'PDT': ['Det'], 'CC': ['Conj'], 'WP$': ['Pron'],
                   'JJR': ['A'], 'VHN': ['V'], 'RBS': ['Adv'], 'VB': ['V'], 'TO': ['V'], 'RB': ['Adv'],
                   'WDT': ['Det'], 'VH': ['V'], 'DT': ['Det'], 'MD': ['V'], 'RP': ['Part'], 'WRB': ['Adv'],
                   'VBN': ['V'], 'VHZ': ['V'], 'NNS': ['N'], 'SENT': ['Punct'], ',': ['Punct'], ':': ['Punct'],
                   'EX': ['Adv'], 'SYM': ['Punct'], '``': ['Punct'], "''": ['Punct'], 'FW': [''], ')': ['Punct'],
                   '(': ['Punct'],'$': ['Punct'], 'VVC': ['VVC'], 'NVC': ['NVC']}


def extract(root, book_nr, msent_id):
    for page in root.findall('page'):
        p = page.get('id')
        chapter = page.find('chapter').text
        sentences = page.findall('sentence')
        # print(p, chapter)
        for s in sentences:
            print(s.text)
            #print(nltk.tokenize.word_tokenize("What's your name"))

            replaced_sent = re.sub("\s*\.\.\.\s*", " ", s.text)
            # replaced_sent = replaced_sent.replace('.', '').replace('?', '').replace('!', '').replace(' …', '')
            # .replace(',', '')

            tagged_list = []
            lemma_list = []
            map_lemma_token = {}
            lemma_tag_list = []
            lemma_simple_tag_list = []

            tags = tagger.tag_text(replaced_sent)
            # print(tags)

            new_tag_array = []
            current_index_position = 0
            for current_word in tags:
                if re.search('\'[a-z]+', current_word):  # apostrophe in word: "n't\tRB\tn't
                    earlier_word = tags[current_index_position - 1]

                    earlier_word = earlier_word.split("\t")
                    tag_earlier_word = earlier_word[1]
                    lemma_earlier_word = earlier_word[2]

                    current_word = current_word.split("\t")
                    tag_current_word = current_word[1]
                    lemma_current_word = current_word[2]

                    combined_word = earlier_word[0] + current_word[0]

                    del new_tag_array[current_index_position - 1]
                    # depending on the combination put together
                    # verb + verb ends with 've
                    print(current_word)
                    print(earlier_word)
                    # print(tag_earlier_word)

                    # if m_processed_item in [["on one's own"]]:
                    #    new_tag_array.append(combined_word + '\tPP')

                    # else:
                    # verb + have
                    if current_word[0] == "'ve" and tag_earlier_word.startswith('V'):
                        new_tag_array.append(combined_word + '\tVVC\t' + lemma_earlier_word + " " + lemma_current_word)

                    # x + genitive s
                    elif current_word[0] == "'s" and tag_current_word == 'POS':
                        new_tag_array.append(combined_word + '\t' + tag_earlier_word + '\t' + lemma_earlier_word + " "
                                             + lemma_current_word)

                    # noun/pronoun + would, will, are, have
                    elif current_word[0] in ["'d", "'ll", "'re", "'ve"] \
                            and (tag_earlier_word.startswith('N') or tag_earlier_word.startswith('P')):
                        new_tag_array.append(combined_word + '\tNVC\t' + lemma_earlier_word + " " + lemma_current_word)

                    # verb + negation ends with n't
                    elif current_word[0] == "n't" and tag_earlier_word.startswith(
                            'V') or tag_earlier_word.startswith('MD'):
                        new_tag_array.append(combined_word + '\tVV\t' + lemma_earlier_word + " " + lemma_current_word)

                    # pronoun + am
                    elif current_word[0] == "'m":
                        new_tag_array.append(combined_word + '\tNVC\t' + lemma_earlier_word + " " + lemma_current_word)

                    # w-word/pronoun/there + is
                    elif tag_earlier_word in ['WP', 'WRB', 'DT', 'NN', 'PP',
                                              'EX'] and tag_current_word == 'VBZ':
                        new_tag_array.append(combined_word + '\tNVC\t' + lemma_earlier_word + " " + lemma_current_word)
                    else:
                        raise Exception(
                            "Doesn't fit any category: " + str(replaced_sent) + str(earlier_word) + str(
                                current_word))
                else:
                    new_tag_array.append(current_word)
                current_index_position += 1
            tags = new_tag_array

            for word in tags:
                word_tag_array = word.split('\t')
                token = word_tag_array[0]
                tag = word_tag_array[1]
                lemma = word_tag_array[2]

                # print(word)

                if word == 'me\tFW\tme':
                    tag = 'PP'

                # [('A', 'DT'), ('car', 'NN'), ('.', '.')]
                if tag in ['CD', 'LS']:
                    tagged_list.append((token, tag))
                else:
                    tagged_list.append((token, word_class_dict[tag][0]))

                # ['a', 'car', '.']
                lemma_list.append(lemma)

                # {'.': ['.'], 'a': ['A'], 'car': ['car']}
                if lemma in map_lemma_token:
                    if token not in map_lemma_token[lemma]:
                        map_lemma_token[lemma].append(token)
                else:
                    map_lemma_token[lemma] = [token]

                # [('a', 'DT'), ('car', 'NN'), ('.', '.')]
                if tag in ['CD', 'LS']:
                    lemma_tag_list.append((lemma, tag))
                else:
                    lemma_tag_list.append((lemma, word_class_dict[tag][0]))

            writer.writerow([msent_id, chapter, book_nr, p, s.text, tagged_list, lemma_list, map_lemma_token,
                             lemma_tag_list])
            msent_id += 1
    return msent_id


def main():
    with open('sentences_book.csv', 'w') as outcsv:
        sent_id = 1
        writer = csv.writer(outcsv, delimiter=';')
        writer.writerow(["_id", "Chapter", "Book", "Page", "Sentence", "Tagged", "Lemma", "LemmaToken", "LemmaTag"])

        sent_id = extract(root_b1, "I", sent_id)
        sent_id = extract(root_b2, "II", sent_id)
        extract(root_b3, "III", sent_id)

    outcsv.close()

if __name__ == '__main__':
    with open('sentences_book.csv', 'w') as outcsv:
        writer = csv.writer(outcsv, delimiter=';')
        writer.writerow(["_id", "Chapter", "Book", "Page", "Sentence", "Tagged", "Lemma", "LemmaToken", "LemmaTag"])

        sent_id = extract(root_b1, "I", sent_id)
        sent_id = extract(root_b2, "II", sent_id)
        extract(root_b3, "III", sent_id)

    outcsv.close()