import os
import sys
import uuid
from yapot import convert_document

def run():
    print("Welcome to yapot!")
    if len(sys.argv) != 2:
        print(("Usage:\n\n\t"
               "python cli-tool.py <pdf_filename> <output_dir>\n\n"))
    else:
        pdf_filename = sys.argv[1]
        #output_dir = sys.argv[2]
        #base_page_name = os.path.expanduser(pdf_filename)

        #if not os.path.exists(output_dir):
        #    os.makedirs(output_dir)

        temp_dir = '{0}'.format(str(uuid.uuid4()))
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        pdf_text = convert_document(
            pdf_filename = pdf_filename,
            #base_page_name = base_page_name,
            resolution = 300,
            delete_files = True,
            page_delineation = '\n--------\n',
            verbose = True,
            temp_dir = temp_dir,
            #make_thumbs = True,
            #thumb_size = 512,
            #thumb_dir = '{0}/thumbs'.format(temp_dir),
            pool_count = 1,
        )

        with open('%s.txt' % pdf_filename, 'w') as f:
            f.write(pdf_text)

        print("Done.")

if __name__ == '__main__':

    run()
