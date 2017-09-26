import csv
import re
import sqlite3
import timeit

import kph
import treetaggerwrapper
from nltk import tokenize as np


status = 1
all_not_found = []
all_double_reading = []
all_pos_not_matched = []
as_noun = []
one_reading = []
one_reading_phrase = []

# --------------------------------- Exceptions -------------------------------------------------------------------------

exceptions = ['Hallo, ich heiße …', 'Hier, bitte!, Bitte schön!', 'Ausgeschlossen!, hier: Jetzt echt, oder?',
              'sobald, hier: als, in dem Moment, als ...', 'glücklich (Glück habend; Glück bringend)',
              'darauf achten, (dass)', 'Längenmaß (91,44 cm)',
              '(entspricht dem deutschen Abitur)', '(Anrede)',
              '(Amtssprache in Indien)', '(als Schulfach)',
              '(nur hinter Uhrzeit zwischen Mitternacht und 12 Uhr mittags)',
              '(nur hinter Uhrzeit zwischen 12 Uhr mittags und Mitternacht)', '(zur Terminplanung)', '(bei Freunden)',
              '(an Kleidungsstücken)', '(= 0,3048 Meter)', '(Briefschlussformel)', '(von Großbritannien)',
              '(Untereinheit des brit. Pfunds)', '(Londoner)', '(Alternativbezeichnung ', '(Kobold)',
              '(systematische wiss. Beobachtung außerhalb des Labors)', '(in der Thronfolge)',
              '(Einrichtung zur Betreuung sterbender Menschen)', '(beim Rugby)', '(= 1,609 km)', '(Zeit)', '(Geld)',
              '(auf dem Wasser)', '(jd, der den Text flüsternd vorspricht)', '(Sprache)',
              'der/die sich im Internat um die Schüler/innen eines Hauses kümmert/kümmern',
              'Aufsicht führende/r Lehrer/in', 'Vergangenheitsform von']

# info: other exceptions can be found at:
#       elif '/' in word and '-' in word:
#       elif '/' in word:

# --------------------------------- TAGGER -----------------------------------------------------------------------------

tagger = treetaggerwrapper.TreeTagger(TAGLANG='en')

# --------------------------------- DATABASE ---------------------------------------------------------------------------

connection = sqlite3.connect("xtag.db")
cursor = connection.cursor()

# --------------------------------- WORD CLASS BOOK-XTAG DICTIONARY ----------------------------------------------------

# d           determiner
# s           substantive
# i           interjection
# v           verb
# av          adverb
# a           adjective
# ph          phrase
# k           conjunction
# p           pronoun
# pr          preposition
# irr         irregular
# s/a
# a/av
# av/pr

word_class_bookxtag_dict = {'d': ['Det'], 's': ['N', 'PropN'], 'v': ['V'], 'av': ['Adv'], 'a': ['A'], 'k': ['Conj'],
                            'p': ['Pron'], 'pr': ['Prep'], 'i': ['I'], 's/a': ['N', 'PropN', 'A'],
                            'a/av': ['A', 'Adv'], 'av/pr': ['Adv', 'Prep'], 'irr': ['V']}

# "Comp", "G", "Part",
# info: NVC and VVC are redundant in this case as the both stand for phrase but here it is just word-to-word.
#       Punct are ignored


# --------------------------------- WORD CLASS PENN-XTAG DICTIONARY ----------------------------------------------------

# CD, EX, FW, IN/that, LS, POS, SENT, SYM, #, $, “, ``, (, ), ,, :

word_class_xtagpenn_dict = {'A': ['JJ', 'JJR', 'JJS'], "Adv": ['RB', 'RBR', 'RBS', 'WRB'], "Conj": ['CC'],
                            'Det': ['DT', 'PDT', 'WDT', 'IN/that'],
                            'N': ['NN', 'NNS', 'NP'], 'Pron': ['PP', 'PP$', 'WP', 'WP$'],
                            'Prep': ['IN'], 'PropN': ['NP', 'NPS'], 'I': ['UH'], 'Part': ['RP'],
                            'V': ['MD', 'TO', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VH', 'VHD', 'VHG', 'VHN',
                                  'VHP', 'VHZ', 'VV', 'VVD', 'VVG', 'VVN', 'VVP', 'VVZ', 'V'],
                            'NVC': ['NVC'], 'VVC': ['VVC']}


# "Comp", "G", "Punct"


# --------------------------------- PROCESSING VOCABULARY --------------------------------------------------------------

def processing_vocabulary(word):
    word = word.replace('(no pl)', '')
    word = word.replace('(pl)', '')
    word = word.replace('(irr)', '')
    word = word.replace('(informal)', '')
    word = word.replace('(informal, pl)', '')
    word = word.replace('(only pl)', '')
    word = word.replace('(BE, informal)', '')
    word = word.replace('(pl, BE)', '')
    word = word.replace('(BE)', '')
    word = word.replace('(BE, no pl)', '')
    word = word.replace('(pl, informal)', '')
    word = word.replace('(no pl, informal)', '')
    word = word.replace('(only pl, informal)', '')
    word = word.replace('(informal, irr)', '')
    word = word.replace('(AE, pl)', '')

    # print(word)
    returned_word = deal_with_punctuation_no_comma(word)

    returned_word = deal_with_parenthesis_english(returned_word)

    if isinstance(returned_word, list):
        return returned_word

    returned_word = deal_with_person(returned_word)

    if isinstance(returned_word, list):
        return returned_word

    returned_word = deal_with_slash(returned_word)

    if isinstance(returned_word, list):
        return returned_word

    returned_word = deal_with_comma_seperating_words(returned_word)

    if isinstance(returned_word, list):
        return returned_word

    returned_word = deal_with_punctuation_comma(returned_word)

    # print(returned_word.strip())
    return [returned_word.strip()]


def deal_with_punctuation_no_comma(word):
    if any(item in word for item in ['.', '?', '!', '…', '...']):
        word = re.sub("\s*\.\.\.\s*", " ", word)
        word = word.replace('.', '').replace('?', '').replace('!', '').replace(' …', '')
    return word


def deal_with_parenthesis_english(word):
    if '(' in word:

        # if word contains plural marker eg.
        # shelf (pl shelves)
        if '(pl ' in word:
            word = word.replace('(', '').replace(')', '')
            array_word = word.split("pl")
            # print([[x.strip(' ')] for x in array_word])
            return [[x.strip(' ')] for x in array_word]

        # if word has an alternate form and plural marker eg.
        # these (= pl of this)
        elif '(= ' in word and 'pl' in word:
            if '(= pl' in word:
                word = word.replace('(', '').replace(')', '')
                array_word = word.split("= pl")
                # print([[x.strip(' ')] for x in array_word])
                return [[x.strip(' ')] for x in array_word]
            # elif ', pl)' in word:  # sports (AE, pl) - maths (informal, pl)
            #    print(word)
            #    word = word.replace(', pl', '=').replace('(', '').replace(')', '')
            #    array_word = word.split("=")
            #    print([[x.strip(' ')] for x in array_word])
            #    return [[x.strip(' ')] for x in array_word]
            elif ', pl ' in word:
                # ft (= foot pl feet)
                first_word = re.sub('\(=.*\)', '', word)
                second_words = word.split("(")[1].replace("=", '').replace(")", '').split(", pl ")
                array_word = [first_word, second_words[0], second_words[1]]
                # print([[x.strip(' ')] for x in array_word])
                return [[x.strip(' ')] for x in array_word]
            else:
                raise ValueError('An unspecified case occured: ' + str(word))

        # if word has an alternate form (no plural) eg.
        # can't (= cannot)
        elif '(= ' in word:
            if word == "can't (= cannot)":
                return [["can't"], ['cannot'], ['can not']]
            word = word.replace('(', '').replace(')', '')
            array_word = word.split("=")
            # print([[x.strip(' ')] for x in array_word])
            return [[x.strip(' ')] for x in array_word]

        elif '(past/to)' in word:
            first_half = word.replace('(past/to)', '')
            array_word = [first_half, first_half + "past", first_half + "to"]
            # print([[x.strip(' ')] for x in array_word])
            return [[x.strip(' ')] for x in array_word]

        elif '(to/for)' in word:
            first_half = word.replace('(to/for)', '')
            array_word = [first_half, first_half + "to", first_half + "for"]
            # print([[x.strip(' ')] for x in array_word])
            return [[x.strip(' ')] for x in array_word]

        # if parenthesis after word contain 'sb' or 'sth'
        # to help oneself (to sth)
        elif any(item in word for item in
                 ['(sth to sb)', '(with sb)', '(to sth)', '(sth to sth)', '(of sth)', '(to sb)',
                  '(sb)', '(about sth)', '(for sth)', '(it for sb)']):
            # print(word)
            first_half = word.split('(')
            if 'sb' in first_half[0] or 'sth' in first_half[0]:
                first_half_without_sbsth = first_half[0].replace(' sb', '').replace(' sth', '')
                array_word = [first_half[0],
                              first_half_without_sbsth,
                              first_half[0] + first_half[1].replace(')', ''),
                              first_half_without_sbsth + first_half[1].replace(')', ''),
                              first_half_without_sbsth + first_half[1].replace(')', '').replace(' sb', "")
                                                                      .replace(" sth", "")]
            else:
                array_word = [first_half[0],
                              first_half[0] + first_half[1].replace(')', ''),
                              first_half[0] + first_half[1].replace(')', '').replace(' sb', "").replace(" sth", "")]
            # print([[x.strip(' ')] for x in array_word])
            return [[x.strip(' ')] for x in array_word]

        # word has a '/' in parenthesis eg.
        # to react (to sb/sth)
        elif '(' in word and '/' in word:
            # print(word)
            # to react (to sb/sth)
            first_half = word.split('(')
            # [to react , to sb/sth)]
            second_half = first_half[1].replace(')', '').split('/')
            # [to sb, sth]
            second_first_half = second_half[0].split(' ')
            # [to, sb]
            array_word = [first_half[0],
                          first_half[0] + second_half[0].replace(' sb', '').replace('sth', ''),
                          first_half[0] + second_half[0],
                          first_half[0] + second_first_half[0] + ' ' + second_half[1]]
            # print([[x.strip(' ')] for x in array_word])
            return [[x.strip(' ')] for x in array_word]

        # if parenthesis directly after word eg.
        # toward(s)
        elif bool(re.search('[a-z]\(', word)):
            # print(word)
            first_word = re.sub('\([a-z]+\)', '', word)
            second_word = word.replace('(', '').replace(')', '')
            array_word = [first_word, second_word]
            # print([[x.strip(' ')] for x in array_word])
            return [[x.strip(' ')] for x in array_word]

        # if parenthesis before word eg.
        # (I'm) sorry
        elif bool(re.search('\) [a-z]', word)):
            # print(word)
            word = word.replace('...', '')
            if ' (' in word:
                first_word = re.sub(' \([A-Za-z]+\)', '', word)
                if 'sb' in first_word or 'sth' in first_word:
                    first_word_without_sbsth = first_word.replace(' sb', '').replace(' sth', '')
                    second_word = word.replace('(', '').replace(')', '')
                    second_word_without_sbsth = word.replace('(', '').replace(')', '').replace(' sb', '').replace(
                        ' sth', '')
                    array_word = [first_word, first_word_without_sbsth, second_word, second_word_without_sbsth]
                else:
                    second_word = word.replace('(', '').replace(')', '')
                    array_word = [first_word, second_word]
            else:
                first_word = re.sub('\([A-Za-z]+\'*[A-Za-z]*\)', '', word)  # (I'm)
                second_word = word.replace('(', '').replace(')', '')
                array_word = [first_word, second_word]
            # print([[x.strip(' ')] for x in array_word])
            return [[x.strip(' ')] for x in array_word]

        # if directly parenthesis before word eg.
        # to show sb (a)round
        elif bool(re.search('\)[a-z]', word)):
            # print(word)
            if ' sb ' in word:
                # to show sb (a)round
                without_sb = word.replace(' sb', '')
                # to show (a)round
                array_without_sb = [re.sub('\([a-z]+\)', '', without_sb), without_sb.replace('(', '').replace(')', '')]
                # [to show round, to show around]
                array_with_sb = [re.sub('\([a-z]+\)', '', word), word.replace('(', '').replace(')', '')]
                array_word = []
                for x in array_without_sb:
                    array_word.append([x.strip(' ')])
                for x in array_with_sb:
                    array_word.append([x.strip(' ')])
                # print(array_word)
                return array_word
            else:
                array_word = [re.sub('\([a-z]+\)', '', word), word.replace('(', '').replace(')', '')]
                # print([[x.strip(' ')] for x in array_word])
                return [[x.strip(' ')] for x in array_word]

        # if parenthesis after word contain just simple word(s) eg.
        # in addition (to), to score (a goal)
        elif '(' in word:
            # print(word)
            split_word = word.split('(')
            array_word = [split_word[0], split_word[0] + split_word[1].replace('(', '').replace(')', '')]
            # print([[x.strip(' ')] for x in array_word])
            return [[x.strip(' ')] for x in array_word]
    else:
        return word


