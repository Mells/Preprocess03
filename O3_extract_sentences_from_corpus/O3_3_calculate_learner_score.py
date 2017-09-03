import ast
from lxml import etree as et
import csv

lemma_chap_book_pos_dict = {}


# ------------------------------------- LEARNER COMPREHENSION POINTS -------------------------------------

# Compute how much of the sentence is comprehensive to the learner
def contains_learned_words(m_sentence, m_chapter, m_book):

    base_chapter = m_chapter
    base_book = convert_string_to_int(m_book)

    len_sent = len(m_sentence)

    no_match = len(m_sentence)

    for m_lemma in m_sentence:
        # (lemma, pos)
        lookup_lemma = m_lemma[0]
        lookup_pos = m_lemma[1]
        # ignore numbers and proper nouns
        if lookup_lemma == "@card@" or lookup_pos in ["NP", "NPS", "SENT", "#", "$", "\"", "''", "'", "(", ")", ",", ":"]:
            continue
        found_current_voc = lemma_chap_book_pos_dict.get(m_lemma, [])
        if len(found_current_voc) == 0:
            # the lemma was not found in the vocabulary
                no_match -= 1
        else:
            # the lemma was found (several times) in the vocabulary
            worst_points = 1;    # the worst points you can reach
            # we keep the best result (best_points) as we have to iterate through all findings
            for found_lemma in found_current_voc:
                # (chapter, book)
                current_points = 0  # the best points you can reach
                found_book = convert_string_to_int(found_lemma[1])
                if base_book >= found_book:
                    # It is in the same book or earlier
                    # If it is in the same book we have to check the chapters
                    if base_book == found_book:
                        if base_chapter == 'Welcome':
                            # convert 'Welcome' to 0 A for easier use
                            base_chap = ["0", "A"]
                        else:
                            base_chap = base_chapter.split("/")

                        if found_lemma[0] == 'Welcome':
                            # convert 'Welcome' to 0 A for easier use
                            found_chapter = ["0", "A"]
                        else:
                            found_chapter = found_lemma[0].split("/")

                        # check if it is in the same chapter
                        if int(base_chap[0]) == int(found_chapter[0]):
                            # it is in the same chapter
                            # check if the subsection is also the same or earlier
                            if base_chap[1][:1] < found_chapter[1][:1]:
                                # it is in the same chapter but in a later subsection
                                current_points += 0.5

                        # it is in a later chapter
                        elif int(base_chap[0]) < int(found_chapter[0]):
                            current_points += 1
                else:
                    # it is in later book
                    current_points += 1

                if current_points < worst_points:
                    worst_points = current_points

            no_match -= worst_points

    matched_points = no_match/len_sent
    return round(matched_points, 2)


# small conversion of the string denoting the number of the book to an integer
def convert_string_to_int(m_book):
    base_book = 0

    if m_book == "I":
        base_book = 1
    if m_book == "II":
        base_book = 2
    if m_book == "III":
        base_book = 3

    return base_book


# ------------------------------------- LOAD NER ----------------------------------------------------------



# ------------------------------------- LOAD LEMMA, CHAPTER AND BOOK --------------------------------------

def load_lemma_chapter_book():
    # --------------- Parser ---------------

    mvoc_parser = et.XMLParser()
    mvoc_tree = et.parse("./input/lemma_chap_book_pos.xml", mvoc_parser)
    mvoc_root = mvoc_tree.getroot()
    # --------------- End ---------------

    for xml_lemma in mvoc_root.findall('lemma'):
        m_lemma = xml_lemma.get('name')
        m_chapter = xml_lemma.find("chapter").get('name')
        m_book = xml_lemma.find("book").get('name')
        m_lemma_pos = xml_lemma.find("pos").get('name')

        if m_lemma in lemma_chap_book_pos_dict:
            lemma_chap_book_pos_dict[(m_lemma, m_lemma_pos)].append((m_chapter, m_book))
        else:
            lemma_chap_book_pos_dict[(m_lemma, m_lemma_pos)] = [(m_chapter, m_book)]


# ------------------------------------- MAIN --------------------------------------------------------------

if __name__ == "__main__":
    new_list = []

    print("#### starting loading lemma-chap-book-pos    ####")
    load_lemma_chapter_book()
    print("#### finished loading lemma-chap-book-pos    ####")

    with open("./output/03_2_calculate_GDEX.csv", 'r') as readsent, open("./output/03_3_calculate_learner_score.csv", "w") as writesent:
        m_reader = csv.reader(readsent, delimiter=';')
        m_writer = csv.writer(writesent, delimiter=';')
        index = 1

        for row in m_reader:
            if index % 100000 == 0:
                print("{:,}".format(index), "/", 14200000)
            index += 1

            # 0       | 1       | 2    | 3    | 4        | 5        | 6
            # vocable | chapter | book | gdex | sentence | lemmatag | lemmavocdict

            chapter = row[1]
            book = row[2]
            lemma_tag = ast.literal_eval(row[5])

            learner_number = contains_learned_words(lemma_tag, chapter, book)
            # print(learner_number)
            m_writer.writerow(row[:4] + [learner_number] + row[4:])
    readsent.close()
    writesent.close()