import csv
from operator import itemgetter
from collections import OrderedDict
import dbm
import sys
import json

# 0           | 1       | 2    | 3    | 4            | 5        | 6        | 7
# Vocable+Tag | Chapter | Book | GDEX | LearnerScore | Sentence | Word+Tag | Lemma+Word

# 0   | 1       | 2                 | 3                        | 4                         | 5             |
# _id | Vokabel | processed_vocable | tagged_processed_vocable | processed_vocable_soundex | lemma_vocable |
# 6                    | 7                           | 8            | 9                     |
# tagged_lemma_vocable | simple_tagged_lemma_vocable | Uebersetzung | processed_translation |
# 10                           | 11                            | 12                | 13                       |
# tagged_processed_translation | processed_translation_soundex | lemma_translation | tagged_lemma_translation |
# 14     | 15         | 16   | 17      | 18           | 19      | 20
# Status | Fundstelle | Band | Wortart | Beispielsatz | Hinweis | BookId


# dictionary für sätze
vocable_to_sentence_dictionary = {}
# dictionary für indexed sentences
indexed_sentences = {}

#try:
#    vocable_to_sentence_db = dbm.open('vocable_to_sentence','c')
#except:
#    print("\n\nError: Unable to open db for corpus\n")
#    sys.stderr.write("\n\nError: Unable to open db for corpus\n")
#    sys.exit(1)


# def create_vocable_to_sentence_database():
#     # für satz in alle Sätze
#     #   lege dictionary an für jeden Vocable+Tag-Chapter-Book : GDEX-LearnerScore-Sentence-Word+Tag-Lemma+Word in satz
#     print("------------- Lege 'sentence_dictiobary' an -------------")
#     with open("03_3_calculate_learner_score.csv", 'r') as readsent:
#         m_reader = csv.reader(readsent, delimiter=';')
#         for row in m_reader:
#             vocable_tag = row[0]
#             chapter = row[1]
#             book = row[2]
#             gdex = float(row[3])
#             learner = float(row[4])
#             sentence = row[5]
#             word_tag = row[6]
#             lemma_word = row[7]
#             # In [2]: json.dumps([1, 2, 3])
#             # Out[2]: '[1, 2, 3]'
#             # In [3]: json.loads(json.dumps([1, 2, 3]))
#             # Out[3]: [1, 2, 3]
#             json_key = json.dumps((vocable_tag, chapter, book))
#             if json_key in vocable_to_sentence_db:
#                 jason_value = json.loads(vocable_to_sentence_db[json_key].decode("utf-8"))
#                 print(jason_value)
#                 jason_value = json.dumps(jason_value.append((gdex, learner, sentence, word_tag, lemma_word)))
#                 print(json.loads(jason_value))
#                 vocable_to_sentence_db[json_key] = jason_value
#             else:
#                 vocable_to_sentence_db[json_key] = json.dumps([(gdex, learner, sentence, word_tag, lemma_word)])
#         readsent.close()
#         print(len(vocable_to_sentence_db))
#         print("------------- ende -------------")


def load_sentence_dictionary():
    # für satz in alle Sätze
    #   lege dictionary an für jeden Vocable+Tag-Chapter-Book : GDEX-LearnerScore-Sentence-Word+Tag-Lemma+Word in satz
    print("------------- Lege 'sentence_dictiobary' an -------------")
    with open("./output/03_3_calculate_learner_score.csv", 'r') as readsent:
        m_reader = csv.reader(readsent, delimiter=';')
        for row in m_reader:
            vocable_tag = row[0]
            if vocable_tag == "[('there', 'RB')]":
                print("found")
            chapter = row[1]
            book = row[2]
            gdex = float(row[3])
            learner = float(row[4])
            sentence = row[5]
            word_tag = row[6]
            lemma_word = row[7]
            if (vocable_tag, chapter, book) in vocable_to_sentence_dictionary:
                vocable_to_sentence_dictionary[(vocable_tag, chapter, book)].append((gdex, learner, sentence, word_tag, lemma_word))
            else:
                vocable_to_sentence_dictionary[(vocable_tag, chapter, book)] = [(gdex, learner, sentence, word_tag, lemma_word)]
    readsent.close()
    print(len(vocable_to_sentence_dictionary))
    print("------------- ende -------------")


