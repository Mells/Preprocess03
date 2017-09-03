class Morphology_Information:
        
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

        #print("MorpInfo:", m_reading)

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
