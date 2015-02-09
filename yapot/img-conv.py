import os
import sys
import subprocess
from yapot import _convert_image_to_text

def _convert_to_tiff(image_filename):

    try:

        FNULL = open(os.devnull, 'w')

        output_filename = '{0}.tiff'.format(image_filename)
        cli_call = [
            'convert',
            image_filename,
            output_filename,
        ]
        subprocess.call(
            cli_call,
            stdout=FNULL,
            stderr=subprocess.STDOUT
        )
    except Exception, e:
        print "ERROR: {0}".format(e)

    return output_filename

def convert_image(image_filename):

    tiff_filename = _convert_to_tiff(image_filename)

    image_text = _convert_image_to_text(tiff_filename)

    #print image_text

    return image_text

if __name__ == '__main__':

    print "Welcome to yapot!"

    if len(sys.argv) != 3:
        print "Usage:\n\n\tpython img-conv.py <image_filename> <output_text_filename>\n\n"
    else:
        image_filename = sys.argv[1]
        text_filename = sys.argv[2]

        success, image_text = convert_image(image_filename)

        if success == True:
            with open(text_filename, 'w') as f:
                f.write(image_text)
            print "Done!"
        else:
            print "Image -> Text conversion was not successful."
