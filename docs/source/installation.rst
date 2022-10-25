Installation
============

Instructions
^^^^^^^^^^^^

From pip
--------

Run::

    pip3 install --upgrade pdfsak

From source
-----------

Clone the repository and run the install script::

    git clone https://github.com/raffaem/pdfsak
    cd pdfsak
    pip3 install .

A new command ``pdfsak`` is now available in your PATH.

Requirements
^^^^^^^^^^^^

General
-------

PDFsak has been tested on Windows (in partiular, Windows 11 with both TexLive and MikTex) and Linux (in particular, Fedora Workstation 35 with TexLive 2021).

It should work also on macOS, although it has not been tested on this platform.

PDFsak needs the following dependencies, which must be present in your `PATH` environmental variable:

* `Python <https://www.python.org/>`_ ≥ 3.6
* A LaTeX distribution

    * The `pdftex` provided must have version ≥ 1.40.17 (released with TexLive 2016)
    * For Linux, I suggest `TexLive <https://www.tug.org/texlive/>`_
    * For Windows, I suggest `MikTex <http://miktex.org/>`_, although PDFsak has also been tested with TexLive under this platform
    * The following packages must be available in your LaTeX distribution:

        * `pdfpages <https://www.ctan.org/pkg/pdfpages>`_
        * `lastpage <https://www.ctan.org/pkg/lastpage>`_
        * `grffile <https://www.ctan.org/pkg/grffile>`_
        * `fancyhdr <https://www.ctan.org/pkg/fancyhdr>`_
        * `textpos <https://www.ctan.org/pkg/textpos>`_
        * `changepage <https://www.ctan.org/pkg/changepage>`_
        * `transparent <https://www.ctan.org/pkg/transparent>`_

* `Ghostscript <https://www.ghostscript.com>`_
* For the simulation of Adobe Acrobat Clearscan, the following optional dependencies are also needed:

    * `potrace <potrace.sf.net>`_
    * `ImageMagick <https://imagemagick.org>`_

You can check whether the dependencies are working as expected by running:
``pdfsak --check-all``

Fedora
------

On Fedora you can install all dependencies with:

``sudo dnf install texlive-pdfpages texlive-lastpage texlive-grffile texlive-fancyhdr texlive-textpos texlive-changepage texlive-transparent ghostscript potrace ImageMagick``

Windows
-------

On Windows, you must install all the dependencies manually, by clicking on the website, downloading the installer and running it.

Please note that only one of MikTex or TexLive is needed, not both.

MikTex is suggested under this OS, since it will provide a basic LaTeX environment, and will let you install the needed packages as it goes on. Just install MikTex, run `pdfsak --check-all`, and let MikTeX install the missing packages.

TexLive, instead, provides you the option to install a complete LaTeX environment, but the installation may require more time.

Note that all the dependencies must be in the `PATH` environment variable. There are a lot of guides that explain how to add a path to the `PATH` environment variable, one of it is `here <https://thegeekpage.com/environment-variables-in-windows-11/#How_to_add_to_the_PATH_variable>`_.