def deal_with_person(word):
    if ' sb' in word or ' sth' in word:
        # print(word)
        if '/' in word:
            # print(word)
            split_word = re.split('[a-z]+/[a-z]+', word)
            pattern = re.compile("[a-z]+/[a-z]+")
            result = pattern.findall(word)
            person_array = result[0].split('/')
            array_word = [split_word[0], split_word[0] + person_array[0], split_word[0] + person_array[1]]
        else:
            first_half = word.replace(' sth', '').replace(' sb', '')
            array_word = [first_half, word]
        # print([[x.strip(' ')] for x in array_word])
        return [[x.strip(' ')] for x in array_word]
    else:
        return word


def deal_with_slash(word):
    if '/' in word:
        # print(word)
        pattern = re.compile("[a-z]+/[a-z]+")
        result = pattern.findall(word)
        # print(result)
        if result and len(result[0]) == len(word):
            # print(result)
            split_array = word.split('/')
            # print([[x.strip(' ')] for x in split_array])
            return [[x.strip(' ')] for x in split_array]
        else:
            # print(word)
            # info: exeception: to be out of/short of breath
            # info: exception: to expect/to have a baby
            if word == 'to be out of/short of breath':
                return [['to be out of breath'], ['to be short of breath']]
            elif word == 'to expect/to have a baby':
                return [['to expect a baby'], ['to have a baby']]
            elif re.search("[a-z]+/[a-z]+", word) is not None:
                # print(word)
                split_word = re.split('[a-z]+/[a-z]+', word)
                pattern = re.compile("[a-z]+/[a-z]+")
                result = pattern.findall(word)
                person_array = result[0].split('/')
                if split_word[1] != '':
                    array_word = [split_word[0] + person_array[0] + split_word[1],
                                  split_word[0] + person_array[1] + split_word[1]]
                else:
                    array_word = [split_word[0] + person_array[0], split_word[0] + person_array[1]]
                # print([[x.strip(' ')] for x in array_word])
                return [[x.strip(' ')] for x in array_word]
            else:
                # print(word)
                # Where is … / Where are …
                # bye / goodbye
                split_array = word.split('/')
                # print([[x.strip(' ')] for x in split_array])
                return [[x.strip(' ')] for x in split_array]
    else:
        return word


def deal_with_comma_seperating_words(word):
    # to get married (irr), to marry;
    if ',' in word:
        if any(item in word for item in ['housemother, housefather, houseparents ', 'was, were',
                                         'to get married , to marry']):
            split_array = word.split(',')
            # print(word)
            # print([[x.strip(' ')] for x in split_array])
            return [[x.strip(' ')] for x in split_array]
        else:
            return word
    else:
        return word


def deal_with_punctuation_comma(word):
    if ',' in word:
        word = word.replace(',', '')
    return word


# --------------------------------- TAG & LEMMATIZE --------------------------------------------------------------------

def tagging_processed_vocable(m_processed_vocable, m_word_class):
    # print("word: ", m_processed_vocable)
    m_tagged_processed_vocable = []
    m_lemma_vocable = []
    m_tagged_lemma_vocable = []
    m_simple_tagged_lemma_vocable = []
    # ['can']
    # [["can't"], ['cannot']]
    # print(m_processed_vocable)
    if isinstance(m_processed_vocable[0], list):  # [["can't"], ['cannot']]
        for processed_item in m_processed_vocable:
            # print("w: ", processed_item)
            # ["can't"]
            # ['cannot']
            if not any(x in processed_item[0] for x in [' sb', ' sth']):  # ['to show sb round']

                first_to = False
                not_found_xtag = []
                no_pos_match = []
                if processed_item[0].startswith("to "):
                    first_to = True

                if word_class == 'ph':
                    no_pos_match, not_found_xtag, m_tagged_processed_vocable_part, m_lemma_vocable_part, \
                        m_tagged_lemma_vocable_part, tagged_lemma_simple_vocable_part = process_a_phrase(processed_item,
                                                                                                         no_pos_match,
                                                                                                         not_found_xtag,
                                                                                                         first_to)
                else:
                    no_pos_match, not_found_xtag, m_tagged_processed_vocable_part, m_lemma_vocable_part, \
                        m_tagged_lemma_vocable_part, tagged_lemma_simple_vocable_part = process_a_word(processed_item,
                                                                                                       m_word_class,
                                                                                                       no_pos_match,
                                                                                                       not_found_xtag,
                                                                                                       first_to)
                    # test:
                    # if no_pos_match:
                    #    print(status, "/", 3020, processed_vocable)
                    #    print("\tNo POS match:", word_class, no_pos_match)
                    # test:
                    # if not_found_xtag:
                    #    print(status, "/", 3020, processed_vocable)
                    #    print("\tNot Found:", set(not_found_xtag))

                    # print(m_tagged_processed_vocable_part)
            else:
                continue
            m_tagged_processed_vocable.append(m_tagged_processed_vocable_part)
            m_lemma_vocable.append(m_lemma_vocable_part)
            m_tagged_lemma_vocable.append(m_tagged_lemma_vocable_part)
            if isinstance(tagged_lemma_simple_vocable_part[0], list):
                m_simple_tagged_lemma_vocable.extend(tagged_lemma_simple_vocable_part)
            else:
                m_simple_tagged_lemma_vocable.append(tagged_lemma_simple_vocable_part)
    else:  # ['can']
        first_to = False
        not_found_xtag = []
        no_pos_match = []
        if m_processed_vocable[0].startswith("to "):
            first_to = True
        # print(word_class)
        if word_class == 'ph':
            no_pos_match, not_found_xtag, m_tagged_processed_vocable, m_lemma_vocable, m_tagged_lemma_vocable, \
                m_simple_tagged_lemma_vocable = process_a_phrase(m_processed_vocable, no_pos_match, not_found_xtag,
                                                                 first_to)
        else:
            no_pos_match, not_found_xtag, m_tagged_processed_vocable, m_lemma_vocable, m_tagged_lemma_vocable, \
                m_simple_tagged_lemma_vocable = process_a_word(m_processed_vocable, m_word_class, no_pos_match,
                                                               not_found_xtag, first_to)
            # test:
            # if no_pos_match:
            #    print(status, "/", 3020, processed_vocable)
            #    print("\tNo POS match:", word_class, no_pos_match)
            # test:
            # if not_found_xtag:
            #    print(status, "/", 3020, processed_vocable)
            #    print("\tNot Found:", set(not_found_xtag))

    # print("tagged: ",m_tagged_processed_vocable, "\nlemma: ", m_lemma_vocable, "\ntaglemma: ", m_tagged_lemma_vocable)
    # print(m_simple_tagged_lemma_vocable)
    # print("x", m_simple_tagged_lemma_vocable)
    return m_tagged_processed_vocable, m_lemma_vocable, m_tagged_lemma_vocable, m_simple_tagged_lemma_vocable


