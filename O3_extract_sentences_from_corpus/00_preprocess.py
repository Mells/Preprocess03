from lxml import etree as et
import nltk
import xml.etree.cElementTree as ET
import csv
import ast
import time
from nltk import word_tokenize


# necessary for named entity recognition. The xml corpus is reformed into plain text format
def create_text():
    parser = et.XMLParser(encoding='iso-8859-5', recover=True)
    tree = et.parse("../corpora/ukwac1_fixed.xml", parser)

    root = tree.getroot()

    with open("../xml_as_text_for_ner.txt", "w") as txt_out:

        for txt in root.findall('text'):
            for sentence in txt.findall('s'):
                sent = ""

                is_single_open = False

                line = sentence.text.split('\n')

                for word, next_word in zip(line, line[1:] + [line[0]]):
                    if word == '':
                        continue

                    word = word.split('\t')
                    next_word = next_word.split('\t')

                    if next_word[0] in [",", ".", "'", ")"]:
                        sent += word[0]
                    elif next_word[0] == "n't":
                        sent += word[0]
                    elif next_word[0] == "'re":
                        sent += word[0]
                    elif next_word[0] == "'s":
                        sent += word[0]
                    elif next_word[0] == "'ll":
                        sent += word[0]
                    elif next_word[0] == ":":
                        sent += word[0]
                    elif word[0] == "(":
                        sent += word[0]
                    elif word[0] == "'":
                        if is_single_open:
                            sent += word[0] + " "
                            is_single_open = False
                        else:
                            sent += word[0]
                            is_single_open = True
                    else:
                        sent += word[0] + " "
                txt_out.write(sent+"\n")


# creates a vocabulary xml file for easier processing
def create_vocabulary_xml():
    with open("../O2_match_vocabulary_to_sentences/matched_vocabulary.csv", 'r') as voc_in:
        sent_reader = csv.reader(voc_in, delimiter=';')
        next(sent_reader)

        voc_root = ET.Element("root")
        pos_root = ET.Element("root")

        pos_list = []
        for v_row in sent_reader:

            voc_doc = ET.SubElement(voc_root, "vocable", name=v_row[1].replace("\“", "&quot"))
            ET.SubElement(voc_doc, "lemma", name=v_row[5].replace("\“", "&quot"))
            ET.SubElement(voc_doc, "chapter", name=v_row[15])
            ET.SubElement(voc_doc, "book", name=v_row[16])
            ET.SubElement(voc_doc, "pos", name=(str(v_row[7]).replace("\“", "&quot")))

            tuple_pair = ast.literal_eval(v_row[7])
            #print(tuple_pair)
            for tp in tuple_pair:
                if isinstance(tp, list):
                    print(tp)
                    for t in tp:
                        #print(t)
                        pos_list.append((str(t[0]).replace("\“", "&quot"),
                                         str(t[1]).replace("\“", "&quot"),
                                         v_row[15],
                                         v_row[16]))
                else:
                    #print(tp)
                    pos_list.append((str(tp[0]).replace("\“", "&quot"),
                                     str(tp[1]).replace("\“", "&quot"),
                                     v_row[15],
                                     v_row[16]))

    pos_list_set = list(set(pos_list))
    for pos_tuple in pos_list_set:
        pos_doc = ET.SubElement(pos_root, "lemma", name=pos_tuple[0])
        ET.SubElement(pos_doc, "pos", name=pos_tuple[1])
        ET.SubElement(pos_doc, "chapter", name=pos_tuple[2])
        ET.SubElement(pos_doc, "book", name=pos_tuple[3])
    tree_voc = ET.ElementTree(voc_root)
    tree_pos = ET.ElementTree(pos_root)
    tree_voc.write("./input/voc.xml")
    tree_pos.write("./input/lemma_chap_book_pos.xml")
    voc_in.close()

if __name__ == "__main__":
    # create_text()
    create_vocabulary_xml()
