from titlecase import titlecase
from spellchecker import SpellChecker
import csv

spell = SpellChecker()
spell.word_frequency.load_text_file('./meshwords.txt')

f = csv.writer(open('titletest.csv', 'w'), lineterminator='\n')


with open('testing.csv') as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for row in itemMetadata:
        title = row['value'].strip()
        title = title.replace('  ', '')
        titleToChange = 0
        mispelledWords = []
        for word in title.split(' '):
            word = word.replace(',', '').replace(':', '').replace('\'', '')
            print(word)
            if word.isupper():
                titleToChange = titleToChange + 1
                badWord = spell.unknown([word])
                if badWord:
                    mispelledWords.append(badWord)
        if titleToChange > 0:
            if len(mispelledWords) == 0:
                newTitle = titlecase(title)
                f.writerow([title]+[newTitle])
            else:
                f.writerow([title]+[mispelledWords])
        else:
            f.writerow([title]+['same'])