def process_a_word(processed_item, m_word_class, no_pos_match, not_found_xtag, first_to):
    m_tagged_processed_vocable_part = []
    m_lemma_vocable_part = []
    m_tagged_lemma_vocable_part = []
    m_simple_tagged_lemma_vocable = []
    change_simple = False

    for processed_word in processed_item[0].split(" "):  # ['to', 'expect', 'a', 'baby']
        # print(processed_word)
        reading_list = []
        simple_reading_list = []
        lemma = ""
        change_pos = (False,)

        # info: there is tagged as exestential there but can not be found like that in xtag. The case word class will
        # be changed to 'RB' to be aligned with 'there;dort, da;aktiv;1/A1;I;av;;' in the same chapter.
        if 'there' in processed_word:
            change_pos = (True, 'Adv')
        # in 'not ... anything else' anything is not correctly tagged, change to Pronoun
        if 'anything' == processed_word:
            change_pos = (True, 'Pron')

        # same words need to be looked up in lower or upper case
        morphology = Morphology(cursor, processed_word)
        number = morphology.get_number_of_readings()
        if number == 0:
            morphology = Morphology(cursor, processed_word.lower())
            number = morphology.get_number_of_readings()

        # info: words that didn't match in POS
        if 'where' == processed_word or 'Where' == processed_word:
            reading_list.append('Adv wh')
            simple_reading_list.append('Adv')
            lemma = morphology.lemma[0]

        elif 'many' == processed_word:
            reading_list.append('A')
            simple_reading_list.append('A')
            lemma = morphology.lemma[0]

        elif 'other' == processed_word:
            reading_list.append('A')
            simple_reading_list.append('A')
            lemma = morphology.lemma[0]

        elif 'own' == processed_word:
            reading_list.append('A')
            simple_reading_list.append('A')
            lemma = morphology.lemma[0]

        # info: words that couldn't be found
        elif 'elephant' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'meridiem' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'pm' == processed_word:
            reading_list.append('PropN')
            simple_reading_list.append('PropN')
            lemma = processed_word

        elif 'sleepover' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'hoover' == processed_word:
            # info only with capital letter in xtag 'Hoover' but taged as V
            reading_list.append('V INF')
            simple_reading_list.append('V')
            lemma = processed_word

        elif 'UK' == processed_word:
            reading_list.append('PropN')
            simple_reading_list.append('PropN')
            lemma = processed_word

        elif 'ft' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'English-speaking' == processed_word:
            reading_list.append('A')
            simple_reading_list.append('A')
            lemma = processed_word

        elif 'unacceptable' == processed_word:
            reading_list.append('A')
            simple_reading_list.append('A')
            lemma = processed_word

        elif 'BBC' == processed_word:
            reading_list.append('PropN')
            simple_reading_list.append('PropN')
            lemma = processed_word

        elif 'Diwali' == processed_word:
            reading_list.append('PropN')
            simple_reading_list.append('PropN')
            lemma = processed_word

        elif 'St' == processed_word:
            reading_list.append('PropN')
            simple_reading_list.append('PropN')
            lemma = processed_word

        elif 'bossy-boots' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'samosa' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'e-mail' == processed_word:
            reading_list.append('V')
            simple_reading_list.append('V')
            lemma = processed_word

        elif 'trapdoor' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'fundraising' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'pre-' == processed_word:
            reading_list.append('Prefix')
            simple_reading_list.append('Prefix')
            lemma = 'pre'

        elif 'never-ending' == processed_word:
            reading_list.append('V')
            simple_reading_list.append('V')
            lemma = 'never-end'

        elif 'girly' == processed_word:
            reading_list.append('A')
            simple_reading_list.append('A')
            lemma = processed_word

        elif 'pointy' == processed_word:
            reading_list.append('A')
            simple_reading_list.append('A')
            lemma = processed_word

        elif 'handprint' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'upload' == processed_word:
            reading_list.append('V')
            simple_reading_list.append('V')
            lemma = processed_word

        elif 'houseparents' == processed_word:
            reading_list.append('PropN pl')
            simple_reading_list.append('PropN')
            lemma = processed_word

        elif 'GCSE' == processed_word:
            reading_list.append('PropN')
            simple_reading_list.append('PropN')
            lemma = processed_word

        elif 'kayaking' == processed_word:
            reading_list.append('PropN')
            simple_reading_list.append('PropN')
            lemma = processed_word

        elif 'light-skinned' == processed_word:
            reading_list.append('A')
            simple_reading_list.append('A')
            lemma = processed_word

        elif 'dark-haired' == processed_word:
            reading_list.append('A')
            simple_reading_list.append('A')
            lemma = processed_word

        elif 'stepdad' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'Welshwoman' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'username' == processed_word:
            reading_list.append('N sg')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'storyline' == processed_word:
            reading_list.append('N sg')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'Asia' == processed_word:
            reading_list.append('PropN')
            simple_reading_list.append('PropN')
            lemma = processed_word

        elif 'balti' == processed_word:
            reading_list.append('PropN sg')
            simple_reading_list.append('PropN')
            lemma = processed_word

        elif 'pinboard' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif '1' == processed_word:
            reading_list.append('CD')
            simple_reading_list.append('CD')
            lemma = '@card@'

        elif 'heptathlon' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'Paralympics' == processed_word:
            reading_list.append('PropN pl')
            simple_reading_list.append('PropN')
            lemma = processed_word

        elif 'page-turner' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'horse-riding' == processed_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = processed_word

        elif 'GPS' == processed_word:
            reading_list.append('PropN')
            simple_reading_list.append('PropN')
            lemma = processed_word

        else:
            # word has been found in xtag, word has more than 1 reading
            if number > 1:
                for num in range(1, number + 1):
                    reading = morphology.get_reading_by_number(num)
                    # reading is returned as a tuple because of sql (reading,)
                    morphology_information = MorphologyInformation(reading[0])
                    morph_pos = morphology_information.pos
                    if change_pos[0]:
                        morph_pos = change_pos[1]
                    if morph_pos in word_class_bookxtag_dict.get(m_word_class, "nothing"):
                        reading_list.append(morphology_information.word_reading)
                        simple_reading_list.append(morph_pos)
                        lemma = morphology_information.lemma
                if reading_list:
                    # info: some double readings
                    # V INF#react;V INF;;;;;;
                    # ['V INF', 'V INF', ...]
                    reading_list = list(set(reading_list))
                    simple_reading_list = list(set(simple_reading_list))
                else:
                    # info: no match between book and xtag. As book and xtag ar 1:1 (besides s, s/a, a/av, av/pr) add
                    # the book equivalent as reading. Known to the learner
                    if not any(item in m_word_class for item in ['s/a', 'a/av', 'av/pr']):
                        # todo s can be N or PropN
                        if m_word_class == 's':
                            if 'direct' == processed_word:
                                reading_list.append("N")
                                simple_reading_list.append('N')
                            else:
                                as_noun.append((processed_item, processed_word))
                                reading_list.append("N")
                                simple_reading_list.append('N')
                        else:
                            reading_list.append(word_class_bookxtag_dict[m_word_class])
                            simple_reading_list.append(word_class_bookxtag_dict[m_word_class][0])
                    else:
                        no_pos_match.append(processed_word)
                        all_pos_not_matched.append(processed_word)
            # word has been found in xtag, word has one reading
            elif number == 1:
                reading = morphology.get_reading_by_number(1)
                morphology_information = MorphologyInformation(reading[0])
                morph_pos = morphology_information.pos
                if change_pos[0]:
                    morph_pos = change_pos[1]
                if morph_pos in word_class_bookxtag_dict.get(m_word_class, "nothing"):
                    reading_list.append(morphology_information.word_reading)
                    simple_reading_list.append(morph_pos)
                    lemma = morphology_information.lemma
                else:  # technically a hack but if hat has just one reading anyway than take that
                    one_reading.append(processed_word)

                    reading_list.append(morphology_information.word_reading)
                    simple_reading_list.append(morph_pos)
                    lemma = morphology_information.lemma
                if not reading_list:
                    no_pos_match.append(processed_word)
                    all_pos_not_matched.append(processed_word)
            # word could not be found in xtag
            else:
                if not any(item in m_word_class for item in ['s/a', 'a/av', 'av/pr']):
                    # todo s can be N or PropN
                    if m_word_class == 's':
                        as_noun.append((processed_item, processed_word))
                        reading_list.append("N")
                        simple_reading_list.append('N')
                    else:
                        reading_list.append(word_class_bookxtag_dict[m_word_class])
                        simple_reading_list.append(word_class_bookxtag_dict[m_word_class][0])
                else:
                    not_found_xtag.append(processed_word)
                    all_not_found.append(processed_word)

        # check for words with more than one reading
        if len(reading_list) > 1:
            # print(status, "/", 3020, processed_vocable)
            # print("\tAllReadings:", processed_word, reading_list)
            all_double_reading.append(processed_word)
        # if there is a accepted reading

        # if reading_list:
        if lemma == "":
            # ('Camden',)
            lemma = morphology.lemma[0]
        # 3 Tuple - m_tagged_processed_vocable_part.append((processed_word, lemma, reading_list))
        m_tagged_processed_vocable_part.append((processed_word, reading_list))
        if processed_word == "to" and first_to:
            first_to = False
        else:
            m_lemma_vocable_part.append(lemma)
            m_tagged_lemma_vocable_part.append((lemma, reading_list))
            m_simple_tagged_lemma_vocable.append((lemma, simple_reading_list))
            if len(simple_reading_list) > 1:
                change_simple = True
                # [[(word, [tag1])][(word, [tag2])]]
                # for tags in simple_reading_list:
                #    m_simple_tagged_lemma_vocable.append([(lemma, tags)])
            # else:
                # m_simple_tagged_lemma_vocable.append((lemma, simple_reading_list[0]))

    if change_simple:
        # [('change', ['V']), ('one', ['Pron', 'N']), ('mind', ['N'])]
        m_simple_tagged_lemma_vocable = split_simple_lemma(m_simple_tagged_lemma_vocable)
    else:
        new_simple = []
        for t in m_simple_tagged_lemma_vocable:
            new_simple.append((t[0], t[1][0]))
        m_simple_tagged_lemma_vocable = new_simple

    return no_pos_match, not_found_xtag, m_tagged_processed_vocable_part, m_lemma_vocable_part, \
        m_tagged_lemma_vocable_part, m_simple_tagged_lemma_vocable


