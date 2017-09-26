import csv
import ast

freq_most_common = []
freq_common = []
# punctuation_pos = ["SENT", "#", "$", "\"", "''", "'", "(", ")", ",", ":"]

# ------------------------------------- GDEX POINTS -----------------------------------------------------


# Sentence length: a sentence between 10 and 20 words long was preferred, with and shorter ones penalized.
# No sentence is longer than 20 words.

def sentence_length(m_lemma_tag):
    # points = 20
    sent_length = len(m_lemma_tag)

    # sentence is greater than 10
    if sent_length >= 10:
        points = 20
    # sentence is smaller than 10
    else:
        points = 20 * (sent_length/10)

    return points


# Word frequencies: a sentence was penalized for each word that was not amongst the commonest 17,000 words in the
# language, with a further penalty applied for rare words.
# max Points = 3
def common_words(m_lemma_tag):
    points = 0
    x = 100 / len(m_lemma_tag)
    # print(len(m_sentence[1]))

    # one free 'Punct' for end of sentence every other is negative
    punctuations = 0
    for m_word in m_lemma_tag:
        if m_word[1] == 'Punct':
            if punctuations == 0:
                points += x
                punctuations += 1
        else:
            # if you ignore proper nouns the resulting 'good' sentences are really bad
            if m_word[0] in freq_most_common:
                points += x
            elif m_word[0] in freq_common:
                points += x/2

    # for m_word in m_sentence[1]:
    #     if m_word[0] in freq_most_common:
    #         points += x
    #     elif m_word[0] in freq_common:
    #         points += x / 2

    points = 50 * (points/100)
    return points


# Sentences containing pronouns and anaphors like this that it or one often fail to present a self-contained piece of
# language which makes sense without further context, so sentences containing these words were penalized.
# max Points = 1
def contain_pronouns_anaphora(m_lemma_tag):
    x = len(m_lemma_tag)
    found = x
    for m_word in m_lemma_tag:
        if m_word[1] == "Pron":
            found -= 1

    points = 20 * (found/x)
    return points


# Whole sentenceidentified as beginning with a capital letter and ending with a full step, exclamation mark, or
# question mark, were preferred.
# max Points = 2
def whole_sentence(m_sentence):
    points = 10
    punctuation = ["!", ".", "?"]
    #quote = ['\'', '"']
    first_letter = m_sentence[:1]
    last_letter = m_sentence[-1]

    if first_letter.isupper():  # or first_letter in quote:
        if last_letter in punctuation:
            pass    # is upper and has punctuation
        else:
            points -= 5     # is upper and has no punctuation
    else:
        if last_letter in punctuation:
            points -= 5     # is not upper and has punctuation
        else:
            points -= 10    # is not upper and has no punctuation

    return points


# ------------------------------------- LOAD FREQUENCIES --------------------------------------------------

def load_frequencies():
    with open('lemma.num.17000.txt', 'r') as freq_in:
        f = csv.reader(freq_in, delimiter=' ')
        row_number = 1
        for row in f:
            if row_number <= 7000:
                freq_most_common.append(row[2])
            else:
                freq_common.append(row[2])
            row_number += 1
    freq_in.close()


def compute_points(m_sentence, m_lemma_tag):

    points_len = sentence_length(m_lemma_tag)                # max 20p
    # print("len", points_len, "/", 20)

    points_common = common_words(m_lemma_tag)                # max 50p
    # print("com", points_common, "/", 50)

    points_pronoun = contain_pronouns_anaphora(m_lemma_tag)  # max 20p
    # print("pro", points_pronoun, "/", 20)

    points_whole_sent = whole_sentence(m_sentence)          # max 10p
    # print("sent", points_whole_sent, "/", 10)

    m_gdex_points = points_len + points_common + points_pronoun + points_whole_sent
    return round(m_gdex_points, 1)


def main():
    if __name__ == "__main__":
        print("#### starting loading sentence file          ####")

        with open("./output/03_1_sentences_from_corpus.txt", 'r') as read_sent, \
                open("./output/03_2_calculate_GDEX.csv", "w") as s_out:
            index = 1
            writer = csv.writer(s_out, delimiter=';')
            good_sentence = 0
            bad_sentence = 0
            for line in read_sent:
                if index % 100000 == 0:
                    print("{:,}".format(index), "/", "{:,}".format(15500000))
                index += 1

                row_as_list = ast.literal_eval(line)

                # 0       | 1       | 2    | 3        | 4        | 5
                # vocable | chapter | book | sentence | lemmatag | lemmavocdict

                sentence = row_as_list[3]
                lemma_tag = row_as_list[4]

                gdex_number = compute_points(sentence, lemma_tag)
                row_as_list.insert(3, gdex_number)

                if gdex_number > 60:
                    good_sentence += 1
                    writer.writerow([row_as_list[0]] + [row_as_list[1]] + [row_as_list[2]] + [row_as_list[3]]
                                    + [row_as_list[4]] + [row_as_list[5]] + [row_as_list[6]])
                else:
                    bad_sentence += 1

        s_out.close()
        read_sent.close()
        print("#### finished loading sentence file          ####")
        print("good:", good_sentence)
        print("bad:", bad_sentence)


if __name__ == "__main__":
    print("#### starting loading sentence file          ####")
    average = 0
    index = 1
    highest = 0
    lowest = 100
    with open("./output/03_1_sentences_from_corpus.txt", 'r') as read_sent, \
            open("./output/03_2_calculate_GDEX.csv", "w") as s_out:

        writer = csv.writer(s_out, delimiter=';')
        good_sentence = 0
        bad_sentence = 0
        for line in read_sent:
            if index % 100000 == 0:
                print("{:,}".format(index), "/", "{:,}".format(15500000))
            index += 1

            row_as_list = ast.literal_eval(line)

            # 0       | 1       | 2    | 3        | 4        | 5
            # vocable | chapter | book | sentence | lemmatag | lemmavocdict

            sentence = row_as_list[3]
            lemma_tag = row_as_list[4]

            gdex_number = compute_points(sentence, lemma_tag)
            row_as_list.insert(3, gdex_number)

            average += gdex_number
            if gdex_number > highest:
                highest = gdex_number
            if gdex_number < lowest:
                lowest = gdex_number

            if gdex_number > 50:
                #print(sentence)
                #if "I can smell" in sentence:
                #    print("gdex:", gdex_number, sentence)
                good_sentence += 1
                writer.writerow([row_as_list[0]] + [row_as_list[1]] + [row_as_list[2]] + [row_as_list[3]]
                                + [row_as_list[4]] + [row_as_list[5]] + [row_as_list[6]])
            else:
                bad_sentence += 1

    s_out.close()
    read_sent.close()
    print("#### finished loading sentence file          ####")
    print("good:\t", good_sentence)
    print("bad:\t", bad_sentence)
    print("avg:\t", gdex_number / index)
    print("high:\t", highest)
    print("low:\t", lowest)
