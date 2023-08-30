Command Line Arguments
======================

Run ::

    pdfsak --help

to see available command line arguments:

::

    usage: pdfsak [-h] [--version] [--latex-engine {pdflatex,xelatex}]
                  [-if INPUT_FILES | -id INPUT_DIRS | -rd]
                  [-o OUTPUT | --out-suffix OUT_SUFFIX | --replace-input]
                  [--paper PAPER_TYPE] [--scale SCALE_FACTOR] [--width WIDTH]
                  [--height HEIGHT] [--nup ROWS COLS] [--offset RIGHT TOP]
                  [--trim Left Bottom Right Top] [--delta X Y] [--custom CUSTOM]
                  [--watermark file anchor hpos vpos scale alpha]
                  [-t text_string anchor hpos vpos] [--text-help] [--font FONT]
                  [--skip-unrecognized-type] [--natural-sorting] [--overwrite]
                  [--blackbg]
                  [--swap-pages SWAP_PAGES | --rotate-pages ROTATE_PAGES | --delete-pages DELETE_PAGES | --add-white-pages | --extract-pages EXTRACT_PAGES]
                  [--clearscan] [--clearscan-density CLEARSCAN_DENSITY]
                  [--clearscan-opttolerance CLEARSCAN_OPTTOLERANCE]
                  [--clearscan-turnpolicy CLEARSCAN_TURNPOLICY]
                  [--clearscan-alphamax CLEARSCAN_ALPHAMAX]
                  [--clearscan-skip-mkbitmap]
                  [--clearscan-filter-size CLEARSCAN_FILTER_SIZE]
                  [--clearscan-upscaling-factor CLEARSCAN_UPSCALING_FACTOR]
                  [--clearscan-threshold CLEARSCAN_THRESHOLD] [--check-all]
                  [--clip] [--rotateoversize] [--landscape] [--frame]
                  [--textpos-showboxes]

    options:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      --latex-engine {pdflatex,xelatex}
                            LaTeX engine to use. Defaults to pdflatex. (default:
                            pdflatex)
      -if INPUT_FILES, --input-file INPUT_FILES
                            Input pdf file. Use this flag again to merge multiple
                            pdf files into one. (default: [])
      -id INPUT_DIRS, --input-dir INPUT_DIRS
                            Input a directory. All pdf files inside it will be
                            merged together, sorted in alphabetical filename
                            order. (default: [])
      -rd, --recursive-dir  Process the PDFs inside a dir recursively. (default:
                            False)
      -o OUTPUT, --output OUTPUT
                            Output filename (default: None)
      --out-suffix OUT_SUFFIX
                            Suffix to add to the first input filename to obtain
                            the output filename (default: _pdfsak)
      --replace-input       Replace first input PDF file with output PDF file.
                            (default: False)
      --paper PAPER_TYPE    Specify output paper size. Can be: a4paper,
                            letterpaper, a5paper, b5paper, executivepaper,
                            legalpaper. The default is to use the same size as the
                            input PDF (default: None)
      --scale SCALE_FACTOR  Scales the image by the desired scale factor. E.g, 0.5
                            to reduce by half, or 2 to double. 0 means auto-
                            scaling (default). (default: 0)
      --width WIDTH         Width of 1 input page (take care of this in case of
                            n-upping) relative to output page width. (default: 0)
      --height HEIGHT       Height of 1 input page (take care of this in case of
                            n-upping) relative to output page height. (default: 0)
      --nup ROWS COLS       N-up pages, follow with number of rows and columns
                            (default: [1, 1])
      --offset RIGHT TOP    The inserted logical pages are being centered on the
                            sheet of paper by default. Use this option, which
                            takes two arguments, to displace them. E.g.
                            --offset=10mm 14mm means that the logical pages are
                            displaced by 10 mm in horizontal direction and by 14
                            mm in vertical direction. In oneside documents,
                            positive values shift the pages to the right and to
                            the top margin, respectively. In ‘twoside’ documents,
                            positive values shift the pages to the outer and to
                            the top margin, respectively. (default: ['0', '0'])
      --trim Left Bottom Right Top
                            Crop pdf page. You can use the following variables:
                            \pdfwidth is the width of a pdf page, \pdfheight is
                            the height of a pdf page. Both are calculated on the
                            first page of the pdf. So for example "--trim 0
                            .5\pdfwidth .2\pdfheight 0" will trim the pages half
                            from the right and 20 per cent from the bottom
                            (default: ['0', '0', '0', '0'])
      --delta X Y           By default logical pages are being arranged side by
                            side. To put some space between them, use the delta
                            option, which takes two arguments. (default: ['0',
                            '0'])
      --custom CUSTOM       Custom pdfpages options (default: None)
      --watermark file anchor hpos vpos scale alpha
                            Add watermark image. (default: None)
      -t text_string anchor hpos vpos, --text text_string anchor hpos vpos
                            Add text to pdf file. 'text_string' is the string to
                            add, special variables can be passed, as well as LaTeX
                            font sizes like \Huge. Pass --text-help for help on
                            how to build this string. 'anchor' sets the side of
                            the text box (the box surrounding the text) where it
                            is anchored (where its position is measured from):'tl'
                            - top-left corner, 'tm' - middle of the top edge, 'tr'
                            - top-right corner, 'bl' - bottom-left corner, 'bm' -
                            middle of the bottom edge, 'br' - bottom-right corner,
                            all other parameters are invalid. 'hpos' and 'vpos'
                            are numbers between 0 and 1 that represent how far is
                            'anchor' from the top left corner of the page.
                            (default: None)
      --text-help           Print help on how to build a text string for the
                            -t/--text option (default: False)
      --font FONT           Font to use for text in the document (default: None)
      --skip-unrecognized-type
                            Skip unrecognized file types when scanning a
                            directory. Otherwise, thrown an error (default: False)
      --natural-sorting     When scanning a folder, use natural sorting algorithm
                            to sort the files inside it (default: False)
      --overwrite           Overwrite output file if it exists already (default:
                            False)
      --blackbg             Make the background black, for e.g. n-upping dark
                            background slides. (default: False)
      --swap-pages SWAP_PAGES
                            A semi-colon separated list of colon-separated page
                            pairs to swap. E.g. "1,5;6,9" will swap page 1 with
                            page 5 and page 6 with page 9. (default: )
      --rotate-pages ROTATE_PAGES
                            A semi-colon separated list of page=angle pairs.
                            Rotation angle is counterclockwise. E.g. "1=90;2=180"
                            will rotate 1st page by 90 degress counterclockwise
                            and 2nd page by 180 degrees. (default: )
      --delete-pages DELETE_PAGES
                            A semi-colon separated list of pages to delete.
                            (default: )
      --add-white-pages     Put a white page after every page. (default: False)
      --extract-pages EXTRACT_PAGES
                            Selects pages to insert. The argument is a comma
                            separated list, containing page numbers (e.g.
                            3,5,6,8), ranges of page numbers (e.g. 4-9) or any
                            combination of the previous. To insert empty pages,
                            use {}. Page ranges are specified by the following
                            syntax: m-n. This selects all pages from m to n.
                            Omitting m defaults to the first page; omitting n
                            defaults to the last page of the document. Another way
                            to select the last page of the document, is to use the
                            keyword last.E.g.: "--extract-pages 3,{},8-11,15" will
                            insert page 3, an empty page, pages from 8 to 11, and
                            page 15. "--extract-pages=-" will insert all pages of
                            the document, "--extract-pages=last-1" will insert all
                            pages in reverse order. (default: -)
      --clearscan           Simulate Adobe Acrobat ClearScan (default: False)
      --clearscan-density CLEARSCAN_DENSITY
                            Density with which to convert PDF into bitmap.
                            (default: 300)
      --clearscan-opttolerance CLEARSCAN_OPTTOLERANCE
                            Set the curve optimization tolerance. The default
                            value is 0.2. Larger values allow more consecutive
                            Bezier curve segments to be joined together in a
                            single segment, at the expense of accuracy. (default:
                            0.2)
      --clearscan-turnpolicy CLEARSCAN_TURNPOLICY
                            Specify how to resolve ambiguities in path
                            decomposition. Must be one of black, white, right,
                            left, minority, majority, or random. Default is
                            minority. Turn policies can be abbreviated by an
                            unambiguous prefix, e.g., one can specify min instead
                            of minority. (default: minority)
      --clearscan-alphamax CLEARSCAN_ALPHAMAX
                            set the corner threshold parameter. The default value
                            is 1. The smaller this value, the more sharp corners
                            will be produced. If this parameter is 0, then no
                            smoothing will be performed and the output is a
                            polygon. If this parameter is greater than 4/3, then
                            all corners are suppressed and the output is
                            completely smooth. (default: 1)
      --clearscan-skip-mkbitmap
                            Skip mkbitmap passage (default: False)
      --clearscan-filter-size CLEARSCAN_FILTER_SIZE
                            Pixel size of high-pass filter to pass to mkbitmap for
                            clearscan. Requires mkbitmap. (default: 2)
      --clearscan-upscaling-factor CLEARSCAN_UPSCALING_FACTOR
                            Upscale the image by this factor using mkbitmap before
                            passing it to potrace. Requires mkbitmap. (default: 1)
      --clearscan-threshold CLEARSCAN_THRESHOLD
                            Threshold level. Requires mkbitmap. (default: 0.5)
      --check-all           Check all dependencies (including optional ones)
                            (default: False)
      --clip                Used togheter with trim, will actually remove the
                            cropped part from the pdfpage. If false, the cropped
                            part is present on the physical file, but the pdf
                            reader is instructed to ignore it. (default: None)
      --rotateoversize      Rotate oversized pages. (default: None)
      --landscape           Output file is in landscape layer instead of portrait.
                            (default: None)
      --frame               Put a frame around every logical page. (default: None)
      --textpos-showboxes   Call textpos package with the showboxes option,
                            putting a frame around every textblock. (default:
                            False)

