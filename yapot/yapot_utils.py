import os
import subprocess

import shutil

from pyPdf import PdfFileWriter
from pyPdf import PdfFileReader

def decrypt_pdf(pdf_filename, password):

    pdf_filename_unsecured = '{0}_unsecured.pdf'.format(pdf_filename)

    with open(os.devnull, 'w') as FNULL:
        subprocess.call(
            [
                'qpdf',
                '--password={0}'.format(password),
                '--decrypt',
                pdf_filename,
                pdf_filename_unsecured,
            ],
            stdout=FNULL,
            stderr=subprocess.STDOUT,
        )

    return pdf_filename_unsecured

def split_pdf(pdf_filename):

    filenames = []
    inputpdf = PdfFileReader(open(pdf_filename, "rb"))
    if inputpdf.getIsEncrypted():
        inputpdf.decrypt('')
    for i in xrange(inputpdf.numPages):
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(i))
        directory = os.path.dirname(pdf_filename)
        if directory == '':
            directory = '.'
        filename = os.path.basename(pdf_filename)
        filename = "{0}/{1}-p{2}.pdf".format(directory,filename,i)
        with open(filename, "wb") as outputStream:
            output.write(outputStream)
        filenames.append(filename)

    return filenames

def pdf_to_image(pdf_filename, image_filename, resolution):

    with open(os.devnull, 'w') as FNULL:

        cli = [
            'convert',
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


        ''''
        cli = [
            'convert',
            '-antialias',
            '-density',
            '300',
            '-black-threshold',
            '50%',
            pdf_filename,
            image_filename,
        ]
        '''

        '''
        shutil.copyfile(pdf_filename, '{0}_inter.pdf'.format(pdf_filename))

        cli = [
            'convert',
            '-density',
            '{0}'.format(resolution),
            '-threshold',
            '50%',
            pdf_filename,
            pdf_filename,
        ]
        print ' '.join(cli)
        subprocess.call(cli)

        cli = [
            'gs',
            '-q',
            '-dQUIET',
            '-dSAFER',
            '-dBATCH',
            '-dNOPAUSE',
            '-dNOPROMPT',
            '-sDEVICE=tiffg4',
            '-r{0}x{0}'.format(resolution),
            '-sOutputFile={0}'.format(image_filename),
            pdf_filename
        ]
        print ' '.join(cli)
        subprocess.call(cli)
     
        #shutil.copyfile(image_filename, '{0}_inter.tiff'.format(image_filename))
        '''

        print 'PDF converted.'
        

        '''
        cli2 = [
            'convert',
            '-antialias',
            '-black-threshold',
            '50%',
            image_filename,
            image_filename,
        ] 
        print ' '.join(cli2)
        subprocess.call(cli2)

        print "Image converted."
        '''

        '''
        subprocess.call(
            [
                'gs',
                '-q',
                '-dQUIET',
                '-dSAFER',
                '-dBATCH',
                '-dNOPAUSE',
                '-dNOPROMPT',
                '-sDEVICE=tiffg4',
                '-r{0}'.format(resolution),
                '-sOutputFile={0}'.format(image_filename),
                pdf_filename,
            ],
        )
        '''

    return None

def make_thumb(image_filename, thumb_filename, thumb_size):

    with open(os.devnull, 'w') as FNULL:
        subprocess.call(
            [
                'convert',
                '-resize',
                '{0}x{0}'.format(thumb_size),
                image_filename,
                thumb_filename,
            ],
        )

    return None

def image_ocr(filename):

    text = ''
    text_filename = '{0}.txt'.format(filename)
    with open(os.devnull, 'w') as FNULL:
        subprocess.call(
            [
                'tesseract',
                filename,
                filename,
                '-psm',
                '6',
            ],
        )
    with open(text_filename, 'r') as f:
        text = f.read()

    return text

def build_output_text(filenames, page_delineation):

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

def cleanup_yapot(pdf_filename, text_filenames):

    try:
        for filename in text_filenames:
            os.remove(filename)
        os.remove('{0}_unsecured.pdf'.format(pdf_filename))
    except Exception, e:
        print e