def process_a_phrase(m_processed_item, no_pos_match, not_found_xtag, first_to):
    m_tagged_processed_vocable_part = []
    m_lemma_vocable_part = []
    m_tagged_lemma_vocable_part = []
    m_simple_tagged_lemma_vocable = []
    change_simple = False
    print(m_processed_item)
    tags = tagger.tag_text(m_processed_item[0])
    # print(tags)
    # ['Welcome\tJJ\twelcome', 'to\tTO\tto']

    # ["can't"]
    # ['ca\tMD\tca', "n't\tRB\tn't"]
    if len(m_processed_item) < len(tags):
        new_tag_array = []
        current_index_position = 0
        # print(tags)
        for current_word in tags:
            if '\'' in current_word:    # apostrophe in word: "n't\tRB\tn't
                earlier_word = tags[current_index_position - 1]
                earlier_word = earlier_word.split("\t")
                tag_earlier_word = earlier_word[1]
                current_word = current_word.split("\t")
                tag_current_word = current_word[1]
                combined_word = earlier_word[0] + current_word[0]
                del new_tag_array[current_index_position - 1]
                # depending on the combination put together
                # verb + verb ends with 've
                print(current_word)
                print(earlier_word)
                # print(tag_earlier_word)

                if m_processed_item in [["on one's own"]]:
                    new_tag_array.append(combined_word + '\tPP')

                else:
                    # verb + have
                    if current_word[0] == "'ve" and tag_earlier_word.startswith('V'):
                        new_tag_array.append(combined_word + '\tVVC')

                    # x + genitive s
                    elif current_word[0] == "'s" and tag_current_word == 'POS':
                        new_tag_array.append(combined_word + '\t' + tag_earlier_word)

                    # noun/pronoun + would, will, are, have
                    elif current_word[0] in ["'d", "'ll", "'re", "'ve"] and (tag_earlier_word.startswith('N') or
                                                                             tag_earlier_word.startswith('P')):
                        new_tag_array.append(combined_word + '\tNVC')

                    # verb + negation ends with n't
                    elif current_word[0] == "n't" and tag_earlier_word.startswith('V') or tag_earlier_word.startswith('MD'):
                        new_tag_array.append(combined_word + '\tV')

                    # pronoun + am
                    elif current_word[0] == "'m":
                        new_tag_array.append(combined_word + '\tNVC')

                    # w-word/pronoun/there + is
                    elif tag_earlier_word in ['WP', 'WRB', 'DT', 'NN', 'PP', 'EX'] and tag_current_word == 'VBZ':
                        new_tag_array.append(combined_word + '\tNVC')
                    else:
                        raise Exception("Doesn't fit any category: " + str(m_processed_item) + str(earlier_word) + str(current_word))
            else:
                new_tag_array.append(current_word)
            current_index_position += 1
        tags = new_tag_array
        print(tags)

    # print(tags)
    for m_word_info in tags:
        reading_list = []
        simple_reading_list = []
        lemma = ""

        split_word = m_word_info.split("\t")
        # print(split_word)

        # 0    | 1   | 2
        # word | Tag | Lemma
        # ca   | MD  | ca

        m_word = split_word[0]
        m_tag = split_word[1]
        # m_lemma = split_word[2]

        # info: there is tagged as exestential there but can not be found like that in xtag. The case word class will
        # be changed to 'RB' to be aligned with 'there;dort, da;aktiv;1/A1;I;av;;' in the same chapter.
        if 'there' == m_word:
            m_tag = 'RB'
        # in 'not ... anything else' anything is not correctly tagged, change to Pronoun
        if 'anything' == m_word:
            m_tag = 'PP'

        if "aren't" == m_word:
            m_tag = 'VB'

        # same words need to be looked up in lower or upper case
        morphology = Morphology(cursor, m_word)
        number = morphology.get_number_of_readings()
        if number == 0:
            morphology = Morphology(cursor, m_word.lower())
            number = morphology.get_number_of_readings()

        # info: words that didn't match in POS
        if 'where' == m_word or 'Where' == m_word:
            reading_list.append('Adv wh')
            simple_reading_list.append('Adv')
            lemma = morphology.lemma[0]

        elif 'many' == m_word:
            reading_list.append('A')
            simple_reading_list.append('A')
            lemma = morphology.lemma[0]

        elif 'other' == m_word:
            reading_list.append('A')
            simple_reading_list.append('A')
            lemma = morphology.lemma[0]

        elif 'own' == m_word:
            reading_list.append('A')
            simple_reading_list.append('A')
            lemma = morphology.lemma[0]

        elif 'CD' == m_tag:
            reading_list.append('CD')
            simple_reading_list.append('CD')
            lemma = morphology.lemma[0]

        # info: words that couldn't be found
        # todo ABR = NP?
        elif 'OTW' == m_word:
            reading_list.append('N')
            reading_list.append('PropN')
            simple_reading_list.append('N')
            simple_reading_list.append('ProP')
            lemma = m_word

        elif 'OMG' == m_word:
            reading_list.append('N')
            reading_list.append('PropN')
            simple_reading_list.append('N')
            simple_reading_list.append('ProP')
            lemma = m_word

        elif 'seal-spotting' == m_word:
            reading_list.append('V')
            simple_reading_list.append('V')
            lemma = m_word

        elif 'LOL' == m_word:
            reading_list.append('N')
            reading_list.append('PropN')
            simple_reading_list.append('N')
            simple_reading_list.append('ProP')
            lemma = m_word

        elif 'neither' == m_word:
            reading_list.append('CC')
            simple_reading_list.append('CC')
            lemma = m_word

        elif 'anymore' == m_word:
            reading_list.append('Adv')
            simple_reading_list.append('Adv')
            lemma = m_word

        elif 'eg' == m_word:
            m_word = 'e.g.'
            reading_list.append('A')
            simple_reading_list.append('A')
            lemma = m_word

        elif 'Elephants' == m_word:
            reading_list.append('N pl')
            simple_reading_list.append('N')
            lemma = 'Elephant'

        elif 'Internet' == m_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = m_word

        elif 'whale-watching' == m_word:
            reading_list.append('V')
            simple_reading_list.append('V')
            lemma = m_word

        elif 'BFF' == m_word:
            reading_list.append('N')
            reading_list.append('PropN')
            simple_reading_list.append('N')
            simple_reading_list.append('ProP')
            lemma = m_word

        elif 'fundraising' == m_word:
            reading_list.append('N')
            simple_reading_list.append('N')
            lemma = m_word

        elif 'asap' == m_word:
            reading_list.append('N')
            reading_list.append('PropN')
            simple_reading_list.append('N')
            simple_reading_list.append('ProP')
            lemma = m_word

        else:
            if number > 1:  # word has more than 1 reading
                for num in range(1, number + 1):
                    reading = morphology.get_reading_by_number(num)
                    # reading is returned as a tuple: (reading,)
                    morphology_information = MorphologyInformation(reading[0])
                    if m_tag in word_class_xtagpenn_dict.get(morphology_information.pos, 'nothing'):
                        reading_list.append(morphology_information.word_reading)
                        simple_reading_list.append(morphology_information.pos)
                        lemma = morphology_information.lemma
                if reading_list:
                    # V INF#react;V INF;;;;;;
                    # ['V INF', 'V INF', ...]
                    reading_list = list(set(reading_list))
                    simple_reading_list = list(set(simple_reading_list))
                else:
                    no_pos_match.append((m_tag, "?", m_word))
                    all_pos_not_matched.append(m_word)
            elif number == 1:  # word has one reading
                reading = morphology.get_reading_by_number(1)
                # reading is returned as a tuple: (reading,)
                morphology_information = MorphologyInformation(reading[0])

                if split_word[1] in word_class_xtagpenn_dict.get(morphology_information.pos, 'nothing'):
                    reading_list.append(morphology_information.word_reading)
                    simple_reading_list.append(morphology_information.pos)
                    # info: exception lemma for cannot
                    if m_word == 'cannot':
                        lemma = 'cannot'
                    else:
                        lemma = morphology_information.lemma
                else:  # technically a hack but if has just one reading anyway then take that
                    one_reading_phrase.append(m_word)

                    reading_list.append(morphology_information.word_reading)
                    simple_reading_list.append(morphology_information.pos)
                    lemma = morphology_information.lemma
                if not reading_list:
                    no_pos_match.append((m_tag, morphology_information.pos, m_word))
                    all_pos_not_matched.append(m_word)
            else:
                not_found_xtag.append(m_word)
                all_not_found.append(m_word)

        # test check for words with more than one reading
        if len(reading_list) > 1:
            # print(status, "/", 3020, processed_vocable)
            # print("\tAllReadings:", m_word, reading_list)
            all_double_reading.append(m_word)
        # if there is a accepted reading
        # if reading_list:
        if lemma == "":
            # ('Camden',)
            lemma = morphology.lemma[0]
        # 3 Tuple - m_tagged_processed_vocable_part.append((m_word, lemma, reading_list))
        m_tagged_processed_vocable_part.append((m_word, reading_list))
        if m_word == "to" and first_to:
            first_to = False
        else:
            m_lemma_vocable_part.append(lemma)
            m_tagged_lemma_vocable_part.append((lemma, reading_list))
            m_simple_tagged_lemma_vocable.append((lemma, simple_reading_list))
            if len(simple_reading_list) > 1:
                change_simple = True
            #    # [[(word, [tag1])][(word, [tag2])]]
            #    for tags in simple_reading_list:
            #        m_simple_tagged_lemma_vocable.append([(lemma, tags)])
            # else:
            #    m_simple_tagged_lemma_vocable.append((lemma, simple_reading_list[0]))

    # print(m_simple_tagged_lemma_vocable)
    # if no_pos_match: print(no_pos_match)
    if change_simple:
        # [('change', ['V']), ('one', ['Pron', 'N']), ('mind', ['N'])]
        m_simple_tagged_lemma_vocable = split_simple_lemma(m_simple_tagged_lemma_vocable)
    else:
        new_simple = []
        for t in m_simple_tagged_lemma_vocable:
            print(t, " - ", m_simple_tagged_lemma_vocable)
            new_simple.append((t[0], t[1][0]))
        m_simple_tagged_lemma_vocable = new_simple

    # print(m_simple_tagged_lemma_vocable)
    return no_pos_match, not_found_xtag, m_tagged_processed_vocable_part, m_lemma_vocable_part, \
        m_tagged_lemma_vocable_part, m_simple_tagged_lemma_vocable


def split_simple_lemma(x):
    height = 1
    width = len(x)
    
    #   | V | Pron  | N |
    #   | V | N     | N |
    
    for item in x:
        if len(item[1]) > 1:
            height *= len(item[1])
   
    matrix = [[0 for w in range(width)] for h in range(height)]     # first: ^v, econd <->
    
    repeat = height
    position = 0
    many_iterate = 1
    
    for item in x:
        len_of_readings = len(item[1])
        if len(item[1]) > 1:
            len_of_readings = len(item[1])
            repeat = int(repeat / len_of_readings)  # how many times is it the same
            new_pos = 0
            for m in range(0, many_iterate):
                for lof in range(0, len_of_readings):   # für die anzahl an readings
                    for i in range(0, repeat):
                        matrix[new_pos][position] = (item[0], item[1][lof])
                        new_pos += 1
        else:
            for i in range(0, height):
                matrix[i][position] = (item[0], item[1][0])
        many_iterate *= len_of_readings
        position += 1

    simple_array = []
    for simple_row in matrix:
        simple_array.append(simple_row)

    return simple_array


# --------------------------------- SOUNDEX ----------------------------------------------------------------------------

def processing_soundex(mprocessed_vocable):
    """ soundex module conforming to Knuth's algorithm
        implementation 2000-12-24 by Gregory Jorgensen
        public domain
    """

    # digits holds the soundex values for the alphabet
    digits = '01230120022455012623010202'
    fc = ''

    soundex = []
    if isinstance(mprocessed_vocable[0], list):
        for name in mprocessed_vocable:
            # split by space so it looks at each word separately
            slit_by_space = name[0].split(' ')
            concat_string = ""
            for word in slit_by_space:
                sndx = ""
                # translate alpha chars in name to soundex digits
                l = len(word)
                for c in word.upper():
                    if c.isalpha():
                        if not fc: 
                            fc = c  # remember first letter
                        d = digits[ord(c) - ord('A')]
                        # duplicate consecutive soundex digits are skipped
                        if not sndx or (d != sndx[-1]):
                            sndx += d

                # replace first digit with first alpha character
                sndx = fc + sndx[1:]

                # remove all 0s from the soundex code
                sndx = sndx.replace('0', '')

                sound = (sndx + (l * '0'))[:l]
                concat_string += sound + " "

            # return soundex code padded to len characters
            # soundex.append([(sndx + (l * '0'))[:l]])
            soundex.append([concat_string.strip()])
    else:
        # translate alpha chars in name to soundex digits
        slit_by_space = mprocessed_vocable[0].split(' ')
        # print("split ", slit_by_space)
        concat_string = ""
        for word in slit_by_space:
            sndx = ""
            # print(word)
            l = len(word)
            for c in word.upper():
                if c.isalpha():
                    if not fc:
                        fc = c  # remember first letter
                    d = digits[ord(c) - ord('A')]
                    # duplicate consecutive soundex digits are skipped
                    if not sndx or (d != sndx[-1]):
                        sndx += d

            # replace first digit with first alpha character
            sndx = fc + sndx[1:]

            # remove all 0s from the soundex code
            sndx = sndx.replace('0', '')

            sound = (sndx + (l * '0'))[:l]
            concat_string += sound + " "

        # return soundex code padded to len characters
        # soundex.append([(sndx + (l * '0'))[:l]])
        soundex.append(concat_string.strip())
    # print(soundex)
    return soundex


# --------------------------------- PROCESSING TRANSLATION -------------------------------------------------------------

