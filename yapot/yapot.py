from wand.image import Image as WandImage
from wand.color import Color as Color

import subprocess
import os
import traceback

from multiprocessing import Queue
from multiprocessing import Pool

import uuid
import time

import shutil

from pyPdf import PdfFileWriter
from pyPdf import PdfFileReader


# Queues!
# You have a single PDF file that gets split into multiple PDFs.  Each PDF is
# one page.  Each of those get converted to images, and each of those images
# get converted to blobs of text.  These queues help manage that workflow.
__pdf_queue = Queue()
__pdf_images = Queue()
__pdf_texts = Queue()


def convert_document(pdf_filename, resolution=200, delete_files=True,
        page_delineation='\n--------\n', verbose=False,
        temp_dir=str(uuid.uuid4()),password='',make_thumbs=False,
        thumb_size=160, thumb_dir='thumbs', thumb_prefix='thumb_page_',
        pool_count=1):
    """ This is the entry-point for the application.

    Here's some info on some of the arguments.

    - temp_dir is a string for where to store the tempfiles of all these
      shell-out operations.  You don't necessarily want to use /var/tmp because
      you might run out of memory with all these huge files.
    - make_thumbs is a boolean and will generate small thumbnail images of each
      page of the pdf (nice!).
    - resolution is an int and it is the DPI resolution of the image that is
      created from the PDF before it is passed into tesseract.  I highly
      recommend this be 200 or greater.  Anything over 400 is going to take an
      extremely long time, with diminishing returns.
    - thumb_size is only the *width* of the thumbnails, the aspect ratio of the
      original document is maintained.
    - pool_count is the number of threads to use.
    """

    success = False
    output_text = ''

    #if True:
    try:

        if verbose == True:
            print "Sanitizing PDF ..."

        pdf_filename_unsecured = '{0}.unsecured.pdf'.format(pdf_filename)

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

        if verbose == True:
            print "Reading PDF ..."

        # get the images from the pdf
        page_count, _ = _get_images_from_pdf(
            pdf_filename = pdf_filename_unsecured, #pdf_filename_no_fonts,#'{0}.unsecured.pdf'.format(pdf_filename),
            resolution = resolution,
            verbose = verbose,
            delete_files = delete_files,
            temp_dir = temp_dir,
            make_thumbs = make_thumbs,
            thumb_size = thumb_size,
            thumb_dir = thumb_dir,
            thumb_prefix = thumb_prefix,
            pool_count = pool_count,
        )

        if verbose == True:
            print "PDF conversion complete, assembling pages ..."

        # allocate space for our pages
        pages = []
        for i in xrange(page_count):
            pages.append(None)

        # assemble the pages in the correct order
        try:
            while(1):
                page_number, page_text = __pdf_texts.get_nowait()
                pages[int(page_number)] = page_text
        except:
            pass

        # return as a large string
        output_text = ''
        for page in pages:
            output_text += '{0}{1}'.format(page,page_delineation)

        if verbose == True:
            print "Done."

        if delete_files == True:
            shutil.rmtree(temp_dir)
            os.remove(pdf_filename_unsecured)

        success = True

    except Exception:
        if verbose == True:
            traceback.print_exc()
        success = False

    return success, output_text

def _get_images_from_pdf(pdf_filename, resolution, verbose, delete_files,
        temp_dir, make_thumbs, thumb_size, thumb_dir, thumb_prefix, pool_count=1):

    success = False
    try:

        if verbose == True:
            print "Splitting PDF into multiple pdf's for processing ..."

        # make sure there is a place to put our temporary pdfs
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        # make sure if we are going to make thumbs, the folde rexists
        if make_thumbs == True:
            if not os.path.exists(thumb_dir):
                os.makedirs(thumb_dir)

        # read input pdf
        inputpdf = PdfFileReader(open(pdf_filename, "rb"))
        if inputpdf.getIsEncrypted():
            inputpdf.decrypt('')

        if verbose == True:
            print "Writing out %i pages ..." % inputpdf.numPages

        # create all of the temporary pdfs
        for i in xrange(inputpdf.numPages):
            output = PdfFileWriter()
            output.addPage(inputpdf.getPage(i))
            #print output.resolvedObjects
            filename = "{0}/document-page-{1}.pdf".format(temp_dir,i)
            with open(filename, "wb") as outputStream:
                output.write(outputStream)
            __pdf_queue.put(i)

        if verbose == True:
            print "Dispatching pdf workers ..."

        # spin up our workers to convert the pdfs to images
        #pool_count = 4
        pool = Pool()
        pool.map_async(
            _pdf_converter_worker,
            [(x, resolution, verbose, delete_files,
                temp_dir, make_thumbs, thumb_size,
                thumb_dir, thumb_prefix) for \
                x in range(pool_count)]
        )

        while __pdf_texts.qsize() != inputpdf.numPages:
            time.sleep(.25)

        if verbose == True:
            print "Done converting PDF."

        success = True

    except Exception, e:
        print str(e)

    return inputpdf.numPages, success

