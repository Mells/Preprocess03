import csv
import re
import sqlite3
import timeit

from O0_preprocess_vocabulary.class_morphology_information import Morphology_Information

from O0_preprocess_vocabulary.classes.class_morphology import Morphology

status = 1
all_not_found = []
# --------------------------------- DATABASE ----------------------------------------------

connection = sqlite3.connect("xtag.db")
cursor = connection.cursor()

# >>> import sqlite3
# >>> connection = sqlite3.connect("company.db")
# cursor = connection.cursor()
# cursor.execute("SELECT * FROM employee")
# print("fetchall:")
# result = cursor.fetchall()
# for r in result:
#     print(r)
# cursor.execute("SELECT * FROM employee")
# print("\nfetch one:")
# res = cursor.fetchone()
# print(res)

# --------------------------------- WORD CLASS DICTIONARY --------------------------------
# d           determiner
# s           substantive
# i           informal(?)
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

word_class_dictionary = {'d': ['Det'], 's': ['N', 'PropN'], 'v': ['V'], 'av': ['Adv'], 'a': ['A'], 'k': ['Conj'],
                         'p': ['Pron'], 'pr': ['Prep'], 'i': ['I'], 's/a': ['N', 'PropN', 'A'],
                         'a/av': ['A', 'Adv'], 'av/pr': ['Adv', 'Prep']}

# "Comp", "G", "NVC", "Part",
# "Punct", "VVC"


# --------------------------------- PROCESSING VOCABULARY ---------------------------------

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
        # can't (= cannot)
        elif '(= ' in word and 'pl' in word:
            if '(= pl' in word:
                word = word.replace('(', '').replace(')', '')
                array_word = word.split("= pl")
                # print([[x.strip(' ')] for x in array_word])
                return [[x.strip(' ')] for x in array_word]
            elif ', pl)' in word: # sports (AE, pl) - maths (informal, pl)
                print(word)
                word = word.replace(', pl', '=').replace('(', '').replace(')', '')
                array_word = word.split("=")
                print([[x.strip(' ')] for x in array_word])
                return [[x.strip(' ')] for x in array_word]
            elif ', pl ' in word:
                # ft (= foot pl feet)
                first_word = re.sub('\(\=.*\)', '', word)
                second_words = word.split("(")[1].replace("=", '').replace(")", '').split(" pl ")
                array_word = [first_word, second_words[0], second_words[1]]
                # print([[x.strip(' ')] for x in array_word])
                return [[x.strip(' ')] for x in array_word]
            else:
                raise ValueError('An unspecified case occured: ' + str(word))

        # if word has an alternate form (no plural) eg.
        # can't (= cannot)
        elif '(= ' in word:
            # todo change lemma of cannot from can to can not
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
        elif any(item in word for item in ['(sth to sb)', '(with sb)', '(to sth)', '(sth to sth)', '(of sth)', '(to sb)',
                                           '(sb)', '(about sth)', '(for sth)', '(it for sb)']):
            # print(word)
            first_half = word.split('(')
            if 'sb' in first_half[0] or 'sth' in first_half[0]:
                first_half_without_sbsth = first_half[0].replace(' sb', '').replace(' sth', '')
                array_word = [first_half[0], first_half_without_sbsth, first_half[0] + first_half[1].replace(')', ''),
                              first_half_without_sbsth + first_half[1].replace(')', '')]
            else:
                array_word = [first_half[0], first_half[0] + first_half[1].replace(')', '')]
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
            array_word = [first_half[0], first_half[0] + second_half[0], first_half[0] + second_first_half[0] +
                          ' ' + second_half[1]]
            # print([[x.strip(' ')] for x in array_word])
            return [[x.strip(' ')] for x in array_word]

        # if parenthesis directly after word eg.
        # toward(s)
        elif bool(re.search('[a-z]\(', word)):
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
                    second_word_without_sbsth = word.replace('(', '').replace(')', '').replace(' sb', '').replace(' sth', '')
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
    if 'sb' in word or 'sth' in word:
        # print(word)
        if '/' in word:
            # print(word)
            split_word = re.split('[a-z]+\/[a-z]+', word)
            pattern = re.compile("[a-z]+\/[a-z]+")
            result = pattern.findall(word)
            person_array = result[0].split('/')
            array_word = [split_word[0], split_word[0] + person_array[0], split_word[0] + person_array[1]]
            # print([[x.strip(' ')] for x in array_word])
            return [[x.strip(' ')] for x in array_word]
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
        pattern = re.compile("[a-z]+\/[a-z]+")
        result = pattern.findall(word)
        # print(result)
        if result and len(result[0]) == len(word):
            # print(result)
            split_array = word.split('/')
            # print([[x.strip(' ')] for x in split_array])
            return [[x.strip(' ')] for x in split_array]
        else:
            #print(word)
            # todo exeception: to be out of/short of breath
            # todo exception: to expect/to have a baby
            if word == 'to be out of/short of breath':
                return [['to be out of breath'], ['to be short of breath']]
            elif word == 'to expect/to have a baby':
                return [['to expect a baby'], ['to have a baby']]
            elif re.search("[a-z]+\/[a-z]+", word) is not None:
                # print(word)
                split_word = re.split('[a-z]+\/[a-z]+', word)
                pattern = re.compile("[a-z]+\/[a-z]+")
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


