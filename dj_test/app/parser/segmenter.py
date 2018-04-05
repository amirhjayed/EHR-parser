from json import dumps
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
# from conv_layout_pdf import layout_pdf
# from ie_modules import ie

from nltk import word_tokenize
from nltk.stem import PorterStemmer


ps = PorterStemmer()


def isHeader(sentence):
    # Maybe store this in CSV files
    # Ignore french ? (NLTk lacks french support)
    kwDict = {
        **dict.fromkeys(['profil', 'summari', 'objective'], 'profil'),
        **dict.fromkeys(['skill', 'Techniques', 'Compétences', 'Langues', 'outil'], 'skill'),
        **dict.fromkeys(['career', 'work', 'experience', 'Expériences'], 'career'),
        **dict.fromkeys(['educ', 'Formation', 'Education'], 'educ'),
        **dict.fromkeys(['interest', 'activ', 'Interêt'], 'interest'),
        **dict.fromkeys(['referenc'], 'references')
    }
    words = word_tokenize(sentence)
    # words = [ps.stem(w) for w in words] // Not for french
    i = set(words) & set(kwDict.keys())
    if i:
        return(kwDict[i.pop()])


class Segmenter:
    def __init__(self, fpath):
        self.fp = open(fpath, 'rb')
        self.segDict = {
            'contact': [],
            'skill': [],
            'educ': [],
            'career': [],
            'interest': [],
            'references': []
        }
        self.seg_flag = False

    def layout_pdf(self):
        """
            Performs layout analysis
            and fills seg lists
        """
        h1 = 'contact'
        parser = PDFParser(self.fp)
        document = PDFDocument(parser)

        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed

        rsrcmgr = PDFResourceManager()
        device = PDFDevice(rsrcmgr)
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox):
                    for lt_text in lt_obj._objs:
                        if isinstance(lt_text, LTTextLine):
                            retstr = lt_text.get_text()
                            retstr = retstr.strip()
                            lt_text_list = list(lt_text)
                            if lt_text_list[-2].fontname.endswith("Bold"):
                                h = isHeader(retstr)
                                if h:
                                    h1 = h
                                else:
                                    self.segDict[h1].append(retstr)
                            else:
                                if(retstr):
                                    self.segDict[h1].append(retstr)
        self.seg_flag = True

    def get_contact(self):
        return self.segDict['contact']

    def get_skill(self):
        return self.segDict['skill']

    def get_educ(self):
        return self.segDict['educ']

    def get_career(self):
        return self.segDict['career']

    def get_interest(self):
        return self.segDict['interest']

    def get_references(self):
        return self.segDict['references']

    def get_json(self):
        if not self.seg_flag:
            self.layout_pdf()
        seg_json = dumps(self.segDict, indent=2, ensure_ascii=False)
        return seg_json
