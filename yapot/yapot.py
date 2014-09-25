from wand.image import Image as WandImage

import subprocess
import os
from multiprocessing import Queue
from multiprocessing import Pool

import uuid
import time

import shutil

from pyPdf import PdfFileWriter
from pyPdf import PdfFileReader

__pdf_queue = Queue()
__pdf_images = Queue()
__pdf_texts = Queue()

def convert_document(pdf_filename, base_page_name='page', resolution=200,
        delete_files=True, page_delineation='\n--------\n',
        verbose=False, temp_dir=str(uuid.uuid4()),password=''):

    success = False
    output_text = ''

    if True:
    #try:

        if verbose == True:
            print "Sanitizing PDF ..."

        with open(os.devnull, 'w') as FNULL:
            subprocess.call(
                [
                    'qpdf',
                    '--password={0}'.format(password),
                    '--decrypt',
                    pdf_filename,
                    '{0}.unsecured.pdf'.format(pdf_filename),
                ],
                stdout=FNULL,
                stderr=subprocess.STDOUT,
            )

        if verbose == True:
            print "Reading PDF ..."

        # get the images from the pdf
        page_count = _get_images_from_pdf(
            pdf_filename = '{0}.unsecured.pdf'.format(pdf_filename),
            resolution = resolution,
            base_page_name = base_page_name,
            verbose = verbose,
            temp_dir = temp_dir,
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
            os.remove('{0}.unsecured.pdf'.format(pdf_filename))

        success = True

    #except Exception, e:
    #    if verbose == True:
    #        print "ERROR: {0}".format(e)
    #    success = False

    return success, output_text

def _get_images_from_pdf(pdf_filename, resolution=200, 
        base_page_name='page', verbose=False, 
        delete_files=True, temp_dir=str(uuid.uuid4())):

    if True:
    #try:

        if verbose == True:
            print "Splitting PDF into multiple pdf's for processing ..."

        # make sure there is a place to put our temporary pdfs
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

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
            filename = "{0}/document-page-{1}.pdf".format(temp_dir,i)
            with open(filename, "wb") as outputStream:
                output.write(outputStream)
            __pdf_queue.put(i)

        if verbose == True:
            print "Dispatching pdf workers ..."

        # spin up our workers to convert the pdfs to images
        pool_count = 8
        pool = Pool()
        result = pool.map_async(
            _pdf_converter_worker, 
            [(x, resolution, verbose, delete_files, temp_dir) for \
                    x in range(pool_count)]
        )

        while not __pdf_queue.empty():
            time.sleep(.25)

        print "Done conerting PDF."

    #except:
    #    pass

    return inputpdf.numPages

def _pdf_converter_worker(args):

    thread_number = args[0]
    resolution = args[1]
    verbose = args[2]
    delete_files = args[3]
    temp_dir = args[4]

    if True:
    #try:

        while(1):

            #print "{0}: Getting page from queue ...".format(thread_number)

            page_number = __pdf_queue.get_nowait()

            pdf_filename = "{0}/document-page-{1}.pdf".format(temp_dir, page_number)

            if verbose == True:
                print "{0}: working on page {1}".format(thread_number, page_number)

            imgs = WandImage(
                filename=pdf_filename,
                resolution=resolution
            )
            
            if verbose == True:
                print "{0}: done with page {1}".format(thread_number, page_number)

            ret_imgs = zip(xrange(len(imgs.sequence)), imgs.sequence)

            if verbose == True:
                print "{0}: saving image data ...".format(thread_number)

            _i, _im = ret_imgs[0]
            success, image_filename = _save_page_image(pdf_filename, _im)

            #print "{0}: saving image {1} filename to list ...".format(thread_number, page_number)

            #__pdf_images.put((int(page_number), image_filename))

            if verbose == True:
                print "{0}: done.".format(thread_number)

            #__pdf_queue.task_done()

            if verbose == True:
                print "{0}: Converting image to text ...".format(thread_number)

            success, page_text = _convert_image_to_text(image_filename, verbose)

            __pdf_texts.put((int(page_number),page_text))

            if delete_files == True:
                if verbose == True:
                    print "{0}: Deleting temp files ..."
                success = _delete_files(image_filename)

    #except Exception, e:
    ##    pass
    #    print str(e)

    if verbose == True:
        print "{0}: Thread exiting.".format(thread_number)

    return 

    

def _save_page_image(pdf_filename, image):

    success = False
    image_filename = ''
    try:

        image_filename = '{0}.png'.format(pdf_filename)
        image.clone().save(
            filename=image_filename
        )

        success = True

    except:
        pass

    return success, image_filename

def _convert_image_to_text(image_filename, verbose=False):

    if verbose == True:
        print "Converting {0} ...".format(image_filename)

    success = False
    page_text = ''
    try:

        FNULL = open(os.devnull, 'w')

        text_filename = '%s.txt' % image_filename
        subprocess.call(['tesseract', image_filename, image_filename],
                        stdout=FNULL, stderr=subprocess.STDOUT)

        with open(text_filename,'r') as f:
            page_text = f.read()

        success = True

    except:
        pass

    if verbose == True:
        print "Done with image OCR."

    return success, page_text

def _delete_files(image_filename):

    success = False
    try:
        os.remove(image_filename)
        os.remove('%s.txt' % image_filename)
        success = True
    except:
        pass

    return success
