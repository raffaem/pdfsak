Examples
========

addtext
-------

This example adds:

- Page numbers in the bottom right corner (in the format `current_page/total_pages`)
- Current date in the top left corner (in the format `day/month/year`)

Here is the command line:

::

    pdfsak --input-file article1.pdf --output addtext.pdf --text "\huge \$page/\$pages" br 1 1 --text "\huge \$day/\$month/\$year" tl 0 0

clearscan
---------

This example simulates Adobe Acrobat Clearscan.

That is, it will vectorize the text of your PDF file, improving quality and readability.

::

    pdfsak --input-file head.pdf --output clearscan.pdf --clearscan

delete_pages
------------

This example delete pages 4,5,10 and 11.

::

    pdfsak --input-file numbered.pdf --output delete_pages.pdf --delete-pages "4,5,10,11"

extract_pages
-------------

This example extract pages 1, 3, and from 20 onwards.

::

    pdfsak --input-file numbered.pdf --output extract_pages.pdf --extract-pages "1,3,20-"

handout2x2
----------

This example creates a 2x2 lecture handout.

Every page of the output file is a 2x2 grid (2 rows and 2 columns).

The left columns will contain pages from the input PDF file.

The right columns will be white.

::

    pdfsak --input-file presentation.pdf --output handout2x2_W.pdf --add-white-pages
    pdfsak --input-file handout2x2_W.pdf --output handout2x2.pdf --nup 2 2 --height 0.32 --landscape --frame --paper a4paper

handout3x2
----------

This example creates a 3x2 lecture handout.

Every page of the output file is a 3x2 grid (3 rows and 2 columns).

The left columns will contain pages from the input PDF file.

The right columns will be white.

::

    pdfsak --input-file presentation.pdf --output handout3x2_W.pdf --add-white-pages
    pdfsak --input-file handout3x2_W.pdf --output handout3x2.pdf --nup 3 2 --height 0.2 --landscape --frame --paper a4paper

img2pdf
-------

This example creates a PDF from images.

::

    pdfsak --input-file img1.jpg --input-file img2.jpg --paper A4 -o img2pdf.pdf

merge
-----

This example merge 2 input PDF files together in a single output PDF file.

::

    pdfsak --input-file article1.pdf --input-file article2.pdf --output merge.pdf

merge_dir
---------

This example merge together all the PDF files in a folder.

Natural sorting is used to determine the order in which the files are merged.

::

    pdfsak --input-dir ./input --output merge_dir.pdf

replace_input
-------------

This example replaces the input PDF file instead of writing to a separate output file.

::

    pdfsak --input-file input.pdf --replace-input --extract-pages "1"

rotate_pages
------------

This example rotate the pages of a input PDF file.

The 2nd page is rotated 90 degrees counterclockwise.

The 3rd page is rotated 180 degrees counterclockwise (it will be upside down).

The 4th page is rotated 270 degrees counterclockwise.

The 5th page is rotated 45 degrees counterclockwise.

::

   pdfsak --input-file input.pdf --output output.pdf --rotate-pages "2=90;3=180;4=270;5=45"

swap_pages
----------

This example swaps the 2nd with the 3rd page, and the 4th with the 5th page.

::

    pdfsak --input-file input.pdf --output output.pdf --swap-pages "2,3;4,5"

watermark
---------

This example adds a watermark to every page.

The watermark is an image file (`../../input/tux.png`) whose center point (`cm`) is positioned at the center of the pages of the input file (`0.5 0.5`). Furthermore, the image is scaled to 20% of its original size (`0.2`) and its transparency is set at 50% (`0.5`).

::

    ../../../pdfsak --input-file ../../input/presentation.pdf --output ../../output/watermark.pdf --watermark ../../input/tux.png cm 0.5 0.5 0.2 0.5
