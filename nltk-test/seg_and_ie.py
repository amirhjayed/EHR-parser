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
from is_header import isHeader
# from ie_modules import ie


class Segmenter:
    def __init__(self, fpath):
        self.fp = open(fpath, 'rb')
        self.segDict = {
            'educ': [],
            'skill': [],
            'career': [],
            'contact': [],
            'interest': [],
            'references': []
        }

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
                            lt_text_list = list(lt_text)
                            if lt_text_list[-2].fontname.endswith("Bold"):
                                h = isHeader(retstr)
                                print(h)
                                if h:
                                    h1 = h
                            else:
                                if(retstr.strip()):
                                    self.segDict[h1].append(retstr)

    def get_text(self):
        # to delete ?
        pass

    def get_json():
        pass


seg = Segmenter("./CV-FR.pdf")
seg.layout_pdf()
data = dumps(seg.segDict, indent=2)
print(data)
