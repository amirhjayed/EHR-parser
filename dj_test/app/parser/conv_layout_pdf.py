from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTChar
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument


path = "../cv-dataset/Mohamed-Amin-Houidi.pdf"
fp = open(path, 'rb')


def convert_pdf(fp):
    """
        Convert PDF to txt
    """
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    outp = './' + "conv_output" + '.txt'
    outf = open(outp, 'wb')
    codec = 'utf-8'
    device = TextConverter(rsrcmgr, outf, codec=codec, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ''
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    outf.close()
    return outp


def layout_pdf(fp):
    parser = PDFParser(fp)
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
                        lt_tmp = list(lt_text)
                        if lt_tmp[-2].fontname.endswith("Bold"):
                            print(lt_text.get_text(), sep="", end="")


layout_pdf(fp)
