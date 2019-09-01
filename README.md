# Pdftools

## About it
Python script to:

* Merge PDF files
* Nup (or tile) pages, that is put more than one logical input pages into a single output page (e.g. print slides with 2 slides in one page)
* Number pages 
* Remove owner protection from PDF files (you are able to open the PDF without a password, but you are not able to copy / print / annotate / exc.)
* Remove metadata from PDF file
* Split one input page in 2 output pages (e.g. scanned book with 2 pages in every pdf page)
* Create slides booklet, 3 slides on the left of output page and 3 white slides on the right
* And lots more

All the operations above can be achieve togheter with a single command line.
Disover all the functionalities by running

	pdftools.py -h
	
## Examples
Here are few examples of what pdftools can do:

* Nup : every page of output file consists of 2 pages on input file, one down the other. Page numbers are added in the bottom right corner. Filename is added upper, center margin. A bit of space between the 2 pages is added. The border of the pages are printed.

		pdftools.py -i input.pdf --out-suffix _nup21 --nup 2 1 --frame --width 0.8 --delta 0 2cm --paginate --overwrite --text $filename 0.4 0.01
	
* Every page of the output file consists of 2 columns. In the left columns there are 3 pages of the input file, one down the other. In the right column there are 3 corresponding white pages. Useful to print slides to bring to class and take notes in the white space. Similar to what PowerPoint does.

		pdftools.py -i input.pdf --out-suffix _W --white-page --fitpaper --overwrite
		pdftools.py -i input_W.pdf --out-suffix _HANDOUT --nup 3 2 --frame --overwrite --paginate --delta 0mm 5mm --width 0.45

## Requirements
* [Python](https://www.python.org/) >= 3.3
* A LaTeX distribution like [TexLive](https://www.tug.org/texlive/) or [MikTex](http://miktex.org/)
* The following packages must be available in your LaTeX distribution. You can check their presence by running

pdftools.py --check-latex

* [pdfpages](https://www.ctan.org/pkg/pdfpages?lang=en)
* [lastpage](https://www.ctan.org/pkg/lastpage)
* [grffile](https://www.ctan.org/pkg/grffile)
* [forloop](https://www.ctan.org/pkg/forloop)
* [fancyhdr](https://www.ctan.org/pkg/fancyhdr?lang=en)
* [textpos](https://www.ctan.org/pkg/textpos)
* [changepage](https://www.ctan.org/pkg/changepage)
