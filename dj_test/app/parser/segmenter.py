from json import dumps
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTLine
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

import csv


class Segmenter:
    def __init__(self, fpath, lang='En'):
        self.fp = open(fpath, 'rb')

        if lang == 'Fr':
            csvfile = open('/home/amir_h/PCD-Related/EHR-parser/dj_test/app/parser/data/fr_headers.csv', 'r')
            self.headers = csv.reader(csvfile)
        else:
            csvfile = open('/home/amir_h/PCD-Related/EHR-parser/dj_test/app/parser/data/en_headers.csv', 'r')
            self.headers = csv.reader(csvfile)

        self.segDict = {
            'contact': [],
            'career': [],
            'education': [],
            'skill': [],
            'interest': [],
        }
        self.seg_flag = False

    def layout_pdf(self):

        # Headers
        headersDict = {
            **dict.fromkeys(next(self.headers), 'profil'),
            **dict.fromkeys(next(self.headers), 'career'),
            **dict.fromkeys(next(self.headers), 'education'),
            **dict.fromkeys(next(self.headers), 'skill'),
            **dict.fromkeys(next(self.headers), 'interest'),
        }
        parser = PDFParser(self.fp)
        document = PDFDocument(parser)
        if not document.is_extractable:
            raise PDFTextExtractionNotAllowed

        rsrcmgr = PDFResourceManager()
        device = PDFDevice(rsrcmgr)
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        current_header = 'contact'
        retstr = ''
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layout = device.get_result()
            line_count = sum(isinstance(x, LTLine) for x in layout)
            if line_count > 3:
                # Segmentation by Line separators (LT Line)

                layout_expanded = []
                for obj in layout:
                    if isinstance(obj, LTTextBox):
                        for line in obj._objs:
                            if isinstance(line, LTTextLine):
                                layout_expanded.append(line)
                    elif isinstance(obj, LTLine):
                        layout_expanded.append(obj)

                layout_expanded = sorted(layout_expanded, key=lambda o: -o.y1)
                for lt_obj in layout_expanded:
                    if isinstance(lt_obj, LTLine):
                        potential_header = retstr.upper().rstrip('S')
                        potential_header = headersDict.get(potential_header)
                        if potential_header:
                            if self.segDict[current_header]:
                                self.segDict[current_header].pop()
                            current_header = potential_header
                    elif isinstance(lt_obj, LTTextLine):
                        retstr = lt_obj.get_text()
                        retstr = retstr.strip()
                        self.segDict[current_header].append(retstr)

            else:
                # Segmentation by checking for BOLD or all UPPER

                # Potential headers need some preprocessig:
                #   -- Ponctuations
                #   -- rstrip('S')
                #   -- avoid redundancy

                for lt_obj in layout:
                    if isinstance(lt_obj, LTTextBox):
                        for lt_text in lt_obj._objs:
                            if isinstance(lt_text, LTTextLine):
                                retstr = lt_text.get_text()
                                retstr = retstr.strip()
                                lt_text_list = list(lt_text)
                                # Segmentaion happens here :
                                if lt_text_list[-2].fontname.endswith("Bold"):
                                    # Check if bold
                                    potential_header = retstr.upper()
                                    potential_header = headersDict.get(potential_header)
                                    if potential_header:
                                        current_header = potential_header
                                    else:
                                        self.segDict[current_header].append(retstr)
                                elif retstr.isupper():
                                    # Check if upper
                                    potential_header = retstr.upper().rstrip('S')
                                    potential_header = headersDict.get(potential_header)
                                    if potential_header:
                                        current_header = potential_header
                                    else:
                                        self.segDict[current_header].append(retstr)
                                else:
                                    # it's not a header, append it to current seg
                                    if(retstr):
                                        self.segDict[current_header].append(retstr)

        self.seg_flag = True

    def get_contact(self):
        return self.segDict['contact']

    def get_skill(self):
        return self.segDict['skill']

    def get_education(self):
        return self.segDict['education']

    def get_career(self):
        return self.segDict['career']

    def get_interest(self):
        return self.segDict['interest']

    def get_json(self):
        if not self.seg_flag:
            self.layout_pdf()
        seg_json = dumps(self.segDict, indent=2, ensure_ascii=False)
        return seg_json


if __name__ == '__main__':
    seg = Segmenter('/home/amir_h/PCD-Related/EHR-parser/cv-dataset/CV-FR.pdf', 'Fr')
    print(seg.get_json())
