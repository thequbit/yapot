yapot
=====

Yet Another PDF OCR Tool


This is a library (tool) that makes PDF -> Text as easy as possble by doing a lot of the hard stuff for you!

You will need ImageMagick, Tesseract, and QPDF to use yapot.

    Ubuntu
    ------
    > sudo apt-get install imagemagick libmagickcore-dev
    > sudo apt-get install tesseract-ocr
    > sudo apt-get install qpdf
        
To use yapot, do the following:

    > pip install yapot
    
Then some code:

    from yapot import convert_document
    
    success, pdf_text = convert_document('file.pdf')
    
    if success == True:
        with open('file.txt', 'w') as f:
            f.write(pdf_text)
    else:
        print "Unable to convert PDF!"
        
It's that simple!

Some more advanced things you can do are set the resolution, page delineation, and tell yapot not to delete temporary files (this can be useful when debugging nasty pdf's).

    success, pdf_text = yapot.convert_document(
        pdf_filename = pdf_filename,       # The name of the pdf file
        resolution = 200,                  # Image DPI resolution
        delete_files = True,               # delete temporary files
        page_delineation = '\n--------\n', # page deination text
        verbose = False,                   # output verbosity
        temp_dir = str(uuid.uuid4()),      # location of temp directory to use
        password = '',                     # password for PDF file
        make_thumbs = True,                # create thrumbnails for each page
        thumb_size = 512,                  # width of thumbnail image
        thumb_dir = './thumbs',            # directory to place thumbnails
        thumb_prefix = 'thumb_page_',      # prefix for thumbnail images
    )