# --------------------------------- TAG & LEMMATIZE ---------------------------------

def tagging_processed_vocable(m_processed_vocable, m_word_class):

    m_tagged_processed_vocable = []
    m_lemma_vocable = []
    m_tagged_lemma_vocable = []
    m_simple_tagged_lemma_vocable = []
    # ['can']
    # [["can't"], ['cannot']]
    # print(m_processed_vocable)
    if isinstance(m_processed_vocable[0], list): # [["can't"], ['cannot']]
        for processed_item in m_processed_vocable:
            # ["can't"]
            # ['cannot']
            if not any(x in processed_item[0] for x in [' sb', ' sth']): # ['to show sb round']
                m_tagged_processed_vocable_part = []
                m_lemma_vocable_part = []
                m_tagged_lemma_vocable_part = []
                first_to = False
                not_found = []
                if processed_item[0].startswith("to "):
                    first_to = True
                for processed_word in processed_item[0].split(" "): # ['to expect a baby']
                    reading_list = []
                    lemma = ""

                    # same words need to be looked up in lower or upper case
                    morphology = Morphology(cursor, processed_word)
                    number = morphology.get_number_of_readings()
                    if number == 0:
                        morphology = Morphology(cursor, processed_word.lower())
                        number = morphology.get_number_of_readings()

                    if number > 1: # word has more than 1 reading
                        for num in range(1,number+1):
                            reading = morphology.get_reading_by_number(num)
                            if reading is None:
                                # TODO word is not found in xtag
                                not_found.append(processed_word)
                                all_not_found.append(processed_word)
                                pass
                            else:
                                morphology_information = Morphology_Information(reading[0])
                                if morphology_information.pos in word_class_dictionary.get(m_word_class, ""):
                                    reading_list.append(reading[0])
                                    lemma = morphology_information.lemma
                    else: # word has one reading
                        reading = morphology.get_reading_by_number(1)
                        if reading is None:
                            # TODO word is not found in xtag
                            not_found.append(processed_word)
                            all_not_found.append(processed_word)
                            pass
                        else:
                            morphology_information = Morphology_Information(reading[0])
                            if morphology_information.pos in word_class_dictionary.get(m_word_class, ""):
                                reading_list.append(reading[0])
                                lemma = morphology_information.lemma
                    # todo : check for words with more than one reading
                    if len(reading_list) > 1:
                        print(status, "/", 3020, processed_vocable)
                        print("\tAllReadings:", reading)
                    # todo NoneType
                    if reading is not None:
                        m_tagged_processed_vocable_part.append((processed_word, reading[0]))
                    if processed_word == "to" and first_to:
                        first_to = False
                    else:
                        if lemma == "":
                            lemma = morphology.lemma
                        m_lemma_vocable_part.append(lemma)
                        # todo NoneType
                        if reading is not None:
                            m_tagged_lemma_vocable_part.append((lemma, reading[0]))
                if not_found:
                    print(status, "/", 3020, processed_vocable)
                    print("\tNot Found:", set(not_found))
        m_tagged_processed_vocable.append(m_tagged_processed_vocable_part)
        m_lemma_vocable.append(m_lemma_vocable_part)
        m_tagged_lemma_vocable.append(m_tagged_lemma_vocable_part)
    else: # ['can']
        first_to = False
        not_found = []
        if m_processed_vocable[0].startswith("to "):
            first_to = True
        print(word_class)
        for processed_word in m_processed_vocable[0].split(" "):  # ['to expect a baby']
            reading_list = []
            lemma = ""

            # same words need to be looked up in lower or upper case
            morphology = Morphology(cursor, processed_word)
            number = morphology.get_number_of_readings()
            if number == 0:
                morphology = Morphology(cursor, processed_word.lower())
                number = morphology.get_number_of_readings()

            # print("number:", number)
            # print("all:", morphology.return_all_readings())
            if number > 1:  # word has more than 1 reading
                for num in range(1, number + 1):
                    reading = morphology.get_reading_by_number(num)
                    if reading is None:
                        # TODO word is not found in xtag
                        not_found.append(processed_word)
                        all_not_found.append(processed_word)
                        pass
                    else:
                        morphology_information = Morphology_Information(reading[0])
                        if morphology_information.pos in word_class_dictionary.get(m_word_class, ""):
                            reading_list.append(reading[0])
                            lemma = morphology_information.lemma
            else:  # word has one reading
                reading = morphology.get_reading_by_number(1)
                if reading is None:
                    # TODO word is not found in xtag
                    not_found.append(processed_word)
                    all_not_found.append(processed_word)
                    pass
                else:
                    morphology_information = Morphology_Information(reading[0])
                    if morphology_information.pos in word_class_dictionary.get(m_word_class, ""):
                        reading_list.append(reading[0])
                        lemma = morphology_information.lemma
            # todo : check for words with more than one reading
            if len(reading_list) > 1:
                print(status, "/", 3020, processed_vocable)
                print("\tAllReadings:", reading[0])
            # todo NoneType
            if reading is not None:
                m_tagged_processed_vocable.append((processed_word, reading[0]))
            if processed_word == "to" and first_to:
                first_to = False
            else:
                if lemma == "":
                    lemma = morphology.lemma
                m_lemma_vocable.append(lemma)
                if reading is not None:
                    m_tagged_lemma_vocable.append((lemma, reading[0]))
        if not_found:
            print(status, "/", 3020, processed_vocable)
            print("\tNot Found:", set(not_found))
    return m_tagged_processed_vocable, m_lemma_vocable, m_tagged_lemma_vocable,


