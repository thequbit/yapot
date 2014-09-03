from wand.image import Image as WandImage
import subprocess
import os

def convert_document(pdf_filename, base_page_name, resolution=200, 
        delete_files = True, page_delineation='\n--------\n', 
        verbose=False):

    success = False
    output_text = ''

    try:
    #if True:

        if verbose:
            print "Reading PDF ..."

        # get the images from the pdf
        imgs = _get_images_from_pdf(
            pdf_filename = pdf_filename,
            resolution = resolution,
        )

        if verbose:
            print "Converting PDF Images ..."

        # wand makes image sequences out of multi-page files
        page_count = len(imgs)
        for i,im in imgs:
            success, image_filename = _save_page_image(i,im,base_page_name)
            if success == True:
                success, page_text = _convert_image_to_text(image_filename)
                if success == True:
                    if delete_files == True:
                        success = _delete_files(image_filename)
                        if success == False:
                            raise Exception('Unable to delete image: %s' % image_filename)
                else:
                    raise Exception('Unable to convert image: %s' % image_filename)

                output_text = "{0}{1}{2}".format(output_text, page_text, page_delineation)

                if verbose:
                    print "Successfully converted page %i of %i." % (i,page_count)

        success = False

    except Exception, e:
        print "ERROR: {0}".format(e)

    return success, output_text

def _get_images_from_pdf(pdf_filename, resolution=200):

    ret_imgs = None
    try:
        imgs = WandImage(
            filename=pdf_filename,
            resolution=resolution
        )
        ret_imgs = zip(xrange(len(imgs.sequence)), imgs.sequence)
    except:
        pass

    return ret_imgs

def _save_page_image(page_number, image, base_page_name='page'):

    success = False
    image_filename = ''
    try:
        image_filename = '%s-%i.png' % (base_page_name, page_number)
        image.clone().save(
            filename=image_filename
        )
        success = True
    except:
        pass

    return success, image_filename

def _convert_image_to_text(image_filename):
    
    success = False
    page_text = ''
    #try:
    if True:
       FNULL = open(os.devnull, 'w')
       
       text_filename = '%s.txt' % image_filename
       subprocess.call(['tesseract',image_filename,image_filename], \
           stdout=FNULL, stderr=subprocess.STDOUT)
       with open(text_filename,'r') as f:
           page_text = f.read()
       success = True
    #except:
    #    pass

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
