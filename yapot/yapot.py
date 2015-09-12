import os
import uuid
import time

from multiprocessing import Queue
from multiprocessing import Pool

import os
import subprocess
import shutil
from PyPDF2 import PdfFileWriter
from PyPDF2 import PdfFileReader

__pdf_filenames = Queue()
__text_filenames = Queue()


def convert_document(pdf_filename,
                     resolution=200,
                     delete_files=True,
                     page_delineation='\n--------\n',
                     verbose=False,
                     temp_dir=str(uuid.uuid4()),password='',
                     thumb_prefix='thumb_page_',
                     pool_count=2):
    filename = decrypt_pdf(pdf_filename, temp_dir, password)
    filenames = split_pdf(filename, temp_dir)
    for filename in filenames:
        __pdf_filenames.put(filename)
    pool = Pool()
    pool.map_async(
        _yapot_worker,
        [(tid, pdf_filename, temp_dir, resolution) for
            tid in range(0, pool_count)],
    )
    while __text_filenames.qsize() != len(filenames):
        time.sleep(1)
    text_filenames = []
    try:
        while(1):
            text_filenames.append(__text_filenames.get_nowait())
    except:
        pass
    text = build_output_text(text_filenames, page_delineation)
    if delete_files:
        cleanup_yapot(temp_dir)
    return text


def _yapot_worker(args):
    tid, pdf_filename, temp_dir, resolution = args
    while(1):
        if not __pdf_filenames.qsize():
            break
        try:
            filename = __pdf_filenames.get_nowait()
        except:
            #  No more files in the queue
            break;
        image_filename = '{0}.tiff'.format(filename)
        success = pdf_to_image(filename, image_filename, resolution)
        try:
            text = image_ocr(image_filename)
        except Exception as e:
            #  TODO: Do something with this error ...
            pass
        text_filename = '{0}.txt'.format(image_filename)
        with open(text_filename,'w') as f:
            f.write(text)
        __text_filenames.put(text_filename)


def decrypt_pdf(pdf_filename, temp_dir, password):
    '''
    Some PDFs are encrypted.  This decrypts it.
    '''
    pdf_filename_unsecured = '{0}/{1}_unsecured.pdf'.format(temp_dir, pdf_filename)
    with open(os.devnull, 'w') as FNULL:
        cli = [
            'qpdf',
            '--password={0}'.format(password),
            '--decrypt',
            pdf_filename,
            pdf_filename_unsecured,
        ]
        subprocess.call(cli)
    return pdf_filename_unsecured


def split_pdf(pdf_filename, temp_dir):
    '''
    Split the PDF into n PDFs ( one for each page ).
    '''
    filenames = []
    inputpdf = PdfFileReader(open(pdf_filename, "rb"))
    if inputpdf.getIsEncrypted():
        inputpdf.decrypt('')
    for i in range(inputpdf.numPages):
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(i))
        filename = os.path.basename(pdf_filename)
        filename = "{0}/{1}-p{2}.pdf".format(temp_dir, filename, i)
        with open(filename, "wb") as outputStream:
            output.write(outputStream)
        filenames.append(filename)

    return filenames


def pdf_to_image(pdf_filename, image_filename, resolution):
    '''
    Converts a single PDF to a TIFF image.
    '''
    with open(os.devnull, 'w') as FNULL:
        cli = [
            'convert',
            '-depth',
            '8',
            '-density',
            '{0}'.format(resolution),
            '-threshold',
            '50%',
            '{0}'.format(pdf_filename),
            '-channel',
            'r',
            '-separate',
            '{0}'.format(image_filename),
        ]
        subprocess.call(cli)
    return None


def make_thumb(image_filename, thumb_filename, thumb_size):
    '''
    Makes a thumbnail from a larger image.
    '''
    with open(os.devnull, 'w') as FNULL:
        cli = [
            'convert',
            '-resize',
            '{0}x{0}'.format(thumb_size),
            image_filename,
            thumb_filename,
        ]
        subprocess.call(cli)
    return None


def image_ocr(filename):
    '''
    Uses tesseract to OCR an image.
    '''
    text = ''
    text_filename = '{0}.txt'.format(filename)
    with open(os.devnull, 'w') as FNULL:
        cli = [
            'tesseract',
            filename,
            filename,
            '-psm',
            '6',
        ]
        subprocess.call(cli)
    with open(text_filename, 'r') as f:
        text = f.read()
    return text


def build_output_text(filenames, page_delineation):
    '''
    Concatenate output text products into a single text blob.
    '''
    text = ''
    ordered_filenames = []
    for i in range(0,len(filenames)):
        ordered_filenames.append('')
    for filename in filenames:
        index = int(filename.split('.pdf.tiff.txt')[0].split('-p')[-1])
        ordered_filenames[index] = filename
    for filename in ordered_filenames:
        with open(filename) as f:
            contents = f.read()
        text += '{0}{1}'.format(contents, page_delineation)
    return text


def cleanup_yapot(output_dir):
    '''
    Clean up all the temp files that yapot makes.
    '''
    shutil.rmtree(output_dir)

