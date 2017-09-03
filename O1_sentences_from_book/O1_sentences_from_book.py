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

word_class_dict = {'JJ': ['A'], 'VVZ': ['V'], 'VBP': ['V'], 'NPS': ['PropN'], 'VHG': ['V'], 'PP$': ['Pron'],
                   'RBR': ['Adv'], 'UH': ['I'], 'JJS': ['A'], 'VBD': ['V'], 'WP': ['Pron'], 'VVD': ['V'], 'VVN': ['V'],
                   'IN/that': ['Det'], 'IN': ['Prep'], 'VHD': ['V'], 'NN': ['N'], 'PP': ['Pron'], 'VBZ': ['V'],
                   'NP': ['PropN'], 'VV': ['V'], 'VBG': ['V'], 'VVG': ['V'], 'VVP': ['V'], 'VHP': ['V'],
                   'NVVC': ['Pron', 'N', 'NVC', 'VVC'], 'PDT': ['Det'], 'CC': ['Conj'], 'WP$': ['Pron'],
                   'JJR': ['A'], 'VHN': ['V'], 'RBS': ['Adv'], 'VB': ['V'], 'TO': ['V'], 'RB': ['Adv'],
                   'WDT': ['Det'], 'VH': ['V'], 'DT': ['Det'], 'MD': ['V'], 'RP': ['Part'], 'WRB': ['Adv'],
                   'VBN': ['V'], 'VHZ': ['V'], 'NNS': ['N'], 'SENT': ['Punct'], ',': ['Punct'], ':': ['Punct'],
                   'EX': ['Adv'], 'SYM': ['Punct'], '``': ['Punct'], "''": ['Punct'], 'FW': [''], ')': ['Punct'],
                   '(': ['Punct'],'$': ['Punct']}


def extract(root, book_nr, msent_id):
    for page in root.findall('page'):
        p = page.get('id')
        chapter = page.find('chapter').text
        sentence = page.findall('sentence')
        # print(p, chapter)
        for s in sentence:
            # print(s.text)
            #print(nltk.tokenize.word_tokenize("What's your name"))

            replaced_sent = re.sub("\s*\.\.\.\s*", " ", s.text)
            replaced_sent = replaced_sent.replace('.', '').replace('?', '').replace('!', '').replace(' …', '').replace(',', '')

            tagged_list = []
            lemma_list = []
            map_lemma_token = {}
            lemma_tag_list = []
            lemma_simple_tag_list = []

            tags = tagger.tag_text(replaced_sent)
            # print(tags)
            for word in tags:
                word_tag_array = word.split('\t')
                token = word_tag_array[0]
                tag = word_tag_array[1]
                lemma = word_tag_array[2]

                if word == 'me\tFW\tme':
                    tag = 'PP'

                # [('A', 'DT'), ('car', 'NN'), ('.', '.')]
                if tag == 'CD':
                    tagged_list.append((token, 'CD'))
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
                if tag == 'CD':
                    lemma_tag_list.append((lemma, 'CD'))
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