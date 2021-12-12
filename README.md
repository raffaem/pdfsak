# PDFsak

## About it
PDFsak (PDF Swiss Army knife) is an utility to manipulate PDF files.

The previous name of the project (as of 2021-10-10) was "pdftools".

It allows you to:

* Merge PDF files
* N-up pages (put more than one input page into a single output page)
* Trim pages
* Extract pages
* Rotate pages
* Swap pages
* Delete pages
* Create handouts
* Add text (like page numbers)
* Remove owner protection from PDF files (the protection that allows you to open the PDF without a password, but not to print/annotate it)
* Remove metadata from PDF file
* Simulate Adobe Acrobat Clearscan
* And more

It work on Linux, macOS and Windows.

## Installation

### From pip

Run:

```
pip3 install pdfsak
```

### From source

Clone the repository and run the install script:

```
git clone https://github.com/raffaem/pdftools
cd pdftools
python3 setup.py install --user
```

A new command `pdfsak` is now available in your PATH.

## Documentation

Checkout the [online documentation](https://pdfsak.readthedocs.io).

## Requirements

* [Python](https://www.python.org/) >= 3.3
* A LaTeX distribution like [TexLive](https://www.tug.org/texlive/) or [MikTex](http://miktex.org/)
    * The following packages must be available in your LaTeX distribution:
        * [pdfpages](https://www.ctan.org/pkg/pdfpages)
        * [lastpage](https://www.ctan.org/pkg/lastpage)
        * [grffile](https://www.ctan.org/pkg/grffile)
        * [forloop](https://www.ctan.org/pkg/forloop)
        * [fancyhdr](https://www.ctan.org/pkg/fancyhdr)
        * [textpos](https://www.ctan.org/pkg/textpos)
        * [changepage](https://www.ctan.org/pkg/changepage)

        On Fedora you can install them by running:

        `sudo dnf install texlive-lastpage texlive-pdfpages texlive-grffile texlive-forloop texlive-fancyhdr texlive-textpos texlive-changepage`

    * You can check the presence of the above required LaTeX packages by running:

        `pdfsak --check-latex`

* [Ghostscript](https://www.ghostscript.com/) must be available through the `gs` command
    * You can check its presence by running:

        `pdfsak --check-ghostscript`

* For the simulation of Adobe Acrobat Clearscan, you will also need:
    * [potrace](potrace.sf.net)
    * [ImageMagick](https://imagemagick.org)
    
    On Fedora you can install these dependencies by running:

    `sudo dnf install potrace ImageMagick`