def processing_translation(m_word):
    if ";" in m_word:
        print(m_word)
    if not any(item in m_word for item in exceptions):

        #array_word = re.compile("(?<=[a-zßöäü/][a-zßöäü] | \)\- | [a-zßöäü\.\-][!\.\)\-] )[,;]\s (?=[A-Za-ßöäüÜÄÖ\(][A-Za-zßöäü])(?![a-z][a-z]\))").split(m_word)
        array_word = re.compile("((?<=[a-zßöäü/][a-zßöäü])|(?<=\)-)|(?<=[a-zßöäü.-][!.)-]))[,;]\s"
                                "(?=[A-Za-ßöäüÜÄÖ(][A-Za-zßöäü])(?![a-z][a-z]\))").split(m_word)

        array_word = deal_with_punctuation_no_comma_german(array_word)
        processed = process_words(array_word)

    else:
        # print(m_word)
        processed = []
        word_array = ['x']
        if 'hier: ' in m_word:
            m_word = m_word.replace("hier: ", "")

        if 'Hallo, ich heiße …' in m_word:
            word_array = ['Hallo, ich heiße']
        elif 'Hier, bitte!, Bitte schön!' in m_word:
            word_array = ['Hier, bitte!', 'Bitte schön!']
        elif 'Ausgeschlossen!' in m_word:
            word_array = ['Ausgeschlossen!', 'Jetzt echt, oder?']
        elif 'sobald, als, in dem Moment, als ...' in m_word:
            word_array = ['sobald', 'als, in dem Moment, als']
        elif 'glücklich (Glück habend; Glück bringend)' in m_word:
            word_array = ['glücklich']
        elif 'darauf achten, (dass)' in m_word:
            word_array = ['darauf achten', 'darauf achten, dass']
        elif 'Längenmaß (91,44 cm)' in m_word:
            word_array = ['Längenmaß', '91,44 cm']
        elif '(entspricht dem deutschen Abitur)' in m_word:
            word_array = ['entspricht dem deutschen Abitur', 'Abitur']
        elif '(Anrede)' in m_word:
            m_word = m_word.replace(" (Anrede)", "")
            word_array = [m_word]
        elif '(Amtssprache in Indien)' in m_word:
            m_word = m_word.replace(" (Amtssprache in Indien)", "")
            word_array = [m_word]
        elif '(als Schulfach)' in m_word:
            m_word = m_word.replace(" (als Schulfach)", "")
            word_array = [m_word]
        elif '(nur hinter Uhrzeit zwischen Mitternacht und 12 Uhr mittags)' in m_word:
            word_array = ['morgens', 'vormittags']
        elif '(nur hinter Uhrzeit zwischen 12 Uhr mittags und Mitternacht)' in m_word:
            word_array = ['nachmittags', 'abends']
        elif '(zur Terminplanung)' in m_word:
            m_word = m_word.replace(" (zur Terminplanung)", "")
            word_array = [m_word]
        elif '(bei Freunden)' in m_word:
            m_word = m_word.replace(" (bei Freunden)", "")
            word_array = [m_word]
        elif '(an Kleidungsstücken)' in m_word:
            m_word = m_word.replace(" (an Kleidungsstücken)", "")
            word_array = [m_word]
        elif '(= 0,3048 Meter)' in m_word:
            m_word = m_word.replace(" (= 0,3048 Meter)", "")
            word_array = [m_word, '0,3048 Meter']
        elif '(Briefschlussformel)' in m_word:
            m_word = m_word.replace(" (Briefschlussformel)", "")
            ar = m_word.split(", ")
            word_array = []
            for item in ar:
                word_array.append(item)
        elif '(von Großbritannien)' in m_word:
            m_word = m_word.replace(" (von Großbritannien)", "")
            word_array = [m_word]
        elif '(Untereinheit des brit. Pfunds)' in m_word:
            m_word = m_word.replace(" (Untereinheit des brit. Pfunds)", "")
            word_array = [m_word]
        elif '(Londoner)' in m_word:
            m_word = m_word.replace(" (Londoner)", "")
            ar = m_word.split(", ")
            word_array = []
            for item in ar:
                word_array.append(item)
        elif '(Alternativbezeichnung ' in m_word:
            word_array = ['Fr.', 'Frau']
        elif '(Kobold)' in m_word:
            m_word = m_word.replace(" (Kobold)", "")
            word_array = [m_word]
        elif '(systematische wiss. Beobachtung außerhalb des Labors)' in m_word:
            m_word = m_word.replace(" (systematische wiss. Beobachtung außerhalb des Labors)", "")
            word_array = [m_word]
        elif '(in der Thronfolge)' in m_word:
            word_array = ['der Nächste', 'die Nächste']
        elif '(Einrichtung zur Betreuung sterbender Menschen)' in m_word:
            m_word = m_word.replace(" (Einrichtung zur Betreuung sterbender Menschen)", "")
            word_array = [m_word]
        elif '(beim Rugby)' in m_word:
            m_word = m_word.replace(" (beim Rugby)", "")
            word_array = [m_word]
        elif '(= 1,609 km)' in m_word:
            m_word = m_word.replace(" (= 1,609 km)", "")
            word_array = [m_word, '1,609 km']
        elif '(Zeit)' in m_word:
            word_array = ['verbringen', 'ausgeben']
        elif '(auf dem Wasser)' in m_word:
            word_array = ['fahren', 'reisen', 'segeln']
        elif '(jd, der den Text flüsternd vorspricht)' in m_word:
            word_array = ['Souffleur', 'Souffleuse']
        elif '(Sprache)' in m_word:
            word_array = ['Bengale', 'Bengalin', 'Bengali', 'bengalisch']
        elif 'der/die sich im Internat um die Schüler/innen eines Hauses kümmert/kümmern' in m_word:
            word_array = ['Angestellte', 'Angestellter']
        elif 'Aufsicht führende/r Lehrer/in' in m_word:
            word_array = ['Nachhilfelehrer', 'Nachhilfelehrerin', 'Tutorin', 'Tutor', 'Lehrerin', 'Lehrer']
        elif 'Vergangenheitsform von' in m_word:
            word_array = [re.sub("[\"„“]", "", m_word)]

        processed.extend([[x.strip(' ')] for x in word_array])
        # print(processed)
        # print()
    return processed


def deal_with_punctuation_no_comma_german(m_array_word):
    return_array = []
    for word in m_array_word:
        if any(item in word for item in ['.', '?', '!', '…', '...']):
            # print(word)
            word = re.sub("\s*\.\.\.\s*", " ", word)
            word = word.replace('.', '').replace('?', '').replace('!', '').replace(' …', '')
            # print(word)
        return_array.append(word)
    return return_array