def _pdf_converter_worker(args):

    thread_number = args[0]
    resolution = args[1]
    verbose = args[2]
    #delete_files = args[3] # never used here...
    temp_dir = args[4]
    make_thumbs = args[5]
    thumb_size = args[6]
    thumb_dir = args[7]
    thumb_prefix = args[8]

    #if True:
    try:

        while(1):

            if verbose == True:
                print "{0}: Getting page from queue ...".format(thread_number)

            if not __pdf_queue.qsize():
                print "{0}: All out of work.".format(thread_number)
                break

            page_number = __pdf_queue.get_nowait()

            pdf_filename = "{0}/document-page-{1}.pdf".format(temp_dir, page_number)
            thumb_filename = "{0}/{1}{2}.png".format(thumb_dir, thumb_prefix, page_number)

            if verbose == True:
                print "{0}: working on page {1}".format(thread_number, page_number)

            imgs = WandImage(
                filename=pdf_filename,
                resolution=int(resolution),
            )

            if verbose == True:
                print "{0}: done with page {1}".format(thread_number, page_number)

            ret_imgs = zip(xrange(len(imgs.sequence)), imgs.sequence)

            if verbose == True:
                print "{0}: saving image data ...".format(thread_number)

            _i, _im = ret_imgs[0]
            success, image_filename = _save_page_image(
                pdf_filename = pdf_filename,
                image = _im,
                thumb_filename = thumb_filename,
                make_thumb = make_thumbs,
                thumb_size = thumb_size,
                thread_number = thread_number,
                verbose = verbose,
            )

            if verbose == True:
                print "{0}: done.".format(thread_number)

            if verbose == True:
                print "{0}: Converting image to text ...".format(thread_number)

            success, page_text = _convert_image_to_text(image_filename, verbose)

            __pdf_texts.put((int(page_number),page_text))

    except Exception as e:
        print "{0}: An error has occured:".format(thread_number)
        print "{0}: ERROR: {1}".format(thread_number,str(e))
        traceback.print_exc()

    if verbose == True:
        print "{0}: Thread exiting.".format(thread_number)

    return



def _save_page_image(pdf_filename, image, thumb_filename,
        make_thumb, thumb_size, thread_number, verbose=False):

    success = False
    image_filename = ''
    if True:
    #try:

        if verbose == True:
            print "{0}: Saving off PDF image ...".format(thread_number)

        try:
          image_filename = '{0}.tiff'.format(pdf_filename)
          bg = WandImage(width=image.width, height=image.height, background=Color("white"))
          bg.composite(image, 0, 0)
          bg.clone().save(
            filename = image_filename,
          )
        except Exception, ex:
          print ex
        #image.clone().save(
        #    filename=image_filename
        #)

        if verbose == True:
            print "{0}: Done saving off PDF image.".format(thread_number)

        if make_thumb == True:

            if verbose == True:
                print "{0}: Making thumb nail image: '{1}' ...".format(thread_number, thumb_filename)

            FNULL = open(os.devnull, 'w')
            cli_call = [
                'convert',
                '-resize',
                '{0}x{0}'.format(thumb_size),
                image_filename,
                thumb_filename,
            ]
            subprocess.call(
                cli_call,
                stdout=FNULL,
                stderr=subprocess.STDOUT
            )

        success = True

    #except:
    #    pass

    return success, image_filename

def _convert_image_to_text(image_filename, verbose=False):

    if verbose == True:
        print "Converting {0} ...".format(image_filename)

    success = False
    page_text = ''
    #if True:
    try:

        FNULL = open(os.devnull, 'w')

        text_filename = '%s.txt' % image_filename
        cli_call = [
            'tesseract',
            image_filename,
            image_filename,
            '-psm',
            '6',
        ]
        subprocess.call(
            cli_call,
            stdout=FNULL,
            stderr=subprocess.STDOUT
        )

        with open(text_filename,'r') as f:
            page_text = f.read()

        success = True

    except:
        pass

    if verbose == True:
        print "Done with image OCR."

    return success, page_text

