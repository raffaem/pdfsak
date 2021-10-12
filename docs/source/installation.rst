Installation
============

Innstructions
^^^^^^^^^^^^^

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

        On Fedora you can install them by running:

        ``sudo dnf install texlive-lastpage texlive-pdfpages texlive-grffile texlive-forloop texlive-fancyhdr texlive-textpos texlive-changepage``

    * You can check the presence of the above required LaTeX packages by running:

        ``pdfsak --check-latex``

* `Ghostscript <https://www.ghostscript.com>`_ must be available through the ``gs`` command
    * You can check its presence by running:

        ``pdfsak --check-ghostscript``
