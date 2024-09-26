import nltk
from nltk import word_tokenize, FreqDist


class FillerWordsAndPhrases:
    """
    Class for filler words and phrases detecting.
    Detects words and phrases from lists and as most common in speech.
    """
    # maximal acceptable percentages and lists of filler words
    params = {
        # multiplier for most common word or phrase occurrence to be compared with others
        "word_count_multiplier": 0.1,
        # minimal percentage for word or phrase to be considered common
        "occurrence_percentage": 0.0001,
        "parasites": ["просто", "вот", "ну", "короче", "типа", "пожалуй", "кстати", "вообще", "буквально", "скажем",
                      "блин", "допустим", "черт", "вроде", "круто", "прикинь", "прикиньте", "реально", "отпад",
                      "отпадно", "клево", "капец", "норм", "слушай", "конечно", "наверное", "вероятно", "кажется"],
        "parasite_phrases": ["так сказать", "как бы", "в натуре", "в общем", "в общемто", "в целом", "в принципе",
                             "как говорится", "как сказать", "на фиг", "то есть", "это самое", "как его", "типа того"]
    }

    def __init__(self, cleaned_transcription):
        """
        Initialization of filler words detection class
        @param cleaned_transcription: text transcription without punctuation marks
        """
        self.cleaned_transcription = cleaned_transcription

    def count_occurrences(self, min_len=5):
        """
        Counts two-words phrases occurrences
        @param min_len: minimal length in letters for phrase to be considered
        @return: list of two-element lists, each with phrase and its occurrence
        """
        pairs = dict()
        words = self.cleaned_transcription.split()
        for i in range(len(words) - 1):
            # create two-word phrases
            phrase = words[i] + ' ' + words[i + 1]
            if len(phrase) > min_len:
                # save phrases with acceptable length
                if phrase not in pairs:
                    pairs[phrase] = 0
                pairs[phrase] += 1
        phrases_from_list = {}

        # rewrite phrases from list into separate dictionary
        for phrase in self.params["parasite_phrases"]:
            if phrase in pairs:
                phrases_from_list[phrase] = pairs[phrase]
        phrase_dic = list(pairs.items())
        phrases = sorted(phrase_dic, key=lambda x: -x[1])
        return phrases, phrases_from_list

    def find_worst_phrases(self, phrases):
        """
        Takes most common phrases from all
        @param phrases: all two-word phrases
        @return: dictionary with key - phrases and value - their occurrences
        """
        num_words = len(self.cleaned_transcription)
        max_repeats = phrases[0][1]
        # if all collocations appear one time - there are no most common phrases
        if max_repeats == 1 or max_repeats / num_words < self.params["occurrence_percentage"]:
            return dict()
        # maximal deviation from most common word or phrase occurrence
        diff = round(max_repeats * self.params["word_count_multiplier"])
        worst_word_pairs = dict()
        # find phrases with small deviation from most common one
        for word_pair, cnt in phrases:
            if cnt >= max_repeats - diff and cnt / num_words >= self.params["occurrence_percentage"]:
                worst_word_pairs[word_pair] = cnt
        return worst_word_pairs

    def get_one_words(self):
        """
        Counts all filler words from params parasites
        @return: frequency dictionary with key - words and value - their occurrences
        """
        text_tokens = word_tokenize(self.cleaned_transcription)
        text_tokens = [token.strip() for token in text_tokens if token in set(self.params["parasites"])]
        text = nltk.Text(text_tokens)
        fdist = FreqDist(text)
        return fdist

    def find_worst_words(self, fdist):
        """
        Takes most common filler words from all
        @param fdist: frequency dictionary with key - words and value - their occurrences
        @return: dictionary with key - words and value - their occurrences
        """
        num_words = len(self.cleaned_transcription)
        if len(fdist) == 0:
            return dict()
        # most common word appearance
        max_repeats = fdist.most_common(1)[0][1]
        if max_repeats == 1 or max_repeats / num_words < self.params["occurrence_percentage"]:
            return dict()
        # maximal deviation from most common word or phrase occurrence
        diff = round(max_repeats * self.params["word_count_multiplier"])
        idx = 1
        # add words with high occurrence percentage
        while idx <= len(fdist) and fdist.most_common(idx)[-1][1] >= max_repeats - diff and \
                fdist.most_common(idx)[-1][1] / num_words >= self.params["occurrence_percentage"]:
            idx += 1
        worst_words = dict(fdist.most_common(idx - 1))
        return worst_words

    def get_filler_words_final(self):
        """
        Concatenates all words and phrases into two dictionaries - all and most common filler words
        @return: two dictionaries with words / phrases and their occurrences
        """
        # find all and most common / listed phrases
        phrases, phrases_from_list = self.count_occurrences()
        worst_phrases = self.find_worst_phrases(phrases)

        # find all and most common / listed words
        fdist = self.get_one_words()
        worst_words = self.find_worst_words(fdist)

        # dicts with all and most common / list words and phrases
        total_dict = dict(worst_phrases) | dict(fdist) | phrases_from_list
        worst_dict = dict(worst_phrases) | dict(worst_words)
        return total_dict, worst_dict
