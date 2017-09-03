import csv
import ast

freq_most_common = []
freq_common = []
#named_entities = []
#punctuation_pos = ["SENT", "#", "$", "\"", "''", "'", "(", ")", ",", ":"]

# ------------------------------------- GDEX POINTS -----------------------------------------------------


# Sentence length: a sentence between 10 and 25 words long was preferred, with longer and shorter ones penalized.
# in our case 20
# max Points = 2
def sentence_length(m_lemma_tag):
    points = 20
    sent_length = len(m_lemma_tag)

    if sent_length >= 10:
        points = 25
    else:
        if sent_length < 10:
            points = 25 * (sent_length/10)

    return points


# Word frequencies: a sentence was penalized for each word that was not amongst the commonest 17,000 words in the
# language, with a further penalty applied for rare words.
# max Points = 3
def common_words(m_lemma_tag):
    points = 0
    x = 100 / len(m_lemma_tag)
    #print(len(m_sentence[1]))
    for m_word in m_lemma_tag:
        if m_word[1] == 'Punct':
            points += x
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

    points = 40 * (points/100)
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

    points = 25 * (found/x)
    return points


# Whole sentenceidentified as beginning with a capital letter and ending with a full step, exclamation mark, or
# question mark, were preferred.
# max Points = 2
def whole_sentence(m_sentence):
    points = 10
    punctuation = ["!", "\"", ".", "?"]
    quote = ['\'', '"']
    first_letter = m_sentence[0][:1]
    last_letter = m_sentence[0][-1]

    if first_letter.isupper() or first_letter in quote:
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
    with open('lemma.num.txt', 'r') as freq_in:
        f = csv.reader(freq_in, delimiter=' ')
        row_number = 1
        for row in f:
            if row_number <= 17000:
                freq_most_common.append(row[2])
            else:
                freq_common.append(row[2])
            row_number += 1
    freq_in.close()


#def load_ner():
#    with open('./input/NER.txt', 'r') as f:
#        for ner in f:
#            named_entities.append(ner.lower())
#    f.close()


def compute_points(m_sentence, m_lemma_tag):
    # ---- GDEX ----
    points_len = sentence_length(m_lemma_tag)                # max 25p
    # print("len", points_len, "/", 25)
    points_common = common_words(m_lemma_tag)                # max 40p
    # print("com", points_common, "/", 40)
    points_pronoun = contain_pronouns_anaphora(m_lemma_tag)  # max 25p
    # print("pro", points_pronoun, "/", 25)
    points_whole_sent = whole_sentence(m_sentence)          # max 10p
    # print("sent", points_whole_sent, "/", 10)

    m_gdex_points = points_len + points_common + points_pronoun + points_whole_sent
    return round(m_gdex_points, 1)


if __name__ == "__main__":
    # new_list = []
    #load_ner()
    print("#### starting loading sentence file          ####")
    with open("./output/03_1_sentences_from_corpus.txt", 'r') as readsent, \
            open("./output/03_2_calculate_GDEX.csv", "w") as s_out:
        index = 1
        writer = csv.writer(s_out, delimiter=';')
        for line in readsent:
            if index % 100000 == 0:
                print("{:,}".format(index), "/", "{:,}".format(14200000))
            index += 1

            row_as_list = ast.literal_eval(line)

            # 0       | 1       | 2    | 3        | 4        | 5
            # vocable | chapter | book | sentence | lemmatag | lemmavocdict

            sentence = row_as_list[3]
            lemma_tag = row_as_list[4]

            gdex_number = compute_points(sentence, lemma_tag)
            row_as_list.insert(3, gdex_number)

            writer.writerow([row_as_list[0]] + [row_as_list[1]] + [row_as_list[2]] + [row_as_list[3]]
                            + [row_as_list[4]] + [row_as_list[5]] + [row_as_list[6]])
    s_out.close()
    readsent.close()
    print("#### finished loading sentence file          ####")
