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


def load_sentence_dictionary():
    # für satz in alle Sätze
    #   lege dictionary an für jeden Vocable+Tag-Chapter-Book : GDEX-LearnerScore-Sentence-Word+Tag-Lemma+Word in satz
    print("------------- Lege 'sentence_dictiobary' an -------------")
    with open("./output/03_3_calculate_learner_score.csv", 'r') as readsent:
        m_reader = csv.reader(readsent, delimiter=';')
        for row in m_reader:
            vocable_tag = row[0]
            # if vocable_tag == "[('there', 'RB')]":
            #    print("found")
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


def create_vocabulary_with_best_sentences():
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
            # print("\t", v, "/", 3020)
            # if v == 118:
            #    print(row)
            v += 1
            lemma_tag = row[7]
            chapter = row[15]
            book = row[16]

            gdex_indexed = []
            learner_indexed = []
            gdex_value = []
            learner_value = []

            # all sentences that fit the vocable
            all_sentences = vocable_to_sentence_dictionary.get((lemma_tag, chapter, book), [])
            # gdex, learner, sentence, word_tag, lemma_word
            # [(a, b, c, d, e), (a, b, c, d, e), (a, b, c, d, e), ...]

            # --- GDEX ---
            # sort the sentences after the highest gdex value
            sorted_after_gdex = sorted(all_sentences, key=itemgetter(0), reverse=True)

            # the number of sentences is greater than or equal 5
            if len(sorted_after_gdex) >= 5:
                # take the 5 best sentences
                primed_gdex_sentences = [sorted_after_gdex[0], sorted_after_gdex[1], sorted_after_gdex[2],
                                         sorted_after_gdex[3], sorted_after_gdex[4]]
                for sent in primed_gdex_sentences:
                    # if the sentence was not yet used save it in the dictionary with the index
                    # 2: sentence, 3: word_tag, 4: lemma_word
                    if (sent[2], sent[3], sent[4]) not in indexed_sentences:
                        indexed_sentences[(sent[2], sent[3], sent[4])] = index
                        gdex_indexed.append(index)
                        gdex_value.append(sent[0])
                        index += 1
                    else:
                        # the sentence was already used at least once add the index to the list
                        gdex_indexed.append(indexed_sentences[(sent[2], sent[3], sent[4])])
                        gdex_value.append(sent[0])
            # the number of sentences is smaller than 5
            else:
                for sent in sorted_after_gdex:
                    # if the sentence was not yet used save it in the dictionary with the index
                    # 2: sentence, 3: word_tag, 4: lemma_word
                    if (sent[2], sent[3], sent[4]) not in indexed_sentences:
                        indexed_sentences[(sent[2], sent[3], sent[4])] = index
                        gdex_indexed.append(index)
                        gdex_value.append(sent[0])
                        index += 1
                    else:
                        # the sentence was already used at least once add the index to the list
                        gdex_indexed.append(indexed_sentences[(sent[2], sent[3], sent[4])])
                        gdex_value.append(sent[0])

            # --- LEARNER ---
            # sort the sentences after the highest learner value
            sorted_after_learner = sorted(all_sentences, key=itemgetter(1), reverse=True)

            # the number of sentences is greater than or equal 5
            if len(sorted_after_learner) >= 5:
                # take the 5 best sentences
                primed_learner_sentences = [sorted_after_learner[0], sorted_after_learner[1], sorted_after_learner[2],
                                            sorted_after_learner[3], sorted_after_learner[4]]
                for item in primed_learner_sentences:
                    # if the sentence was not yet used save it in the dictionary with the index
                    # 2: sentence, 3: word_tag, 4: lemma_word
                    if (item[2], item[3], item[4]) not in indexed_sentences:
                        indexed_sentences[(item[2], item[3], item[4])] = index
                        learner_indexed.append(index)
                        learner_value.append(sent[1])
                        index += 1
                    else:
                        # the sentence was already used at least once add the index to the list
                        learner_indexed.append(indexed_sentences[(item[2], item[3], item[4])])
                        learner_value.append(sent[1])
            else:
                for item in sorted_after_learner:
                    # if the sentence was not yet used save it in the dictionary with the index
                    # 2: sentence, 3: word_tag, 4: lemma_word
                    if (item[2], item[3], item[4]) not in indexed_sentences:
                        indexed_sentences[(item[2], item[3], item[4])] = index
                        learner_indexed.append(index)
                        learner_value.append(sent[1])
                        index += 1
                    else:
                        # the sentence was already used at least once add the index to the list
                        learner_indexed.append(indexed_sentences[(item[2], item[3], item[4])])
                        learner_value.append(sent[1])

            print(row[1], [gdex_indexed], [learner_indexed])
            print(row[1], gdex_value, learner_value)
            m_writer.writerow(row + [gdex_indexed] + [learner_indexed])
    readvoc.close()
    writevoc.close()
    print("------------- ende -------------")


def create_sentence_file():
    # für jeden satz in dictionary schreibe zu file
    #   index | satz | Word+Tag | Lemma+Word
    print("------------- iterate durch sentences -------------")
    with open("./output/03_04_sentences.csv", 'w') as write_sent:
        m_writer = csv.writer(write_sent, delimiter=';')

        m_writer.writerow(["_id"] + ["sentence"] + ["wordTag"] + ["lemmaWord"])

        ordered_indexed_sentences = OrderedDict(sorted(indexed_sentences.items(), key=itemgetter(1)))

        o = len(ordered_indexed_sentences)
        i = 1
        for key, value in ordered_indexed_sentences.items():
            # print(key, value)
            # print("\t", i, "/", o)
            i += 1
            m_writer.writerow([value] + [key[0]] + [key[1]] + [key[2]])
    write_sent.close()
    print("------------- ENDE -------------")


def test_sentence_file():
    with open("./output/03_0x_test_sentences.txt", 'w') as write_sent:

        ordered_indexed_sentences = OrderedDict(sorted(indexed_sentences.items(), key=itemgetter(1)))

        for key, value in ordered_indexed_sentences.items():
            write_sent.write(key[0]+"\n")
    write_sent.close()


def main():
    load_sentence_dictionary()
    create_vocabulary_with_best_sentences()
    create_sentence_file()
    # just to see which sentences are the best
    test_sentence_file()


if __name__ == '__main__':

    load_sentence_dictionary()
    create_vocabulary_with_best_sentences()
    create_sentence_file()
    # just to see which sentences are the best
    test_sentence_file()