# --------------------------------- SOUNDEX ---------------------------------

def processing_soundex(mprocessed_vocable):
    """ soundex module conforming to Knuth's algorithm
        implementation 2000-12-24 by Gregory Jorgensen
        public domain
    """

    # digits holds the soundex values for the alphabet
    digits = '01230120022455012623010202'
    sndx = ''
    fc = ''

    soundex = []
    l = 0
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
                        if not fc: fc = c  # remember first letter
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
            #soundex.append([(sndx + (l * '0'))[:l]])
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


# --------------------------------- PROCESSING TRANSLATION ---------------------------------

def processing_translation(mword):
    deal_with_parenthesis_german2(mword)


def deal_with_parenthesis_german(mword):
    if '(' in mword:

        # if parenthesis directly after word and contains a comma eg. sein(e, r)
        if bool(re.search('[a-z]\([a-z]+,\s[a-z]+\)', mword)):
            # exclude cases like diese(r, s), das
            if bool(re.search('\),\s[a-z]', mword)) or bool(re.search('[a-z][a-z]+,\s[a-z][a-z]+', mword)):
                # print(mword)
                pass
            else:
                #print(mword)
                # todo 'kein(e, en) ... (mehr) haben', 'ein(e) kleine(s, r)', 'Sehr geehrte(r) ..., hier: Liebe(r, s) ...'
                # sein(e, r)
                first_word = re.sub('\([a-z],\s[a-z]+\)', '', mword)
                # sein
                second_word = re.search('\([a-z],\s[a-z]+\)', mword)
                second_word = second_word.group(0).replace('(', '').replace(')', '').replace(' ', '').split(',')
                # [e, r]
                if any(item in first_word[-1] for item in ['a', 'e', 'i', 'o', 'u']):
                    array_word = [first_word, first_word+second_word[0], first_word+second_word[1]]
                else:
                    array_word = [first_word, first_word + second_word[0], first_word + second_word[0] + second_word[1]]
                # print([[x.strip(' ')] for x in array_word])
                return [[x.strip(' ')] for x in array_word]

        # if parenthesis directly after word eg. ein(e)
        elif bool(re.search('[a-z]\(', mword)):
            print(mword)
            first_word = re.sub('\([a-z]+\)', '', mword)
            second_word = mword.replace('(', '').replace(')', '')
            array_word = [first_word, second_word]
            print([[x.strip(' ')] for x in array_word])
            return [[x.strip(' ')] for x in array_word]


