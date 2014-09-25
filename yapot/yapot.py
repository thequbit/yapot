from wand.image import Image as WandImage
import subprocess
import os
from multiprocessing import Queue
from multiprocessing import Pool

import time

from pyPdf import PdfFileWriter
from pyPdf import PdfFileReader

__pdf_queue = Queue()
__pdf_images = Queue()

def convert_document(pdf_filename, base_page_name='page', resolution=200,
        delete_files = True, page_delineation='\n--------\n',
        verbose=False):

    success = False
    output_text = ''

    #try:
    if True:

        if verbose:
            print "Reading PDF ..."

        # get the images from the pdf
        imgs = _get_images_from_pdf(
            pdf_filename = pdf_filename,
            resolution = resolution,
            base_page_name = base_page_name,
        )

        if verbose:
            print "Converting PDF Images ..."

        # wand makes image sequences out of multi-page files
        page_count = len(imgs)
        completed_pages = 0
        for image_filename in imgs:
            #success, image_filename = _save_page_image(i,im,base_page_name)
            #if success == True:
                print "\n\n"
                print image_filename
                print "\n\n"
                success, page_text = _convert_image_to_text(image_filename)
                if success == True:
                    if delete_files == True:
                        success = _delete_files(image_filename)
                        if success == False:
                            raise Exception('Unable to delete image: %s' % image_filename)
                else:
                    raise Exception('Unable to convert image: %s' % image_filename)

                output_text = "{0}{1}{2}".format(output_text, page_text, page_delineation)

                completed_pages += 1

                if verbose:
                    print "Successfully converted page %i of %i." % (i,page_count)

        success = False

    #except Exception, e:
    #    print "ERROR: {0}".format(e)

    return success, output_text

def _get_images_from_pdf(pdf_filename, resolution=200, base_page_name='page'):

    ret_images = []
    #__pdf_images = []
    #try:
    if True:

        print "Splitting PDF into multiple pdf's for processing ..."

        # make sure there is a place to put our temporary pdfs
        if not os.path.exists('temp'):
            os.makedirs('temp')

        # read input pdf
        inputpdf = PdfFileReader(open(pdf_filename, "rb"))
        if inputpdf.getIsEncrypted():
            inputpdf.decrypt('')

        print "Writing out %i pages ..." % inputpdf.numPages

        # create all of the temporary pdfs
        for i in range(0,16): #xrange(inputpdf.numPages):
            output = PdfFileWriter()
            output.addPage(inputpdf.getPage(i))
            filename = "temp/document-page-%s.pdf" % i
            with open(filename, "wb") as outputStream:
                output.write(outputStream)
            __pdf_queue.put(i)
            ret_images.append(None)

        #print __pdf_images[0]

        #print "Queue holds {0} pdfs, to be converted into {1} images.".format(
        #    __pdf_queue.qsize(),
        #    len(__pdf_images),
        #)

        print "Dispatching pdf workers ..."

        # spin up our workers to convert the pdfs to images
        pool_count = 8
        pool = Pool()
        result = pool.map_async(
            _pdf_converter_worker, 
            [(x, resolution, base_page_name) for x in range(pool_count)]
        )

        while not __pdf_queue.empty():
            time.sleep(.25)
        
        #if True:
        try:
            while(1):
                image_number,image_filename = __pdf_images.get_nowait()
                ret_images[image_number] = image_filename
        except:
            pass

        #print __pdf_images

        print ret_images

        print "Done conerting PDF."

    #except:
    #    pass

    return ret_images

def _pdf_converter_worker(args):

    thread_number = args[0]
    resolution = args[1]
    base_page_name = args[2]

    #if True:
    try:

        while(1):

            #print "{0}: Getting page from queue ...".format(thread_number)

            page_number = __pdf_queue.get_nowait()

            print "{0}: working on page {1}".format(thread_number, page_number)

            imgs = WandImage(
                filename="temp/document-page-{0}.pdf".format(page_number),
                resolution=resolution
            )

            #print "{0}: done with page {1}".format(thread_number, page_number)

            ret_imgs = zip(xrange(len(imgs.sequence)), imgs.sequence)

            #print "{0}: saving image data ...".format(thread_number)

            _i, _im = ret_imgs[0]
            success, image_filename = _save_page_image(page_number, _im, base_page_name)

            #print "{0}: saving image {1} filename to list ...".format(thread_number, page_number)

            __pdf_images.put((int(page_number), image_filename))

            #print "{0}: done.".format(thread_number)

            #__pdf_queue.task_done()

    except Exception, e:
    #    pass
        print str(e)

    return 

    

def _save_page_image(page_number, image, base_page_name='page'):

    success = False
    image_filename = ''
    #try:
    if True:
        image_filename = '%s-%i.png' % (base_page_name, page_number)
        image.clone().save(
            filename=image_filename
        )
        success = True
    #except:
    #    pass

    return success, image_filename

def _convert_image_to_text(image_filename):

    print "Converting {0} ...".format(image_filename)

    success = False
    page_text = ''
    #try:
    if True:
        FNULL = open(os.devnull, 'w')

        text_filename = '%s.txt' % image_filename
        subprocess.call(['tesseract', image_filename, image_filename],
                        stdout=FNULL, stderr=subprocess.STDOUT)
        with open(text_filename,'r') as f:
            page_text = f.read()
        success = True
    #except:
    #    pass

    print "Done."

    return success, page_text

def _delete_files(image_filename):

    success = False
    #try:
    if True:
        os.remove(image_filename)
        os.remove('%s.txt' % image_filename)
        success = True
    #except:
    #    pass

    return success
