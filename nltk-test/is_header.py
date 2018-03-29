from nltk import word_tokenize
from nltk.stem import PorterStemmer


ps = PorterStemmer()


def isHeader(sentence):
    # Maybe store this in CSV files
    # Ignore french ? (NLTk lacks french support)
    kwDict = {
        **dict.fromkeys(['profil', 'summari', 'objective'], 'profil'),
        **dict.fromkeys(['skill', 'Techniques', 'Compétences', 'Langues'], 'skill'),
        **dict.fromkeys(['career', 'work', 'experience', 'Expériences'], 'career'),
        **dict.fromkeys(['educ', 'Formation', ], 'educ'),
        **dict.fromkeys(['interest', 'activ', 'Interêt'], 'interest'),
        **dict.fromkeys(['referenc'], 'references')
    }
    words = word_tokenize(sentence)
    # words = [ps.stem(w) for w in words] // Not for french
    i = set(words) & set(kwDict.keys())
    if i:
        return(kwDict[i.pop()])
