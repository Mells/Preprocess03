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

    # private MorphObject setEmpty(boolean empty)
    # {
    #     isEmpty = empty;
    #     return this;
    # }
    #
    # public boolean isEmpty()
    # {
    #     return isEmpty;
    # }
    # /**
    #  * Generates an empty sentence to use as a non-null placeholder in case of errors.
    #  *
    #  * @return A generic, empty morph object
    #  */
    # public static MorphObject emptyObject()
    # {
    #     return new MorphObject(-1, "", "", "", "", "", "", "", "", "", "").setEmpty(true);
    # }
    # @Override
    # public boolean equals(Object o)
    # {
    #     if (this == o) return true;
    #     if (o == null || getClass() != o.getClass()) return false;
    #
    #     MorphObject vocObject = (MorphObject) o;
    #
    #     return id == vocObject.id;
    # }
    #
    # @Override
    # public int hashCode()
    # {
    #     return id;
    # }
    #
    # @Override
    # public String toString()
    # {
    #     return "MorphObject{" +
    #             "id=" + id +
    #             ", word='" + word + '\'' +
    #             ", lemma='" + lemma + '\'' +
    #             ", reading1='" + reading1 + '\'' +
    #             ", reading2='" + reading2 + '\'' +
    #             ", reading3='" + reading3 + '\'' +
    #             ", reading4='" + reading4 + '\'' +
    #             ", reading5='" + reading5 + '\'' +
    #             ", reading6='" + reading6 + '\'' +
    #             ", reading7='" + reading7 + '\'' +
    #             ", reading8='" + reading8 + '\'' +
    #            '}';
    # }
    # }