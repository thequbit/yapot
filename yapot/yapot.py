import os
import uuid
import time

from multiprocessing import Queue
from multiprocessing import Pool

from yapot_utils import(
    decrypt_pdf,
    image_ocr,
    make_thumb,
    pdf_to_image,
    split_pdf,
    build_output_text,
    cleanup_yapot,
    )

__pdf_filenames = Queue()
__text_filenames = Queue()

def convert_document(pdf_filename,
                     resolution=200,
                     delete_files=True,
                     page_delineation='\n--------\n',
                     verbose=False,
                     temp_dir=str(uuid.uuid4()),password='',
                     make_thumbs=False,
                     thumb_size=160,
                     thumb_dir='thumbs',
                     thumb_prefix='thumb_page_',
                     pool_count=1):

    print "M: Start."

    filename = decrypt_pdf(pdf_filename, password)
    
    filenames = split_pdf(filename)

    for filename in filenames:
        __pdf_filenames.put(filename)

    print "M: Spinning up {0} workers.".format(pool_count)
    print "M: Converting {0} pages.".format(__pdf_filenames.qsize())

    pool = Pool()
    pool.map_async(
        _yapot_worker,
        [(tid, pdf_filename, make_thumbs, thumb_size, resolution) for \
            tid in range(0, pool_count)],
    )

    print "M: Waiting for pool to finish."

    while __text_filenames.qsize() != len(filenames):
        time.sleep(1)

    print "M: Building output text."

    text_filenames = []
    try:
        while(1):
            text_filenames.append(__text_filenames.get_nowait())
    except:
        pass

    text = build_output_text(text_filenames, page_delineation)

    if delete_files:
        cleanup_yapot(pdf_filename, text_filenames)

    print "M: Done."

    return text

def _yapot_worker(args):

    tid, pdf_filename, make_thumbs, thumb_size, resolution = args

    print "{0}: Worker started.".format(tid)

    while(1):

        if not __pdf_filenames.qsize():
            print "{0}: No more work.".format(tid)
            break

        try:
            filename = __pdf_filenames.get_nowait()
        except Queue.Empty:
            break;

        print "{0}: Working on: '{1}'".format(tid, filename)

        image_filename = '{0}.tiff'.format(filename)

        success = pdf_to_image(filename, image_filename, resolution)

        print "{0}: Pdf to Image conversion complete.".format(tid)

        if make_thumbs:
            thumbs_dir = '{0}_thumbs'.format(pdf_filename)
            if not os.path.exists(thumbs_dir):
                os.makedirs(thumbs_dir)
            thumb_filename = '{0}/{1}_thumb.png'.format(thumbs_dir, image_filename)
            succes = make_thumb(image_filename, thumb_filename, thumb_size)
            print "{0}: Thumbnail created.".format(tid)

        try:
            text = image_ocr(image_filename)
        except Exception, e:
            print str(e)
        print "{0}: Image OCR complete.".format(tid)

        os.remove(filename)
        os.remove(image_filename)

        text_filename = '{0}.txt'.format(image_filename)
        with open(text_filename,'w') as f:
            f.write(text)

        print "{0}: OCR Text written to disk.".format(tid)

        __text_filenames.put(text_filename)

        print "{0}: Done with conversion: '{1}'.".format(tid, filename)

    print "{0}: Worker exiting.".format(tid)
