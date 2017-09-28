#!/usr/bin/env python
import argparse
import sys
import codecs
if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
from collections import defaultdict as dd
import re
import os.path
import gzip
import tempfile
import shutil
import atexit

# Use word_tokenize to split raw text into words
from string import punctuation
from string import ascii_letters

import nltk
from nltk.tokenize import word_tokenize

scriptdir = os.path.dirname(os.path.abspath(__file__))

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

def addonoffarg(parser, arg, dest=None, default=True, help="TODO"):
  ''' add the switches --arg and --no-arg that set parser.arg to true/false, respectively'''
  group = parser.add_mutually_exclusive_group()
  dest = arg if dest is None else dest
  group.add_argument('--%s' % arg, dest=dest, action='store_true', default=default, help=help)
  group.add_argument('--no-%s' % arg, dest=dest, action='store_false', default=default, help="See --%s" % arg)


class LimerickDetector:

    def __init__(self):
        """
        Initializes the object to have a pronunciation dictionary available
        """
        self._pronunciations = nltk.corpus.cmudict.dict()

    def syllables(self,lineList):
        count = 0
        for word in lineList:
            count += self.num_syllables(word.lower())
        return count

    def num_syllables(self, word):
        """
        Returns the number of syllables in a word.  If there's more than one
        pronunciation, take the shorter one.  If there is no entry in the
        dictionary, return 1.
        """
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

    def processP(self,wordDict):
        j = 0
        while(j < len(wordDict)):
            i = 0
            word = wordDict[j]
            while(i < len(word)):
                if(self.containsDigit(word[i])):
                    wordDict[j] = word[i:]
                    break
                i += 1
            j += 1
        return wordDict

    def containsDigit(self,s):
        return any(char.isdigit() for char in s)

    def rhymeLines(self,lineA, lineB):
        if self.rhymes(lineA[-1],lineB[-1]):
            return True
        return False

    def rhymes(self, a, b):
        """
        Returns True if two words (represented as lower-case strings) rhyme,
        False otherwise. """
        try:
            dictA = self.processP(self._pronunciations[a])
            dictB = self.processP(self._pronunciations[b])
            listA = []
            listB = []
            for word in dictA:
                listA.append("".join(str(ele) for ele in word))
            for word in dictB:
                listB.append("".join(str(ele) for ele in word))
            for strA in listA:
                for strB in listB:
                    if(self.helper(strA, strB)):
                        return True
        # TODO: provide an implementation!
            return False
        except:
            return False

    def helper(self,a,b):
        if(len(a) <= len(b)):
            small = a
            big = b
        else:
            small = b
            big = a
        return big.endswith(small)

    def removePunctuation(self,TokenWord):
        i = 0
        while i < len(TokenWord):
            if TokenWord[i] in punctuation:
                del TokenWord[i]
            i += 1
        return TokenWord

    def is_limerick(self, text):
        """
        Takes text where lines are separated by newline characters.  Returns
        True if the text is a limerick, False otherwise.

        A limerick is defined as a poem with the form AABBA, where the A lines
        rhyme with each other, the B lines rhyme with each other, and the A lines do not
        rhyme with the B lines.


        Additionally, the following syllable constraints should be observed:
          * No two A lines should differ in their number of syllables by more than two.
          * The B lines should differ in their number of syllables by no more than two.
          * Each of the B lines should have fewer syllables than each of the A lines.
          * No line should have fewer than 4 syllables

        (English professors may disagree with this definition, but that's what
        we're using here.)


        """
        text = text.splitlines()
        listText = []
        for t in text:
            l = self.removePunctuation(word_tokenize(t))
            if len(l) > 0:
                listText.append(l)
        if len(listText) != 5:
            return False
        sa1 = self.syllables(listText[0])
        sa2 = self.syllables(listText[1])
        sa5 = self.syllables(listText[4])
        sb3 = self.syllables(listText[2])
        sb4 = self.syllables(listText[3])

        if(min(sa1,sa2,sa5,sb3,sb4) < 4):
            return False
        if(abs(sa1 - sa2) > 2 or abs(sa2 - sa5) > 2 or abs(sa1 - sa5) > 2):
            return False
        if(abs(sb3 - sb4) > 2):
            return False
        if(min(sa1,sa2,sa5) <= max(sb3,sb4)):
            return False
        if not self.rhymeLines(listText[0],listText[1]) or not self.rhymeLines(listText[1],listText[4]) or not self.rhymeLines(listText[4],listText[0]):
            return False
        if not self.rhymeLines(listText[2],listText[3]):
            return False
        # TODO: provide an implementation!
        return True

    def apostrophe_tokenize(self, text):
        resultList = []
        w = ''
        for c in text:
            if c != ' ':
                if c in string.ascii_letters or c == "'":
                    w += c
                else:
                    resultList.append(c)
            else:
                if w:
                    resultList.append(w)
                    w = ''
        return resultList

    def guess_syllables(self,word):
        word = word.lower()
        vowels = {'a','e','i','o','u'}
        count = 0
        i = 0
        while(i < len(word)):
            if word[i] in vowels:
                count += 1
                j = i
                while(j < len(word) and word[j] in vowels):
                    j += 1
                i = j
                continue
            elif (word[i] == 'y' and i + 1 < len(word) and word[i+1] not in vowels) or (word[i] == 'y' and i + 1 >= len(word)):
                count += 1
            i += 1
        if word[len(word) - 1] == 'e' and i != 0 and count > 1:
            count -= 1
        return count

# The code below should not need to be modified
def main():
  parser = argparse.ArgumentParser(description="limerick detector. Given a file containing a poem, indicate whether that poem is a limerick or not",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  addonoffarg(parser, 'debug', help="debug mode", default=False)
  parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file")
  parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")




  try:
    args = parser.parse_args()
  except IOError as msg:
    parser.error(str(msg))

  infile = prepfile(args.infile, 'r')
  outfile = prepfile(args.outfile, 'w')

  ld = LimerickDetector()
  lines = ''.join(infile.readlines())
  outfile.write("{}\n-----------\n{}\n".format(lines.strip(), ld.is_limerick(lines)))

if __name__ == '__main__':
  main()
