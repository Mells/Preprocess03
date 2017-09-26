from lxml import etree as et
import csv
import re

word_class_dict = {'JJ': 'A', 'VVZ': 'V', 'VBP': 'V', 'NPS': 'PropN', 'VHG': 'V', 'PP$': 'Pron',
                   'RBR': 'Adv', 'UH': 'I', 'JJS': 'A', 'VBD': 'V', 'WP': 'Pron', 'VVD': 'V', 'VVN': 'V',
                   'IN/that': 'Det', 'IN': 'Prep', 'VHD': 'V', 'NN': 'N', 'PP': 'Pron', 'VBZ': 'V',
                   'NP': 'PropN', 'VV': 'V', 'VBG': 'V', 'VVG': 'V', 'VVP': 'V', 'VHP': 'V',
                   'PDT': 'Det', 'CC': 'Conj', 'WP$': 'Pron',
                   'JJR': 'A', 'VHN': 'V', 'RBS': 'Adv', 'VB': 'V', 'TO': 'V', 'RB': 'Adv',
                   'WDT': 'Det', 'VH': 'V', 'DT': 'Det', 'MD': 'V', 'RP': 'Part', 'WRB': 'Adv',
                   'VBN': 'V', 'VHZ': 'V', 'NNS': 'N', 'SENT': 'Punct', ',': 'Punct', ':': 'Punct',
                   'EX': 'Adv', 'SYM': 'Punct', '``': 'Punct', "''": 'Punct', 'FW': '', ')': 'Punct',
                   '(': 'Punct', '$': 'Punct', '#': 'Punct', 'CD': 'CD', 'POS': 'G', 'LS': 'LS', 'VVC': 'VVC',
                   'NVC': 'NVC', 'FW': 'FW'}