def get_the_best_sentences():
    # für vokabel( +tag) in vokabelliste
    #   bekomme alle sätze für vokabel( +tag)
    #   sortiere nach gdex
    #       für die besten 5 werte
    #           wenn satz noch nicht in dictionary speichere und merke nummer
    #           wenn bekomme index nummer
    #   sortiere nach learner
    #       für die besten 5 werte
    #           wenn satz noch nicht in dictionary speichere und merke nummer
    #           wenn bekomme index nummer
    #   füge in datei ein
    print("------------- iterate durch vocabulary -------------")
    with open("../O2_match_vocabulary_to_sentences/matched_vocabulary.csv", 'r') as readvoc, \
            open("./output/03_04_vocabulary.csv", 'w') as writevoc:
        m_reader = csv.reader(readvoc, delimiter=';')
        m_writer = csv.writer(writevoc, delimiter=';')

        header = next(m_reader)
        m_writer.writerow(header + ["gdex"] + ["learner"])

        index = 0
        v = 1
        for row in m_reader:
            print("\t", v, "/", 3020)
            if v == 118:
                print(row)
            v += 1
            lemma_tag = row[7]
            chapter = row[15]
            book = row[16]

            gdex_indexed = []
            learner_indexed = []

            all_sentences = vocable_to_sentence_dictionary.get((lemma_tag, chapter, book), [])
            # gdex, learner, sentence, word_tag, lemma_word
            # [(a, b, c, d, e), (a, b, c, d, e), (a, b, c, d, e), ...]

            sorted_after_gdex = sorted(all_sentences, key=itemgetter(0), reverse=True)

            if len(sorted_after_gdex) >= 5:
                primed_gdex_sentences = [sorted_after_gdex[0], sorted_after_gdex[1], sorted_after_gdex[2],
                                         sorted_after_gdex[3], sorted_after_gdex[4]]
                #print(primed_gdex_sentences)
                for item in primed_gdex_sentences:
                    #print("-", item[2])
                    if (item[2], item[3], item[4]) not in indexed_sentences:
                        indexed_sentences[(item[2], item[3], item[4])] = index
                        gdex_indexed.append(index)
                        index += 1
                    else:
                        gdex_indexed.append(indexed_sentences[(item[2], item[3], item[4])])
            else:
                #print(sorted_after_gdex)
                for item in sorted_after_gdex:
                    #print(">", item[2])
                    if (item[2], item[3], item[4]) not in indexed_sentences:
                        indexed_sentences[(item[2], item[3], item[4])] = index
                        gdex_indexed.append(index)
                        index += 1
                    else:
                        gdex_indexed.append(indexed_sentences[(item[2], item[3], item[4])])

            sorted_after_learner = sorted(all_sentences, key=itemgetter(1), reverse=True)

            if len(sorted_after_learner) >= 5:
                primed_learner_sentences = [sorted_after_learner[0], sorted_after_learner[1], sorted_after_learner[2],
                                            sorted_after_learner[3], sorted_after_learner[4]]
                for item in primed_learner_sentences:
                    if (item[2], item[3], item[4]) not in indexed_sentences:
                        indexed_sentences[(item[2], item[3], item[4])] = index
                        learner_indexed.append(index)
                        index += 1
                    else:
                        learner_indexed.append(indexed_sentences[(item[2], item[3], item[4])])
            else:
                for item in sorted_after_learner:
                    if (item[2], item[3], item[4]) not in indexed_sentences:
                        indexed_sentences[(item[2], item[3], item[4])] = index
                        learner_indexed.append(index)
                        index += 1
                    else:
                        learner_indexed.append(indexed_sentences[(item[2], item[3], item[4])])
            print([gdex_indexed], [learner_indexed])
            m_writer.writerow(row + [gdex_indexed] + [learner_indexed])
    readvoc.close()
    writevoc.close()
    print("------------- ende -------------")


def create_sentence_file():
    # für jeden satz in dictionary schreibe zu file
    #   index | satz | Word+Tag | Lemma+Word
    print("------------- iterate durch sentences -------------")
    with open("./output/03_04_sentences.csv", 'w') as writesent:
        m_writer = csv.writer(writesent, delimiter=';')

        m_writer.writerow(["_id"] + ["sentence"] + ["wordTag"] + ["lemmaWord"])

        ordered_indexed_sentences = OrderedDict(sorted(indexed_sentences.items(), key=itemgetter(1)))

        o = len(ordered_indexed_sentences)
        i = 1
        for key, value in ordered_indexed_sentences.items():
            #print(key, value)
            #print("\t", i, "/", o)
            i += 1
            m_writer.writerow([value] + [key[0]] + [key[1]] + [key[2]])
    writesent.close()
    print("------------- ENDE -------------")


if __name__ == '__main__':

    #create_vocable_to_sentence_database()  -- not working
    load_sentence_dictionary()
    get_the_best_sentences()
    create_sentence_file()