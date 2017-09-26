import csv
import re

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


# --------------------------------- TESTS ------------------------------------------------------------------------------

def test01():
    status = 1
    number = 0
    with open('Vokabelliste.csv', 'r') as vocin, open("phrases.csv", 'w') as vocout, open("#xtagmorph.csv", 'r') as xin:
        vocreader = csv.reader(vocin, delimiter=';')
        vocwriter = csv.writer(vocout, delimiter=';')
        xreader = csv.reader(xin, delimiter=';')

        header = next(vocreader)
        vocwriter.writerow(header)

        # for row in vocreader:
        # print(status, '/', 3020)

        # if 'i' == row[5]:
        #    print(row)

        #     print(row[0])
        #     if 'ph' == row[5]:
        #         vocwriter.writerow(row)
        #         result = processing_vocabulary(row[0])
        #         if isinstance(result[0], list):
        #             for item in result:
        #                 sp = item[0].split(" ")
        #                 if len(sp) >=3:
        #                     pass
        #                 else:
        #                     print(item)
        #                     number += 1
        #         else:
        #             sp = result[0].split(" ")
        #             if len(sp) >= 3:
        #                 pass
        #             else:
        #                 print(result)
        #                 number += 1
        #     status += 1
        #
        # print("ph:", number)
        for row in xreader:
            if not row[9] == '':
                print(row)
                # print(len(row))


def split_simple_lemma(x):
    height = 1
    width = len(x)
    #   | V | Pron  | N |
    #   | V | N     | N |
    for item in x:
        if len(item[1]) > 1:
            height *= len(item[1])
    Matrix = [[0 for x in range(width)] for y in range(height)] # first: ^v, econd <->
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
                print("iteration: ", m,"/",many_iterate)
                for lof in range(0, len_of_readings):   # für die anzahl an readings
                    for i in range(0, repeat):
                        Matrix[new_pos][position] = (item[0], item[1][lof])
                        new_pos += 1
                for row in Matrix:
                    print(row)
                print()
        else:
            for i in range(0, height):
                Matrix[i][position] = (item[0], item[1][0])
        many_iterate *= len_of_readings
        position += 1

    simple_array = []
    for row in Matrix:
        simple_array.append(row)

    return simple_array

    #for row in Matrix:
    #    print(row)


def array_to_table():
    exceptions = ['Hallo, ich heiße …', 'Hier, bitte!, Bitte schön!', 'Ausgeschlossen!, hier: Jetzt echt, oder?',
                  'sobald, hier: als, in dem Moment, als ...', 'glücklich (Glück habend; Glück bringend)',
                  'darauf achten, (dass)', 'Wikinger/in; wikingisch', 'Längenmaß (91,44 cm)',
                  '(entspricht dem deutschen Abitur)', '(Anrede)',
                  '(Amtssprache in Indien)', '(als Schulfach)',
                  '(nur hinter Uhrzeit zwischen Mitternacht und 12 Uhr mittags)',
                  '(nur hinter Uhrzeit zwischen 12 Uhr mittags und Mitternacht)', '(zur Terminplanung)',
                  '(bei Freunden)',
                  '(an Kleidungsstücken)', '(= 0,3048 Meter)', '(Briefschlussformel)', '(von Großbritannien)',
                  '(Untereinheit des brit. Pfunds)', '(Londoner)', '(Alternativbezeichnung ', '(Kobold)',
                  '(systematische wiss. Beobachtung außerhalb des Labors)', '(in der Thronfolge)',
                  '(Einrichtung zur Betreuung sterbender Menschen)', '(beim Rugby)', '(= 1,609 km)', '(Zeit)', '(Geld)',
                  '(auf dem Wasser)', '(jd, der den Text flüsternd vorspricht)', '(Sprache)',
                  'der/die sich im Internat um die Schüler/innen eines Hauses kümmert/kümmern',
                  'Aufsicht führende/r Lehrer/in', 'Vergangenheitsform von']
    #print(" \\\\\n".join([str(entry) for entry in exceptions]))
    for entry in exceptions:
        print("\item " + entry)

# --------------------------------- MAIN -------------------------------------------------------------------------------

# 0       | 1            | 2      | 3          | 4    | 5       | 6            | 7
# Vokabel | Uebersetzung | Status | Fundstelle | Band | Wortart | Beispielsatz | Hinweis

if __name__ == '__main__':

    # test01()
    #split_simple_lemma()
    array_to_table()