def import_as_csv():
    ignored_sentences = 0

    greater_than_20 = 0
    smaller_than_3 = 0
    sentence_is_upper = 0

    sent_parser = et.XMLParser(encoding='iso-8859-5', recover=True)
    sent_tree = et.parse("ukwac1_fixed.xml", sent_parser)
    sent_root = sent_tree.getroot()

    max_text = len(sent_root.findall('text'))
    index = 1

    with open("ukwac_as_csv.csv", 'w', encoding='iso-8859-5') as s_writer:

        s_w = csv.writer(s_writer, delimiter=';')

        for txt in sent_root.findall('text'):
            #print(index, ' - ', max_text)
            for sent in txt.findall('s'):

                new_row_string = ""
                simple_lemma_tag_tuple = []
                map_lemma_token = {}
                word_list = []

                line = sent.text.split('\n')

                tags = []

                for word_arguments in line:
                    # used	use	VVD	8	5	PMOD

                    if word_arguments == '':
                        continue

                    word_arguments = word_arguments.split('\t')

                    w_token = word_arguments[0]
                    try:
                        w_tag = word_arguments[2]
                    except:
                        raise ValueError(word_arguments)
                    w_lemma = word_arguments[1]
                    tags.append(w_token + "\t" + w_tag + "\t" + w_lemma)

                new_tag_array = []
                current_tag_position = 0
                current_new_tag_position = 0
                for current_word in tags:
                    if current_word.startswith(("'ve", "'s", "'d", "'ll", "'re", "'m", "n't")):  # apostrophe in word: "n't\tRB\tn't
                        earlier_word = tags[current_tag_position - 1]

                        earlier_word = earlier_word.split("\t")
                        token_earlier_word = earlier_word[0].replace(u"\x93", "")
                        tag_earlier_word = earlier_word[1]
                        lemma_earlier_word = earlier_word[2]

                        current_word = current_word.split("\t")
                        token_current_word = current_word[0]
                        tag_current_word = current_word[1]
                        lemma_current_word = current_word[2]

                        combined_word = token_earlier_word + token_current_word

                        # depending on the combination put together

                        # verb + have
                        if token_current_word == "'ve" and tag_earlier_word.startswith(('V', 'WP')):
                            new_tag_array.append(
                                combined_word + '\tVVC\t' + lemma_earlier_word + " " + lemma_current_word)

                        # x + genitive s
                        elif token_current_word == "'s" and tag_current_word == 'POS':
                            new_tag_array.append(
                                combined_word + '\t' + tag_earlier_word + '\t' + lemma_earlier_word + " "
                                + lemma_current_word)

                        # noun/pronoun + would, will, are, have
                        elif token_current_word in ["'d", "'ll", "'re", "'ve"] \
                                and (tag_earlier_word.startswith(('N', 'PP', 'W', 'R', 'EX', 'DT'))):
                            new_tag_array.append(
                                combined_word + '\tNVC\t' + lemma_earlier_word + " " + lemma_current_word)

                        # modal verb + have
                        elif tag_earlier_word == 'MD' and tag_current_word.startswith('VH'):
                            new_tag_array.append(combined_word + '\tVVC\t'
                                                 + lemma_earlier_word + " " + lemma_current_word)

                        # verb + negation ends with n't
                        elif token_current_word == "n't" and tag_earlier_word.startswith(('V', 'MD')):
                            new_tag_array.append(
                                combined_word + '\t' + tag_earlier_word + '\t' + lemma_earlier_word + " "
                                + lemma_current_word)

                        # pronoun + am
                        elif token_current_word == "'m":
                            new_tag_array.append(
                                combined_word + '\tNVC\t' + lemma_earlier_word + " " + lemma_current_word)

                        # w-word/pronoun/there + is
                        elif tag_earlier_word.startswith(('W', 'DT', 'N', 'PP', 'V', 'EX', 'RB', 'IN')) \
                                and tag_current_word == 'VBZ':
                            new_tag_array.append(
                                combined_word + '\tNVC\t' + lemma_earlier_word + " " + lemma_current_word)

                        # noun/pronoun/W/there + has
                        elif tag_earlier_word.startswith(('N', 'PP', 'W', 'EX', 'RB', 'DT', 'VV')) and tag_current_word == 'VHZ':
                            new_tag_array.append(
                                combined_word + '\tNVC\t' + lemma_earlier_word + " has")

                        elif re.match("[Ww]o", token_earlier_word) and token_current_word == "n't":
                            new_tag_array.append(
                                combined_word + '\tVV\t' + "will" + " " + "not")

                        elif re.match("[Aa]i", token_earlier_word) and token_current_word == "n't":
                            new_tag_array.append(
                                combined_word + '\tVV\t' + "be" + " " + "not")

                        elif re.match("[Cc]a", token_earlier_word) and token_current_word == "n't":
                            new_tag_array.append(
                                combined_word + '\tVV\t' + "can" + " " + "not")

                        elif re.match("[Hh]av", token_earlier_word) and token_current_word == "n't":
                            new_tag_array.append(
                                "haven't" + '\tVV\t' + "have" + " " + "not")

                        # exception wrongly tagged or old language
                        elif tag_earlier_word.startswith('VV') and token_current_word == "'d":
                            new_tag_array.append("would\tMD\twill")
                            current_tag_position += 1
                            current_new_tag_position += 1
                            continue

                        elif (tag_earlier_word.startswith('JJ') and tag_current_word.startswith(('V', 'RB', 'MD'))) or \
                             (tag_earlier_word == 'CD' and tag_current_word.startswith(('V', 'RB', 'MD'))) or \
                             (tag_earlier_word == 'TO' and tag_current_word.startswith(('V', 'RB', 'MD'))) or \
                             (tag_earlier_word == 'IN' and tag_current_word.startswith(('V', 'RB', 'MD'))) or \
                             (tag_earlier_word == 'CC' and tag_current_word.startswith(('MD', 'RB', 'VB'))) or \
                             (tag_earlier_word.startswith('N') and tag_current_word.startswith(('V', 'RB', 'MD'))) or \
                             (tag_earlier_word == 'RB' and tag_current_word == 'RB') or \
                             (tag_earlier_word == 'UH' and tag_current_word.startswith(('V', 'MD'))) or \
                             (tag_earlier_word == 'FW' and tag_current_word.startswith(('V', 'RB', 'MD'))) or \
                             (tag_earlier_word == 'DT' and tag_current_word.startswith(('NN', 'RB'))) or \
                             (tag_earlier_word == ':' and tag_current_word == 'MD') or \
                             (tag_earlier_word == 'SYM' and tag_current_word.startswith(('VB', 'VH', 'MD'))) or \
                             (tag_earlier_word == 'RP' and tag_current_word.startswith('V')) or \
                             (tag_earlier_word == 'MD' and tag_current_word.startswith(('MD', 'VB'))) or \
                             (tag_earlier_word.startswith(('(', 'CD')) and tag_current_word.startswith(('RB', 'MD'))) or \
                             (tag_earlier_word.startswith('VV') and tag_current_word.startswith('MD')):

                            # ['to', 'TO', 'to']["'s", 'VBZ', 'be']

                            # ['across', 'IN', 'across']["'ll", 'MD', 'will']
                            # ['OK', 'JJ', 'OK']["'d", 'MD', 'will']
                            # ['AND', 'CC', 'and']["'d", 'MD', 'will']

                            # ['ear', 'NN', 'ear']["n't", 'RB', "n't"]
                            # ['Saturday-do', 'NP', 'Saturday-do']["n't", 'RB', "n't"]

                            # ['Ah', 'UH', 'ah']["'ve", 'VHP', 'have']
                            # ['was(', 'JJ', 'was(']["n't", 'RB', "n't"]
                            # ['ex', 'FW', 'ex']["'s", 'VBZ', 'be']
                            # ['the', 'DT', 'the']["n'th", 'NN', "n'th"]

                            # ['-', ':', '-']["'d", 'MD', 'will']
                            # ['if', 'IN', 'if']["'s", 'VHZ', 'have']

                            # ['there/wo', 'RB', 'there/wo']["n't", 'RB', "n't"]
                            # ['e', 'SYM', 'e']["'re", 'VBP', 'be']

                            ignored_sentences += 1
                            break

                        else:
                            raise Exception(
                                str(index) + ": Doesn't fit any category: " + str(sent.text) + str(earlier_word) + str(
                                    current_word))

                        del new_tag_array[current_new_tag_position - 1]
                        current_new_tag_position = current_new_tag_position - 1

                    else:
                        new_tag_array.append(current_word)
                    current_tag_position += 1
                    current_new_tag_position += 1
                tags = new_tag_array

                for word in tags:
                    word_tag_array = word.split('\t')
                    token = word_tag_array[0]
                    tag = word_tag_array[1]
                    lemma = word_tag_array[2]
                    word_list.append(token)

                    # print(word)

                    if word == 'me\tFW\tme':
                        tag = 'PP'

                    # {'.': ['.'], 'a': ['A'], 'car': ['car']}
                    if lemma in map_lemma_token:
                        if token not in map_lemma_token[lemma]:
                            map_lemma_token[lemma].append(token)
                    else:
                        map_lemma_token[lemma] = [token]

                    # [('a', 'DT'), ('car', 'NN'), ('.', '.')]
                    if tag in ['CD', 'LS']:
                        simple_lemma_tag_tuple.append((lemma, tag))
                    else:
                        try:
                            simple_lemma_tag_tuple.append((lemma, word_class_dict[tag]))
                        except:
                            raise ValueError(word, tag)

                if len(word_list) < 21:
                    greater_than_20 += 1
                elif len(word_list) > 2:
                    smaller_than_3 += 1

                if 21 > len(word_list) > 2:
                    new_row_string += " ".join(word_list) + "\n"
                    new_row_string = new_row_string.strip()
                    if not new_row_string.isupper():
                        # print(new_row_string)
                        s_w.writerow([new_row_string] + [str(simple_lemma_tag_tuple)] + [str(map_lemma_token)])
                    else:
                        sentence_is_upper += 1
            index += 1

    # print("Number of all sentences:\t", index) -- number of all texts
    print("Number of long sentences:\t", greater_than_20)
    print("Number of short sentences:\t", smaller_than_3)
    print("Number of upper sentences:\t", sentence_is_upper)


def delete_double_lines():

    unique_lines = set(open('ukwac_as_csv.csv', 'r', encoding='iso-8859-5').readlines())
    print("Before delete:", len(unique_lines))
    open('ukwac_as_csv_fixed.csv', 'w', encoding='iso-8859-5').writelines(set(unique_lines))
    print("After delete:", len(set(unique_lines)))


if __name__ == '__main__':
    import_as_csv()
    delete_double_lines()
    # print(ignored_sentences)
