yapot
=====

Yet Another PDF OCR Tool


This is a library (tool) that makes PDF -> Text as easy as possble by doing a lot of the hard stuff for you!

You will need ImageMagick and Tesseract to use yapot.

    Ubuntu
    ------
    > sudo apt-get install imagemagick libmagickcore-dev
    > sudo apt-get install tesseract-ocr
        
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
        base_page_name = base_page_name,   # The base of each page's image (default 'page')
        resolution = 200,                  # Image DPI resolution (default 200)
        delete_files = True,               # delete temporary files (default True)
        page_delineation = '\n--------\n', # page deination text (default '\n--------\n')
        verbose = True,                       # output verbosity (default False)
    )

