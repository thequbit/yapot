import sys
import yapot

pdf_filename = sys.argv[1]
base_page_name = sys.argv[2]

success, pdf_text = yapot.write_out_images(
    pdf_filename = pdf_filename,
    base_page_name = base_page_name,
    resolution = 200,
    delete_files = False,
    page_delineation = '\n--------\n',
    verbose = True,
)

print pdf_text
