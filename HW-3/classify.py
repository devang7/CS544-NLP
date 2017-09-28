#!/usr/bin/env python
from collections import defaultdict
from csv import DictReader, DictWriter

import nltk
import codecs
import sys
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import TreebankWordTokenizer
from string import punctuation

kTOKENIZER = TreebankWordTokenizer()

def morphy_stem(word):
    """
    Simple stemmer
    """
    stem = wn.morphy(word)
    if stem:
        return stem.lower()
    else:
        return word.lower()

class FeatureExtractor:
    def __init__(self):
        """
        You may want to add code here
        """
        self._pronunciations = nltk.corpus.cmudict.dict()
        None

    def features(self, text):
        features = {}
        prev = len(text)
        text = ''.join(ch for ch in text if ch not in punctuation)
        punch = prev - len(text)
        d = defaultdict(int)
        total_words = 0
        words = kTOKENIZER.tokenize(text)
        vowel_words = 0
        word_len = 0
        words_c = 0
        syllable = 0
        for idx, val in enumerate(words):
            word_len += len(morphy_stem(val))
            if idx == 0:
                features[val] = 1
                features["first*"] = val
            if idx == len(words) - 1:
                features[val] = 1
                features["last*"] = val
            v,c = self.vowel(val.lower())
            vowel_words += v
            words_c += c
            syllable += self.syllableCount(val.lower())
            if morphy_stem(val) in features:
                features[morphy_stem(val)] += 1
            else:
                features[morphy_stem(val)] = 1
            total_words += 1
        features["unique_words"] = len(d)
        features["total_words"] = total_words
        features["punct"] = punch
        features["total_vowl"] = vowel_words
        features["total_cons"]  = words_c
        features["syllable"] = syllable
        return features

    def vowel(self, word):
        count_v = 0
        count_c = 0
        for i in word:
            if i in ['a','e','i','o','u']:
                count_v += 1
            else: count_c += 1
        return count_v, count_c

    def syllableCount(self, word):
        min = 100000
        try:
            for word in self._pronunciations[word]:
                syllable = 0
                for s in word:
                    if self.containsDigit(s):
                        syllable += 1
                if syllable <= min :
                    min = syllable
        # TODO: provide an implementation!
            if min == 100000:
                return 1
            return min
        except:
            return 1

    def containsDigit(self,s):
        return any(char.isdigit() for char in s)


reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')


def prepfile(fh, code):
  if type(fh) is str:
    fh = open(fh, code)
  ret = gzip.open(fh.name, code if code.endswith("t") else code+"t") if fh.name.endswith(".gz") else fh
  if sys.version_info[0] == 2:
    if code.startswith('r'):
      ret = reader(fh)
    elif code.startswith('w'):
      ret = writer(fh)
    else:
      sys.stderr.write("I didn't understand code "+code+"\n")
      sys.exit(1)
  return ret

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("--trainfile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input train file")
    parser.add_argument("--testfile", "-t", nargs='?', type=argparse.FileType('r'), default=None, help="input test file")
    parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")
    parser.add_argument('--subsample', type=float, default=1.0,
                        help='subsample this fraction of total')
    args = parser.parse_args()
    trainfile = prepfile(args.trainfile, 'r')
    if args.testfile is not None:
        testfile = prepfile(args.testfile, 'r')
    else:
        testfile = None
    outfile = prepfile(args.outfile, 'w')

    # Create feature extractor (you may want to modify this)
    fe = FeatureExtractor()

    # Read in training data
    train = DictReader(trainfile, delimiter='\t')

    # Split off dev section
    dev_train = []
    dev_test = []
    full_train = []

    for ii in train:
        if args.subsample < 1.0 and int(ii['id']) % 100 > 100 * args.subsample:
            continue
        feat = fe.features(ii['text'])
        #print feat
        if int(ii['id']) % 5 == 0:
            dev_test.append((feat, ii['cat']))
        else:
            dev_train.append((feat, ii['cat']))
        full_train.append((feat, ii['cat']))

    """print(dev_test)"""
    # Train a classifier
    sys.stderr.write("Training classifier ...\n")
    classifier = nltk.classify.NaiveBayesClassifier.train(dev_train)
    classifier.show_most_informative_features(3)
    right = 0
    total = len(dev_test)
    for ii in dev_test:
        prediction = classifier.classify(ii[0])
        if prediction == ii[1]:
            right += 1
    sys.stderr.write("Accuracy on dev: %f\n" % (float(right) / float(total)))

    if testfile is None:
        sys.stderr.write("No test file passed; stopping.\n")
    else:
        # Retrain on all data
        classifier = nltk.classify.NaiveBayesClassifier.train(dev_train + dev_test)

        # Read in test section
        test = {}
        for ii in DictReader(testfile, delimiter='\t'):
            test[ii['id']] = classifier.classify(fe.features(ii['text']))

        # Write predictions
        o = DictWriter(outfile, ['id', 'pred'])
        o.writeheader()
        for ii in sorted(test):
            o.writerow({'id': ii, 'pred': test[ii]})