def deal_with_parenthesis_german2(mword):

    #print(mword)
    # TODO: exclude 'Hallo, ich heiße …' evtl andere

    array_word = re.compile("(?<=[a-z][a-z]|[a-z]\)|[a-z]!),\s(?=[A-Za-z][a-z]|\([a-z])").split(mword)
    #print(array_word)
    processed = []
    for item in array_word:
        if '(' in item:
            #print(item)
            # if parenthesis directly after word eg. ein(e)
            if bool(re.search('[a-z]\([a-z]+\)', item)):
                print(item)
                first_word = re.sub('\([a-z]+\)', '', item)
                second_word = re.sub('(?<=[a-z])\((?=[a-z]+)\)', '', item)
                #second_word = item.replace('(', '').replace(')', '')
                array_word = [first_word, second_word]
                print([[x.strip(' ')] for x in array_word])
                processed.append([x.strip(' ') for x in array_word])
    #print()

    #print()

        # # if parenthesis directly after word and contains a comma eg. sein(e, r)
        # if bool(re.search('[a-z]\([a-z]+,\s[a-z]+\)', mword)):
        #     # exclude cases like diese(r, s), das
        #     if bool(re.search('\),\s[a-z]', mword)) or bool(re.search('[a-z][a-z]+,\s[a-z][a-z]+', mword)):
        #         # print(mword)
        #         pass
        #     else:
        #         # print(mword)
        #         # todo 'kein(e, en) ... (mehr) haben', 'ein(e) kleine(s, r)', 'Sehr geehrte(r) ..., hier: Liebe(r, s) ...'
        #         # sein(e, r)
        #         first_word = re.sub('\([a-z],\s[a-z]+\)', '', mword)
        #         # sein
        #         second_word = re.search('\([a-z],\s[a-z]+\)', mword)
        #         second_word = second_word.group(0).replace('(', '').replace(')', '').replace(' ', '').split(
        #             ',')
        #         # [e, r]
        #         if any(item in first_word[-1] for item in ['a', 'e', 'i', 'o', 'u']):
        #             array_word = [first_word, first_word + second_word[0], first_word + second_word[1]]
        #         else:
        #             array_word = [first_word, first_word + second_word[0],
        #                           first_word + second_word[0] + second_word[1]]
        #         # print([[x.strip(' ')] for x in array_word])
        #         return [[x.strip(' ')] for x in array_word]
        #
        # # if parenthesis directly after word eg. ein(e)
        # elif bool(re.search('[a-z]\(', mword)):
        #     print(mword)
        #     first_word = re.sub('\([a-z]+\)', '', mword)
        #     second_word = mword.replace('(', '').replace(')', '')
        #     array_word = [first_word, second_word]
        #     print([[x.strip(' ')] for x in array_word])
        #     return [[x.strip(' ')] for x in array_word]

# --------------------------------- MAIN ---------------------------------

if __name__ == '__main__':

    # todo deleted rows: ;als;aktiv;3/A2;I;k;;
    # todo              ;der/die/das;passiv;1/C2;II;d;;

    start = timeit.default_timer()

    # 0       | 1            | 2      | 3          | 4    | 5       | 6            | 7
    # Vokabel | Uebersetzung | Status | Fundstelle | Band | Wortart | Beispielsatz | Hinweis

    with open('test.csv', 'r') as vocin, open("updated_vocabulary.csv", 'w') as vocout:
        vocreader = csv.reader(vocin, delimiter=';')
        vocwriter = csv.writer(vocout, delimiter=';')

        header = next(vocreader)
        vocwriter.writerow(['_id'] + [header[0]] + ['processed_vocable'] + ['tagged_processed_vocable'] +
                           ['processed_vocable_soundex'] + ['lemma_vocable'] + ['tagged_lemma_vocable'] +
                           [header[1]] + ['processed_translation'] + ['tagged_processed_translation'] +
                           ['processed_translation_soundex'] + ['lemma_translation'] + ['tagged_lemma_translation'] +
                           header[2:])

        for row in vocreader:
            #print(status, '/', 3020)
            row_id = status

            #print(row[0])
            #if ',' in row[0]:
            #    print(row[0])

            processed_vocable = processing_vocabulary(row[0])
            # print(processed_vocable)

            word_class = row[5]
            tagged_processed_vocable, lemma_vocable, tagged_lemma_vocable = tagging_processed_vocable(processed_vocable, word_class)

            # processed_vocable_soundex = processing_soundex(processed_vocable)

            # processed_translation = processing_translation(row[1]) -- not done
            processed_translation = ['']
            tagged_processed_translation = ['']
            processed_translation_soundex = ['']
            lemma_translation = ['']
            tagged_lemma_translation = ['']

            # vocwriter.writerow([row_id] + [row[0]] + [processed_vocable] + [tagged_processed_vocable] +
            #                    [processed_vocable_soundex] + [lemma_vocable] + [tagged_lemma_vocable] +
            #                    [row[1]] + [processed_translation] + [tagged_processed_translation] +
            #                    [processed_translation_soundex] + [lemma_translation] + [tagged_lemma_translation] +
            #                    row[2:])

            status += 1
    print(set(all_not_found))
    print (timeit.default_timer() - start)