def process_words(m_array_word):
    processed = []
    for word in m_array_word:
        word = word.strip()
        # deal with parenthesis
        if '(' in word:
            # if 'etw' in word or 'jdn' in word:
            # print(word)

            # print(word)

            # if parenthesis directly before and after word e.g. (irgend)ein(e)
            if bool(re.search('\([a-z]+\)[a-z]+\([a-z]+\)', word)):
                # print(word)
                first_word = word.replace("(", "").split(")")[0]
                middle_word = re.sub('\([a-z]+\)', '', word)
                last_word = word.replace(")", "").split("(")[2]
                word_array = [middle_word, first_word + middle_word, first_word + middle_word + last_word,
                              middle_word + last_word]
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # if parenthesis in the middle of the word e.g. Abschied(s)-
            elif bool(re.search('[a-z]+\([a-z]+\)([a-z]+|-)', word)):
                # print(word)
                if '/' in word:
                    first_part = re.match('[a-z]+\([a-z]+\)/[a-z]+\([a-z]+\)[a-z]*', word).group().split("/")
                    fw_fp = re.sub('\([a-z]+\)', '', first_part[0])
                    sw_fp = fw_fp + first_part[0].replace(')', '').split('(')[1]
                    fw_sp = re.sub('\([a-z]+\)', '', first_part[1])
                    sw_sp = first_part[1].replace(')', '').replace('(', '')
                    third_part = re.sub('[a-z]+\([a-z]+\)/[a-z]+\([a-z]+\)[a-z]*', '', word)
                    word_array = [fw_fp + third_part, sw_fp + third_part, fw_sp + third_part, sw_sp + third_part]
                    processed.extend([[x.strip()] for x in word_array])
                else:
                    # print(word)
                    first_word = re.sub('\([a-z]+\)', '', word)
                    second_word = word.replace("(", "").replace(")", "")
                    word_array = [first_word, second_word]
                    processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # if parenthesis directly after word
            # eg. ein(e), Lass(t) uns, hier: irgendein(e), ein(e) kleine(s, r), nach vorn(e)
            elif bool(re.search('[a-z]\([a-z]+\)', word)):
                # print(word)
                # it is just one word e.g. ein(e)
                if len(word.split(" ")) < 2:
                    # print(word)
                    first_word = re.sub('\([a-z]+\)', '', word)
                    second_word = word.replace("(", "").replace(")", "")
                    word_array = [first_word, second_word]
                    processed.extend([[x.strip(' ')] for x in word_array])
                # more than one word e.g. Komm(t) jetzt!
                else:
                    # print(word)
                    # 'hier:' is in word
                    if "hier: " in word:
                        word = word.replace("hier: ", "")
                        # print(word)
                        if len(word.split(" ")) < 2:  # just one word left
                            first_word = re.sub('\([a-z]+\)', '', word)
                            second_word = word.replace("(", "").replace(")", "")
                            word_array = [first_word, second_word]
                            processed.extend([[x.strip(' ')] for x in word_array])
                            # print(processed)
                        else:  # two words left
                            # print(word)
                            first_part = word.split(" ")
                            fw_fp = re.sub('\([a-z]+\)', '', first_part[0])
                            sw_fp = fw_fp + first_part[0].replace(")", "").split("(")[1]
                            fw_sp = re.sub('\([a-z]+\)', '', first_part[1])
                            sw_sp = first_part[1].replace(")", "").replace("(", "")
                            word_array = [fw_fp, sw_fp, fw_sp, sw_sp]
                            processed.extend([[x.strip(' ')] for x in word_array])
                            # print(processed)

                    # word(x) word(y,z)
                    elif bool(re.search('[a-z]\([a-z]+,', word)):  # ein(e) kleine(s, r)
                        # print(word)
                        first_part = re.match('[a-z]+\([a-z]+\)', word).group()
                        # ein(e)
                        second_part = word.replace(first_part, '').strip()
                        # kleine(s, r)
                        first_word_of_first_part = re.sub('\([a-z]+\)', '', first_part)
                        # ein
                        second_word_of_first_part = first_word_of_first_part + first_part.replace(")", "").split("(")[1]
                        # eine
                        first_word_of_second_part = re.sub('\([a-z],\s[a-z]+\)', '', second_part)
                        # kleine
                        endings_of_first_word_of_second_part = re.search('\([a-z],\s[a-z]+\)', second_part)
                        endings_of_first_word_of_second_part = endings_of_first_word_of_second_part.group(0) \
                            .replace('(', '').replace(')', '').replace(' ', '').split(',')
                        # [e, r]

                        # test
                        # orginal: ein(e) kleine(s, r)
                        # eine(m) klein(e, m)
                        # print("eine(m) klein(e, m)")
                        # first_word_of_first_part = 'eine'
                        # second_word_of_first_part = 'einem'
                        # first_word_of_second_part = 'klein'
                        # endings_of_first_word_of_second_part = ['e', 'm']

                        word_array = []

                        for iter_word in [first_word_of_first_part, second_word_of_first_part]:
                            if any(item in iter_word[-1] for item in ['a', 'e', 'i', 'o', 'u']):
                                # the first word ends with vocal
                                if any(item in first_word_of_second_part[-1] for item in ['a', 'e', 'i', 'o', 'u']):
                                    # the second word ends with a vocal
                                    word_array.append(iter_word + " " + first_word_of_second_part)
                                else:
                                    # the second word ends with a consonant
                                    word_array.append(iter_word + " " + first_word_of_second_part +
                                                      str(endings_of_first_word_of_second_part[0]))
                            else:
                                # the first word does end on a consonant
                                if any(item in first_word_of_second_part[-1] for item in ['a', 'e', 'i', 'o', 'u']):
                                    # the second word ends on a vocal e.g. kleine
                                    word_array.append(iter_word + " " + first_word_of_second_part +
                                                      str(endings_of_first_word_of_second_part[0]))
                                    word_array.append(first_word_of_first_part + " " + first_word_of_second_part +
                                                      str(endings_of_first_word_of_second_part[1]))
                                else:
                                    # the second word ends with a consonant
                                    word_array.append(iter_word + " " + first_word_of_second_part +
                                                      str(endings_of_first_word_of_second_part[0]) +
                                                      str(endings_of_first_word_of_second_part[1]))
                        processed.extend([[x.strip(' ')] for x in word_array])

                    # Lass(t) uns, (ganz) allein(e)
                    else:  # if bool(re.search('\([a-z]+\)\s', word)):
                        # print(word)
                        # still more than one () in word e.g. (ganz) allein(e)
                        if word.count('(') > 1:
                            # print(word)
                            first_word = word.split(" ")[0].replace("(", "").replace(")", "")
                            # ganz
                            second_word = re.sub("\([a-z]+\)", "", word.split(" ")[1])
                            # allein
                            ending_second_word = word.split(" ")[1].replace(")", "").split("(")[1]
                            # e
                            word_array = [second_word, second_word + ending_second_word,
                                          first_word + " " + second_word,
                                          first_word + " " + second_word + ending_second_word]
                            processed.extend([[x.strip(' ')] for x in word_array])
                            # print(processed)
                        # one parenthesis left, e.g. Lass(t) uns,
                        else:
                            # print(word)
                            first_word = re.sub("\([a-z]\)", "", word)
                            second_word = word.replace("(", "").replace(")", "")
                            word_array = [first_word, second_word]
                            processed.extend([[x.strip(' ')] for x in word_array])
                            # print(processed)

            # a parenthesis before a parenthesis which is directly before a word e.g. (miteinander) (ver)mischen
            elif bool(re.search('\([a-z]+\)\s\([a-z]+\)[a-z]+', word)):
                # print(word)
                first_word = word.split(" ")[0].replace("(", "").replace(")", "")
                # miteinander
                second_word = re.sub("\([a-z]+\)", "", word.split(" ")[1])
                # mischen
                prefix_second_word = re.match("\([a-z]+\)", word.split(" ")[1])
                prefix_second_word = prefix_second_word.group().replace("(", "").replace(")", "")
                # ver
                word_array = [second_word, prefix_second_word + second_word,
                              first_word + " " + second_word, first_word + " " + prefix_second_word + second_word]
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # parenthesis directly before word e.g. (an)hören, hier: (Eisen)bahn
            elif bool(re.search('\([A-Za-zßöüä]+\)[a-zßöüä]+', word)):
                # print(word)
                if "hier: " in word:
                    word = word.replace("hier: ", "")
                first_word = re.sub("\([A-Za-z]+\)", "", word)
                second_word = word.replace("(", "").replace(")", "")
                word_array = [first_word, second_word]
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # parenthesis before word e.g. (zu) spät, kein(e, en) (mehr) haben
            elif bool(re.search('\([A-Za-zßöüä]+\)\s[a-zA-Zßöüä]+', word)):
                # print(word)
                # more than one parenthesis in word
                if word.count("(") > 1:
                    # print(word)
                    first_word = re.sub("\(.*", "", word.split(") ")[0])
                    pattern = re.compile('\([a-z]+,\s[a-z]+\)')
                    first_word_endings = re.search(pattern, word).group().replace("(", "").replace(")", "").split(", ")
                    second_word = word.split(") ")[1].replace("(", "").replace(")", "")
                    third_word = word.split(") ")[2]
                    word_array = [first_word + first_word_endings[0] + ' ' + third_word,
                                  first_word + first_word_endings[1] + ' ' + third_word,
                                  first_word + first_word_endings[0] + ' ' + second_word + ' ' + third_word,
                                  first_word + first_word_endings[1] + ' ' + second_word + ' ' + third_word]
                    processed.extend([[x.strip()] for x in word_array])
                    # print(processed)
                else:
                    # print(word)
                    pattern = re.compile('\([a-z]+\)\s')
                    first_word = re.sub(pattern, "", word)
                    second_word = word.replace("(", "").replace(")", "")
                    word_array = [first_word, second_word]
                    processed.extend([[x.strip(' ')] for x in word_array])
                    # print(processed)

            # parenthesis directly after word two endings e.g. diese(r, s)
            elif bool(re.search("\([a-z]+,\s[a-z]+\)", word)):
                # print(word)
                if 'hier: ' in word:
                    word = word.replace("hier: ", "")
                if word.count(" ") > 1:
                    # print(word)
                    first_word = re.split("(?<=[a-zA-Z])\s(?=[a-zA-Z])", word)[0]
                    second_word = re.split("(?<=[a-zA-Z])\s(?=[a-zA-Z])", word)[1].split("(")[0]
                    second_word_endings = re.split("(?<=[a-zA-Z])\s(?=[a-zA-Z])", word)[1] \
                        .split('(')[1].replace(')', '').split(', ')
                    word_array = [first_word + ' ' + second_word]

                    if any(item in second_word[-1] for item in ['a', 'e', 'i', 'o', 'u']):
                        word_array.append(first_word + " " + second_word + second_word_endings[0])
                        word_array.append(first_word + " " + second_word + second_word_endings[1])
                    else:
                        word_array.append(first_word + " " + second_word + second_word_endings[0])
                        word_array.append(
                            first_word + " " + second_word + second_word_endings[0] + second_word_endings[1])
                else:
                    # print(word)
                    second_word = word.split("(")[0]
                    second_word_endings = word.split("(")[1].replace(")", "").split(", ")
                    word_array = [second_word]

                    if any(item in second_word[-1] for item in ['a', 'e', 'i', 'o', 'u']):
                        word_array.append(second_word + second_word_endings[0])
                        word_array.append(second_word + second_word_endings[1])
                    else:
                        word_array.append(second_word + second_word_endings[0])
                        word_array.append(second_word + second_word_endings[0] + second_word_endings[1])
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # parenthesis directly after word three endings e.g. ein(e, er, es)
            elif bool(re.search("\([a-z]+,\s[a-z]+,\s[a-z]+\)", word)):
                # print(word)
                first_word = word.split("(")[0]
                first_word_endings = word.split("(")[1].replace(")", "").split(", ")
                word_array = [first_word,
                              first_word + first_word_endings[0],
                              first_word + first_word_endings[1],
                              first_word + first_word_endings[2]]
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # parenthesis after word that includes '/' e.g. Viertel (nach/vor)
            elif bool(re.search("[a-z]\s\([a-z]+/[a-z]+", word)):
                # print(word)
                first_word = word.split("(")[0]
                second_word_endings = word.split("(")[1].replace(")", "").split("/")
                word_array = [first_word + second_word_endings[0], first_word + second_word_endings[1]]
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # parenthesis directly after word that includes '/' e.g. solch(er/es)
            elif bool(re.search("[a-z]\([a-z]+/[a-z]+", word)):
                # print(word)
                if len(word.split()) > 1:
                    # print(word)
                    first_part = word.split()[0]
                    first_word = first_part.split("(")[0]
                    first_word_endings = first_part.split("(")[1].replace(")", "").split("/")
                    second_word = word.split()[1]
                    word_array = [first_word + " " + second_word,
                                  first_word + first_word_endings[0] + " " + second_word,
                                  first_word + first_word_endings[1] + " " + second_word,
                                  first_word + first_word_endings[2] + " " + second_word]
                else:
                    # print(word)
                    first_word = word.split("(")[0]
                    first_word_endings = word.split("(")[1].replace(")", "").split("/")
                    word_array = [first_word, first_word + first_word_endings[0],
                                  first_word + first_word_endings[1]]
                    if len(first_word_endings) == 3:
                        word_array.append(first_word + first_word_endings[2])
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # parenthesis directly before word that includes '/' e.g. (Straßen-/Verkehrs)schild
            elif bool(re.search("\([a-zA-Zß]+-/[a-zA-Z]+\)[a-zA-Z]+", word)):
                # print(word)
                main_word = word.split(")")[1]
                prefixes = word.split(")")[0].replace("(", "").split("-/")
                word_array = [prefixes[0] + main_word, prefixes[1] + main_word]
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # parenthesis directly after word that includes '-' e.g. Spielzeug(-), Universität(s-)
            elif bool(re.search("\([a-z]*-\)", word)):
                # print(word)
                word_array = [re.sub("\([a-z]*-\)", "", word)]
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # parenthesis after word e.g. Angst haben/sich fürchten (vor)
            elif bool(re.search("[a-zA-ZöäüÜÄÖ]+\s\([a-züäö]+\)", word)):
                # print(word)
                if "hier: " in word:
                    word = word.replace("hier: ", "")
                if "/" in word:
                    # print(word)
                    first_part = re.search("[a-zA-ZüäöÜÄÖß]+\s*[a-zA-ZüäöÜÄÖß]*/[a-zA-ZüäöÜÄÖß]+\s*[a-zA-ZüäöÜÄÖß]*",
                                           word).group()
                    first_word = first_part.split("/")
                    second_word = re.search("(?<=\()[a-zA-ZüäöÜÄÖß]+(?=\))", word).group()
                    word_array = [first_word[0] + ' ' + second_word, first_word[1] + ' ' + second_word]
                else:
                    # print(word)
                    first_word = re.sub("\([a-zA-ZüäöÜÄÖß]+\)", "", word)
                    second_word = re.search("(?<=\()[a-zA-ZüäöÜÄÖß]+(?=\))", word).group()
                    word_array = [first_word, first_word + second_word]
                processed.extend([[x.strip()] for x in word_array])
                # print(processed)

            # parenthesis after word with more than one word e.g. Ich bin zehn (Jahre alt)
            elif bool(re.search("[a-zA-ZöäüÜÄÖ]+\s\([a-zA-ZßÜÄÖüäö]+(\s[a-zA-ZßÜÄÖüäö]+)+\)\Z", word)):
                # print(word)
                if "z B " in word:
                    word = word.replace("z B ", "z. B. ")
                    first_word = re.sub("\([a-zA-ZßÜÄÖüäö]+(\s[a-zA-ZßÜÄÖüäö]+)+\)", "", word)
                    second_word = re.search("(?<=\()[a-zA-ZßÜÄÖüäö]+(\s[a-zA-ZßÜÄÖüäö]+)+(?=\))", word).group()
                    word_array = [first_word, second_word]
                else:
                    # print(word)
                    first_word = re.sub("\([a-zA-ZßÜÄÖüäö]+(\s[a-zA-ZßÜÄÖüäö]+)+\)", "", word)
                    second_word = re.search("(?<=\()[a-zA-ZßÜÄÖüäö]+(\s[a-zA-ZßÜÄÖüäö]+)+(?=\))", word).group()
                    word_array = [first_word, first_word + second_word]
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # parenthesis that is between words e.g. sich (anfangen zu) fürchten
            elif bool(re.search("[a-zA-ZöäüÜÄÖ]+\s\([a-zA-ZßÜÄÖüäö]+(\s[a-zA-ZßÜÄÖüäö]+)+\)", word)):
                # print(word)
                first_version = re.sub("\([a-zA-ZßÜÄÖüäö]+(\s[a-zA-ZßÜÄÖüäö]+)+\)\s", "", word)
                second_version = word.replace("(", "").replace(")", "")
                word_array = [first_version, second_version]
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # parenthesis directly before word with '-' e.g. (Zeitungs-)Bericht
            elif bool(re.search("\([a-zA-Z]+-\)", word)):
                # print(word)
                if "hier: " in word:
                    word = word.replace("hier: ", "")
                first_version = re.sub("\([a-zA-Z]+-\)", "", word)
                second_version = word.replace("(", "").replace(")", "")
                word_array = [first_version, second_version]
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # parenthesis before word with '/' e.g. (auf jdn/etw) reagieren, (du/Sie) selbst
            elif bool(re.search("[a-zA-Z]+/[a-zA-Z]+(?=\))", word)):
                # print(word)
                first_word = word.split(")")[1]
                prefixes = word.split(")")[0].replace("(", "")
                if len(prefixes.split()) > 1:
                    first_prefixes = prefixes.split()[0]
                    second_prefixes = prefixes.split()[1].split("/")
                    word_array = [first_word, first_prefixes + " " + second_prefixes[0] + first_word,
                                  first_prefixes + " " + second_prefixes[1] + first_word]
                else:
                    prefixes = word.split(")")[0].replace("(", "").split("/")
                    word_array = [first_word, prefixes[0] + first_word, prefixes[1] + first_word]
                processed.extend([[x.strip(' ')] for x in word_array])
                #print(processed)

            # word that still contains '/' - (über etw) traurig/aufgebracht sein
            elif "/" in word:
                # print(word)
                parenthesis = re.search("(?<=\()[a-züäö]+\s[a-z]+(?=\))", word).group()
                middle_words = word.split()[2].split("/")
                last_word = word.split()[3]
                word_array = [middle_words[0] + " " + last_word,
                              middle_words[1] + " " + last_word,
                              parenthesis + " " + middle_words[0] + " " + last_word,
                              parenthesis + " " + middle_words[1] + " " + last_word]
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # all parenthesis words that are left
            else:
                # print(word)
                first_version = re.sub("\([a-zA-ZäüöÜÄÖß-]+(\s[a-zA-ZäüöÜÄÖß-]+)*\)", "", word)
                second_version = word.replace("(", "").replace(")", "")
                word_array = [first_version, second_version]
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)
        else:
            # print("w", word)
            if 'auch: ' in word:
                word = re.sub("(hier\s)*auch:\s", "", word)
            if 'hier: ' in word:
                word = word.replace("hier: ", "")

            # a '/' in word to seperate between female and male form e.g. Freund/in
            if "/in" in word:
                # print(word)
                first_word = word.split("/")[0]
                second_word = word.replace("/", "")
                word_array = [first_word, second_word]
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # a '/' in word to seperate between forms e.g. Deutsche/r, kein/e
            elif bool(re.search("/[er]\Z", word)):
                #print(word)
                first_word = word.split("/")[0]
                second_word = word.replace("/", "")
                word_array = [first_word, second_word]
                processed.extend([[x.strip(' ')] for x in word_array])
                #print(processed)

            # slash denoting separate words
            elif '/' in word and len(word.split()) == 1 and '-' not in word:
                # print(word)
                words = word.split("/")
                word_array = []
                for w in words:
                    word_array.append(w)
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # after the schema der-/die-/dasjenige
            elif '/' in word and '-' in word:
                # print(word)
                if 'der-/die-/dasselbe' in word:
                    word_array = ['derselbe', 'dieselbe', 'dasselbe']
                elif 'Wohltätigkeits-/Benefiz-' in word:
                    word_array = ['Wohltätigkeits', 'Benefiz']
                elif 'der-/die-/dasjenige' in word:
                    word_array = ['derjenige', 'diejenige', 'dasjenige']
                elif 'Aufnahme-/Tonstudio' in word:
                    word_array = ['Aufnahmestudio', 'Tonstudio']
                elif 'Höhlenwandern/-wanderung' in word:
                    word_array = ['Höhlenwandern', 'Höhlenwanderung']
                elif 'Wohltätigkeits-/Benefiz -' in word:
                    word_array = ['Wohltätigkeits', 'Benefiz']
                else:
                    word_array = []
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            elif 'jdn/etw' in word or 'jdm/etw' in word or 'etw/jdn' in word:
                # print(word)
                words = word.split()
                one = ""
                two = ""
                word_array = []
                for w in words:
                    if w == 'jdn/etw' or w == 'jdm/etw' or w == 'etw/jdn':
                        one += " " + w.split("/")[0]
                        two += " " + w.split("/")[1]
                    else:
                        one += " " + w
                        two += " " + w
                word_array.append(one)
                word_array.append(two)
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # all other words that include a '/'
            elif '/' in word:
                # print(word)
                if 'Das ist mein Bruder/meine Schwester' in word:
                    word_array = ['Das ist mein Bruder', 'Das ist meine Schwester']
                elif 'Wo ist / Wo sind' in word:
                    word_array = ['Wo ist', 'Wo sind']
                elif 'Wie spät/Wie viel Uhr ist es' in word:
                    word_array = ['Wie spät ist es', 'Wie viel Uhr ist es']
                elif 'Wie spät/Wie viel Uhr ist es' in word:
                    word_array = ['Wie spät ist es', 'Wie viel Uhr ist es']
                elif 'einen Ausflug/eine Reise machen' in word:
                    word_array = ['einen Ausflug machen', 'eine Reise machen']
                elif 'der/die andere' in word:
                    word_array = ['der andere', 'die andere']
                elif 'Was kostet/kosten' in word:
                    word_array = ['Was kostet', 'Was kosten']
                elif 'schade/bedauerlich sein' in word:
                    word_array = ['schade sein', 'bedauerlich sein']
                elif 'rechts/links abbiegen' in word:
                    word_array = ['rechts abbiegen', 'links abbiegen']
                elif 'Wie geht es dir/Ihnen/euch' in word:
                    word_array = ['Wie geht es dir', 'Wie geht es Ihnen', 'Wie geht es euch']
                elif 'in Urlaub gehen/fahren' in word:
                    word_array = ['in Urlaub gehen', 'in Urlaub fahren']
                elif 'der/die andere' in word:
                    word_array = ['der andere', 'die andere']
                elif 'frei haben/sein' in word:
                    word_array = ['frei haben', 'frei sein']
                elif 'am liebsten/am meisten' in word:
                    word_array = ['am liebsten', 'am meisten']
                elif 'der/die/das Einzige' in word:
                    word_array = ['der Einzige', 'die Einzige', 'das Einzige']
                elif 'Glück bringen/Unglück bringen' in word:
                    word_array = ['Glück bringen', 'Unglück bringen']
                elif 'Worum geht es in/bei' in word:
                    word_array = ['Worum geht es in', 'Worum geht es bei']
                elif 'einen Ausflug/eine Reise machen' in word:
                    word_array = ['einen Ausflug machen', 'eine Reise machen']
                elif 'rechts/links abbiegen' in word:
                    word_array = ['rechts abbiegen', 'links abbiegen']
                elif 'in einem Film/Theaterstück die Hauptrolle spielen' in word:
                    word_array = ['in einem Film die Hauptrolle spielen',
                                  'in einem Theaterstück die Hauptrolle spielen']
                elif 'jede/r andere' in word:
                    word_array = ['jede andere', 'jeder andere']
                elif 'jdn/sich lächerlich machen' in word:
                    word_array = ['jdn lächerlich machen', 'jdn/sich lächerlich machen']
                elif 'mit jdm Mitgefühl/Mitleid haben' in word:
                    word_array = ['mit jdm Mitgefühl haben', 'mit jdm Mitleid haben']
                elif 'für immer beste Freundinnen/Freunde' in word:
                    word_array = []
                elif 'der/die/das jüngste /neueste' in word:
                    word_array = ['der jüngste', 'die jüngste', 'das jüngste', 'der neueste', 'die neueste',
                                  'das neueste']
                elif 'das Beste aus etw machen/herausholen' in word:
                    word_array = ['das Beste aus etw machen', 'das Beste aus herausholen']
                elif 'sich einer Sache bewusst sein/werden' in word:
                    word_array = ['sich einer Sache bewusst sein', 'sich einer Sache bewusst werden']
                elif 'in Verlegenheit/eine peinliche Lage bringen' in word:
                    word_array = ['in Verlegenheit bringen', 'in eine peinliche Lage bringen']
                elif 'online veröffentlichter Beitrag/Artikel/Eintrag' in word:
                    word_array = ['online veröffentlichter Beitrag', 'online veröffentlichter Artikel',
                                  'online veröffentlichter Eintrag']
                elif 'der/die/das Einzige' in word:
                    word_array = ['der Einzige', 'die Einzige', 'das Einzige']
                elif 'einen Sonnenbrand haben/bekommen' in word:
                    word_array = ['einen Sonnenbrand haben', 'einen Sonnenbrand bekommen']

                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # words that end with '-' e.g. Lieblings-
            elif word and word[-1] == '-':
                # print(word)
                word_array = [word, word[:-1]]
                processed.extend([[x.strip(' ')] for x in word_array])
                # print(processed)

            # everything else
            else:
                word_array = [word]
                processed.extend([[x.strip(' ')] for x in word_array])
    return processed


