import csv
import ast
from lxml import etree as et
import timeit

if __name__ == "__main__":

    # --------------------------------- LOADING VOCABULARY -----------------------------------------

    print("#### starting loading vocabulary             ####")
    voc_parser = et.XMLParser()
    voc_tree = et.parse("./input/voc.xml", voc_parser)

    voc_root = voc_tree.getroot()
    print("#### finished loading vocabulary             ####")

# --------------------------------- LOADING XML ------------------------------------------------

    print("#### starting loading xml                    ####")
    all_s = []
    #with open('../0X_corrections/test.csv', 'r', encoding='iso-8859-5') as sentin:
    with open('./OX_corrections/ukwac_as_csv_fixed.csv', 'r', encoding='iso-8859-5') as sentin:
        s_reader = csv.reader(sentin, delimiter=';')
        indexed_sentences_with_pos = {}
        indexed_sentences = {}
        sentence_index = 0
        for s_row in s_reader:
            no_duplicate = []
            sentence = []

            # 0        | 1        | 2
            # sentence | lemmatag | lemmavocdict

            s_lemma_tuple = ast.literal_eval(s_row[1])
            for lemma_tuple in s_lemma_tuple:
                lemma = lemma_tuple[0]
                pos = lemma_tuple[1]
                if lemma_tuple not in no_duplicate:
                    no_duplicate.append(lemma_tuple)
                    if lemma_tuple in indexed_sentences_with_pos:
                        indexed_sentences_with_pos[lemma_tuple].append(sentence_index)
                    else:
                        indexed_sentences_with_pos[lemma_tuple] = [sentence_index]
            all_s.append([s_row[0].strip(), s_lemma_tuple, s_row[2]])
            sentence_index += 1
    sentin.close()
    print("#### finished indexing sentences             ####")

    # --------------------------------- ITERATING VOCABULARY ----------------------------------------

    print("#### starting iterating over vocabulary      ####")
    finished_vocable_list = []
    num_voc = 1

    start = timeit.default_timer()

    with open("./output/03_1_sentences_from_corpus.txt", "w") as s_out:
        for xml_voc in voc_root.findall('vocable'):

            voc = xml_voc.get('name')
            voc_as_lemma = xml_voc.find('lemma').get('name')
            chapter = xml_voc.find("chapter").get('name')
            book = xml_voc.find("book").get('name')
            voc_lemma_pos = xml_voc.find("pos").get('name')

            print(num_voc, "/", 3022, " - ", voc_as_lemma)

            lemma_pos_as_list = ast.literal_eval(voc_lemma_pos)

            # [('welcome', 'JJ'), ('to', 'TO')]
            # [[('ca', 'MD'), (n't, 'RB')], [('can', 'MD')], [('can', 'MD'), ('not', 'RB')]]
            if isinstance(lemma_pos_as_list[0], list):
                # eg. [[('ca', 'MD'), (n't, 'RB')], [('can', 'MD')], [('can', 'MD'), ('not', 'RB')]]

                sentence_indexed = []
                half_finished_vocable_list = []

                for lemma_tag_list in lemma_pos_as_list:
                    # [('ca', 'MD'), (n't, 'RB')]
                    sentence_list_1 = []
                    first = True
                    same_indexes = []
                    do_compute = True
                    for lemma_tag_tuple in lemma_tag_list:
                        # ('ca', 'MD')
                        if first:
                            # The method get() returns a value for the given key. If key is not available then returns
                            # default value None.
                            sentence_list_1 = indexed_sentences_with_pos.get(lemma_tag_tuple, [])

                            if not sentence_list_1:
                                do_compute = False
                                break

                            # in case its just one word
                            same_indexes = sentence_list_1
                            first = False
                        else:
                            # The method get() returns a value for the given key. If key is not available then returns
                            # default value None.
                            sentence_list_2 = indexed_sentences_with_pos.get(lemma_tag_tuple, [])

                            if not sentence_list_2:
                                do_compute = False
                                break

                            same_indexes = set(sentence_list_1).intersection(sentence_list_2)
                            sentence_list_1 = same_indexes

                    sentence_indexed.extend(same_indexes)

                    if do_compute:
                        set_index = list(set(sentence_indexed))

                        for index in set_index:
                            half_finished_vocable_list.append((index, chapter, book))

                half_finished_vocable_list = sorted(list(set(half_finished_vocable_list)))

                for indexed_tuple in half_finished_vocable_list:
                    ndx = indexed_tuple[0]
                    chptr = indexed_tuple[1]
                    bk = indexed_tuple[2]
                    sentence = all_s[ndx]
                    s_out.write(str([lemma_pos_as_list, chapter, book, sentence[0], sentence[1], sentence[2]])+"\n")
                    #finished_vocable_list.append([lemma_pos_as_list, chptr, bk,
                    #                              sentence[0], sentence[1], sentence[2]])

                print("\tfound:", len(half_finished_vocable_list))

            else:
                # eg. [('welcome', 'JJ'), ('to', 'TO')]
                sentence_list_1 = []
                first = True
                same_indexes = []
                sentence_indexed = []
                do_compute = True
                for lemma_tag_tuple in lemma_pos_as_list:
                    # ('welcome', 'JJ')
                    if first:
                        # The method get() returns a value for the given key. If key is not available then returns
                        # default value None.
                        sentence_list_1 = indexed_sentences_with_pos.get(lemma_tag_tuple, [])

                        if not sentence_list_1:
                            do_compute = False
                            break

                        # in case its just one word
                        same_indexes = sentence_list_1
                        first = False
                    else:
                        # The method get() returns a value for the given key. If key is not available then returns
                        # default value None.
                        sentence_list_2 = indexed_sentences_with_pos.get(lemma_tag_tuple, [])

                        if not sentence_list_2:
                            do_compute = False
                            break

                        same_indexes = set(sentence_list_1).intersection(sentence_list_2)
                        sentence_list_1 = same_indexes

                sentence_indexed.extend(same_indexes)

                if do_compute:

                    set_index = list(set(sentence_indexed))

                    for index in set_index:
                        sentence = all_s[index]
                        s_out.write(str([lemma_pos_as_list, chapter, book, sentence[0], sentence[1], sentence[2]])+"\n")
                        #finished_vocable_list.append([lemma_pos_as_list, chapter, book, sentence[0], sentence[1], sentence[2]])

                print("\tfound:", len(sentence_indexed))

            num_voc += 1
        s_out.flush()
    print("#### finished iterating over vocabulary      ####")

    #print("#### starting writing to file                ####")
    #with open("03_1_sentences_from_corpus.txt", "w") as s_out:
    #    for found_s in finished_vocable_list:
    #        s_out.write(str(found_s)+"\n")

    #s_out.close()
    #print("#### finished writing to file                ####")

    end = timeit.default_timer()
    run_time = end-start
    print("Time: ", str(run_time))
