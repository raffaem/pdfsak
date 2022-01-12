Installation
============

Instructions
^^^^^^^^^^^^

From pip
--------

Run::

    pip3 install pdfsak

From source
-----------

Clone the repository and run the install script::

    git clone https://github.com/raffaem/pdftools
    cd pdftools
    python3 setup.py install --user

A new command ``pdfsak`` is now available in your PATH.

Requirements
^^^^^^^^^^^^

General
-------

You can check whether the dependencies are working as expected by running:
``pdfsak --check-all``

PDFsak needs the following dependencies (which must be present in your `PATH`):

* `Python <https://www.python.org/>`_ >= 3.5
* A LaTeX distribution like `TexLive <https://www.tug.org/texlive/>`_ or `MikTex <http://miktex.org/>`_
    * The following packages must be available in your LaTeX distribution:
        * `pdfpages <https://www.ctan.org/pkg/pdfpages>`_
        * `lastpage <https://www.ctan.org/pkg/lastpage>`_
        * `grffile <https://www.ctan.org/pkg/grffile>`_
        * `forloop <https://www.ctan.org/pkg/forloop>`_
        * `fancyhdr <https://www.ctan.org/pkg/fancyhdr>`_
        * `textpos <https://www.ctan.org/pkg/textpos>`_
        * `changepage <https://www.ctan.org/pkg/changepage>`_
        * `transparent <https://www.ctan.org/pkg/transparent>`_
* `Ghostscript <https://www.ghostscript.com>`_
* For the simulation of Adobe Acrobat Clearscan, the following optional dependencies are also needed:
    * `potrace <potrace.sf.net>`_
    * `ImageMagick <https://imagemagick.org>`_

Fedora
------

On Fedora you can install all dependencies with:

``sudo dnf install texlive-pdfpages texlive-lastpage texlive-grffile texlive-forloop texlive-fancyhdr texlive-textpos texlive-changepage texlive-transparent ghostscript potrace ImageMagick``