# --------------------------------- GERMAN SOUNDEX ---------------------------------------------------------------------

def processing_translation_soundex(m_processed_translation):
    # print(m_processed_translation)
    # [['nicht können']], [['ein'], ['eine']]
    koelner_soundex = []
    for vocable in m_processed_translation:
        # ['nicht können'], ['ein']
        koelner = ""
        for word in np.word_tokenize(vocable[0], 'german'):
            # print(type(word))
            koelner += " " + kph.encode(word)
        if len(m_processed_translation) > 1:
            koelner_soundex.append([koelner.strip()])
        else:
            koelner_soundex.append(koelner.strip())
    # print(koelner_soundex)
    return koelner_soundex

# --------------------------------- CLASS ------------------------------------------------------------------------------


class Morphology:

    def __init__(self, cursor, word):
        self.cursor = cursor
        # _id;Word;Lemma;Reading1;Reading2;Reading3;Reading4;Reading5;Reading6;Reading7;Reading8
        # cursor.execute("SELECT * FROM employee")
        # print("Morph: word", word)
        word = word.replace("'", "''")
        # print("Morph: word", word)
        self.counter = 0
        self.all_readings = ""
        self.id = cursor.execute("SELECT _id FROM xtagmorph where Word = '" + word + "'").fetchone()
        self.word = word
        self.lemma = cursor.execute("SELECT Lemma FROM xtagmorph where Word = '" + word + "'").fetchone()
        self.reading1 = cursor.execute("SELECT Reading1 FROM xtagmorph where Word = '" + word + "'").fetchone()
        self.reading2 = cursor.execute("SELECT Reading2 FROM xtagmorph where Word = '" + word + "'").fetchone()
        self.reading3 = cursor.execute("SELECT Reading3 FROM xtagmorph where Word = '" + word + "'").fetchone()
        self.reading4 = cursor.execute("SELECT Reading4 FROM xtagmorph where Word = '" + word + "'").fetchone()
        self.reading5 = cursor.execute("SELECT Reading5 FROM xtagmorph where Word = '" + word + "'").fetchone()
        self.reading6 = cursor.execute("SELECT Reading6 FROM xtagmorph where Word = '" + word + "'").fetchone()
        self.reading7 = cursor.execute("SELECT Reading7 FROM xtagmorph where Word = '" + word + "'").fetchone()
        # self.reading8 = cursor.execute("SELECT Reading8 FROM xtagmorph where Word = '" + word + "'").fetchone()

        # print("Morph: query", "SELECT Reading1 FROM xtagmorph where Word = '" + word + "'")
        # print("Morph: reading1", self.reading1)

    def get_number_of_readings(self):
        if self.reading1 is not None and not self.reading1[0] == '':
            self.counter += 1
        if self.reading2 is not None and not self.reading2[0] == '':
            self.counter += 1
        if self.reading3 is not None and not self.reading3[0] == '':
            self.counter += 1
        if self.reading4 is not None and not self.reading4[0] == '':
            self.counter += 1
        if self.reading5 is not None and not self.reading5[0] == '':
            self.counter += 1
        if self.reading6 is not None and not self.reading6[0] == '':
            self.counter += 1
        if self.reading7 is not None and not self.reading7[0] == '':
            self.counter += 1
        # if self.reading8 is not None and not self.reading8[0] == '':
        #    self.counter += 1

        return self.counter

    def get_reading_by_number(self, number):
        if number == 1:
            return self.reading1
        elif number == 2:
            return self.reading2
        elif number == 3:
            return self.reading3
        elif number == 4:
            return self.reading4
        elif number == 5:
            return self.reading5
        elif number == 6:
            return self.reading6
        elif number == 7:
            return self.reading7
        # elif number == 8:
        #    return self.reading8

    def return_all_readings(self):
        if self.reading1 is not None and not self.reading1[0] == '':
            self.all_readings += self.reading1[0]
        if self.reading2 is not None and not self.reading2[0] == '':
            self.all_readings += ";" + self.reading2[0]
        if self.reading3 is not None and not self.reading3[0] == '':
            self.all_readings += ";" + self.reading3[0]
        if self.reading4 is not None and not self.reading4[0] == '':
            self.all_readings += ";" + self.reading4[0]
        if self.reading5 is not None and not self.reading5[0] == '':
            self.all_readings += ";" + self.reading5[0]
        if self.reading6 is not None and not self.reading6[0] == '':
            self.all_readings += ";" + self.reading6[0]
        if self.reading7 is not None and not self.reading7[0] == '':
            self.all_readings += ";" + self.reading7[0]
        # if self.reading8 is not None and not self.reading8[0] == '':
        #    self.all_readings += ";" + self.reading8[0]

        return self.all_readings


