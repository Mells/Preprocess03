import csv
import ast


def main():
    with open("../O1_sentences_from_book/sentences_book.csv", 'r') as sentin,\
            open('../O0_preprocess_vocabulary/updated_vocabulary.csv', 'r') as vocin:
        with open("matched_vocabulary.csv", 'w') as vocout, open("not_matched.csv", 'w') as nmatched:

            found = 0
            not_found = 0

            sentreader = csv.reader(sentin, delimiter=';')
            vocreader = csv.reader(vocin, delimiter=';')
            vocwriter = csv.writer(vocout, delimiter=';')
            no_matched = csv.writer(nmatched, delimiter=';')

            old_header = next(vocreader)
            vocwriter.writerow(old_header[0:] + ["BookId"])

            next(sentreader)

            # 0   | 1       | 2         | 3      | 4       | 5     | 6            | 7      | 8            | 9            |
            # _id | Vokabel | processed | tagged | soundex | lemma | tagged_lemma | simple | Uebersetzung | translation  |
            #  10    | 11      | 12    | 13           | 14     | 15         | 16   | 17      | 18           | 19
            # tagged | soundex | lemma | tagged_lemma | Status | Fundstelle | Band | Wortart | Beispielsatz | Hinweis

            for v_row in vocreader:
                v_lemma_tag_list = ast.literal_eval(v_row[7])
                # [('welcome', ['A']), ('to', ['V']), ('Camden', ['PropN']), ('town', ['N'])]
                sent_id_list = []
                # sent_id_list_all = []
                print(v_row[0], v_lemma_tag_list)
                if isinstance(v_lemma_tag_list[0], list):
                    # [[('have', 'VH'), ('a', 'DT'), ('shower', 'NN')], [('take', 'VV'), ('a', 'DT'), ('shower', 'NN')]]
                    for v_list in v_lemma_tag_list:
                        # [('have', 'VH'), ('a', 'DT'), ('shower', 'NN')]
                        for s_row in sentreader:
                            s_lemma_tag_list = ast.literal_eval(s_row[8])
                            # [('first', 'RB'), ('he', 'PP'), ('want', 'VVD'), ('to', 'TO'),
                            # ('have', 'VH'), ('a', 'DT'), ('shower', 'NN'), ...]
                            if set(v_list) < set(s_lemma_tag_list):
                                # sent_id_list_all.append(s_row[0])
                                # delete the exercise number if present so that it matches the sentences exclude 'welcome'
                                # 3/C11 -> 3/C
                                if v_row[15] == 'Welcome':
                                    chapter = v_row[15]
                                elif len(v_row[15]) > 3:
                                    chapter = v_row[15][:3]
                                else:
                                    chapter = v_row[15]

                                # match book and chapter
                                if v_row[16] == s_row[2] and chapter == s_row[1]:
                                    sent_id_list.append(s_row[0])
                        sentin.seek(0)
                        next(sentreader)

                else:
                    # [('welcome', ['A']), ('to', ['V']), ('Camden', ['PropN']), ('town', ['N'])]
                    for s_row in sentreader:

                        # 0   | 1       | 2    | 3    | 4        | 5      | 6     | 7          | 8
                        # _id | Chapter | Book | Page | Sentence | Tagged | Lemma | LemmaToken | LemmaTag

                        s_lemma_tag_list = ast.literal_eval(s_row[8])
                        # [('a', ['Det']), ('car', ['N'])]

                        if set(v_lemma_tag_list) < set(s_lemma_tag_list):
                            # sent_id_list_all.append(s_row[0])
                            # delete the exercise number if present so that it matches the sentences exclude 'welcome'
                            # 3/C11 -> 3/C (welcome -> wel)
                            if v_row[15] == 'Welcome':
                                chapter = v_row[15]
                            elif len(v_row[15]) > 3:
                                chapter = v_row[15][:3]
                            else:
                                chapter = v_row[15]

                            # match book and chapter
                            if v_row[16] == s_row[2] and chapter == s_row[1]:
                                sent_id_list.append(s_row[0])
                    sentin.seek(0)
                    next(sentreader)

                sent_id_list = list(set(sent_id_list))
                # sent_id_list_all = list(set(sent_id_list_all))
                print(sent_id_list)
                # print(sent_id_list_all)
                if sent_id_list:
                    found += 1
                else:
                    not_found += 1
                    no_matched.writerow(v_row[0:2])
                vocwriter.writerow(v_row[0:] + [sent_id_list])
        print("found:", found)
        print("not found:", not_found)

if __name__ == '__main__':
    main()