class MorphologyInformation:
    def __init__(self, m_reading):
        self.lemma = ""
        self.pos = ""
        self.number = ""
        self.lingTime = ""
        self.infoLemma = ""
        self.lingCase = ""
        self.gender = ""

        self.posList = ["A", "Adv", "Comp", "Conj", "Det", "G", "I", "N", "NVC", "Part",
                        "Punct", "Pron", "Prep", "PropN", "V", "VVC"]
        self.caseList = ["acc", "nom", "GEN", "nomacc"]
        self.timeList = ["PAST", "PRES", "PPART", "PROG"]
        self.genderList = ["masc", "fem", "neut", "reffem", "refmasc"]
        self.numberList = ["1sg", "2sg", "3sg", "1pl", "2pl", "3pl", "pl", "SG", "2nd",
                           "3rd", "ref1sg", "ref2sg", "ref3sg", "ref1pl", "ref2pl", "ref3pl"]

        self.isWeakVerb = False
        self.isStrongVerb = False
        self.isInfinitive = False
        self.isContractions = False
        self.isNegation = False
        self.isPassive = False
        self.isIndaux = False
        self.isComparative = False
        self.isSuperlative = False
        self.isReflexive = False
        self.isTO = False
        self.isWh = False
        self.isCONTR = False

        self.word_reading = ""

        # print("MorpInfo: reading", reading)

        if "#" in m_reading:
            reading_with_lemma = m_reading.split("#")
            # print("MorpInfo: lemmaSplit", reading_with_lemma)
            self.lemma = reading_with_lemma[1].strip()
        else:
            reading_with_lemma = [m_reading]
            # print("MorpInfo: NoLemmaSplit", reading_with_lemma)
        self.word_reading = reading_with_lemma[0]
        reading = reading_with_lemma[0].strip().split(" ")

        # print("MorpInfo:", m_reading)

        if reading[0] == "Punct":
            self.set_pos_tag(m_reading)
        elif reading[0] == "Prep":
            self.set_pos_tag(reading)
        elif reading[0] == "Conj":
            self.set_pos_tag(reading)
        elif reading[0] == "Comp":
            self.set_pos_tag(reading)
        elif reading[0] == "G":
            self.set_pos_tag(reading)
        elif reading[0] == "I":
            self.set_pos_tag(reading)
        elif reading[0] == "Part":
            self.set_pos_tag(reading)
        elif reading[0] == "Adv":
            self.set_adverb_tag(reading)
        elif reading[0] == "A":
            self.set_adjective_tag(reading)
        elif reading[0] == "VVC":
            self.set_vvc_tag(reading)
        elif reading[0] == "PropN":
            self.set_proper_noun_tag(reading)
        elif reading[0] == "N":
            self.set_noun_tag(reading)
        elif reading[0] == "Det":
            self.set_determiner_tag(reading)
        elif reading[0] == "NVC":
            self.set_nvc_tag(reading)
        elif reading[0] == "V":
            self.set_verb_tag(reading)
        elif reading[0] == "Pron":
            self.set_pronoun_tag(reading)

    def set_adverb_tag(self, reading):
        # Adv {'wh'}
        self.set_pos_tag(reading)
        self.set_wh_tag(reading)

    def set_adjective_tag(self, reading):
        # A {'SUPER', 'COMP'}
        self.set_pos_tag(reading)
        if "COMP" in reading:
            self.isComparative = True
        elif "SUPER" in reading:
            self.isSuperlative = True

    def set_vvc_tag(self, reading):
        # VVC {'PRES', 'INF'}
        self.set_pos_tag(reading)
        self.set_time_tag(reading)
        self.set_infinitive_tag(reading)

    def set_proper_noun_tag(self, reading):
        # PropN {'3sg', '3pl', 'GEN'}
        self.set_pos_tag(reading)
        self.set_number_tag(reading)
        self.set_case_tag(reading)

    def set_noun_tag(self, reading):
        # N {'3sg', 'masc', '3pl', 'GEN'}
        self.set_pos_tag(reading)
        self.set_number_tag(reading)
        self.set_case_tag(reading)
        self.set_gender_tag(reading)

    def set_determiner_tag(self, reading):
        # Det {'ref2sg', 'ref3pl', 'ref2nd', 'ref1sg', 'ref3sg', 'ref1pl', 'refmasc', 'wh', 'reffem', 'GEN'}
        self.set_pos_tag(reading)
        self.set_number_tag(reading)
        self.set_case_tag(reading)
        self.set_gender_tag(reading)
        self.set_wh_tag(reading)

    def set_nvc_tag(self, reading):
        # NVC {'1sg', '3sg', 'masc', 'fem', 'neut', 'STR', 'wh', '3pl', 'PAST', 'PRES', '1pl', '2nd'}
        self.set_pos_tag(reading)
        self.set_number_tag(reading)
        self.set_case_tag(reading)
        self.set_gender_tag(reading)
        self.set_wh_tag(reading)
        self.set_time_tag(reading)
        self.set_strong_verb_tag(reading)

    def set_verb_tag(self, reading):
        # V {'1sg', 'INDAUX', '3sg', 'NEG', 'INF', 'PROG', 'TO', 'STR', 'pl', '3pl', 'PAST', 'PRES', 'WK', 'PPART',
        # 'PASSIVE', 'CONTR', '2sg'}
        self.set_pos_tag(reading)
        self.set_number_tag(reading)
        self.set_indaux_tag(reading)
        self.set_negation_tag(reading)
        self.set_infinitive_tag(reading)
        self.set_time_tag(reading)
        self.set_to_tag(reading)
        self.set_strong_verb_tag(reading)
        self.set_weak_verb_tag(reading)
        self.set_passive_tag(reading)
        self.set_contr_tag(reading)

    def set_pronoun_tag(self, reading):
        # Pron {'ref2sg', '3sg', 'masc', 'ref3pl', '2pl', '3rd', '1sg', 'fem', 'reffem', 'refmasc', 'neut', 'wh',
        # '3pl', 'nomacc', 'ref1sg', '1pl', 'ref3sg', 'GEN', 'ref1pl', 'ref2nd', 'NEG', 'nom', 'acc', 'refl',
        # '2nd', '2sg'}
        self.set_pos_tag(reading)
        self.set_number_tag(reading)
        self.set_gender_tag(reading)
        self.set_wh_tag(reading)
        self.set_case_tag(reading)
        self.set_negation_tag(reading)
        self.set_reflexive_tag(reading)

    def set_pos_tag(self, reading):
        self.pos = reading[0]

    def set_wh_tag(self, reading):
        if "wh" in reading:
            self.isWh = True

    def set_infinitive_tag(self, reading):
        if "INF" in reading:
            self.isInfinitive = True

    def set_strong_verb_tag(self, reading):
        if "STR" in reading:
            self.isStrongVerb = True

    def set_weak_verb_tag(self, reading):
        if "WK" in reading:
            self.isWeakVerb = True

    def set_indaux_tag(self, reading):
        if "INDAUX" in reading:
            self.isIndaux = True

    def set_negation_tag(self, reading):
        if "NEG" in reading:
            self.isNegation = True

    def set_to_tag(self, reading):
        if "TO" in reading:
            self.isTO = True

    def set_passive_tag(self, reading):
        if "PASSIVE" in reading:
            self.isPassive = True

    def set_contr_tag(self, reading):
        if "CONTR" in reading:
            self.isCONTR = True

    def set_reflexive_tag(self, reading):
        if "refl" in reading:
            self.isReflexive = True

    def set_time_tag(self, reading):
        self.lingTime = set(reading).intersection(set(self.timeList))

    def set_number_tag(self, reading):
        self.number = set(reading).intersection(set(self.numberList))

    def set_case_tag(self, reading):
        self.lingCase = set(reading).intersection(set(self.caseList))

    def set_gender_tag(self, reading):
        self.gender = set(reading).intersection(set(self.genderList))

# --------------------------------- MAIN -------------------------------------------------------------------------------

if __name__ == '__main__':

    # missing one translation
    # info: deleted rows: ;als;aktiv;3/A2;I;k;;
    # info:              ;der/die/das;passiv;1/C2;II;d;;
    # info:              became;;passiv;6/P11;II;;;
    # info:              golf;;passiv;6/O5;II;;;

    # no word class
    # info: introduced and added word class prefix to: pre-;Vor-;passiv;4/A1;II;prefix;;
    # is under exceptions process_word

    # info: added word class Noun to: Miss (BE);hier: Frau Lehrerin (Anrede);passiv;4/C1;II;;;
    # to be consistent with xtag
    # info: added word class Noun to: Mr (= Mister);Herr (Anrede);aktiv;1/B6;I;;*Mr* Scott;ID1389841
    # to be consistent with xtag

    start = timeit.default_timer()

    # 0       | 1            | 2      | 3          | 4    | 5       | 6            | 7
    # Vokabel | Uebersetzung | Status | Fundstelle | Band | Wortart | Beispielsatz | Hinweis

    with open('Vokabelliste.csv', 'r') as vocin, open("updated_vocabulary_3_tuple.csv", 'w') as vocout:
        vocreader = csv.reader(vocin, delimiter=';')
        vocwriter = csv.writer(vocout, delimiter=';')

        header = next(vocreader)
        vocwriter.writerow(['_id'] + [header[0]] + ['processed_vocable'] + ['tagged_processed_vocable'] +
                           ['processed_vocable_soundex'] + ['lemma_vocable'] + ['tagged_lemma_vocable'] +
                           ['tagged_lemma_simple_vocable'] +
                           [header[1]] + ['processed_translation'] + ['tagged_processed_translation'] +
                           ['processed_translation_soundex'] + ['lemma_translation'] + ['tagged_lemma_translation'] +
                           header[2:])

        for row in vocreader:
            print(status, '/', 3018)
            row_id = status

            processed_vocable = processing_vocabulary(row[0])
            # print(processed_vocable)

            word_class = row[5]
            tagged_processed_vocable, lemma_vocable, tagged_lemma_vocable, tagged_lemma_simple_vocable = \
                tagging_processed_vocable(processed_vocable, word_class)

            processed_vocable_soundex = processing_soundex(processed_vocable)

            processed_translation = processing_translation(row[1])  # -- not done
            tagged_processed_translation = ['']
            processed_translation_soundex = processing_translation_soundex(processed_translation)
            lemma_translation = ['']
            tagged_lemma_translation = ['']

            vocwriter.writerow([row_id] + [row[0]] + [processed_vocable] + [tagged_processed_vocable] +
                               [processed_vocable_soundex] + [lemma_vocable] + [tagged_lemma_vocable] +
                               [tagged_lemma_simple_vocable] +
                               [row[1]] + [processed_translation] + [tagged_processed_translation] +
                               [processed_translation_soundex] + [lemma_translation] + [tagged_lemma_translation] +
                               row[2:])

            status += 1
    print("\n\n")
    print("Not Found", len(set(all_not_found)), set(all_not_found), "\n")
    # print("Double Reading", len(set(all_double_reading)), set(all_double_reading), "\n")
    print("No POS Match", len(set(all_pos_not_matched)), set(all_pos_not_matched), "\n")
    print("Noun", len(as_noun), as_noun, "\n")
    print("One", len(one_reading), one_reading, "\n")
    print("OnePh", len(one_reading_phrase), one_reading_phrase, "\n")
    print(timeit.default_timer() - start)
