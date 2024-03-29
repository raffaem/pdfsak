#!/usr/bin/env python3
# coding=utf8

# Copyright (c) 2022 Raffaele Mancuso

import sys
import zipfile  # Used to compress debug files togheter to be sent for analysis
import datetime
import tempfile
import os
import shutil
import argparse
import subprocess
from string import Template
import re
import errno
import random
import hashlib
from collections import namedtuple
from tqdm import tqdm
import platform
import copy
from natsort import natsorted
from multiprocessing import Process
import packaging.version
from pdfsak.pdfsak_version import __version__

# To restore cwd at the end, otherwise we get a exception
previous_cwd = os.getcwd()
temp_dir = None
today = datetime.datetime.now()
debug = False
pdflatex_min_ver = "1.40.17"
xelatex_min_ver = "0.9999"

# -Calculate needed rounds of compilation
needed_comp_rounds = 2
EXIT_SUCCESS = 0
EXIT_FAIL = 1
clearscan_filter_size_default = 2
clearscan_upscaling_factor_default = 1
clearscan_threshold_default = 0.5


def getGSBin():
    if os.name == "nt":
        # `gswin64` is a GUI interface. The CLI is called `gswin64c`
        return "gswin64c"
    elif os.name == "posix":
        return "gs"
    else:
        printMsgAndExit(
            f"ERROR: OS {os.name} not recognized: cannot infer Ghostscript path",
            EXIT_FAIL,
        )


def linuxize(path):
    return str(path).replace("\\", "/")


def getPageCount(infp):
    cmd = [
        getGSBin(),
        "-q",
        "-dNOSAFER",
        "-dNODISPLAY",
        "-c",
        f"({linuxize(infp)}) (r) file runpdfbegin pdfpagecount = runpdfend quit",
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        printMsgAndExit(
            f"ERROR: Cannot get page count.\n "
            f"cmd: {cmd}\nstdout: {res.stdout}\nstderr: {res.stderr}",
            EXIT_FAIL,
        )
    try:
        p = int(res.stdout.strip())
    except ValueError:
        printMsgAndExit(
            f"ERROR: ValueError while convering page count to int.\n"
            f"cmd: {cmd}\nstdout: {res.stdout}\nstderr: {res.stderr}",
            EXIT_FAIL,
        )
    return p


def trimArrayToStr(timarr):
    # trim_str = "{"
    trim_str = ""
    trim_str += f"{timarr[0]:.2}" + "\\pdfwidth{} "
    trim_str += f"{timarr[1]:.2}" + "\\pdfheight{} "
    trim_str += f"{timarr[2]:.2}" + "\\pdfwidth{} "
    trim_str += f"{timarr[3]:.2}" + "\\pdfheight{} "
    # trim_str += "}"
    trim_str = re.sub(r"1.0\\pdf(width|height){}", "0.0", trim_str)
    return trim_str


# Return 'pdf' if it's a pdf file, 'img' if it's an image file, or 'unknown' if it is not recognized
def getFileType(filepath):
    curr_ext = os.path.splitext(filepath)[1]
    curr_ext = curr_ext.lower()
    if curr_ext == ".pdf":
        return "pdf"
    elif (
        curr_ext == ".jpg"
        or curr_ext == ".jpeg"
        or curr_ext == ".gif"
        or curr_ext == ".png"
        or curr_ext == ".bmp"
    ):
        return "img"
    else:
        return "unknown"


# Check functions


def checkLatexCompiler(args):
    res_class = namedtuple(
        "LatexCompilerCheck", ["file_found", "stdout", "stderr", "verstr", "verok"]
    )
    try:
        pobj = subprocess.run([args.latex_engine, "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        return res_class(False, None, None, None, None)
    verstr = pobj.stdout.split("\n")[0]
    verstr = verstr.replace("pdfTeX", "")
    verstr = re.sub(r"\(.*\)", "", verstr)
    verstr = verstr.strip().split("-")[-1]
    ver = packaging.version.parse(verstr)
    if args.latex_engine == "pdflatex":
        minver = packaging.version.parse(pdflatex_min_ver)
    else:
        minver = packaging.version.parse(xelatex_min_ver)
    verok = ver >= minver
    return res_class(True, pobj.stdout.strip(), pobj.stderr.strip(), verstr, verok)


def checkLatexCompilerCLI(args):
    res = checkLatexCompiler(args)
    if not res.file_found:
        print(f"{args.latex_engine} NOT FOUND")
        return res
    if args.latex_engine == "pdflatex":
        minver = packaging.version.parse(pdflatex_min_ver)
    else:
        minver = packaging.version.parse(xelatex_min_ver)
    if res.verok:
        status = f"OK ({res.verstr} >= {minver}):"
    else:
        status = f"NOT OK ({res.verstr} < {minver}):"
    line0 = res.stdout.split("\n")[0].strip()
    print(f"{args.latex_engine} {status} {line0}")
    return res


def checkLatexPackage(pkgname, args):
    latex_tex_fp = "check.tex"
    latex_script = (
        "\\documentclass{article} \
    \n\\usepackage{"
        + pkgname
        + "} \
    \n\\begin{document}\
    \nHello\
    \n\\end{document}"
    )
    # Write latex file
    with open(latex_tex_fp, "w", encoding="utf8") as fh:
        fh.write(latex_script)
    # Compile latex file
    cmd = [args.latex_engine, "--shell-escape", "--interaction=nonstopmode", latex_tex_fp]
    res = subprocess.run(cmd, capture_output=True, text=True)
    # Read log file and look for package version
    ver = None
    try:
        with open("check.log") as fh:
            data = fh.read()
    except FileNotFoundError:
        data = ""
    ver_re = re.search(f"^Package: {pkgname} (.*)$", data, re.MULTILINE)
    if ver_re:
        try:
            ver = ver_re.group(1)
        except IndexError:
            pass
    if ver:
        try:
            ver = " ".join(ver.split()[:2])
        except:
            pass
    # Remove temp files
    removeFile("check.tex")
    removeFile("check.pdf")
    removeFile("check.aux")
    removeFile("check.log")
    # Return
    res_class = namedtuple("LatexPackageCheck", ["ok", "stdout", "stderr", "ver"])
    return res_class(
        ok=(res.returncode == 0),
        stdout=res.stdout.strip(),
        stderr=res.stderr.strip(),
        ver=ver,
    )


def checkLatexPackageCLI(pkgname, args):
    res = checkLatexPackage(pkgname, args)
    if not res.ok:
        print(f"Checking LaTeX package '{pkgname}': MISSING")
        print(f"stdout='{res.stdout}'")
        print(f"stderr='{res.stderr}'")
    else:
        print(f"Checking LaTeX package '{pkgname}' OK: {res.ver}")


def checkLatexInstallationCLI(args):
    checkLatexCompilerCLI(args)
    checkLatexPackageCLI("grffile", args)
    checkLatexPackageCLI("pdfpages", args)
    checkLatexPackageCLI("lastpage", args)
    checkLatexPackageCLI("fancyhdr", args)
    checkLatexPackageCLI("geometry", args)
    checkLatexPackageCLI("calc", args)
    checkLatexPackageCLI("graphicx", args)
    checkLatexPackageCLI("transparent", args)
    checkLatexPackageCLI("xparse", args)
    checkLatexPackageCLI("letltxmacro", args)
    checkLatexPackageCLI("changepage", args)
    checkLatexPackageCLI("textpos", args)
    if args.latex_engine != "pdflatex":
        checkLatexPackageCLI("fontspec", args)


def checkImageMagick():
    res_class = namedtuple("ImageMagickCheck", ["ok", "stdout", "stderr"])
    try:
        ver = subprocess.run(["magick", "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        return res_class(False, None, None)
    return res_class(True, ver.stdout.strip(), ver.stderr.strip())


def checkImageMagickCLI():
    res = checkImageMagick()
    if not res.ok:
        print("ImageMagick NOT FOUND")
    else:
        r = res.stdout.split("\n")[0]
        r = r.replace("https://imagemagick.org", "")
        r = r.replace("Version: ImageMagick ", "")
        print(f"ImageMagick OK: {r}")
    return res


def checkPotrace():
    res_class = namedtuple("PotraceCheck", ["ok", "stdout", "stderr"])
    try:
        ver = subprocess.run(["potrace", "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        return res_class(False, None, None)
    return res_class(True, ver.stdout.strip(), ver.stderr.strip())


def checkPotraceCLI():
    res = checkPotrace()
    if not res.ok:
        print("Potrace NOT FOUND")
    else:
        r = res.stdout.split("\n")[0]
        r = r.replace("potrace", "").strip().split()[0]
        if r[-1] == ".":
            r = r[:-1]
        print(f"Potrace OK: {r}")
    return res


def checkMKBitmap():
    res_class = namedtuple("MKBitmapCheck", ["ok", "stdout", "stderr"])
    try:
        ver = subprocess.run(["mkbitmap", "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        return res_class(False, None, None)
    return res_class(True, ver.stdout.strip(), ver.stderr.strip())


def checkMKBitmapCLI():
    res = checkMKBitmap()
    if not res.ok:
        print("mkbitmap NOT FOUND")
    else:
        r = res.stdout.split("\n")[0]
        r = r.replace("mkbitmap", "").strip().split()[0]
        if r[-1] == ".":
            r = r[:-1]
        print(f"mkbitmap OK: {r}")
    return res


def checkGhostscript():
    res_class = namedtuple("GhostscriptCheck", ["ok", "stdout", "stderr"])
    try:
        ver = subprocess.run([getGSBin(), "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        return res_class(False, None, None)
    return res_class(True, ver.stdout.strip(), ver.stderr.strip())


def checkGhostscriptCLI():
    res = checkGhostscript()
    if not res.ok:
        print("Ghostscript NOT FOUND")
    else:
        r = res.stdout.split("\n")[0]
    # Check Ghostscript version
    ver1 = int(res.stdout.split(".")[0])
    if ver1 < 9:
        print(f"Error: Ghostscript version {r} is too old. Please update it.")
    else:
        print(f"Ghostscript OK: {r}")
    return res


def checkAllCLI(args):
    global temp_dir
    temp_dir = createTempDir(args.debug, args.debug_folder)
    print("os.name:", os.name)
    print("platform.system():", platform.system())
    print("platform.release():", platform.release())
    print("CWD:", os.getcwd())
    print("PATH:", os.environ["PATH"])
    print("Python:", sys.version)
    print(f"PDFsak version: {__version__}")
    checkLatexInstallationCLI(args)
    checkImageMagickCLI()
    checkPotraceCLI()
    checkMKBitmapCLI()
    checkGhostscriptCLI()
    printMsgAndExit("", 0)


def removeFile(filename):
    # see: https://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:  # errno.ENOENT = no such file or directory
            raise  # re-raise exception if a different error occurred


def printMsgAndExit(msg, code):
    global debug
    global temp_dir
    os.chdir(previous_cwd)
    # Remove temporary directory, except if we are in debug mode
    if temp_dir and os.path.isdir(temp_dir) and (not debug):
        shutil.rmtree(temp_dir)
    if msg and msg != "":
        print(msg)
    exit(code)


# Convert an array into a string
# Used to convert command line passed arrays, like "delta", "offset" options
def arrayToString(arr, ldelim="", rdelim=""):
    ostr = ""
    for i in range(0, len(arr)):
        ostr += ldelim + str(arr[i]) + rdelim + " "
    return ostr


def printTextHelp():
    print(
        "Prepend these variables with a $ sign (e.g. $day). \
        Note that in bash, the $ sign must be escaped (\\$): \
        \nday = day of today \
        \nmonth = today month \
        \nyear = today year \
        \npage = current page \
        \npages = total number of pages"
    )


def createTempDir(debug=False, debug_folder=None):
    global temp_dir
    # If NOT in debug mode, temporary directory is created in system temporary folder
    if not debug:
        # avoid out of scope
        temp_dir = tempfile.mkdtemp(prefix="pdfsak")
    # If in debug mode, temporary directory is created in current working directory
    else:
        temp_dir = os.path.join(os.getcwd(), debug_folder)
        os.mkdir(temp_dir)
        print(f"Creating debug temporary directory {temp_dir}")
    # Change working directory to the temp folder. In this way, latex temporary files are created there
    os.chdir(temp_dir)
    return temp_dir


def anchor2coords(s):
    if s == "tl":
        anchh, anchv = 0, 0
    elif s == "tm":
        anchh, anchv = 0.5, 0
    elif s == "tr":
        anchh, anchv = 1, 0
    elif s == "cl":
        anchh, anchv = 0, 0.5
    elif s == "cm":
        anchh, anchv = 0.5, 0.5
    elif s == "cr":
        anchh, anchv = 1, 0.5
    elif s == "bl":
        anchh, anchv = 0, 1
    elif s == "bm":
        anchh, anchv = 0.5, 1
    elif s == "br":
        anchh, anchv = 1, 1
    else:
        printMsgAndExit(f"Argument {text[1]} not valid", EXIT_FAIL)
    return anchh, anchv


def get_backup_path(fp):
    parts = os.path.splitext(fp)
    for i in range(1, 100):
        num = random.randint(1, 2**16)
        numenc = str(num).encode()
        h = hashlib.sha256(numenc).hexdigest()[:5]
        backupfp = parts[0] + "_backup_" + h + parts[1]
        if not os.path.isfile(backupfp):
            return backupfp
    printMsgAndExit(
        "ERROR: Cannot get a non-existent name for backup file in a reasonable amount of trials"
    )


# The core of the software
def run(args):
    # Build args.text as list if not defined, otherwise crash/we need to make a test every time
    if not args.text:
        args.text = list()

    if not args.watermark:
        args.watermark = list()

    if not args.booleans:
        args.booleans = list()

    # If the --paper option is not specified, we pass "fitpaper" to pdfpages by default
    if (args.paper is None) and ("landscape" not in args.booleans):
        args.booleans.append("fitpaper")

    # debug-no-compile implies debug
    if args.debug_no_compile or args.debug_folder != "temp":
        args.debug = True

    # ****Process options got from command line****

    # 1. Check PDF input files
    input_pdf_files = []
    input_img_files = []

    # -Process directory, walk through every file in it-
    for indir in args.input_dirs:
        if not os.path.isdir(indir):
            printMsgAndExit(f"ERROR: {indir} is not a directory ", EXIT_FAIL)
        for root, dirs, files in os.walk(indir):
            if (root != indir) and (not args.recursive):
                print(f"root={root} and not recursive, skipping")
                continue
            if args.natural_sorting:
                files = natsorted(files)
            else:
                files.sort()
            print("Files after sorting: ")
            print("\n".join(files))
            for file in files:
                filefp = os.path.join(root, file)
                args.input_files.append(filefp)

    # -Process files-
    for infile in args.input_files:
        if not os.path.isfile(infile):
            printMsgAndExit(f"ERROR: Input file {infile} doesn't exist.", EXIT_FAIL)

        ftype = getFileType(infile)

        infileabs = os.path.abspath(infile)

        if ftype == "pdf":
            input_pdf_files.append(infileabs)
            if args.verbose == True:
                print(f"Adding PDF file: '{infile}'")
        elif ftype == "img":
            input_img_files.append(infileabs)
            if args.verbose == True:
                print(f"Adding image file: '{infile}'")
        else:
            if args.skip_unreco_type:
                print(
                    f"WARNING: Skipping unrecognized file type '{ftype}' for '{infile}'"
                )
                continue
            else:
                printMsgAndExit(
                    f"ERROR: Unrecognized file type '{ftype}' for '{infile}'", EXIT_FAIL
                )

    # 2. Check output file
    if not args.replace_input:
        if args.output == None:
            # If no output file was specified, append "args.out_suffix" to the first input file name
            args.output = (
                os.path.splitext(input_pdf_files[0])[0] + args.out_suffix + ".pdf"
            )
        # Take absolute path to make shutil.copy happy
        args.output = os.path.abspath(args.output)
        # Check that output pdf file doesn't exist yet
        if os.path.isfile(args.output):
            if args.overwrite:
                os.remove(args.output)
            else:
                printMsgAndExit(
                    f"FATAL ERROR: File {args.output} already exists. "
                    "Use --overwrite if you want to overwrite it",
                    EXIT_FAIL,
                )

    # 3. Create temporary directory
    temp_dir = createTempDir(args.debug, args.debug_folder)

    # 4. Pre-compiling

    # -Latex input and pdf output file
    # Relative path -> We are already in the temporary directory
    latex_tex_fp = "latex_file.tex"
    latex_pdf_fp = "latex_file.pdf"
    # Check for existence of the LaTeX file and remove it. Useful in debug mode.
    if os.path.isfile(latex_tex_fp):
        os.remove(latex_tex_fp)

    # -In landscape mode, rows and columns number for nup are swapped
    if "landscape" in args.booleans:
        args.nup[0], args.nup[1] = args.nup[1], args.nup[0]

    # -Process offset and delta strings
    args.offset[0] = args.offset[0].replace(r"_", r"-")
    args.offset[1] = args.offset[1].replace(r"_", r"-")
    args.delta[0] = args.delta[0].replace(r"_", r"-")
    args.delta[1] = args.delta[1].replace(r"_", r"-")

    # 5. Create LaTeX script
    latex_script = r"% !TeX TS-program = " + args.latex_engine + "\n"
    latex_script += r"\documentclass"
    if args.paper is not None:
        latex_script += "[" + args.paper + "]"
    latex_script += (
        "{article}\n"
        "\\usepackage[utf8x]{inputenc}\n"
        "%To avoid problems with pdf filenames. N.B. MUST BE BEFORE PDFPAGES TO AVOID BUG!\n"
        "\\usepackage[multidot, extendedchars]{grffile}\n"
        "\\usepackage{pdfpages, lastpage, fancyhdr, geometry, calc, graphicx, transparent}\n"
        "\\usepackage{xparse,letltxmacro}\n"
        "\\usepackage{changepage} %Implement check to get if current page is odd or even\n"
    )

    # Suppress metadata
    # see: https://mailman.ntg.nl/pipermail/ntg-pdftex/2016-March/004071.html
    # see: https://tex.stackexchange.com/questions/95080/making-an-anonymous-pdf-file-using-pdflatex/225790#225790
    # see section 8.2 of pdftex manual: https://ctan.mirror.garr.it/mirrors/ctan/systems/doc/pdftex/manual/pdftex-a.pdf
    if args.latex_engine == "pdflatex":
        latex_script += """
        \pdfinfo{
           /Author ()
           /Title  ()
           /Subject ()
           /Keywords ()
       }
       \pdfinfoomitdate=1
       \pdftrailerid{} %Remove ID
       \pdfsuppressptexinfo15 %Suppress PTEX.Fullbanner and info of imported PDFs
       """
    else:
       print("WARNING: Using a latex engine different than pdflatex. PDF metadata will be kept.")

    if args.textpos_showboxes:
        latex_script += "\\usepackage[absolute, showboxes]{textpos}\n"
    else:
        latex_script += "\\usepackage[absolute]{textpos}\n"

    latex_script += (
        "\\strictpagecheck\n"
        "\\newcounter{pdfpagenum}\n"
        "% Save shape of the PDF file\n"
        "\\newsavebox{\\mybox}\n"
        "\\newlength{\\pdfwidth}\n"
        "\\newlength{\\pdfheight}\n"
    )

    # Font
    if(args.font):
        if args.latex_engine != "xelatex":
            printMsgAndExit("ERROR: --font option requires --latex-engine xelatex", EXIT_FAIL)
        latex_script += (
            "\\usepackage{fontspec}\n"
            "\\setmainfont{"+args.font+"}"
        )

    # Black magic to have PDF files with commas in their filename work
    # See: https://tex.stackexchange.com/a/372722/74382
    # only for pdflatex
    # xelatex will include only the first page of the PDF
    # if we redefine \includepdf this way
    if args.latex_engine == "pdflatex":
        latex_script += (
            r"% save the original macro" + "\n"
            r"\LetLtxMacro\ORIincludepdf\includepdf" + "\n"
            r"\ExplSyntaxOn" + "\n"
            r"\RenewDocumentCommand{\includepdf}{O{}m}" + "\n"
            r"{" + "\n"
            r"% store the file name as a string" + "\n"
            r"\tl_set:Nx \l_tmpa_tl { \tl_to_str:n { #2 } }" + "\n"
            r"% replace commas (catcode 12) with commas (catcode 11)" + "\n"
            r"\tl_replace_all:Nnf \l_tmpa_tl { , } { \char_generate:nn { `, } { 11 } }"
            + "\n"
            r"\ORIincludepdf[#1]{\l_tmpa_tl}" + "\n"
            r"}" + "\n"
            r"\cs_generate_variant:Nn \tl_replace_all:Nnn { Nnf }" + "\n"
            r"\ExplSyntaxOff" + "\n"
        )

    # Generate variables to hold the text boxes and the text boxes' widths
    # for i in range(len(args.text)):
    #    latex_script += "\\newsavebox{\\textbox"+str(i)+"}\n"
    #    latex_script += "\\newlength{\\textbox"+str(i)+"width}\n"
    latex_script += "\\newsavebox{\\textbox}\n"
    latex_script += "\\newlength{\\textboxwidth}\n"

    # Create a fancy pagestyle
    latex_script += "\\fancypagestyle{mystyle}"
    latex_script += (
        "{\n\t\\fancyhf{} % Start with clearing everything in the header and footer"
    )
    latex_script += "\n\t\\renewcommand{\\headrulewidth}{0pt}% No header rule"
    latex_script += "\n\t\\renewcommand{\\footrulewidth}{0pt}% No footer rule\n\t"

    # Process add text
    for texti, text in enumerate(args.text):
        # `text` is in the format [STRING, ANCHOR, WIDTH, HEIGHT]
        st = text[0]
        anchor = text[1]
        width = text[2]
        height = text[3]

        # Process text string
        text_proc = Template(st).substitute(
            day=today.day,
            month=today.month,
            year=today.year,
            page=r"\thepage",
            pages=r"\pageref{LastPage}",
        )
        text_proc = text_proc.replace(r" ", r"~")  # otherwise spaces will get ignored
        text_proc = text_proc.replace(r"_", r"\_")  # otherwise error occurs

        # Position template
        anchh, anchv = anchor2coords(anchor)

        # The default position of textpos is the top left page corner.
        # In landscape mode this become the top right corner (rotation of 90 degress clockwise)
        # But we want the units always expressed related to the top left corner. So we convert them.
        if "landscape" in args.booleans:
            width, height = height, width  # swap them
            text_proc = "\\rotatebox{90}{" + text_proc + "}"

        # Get width of the text box
        latex_script += "\\savebox{\\textbox}{" + text_proc + "}\n"
        latex_script += "\t\\settowidth{\\textboxwidth}{\\usebox{\\textbox}}\n"

        # Use textpos package: https://ctan.mirror.garr.it/mirrors/ctan/macros/latex/contrib/textpos/textpos.pdf
        # textblock wants the position of the upper left corner of the text box.
        # Starred version requires positions expressed as length (not relative to TPHorizModule)
        latex_script += "\t\\begin{textblock*}{\\textboxwidth}"
        latex_script += f"[{anchh},{anchv}]"
        latex_script += (
            "(" + str(width) + "\\paperwidth, " + str(height) + "\\paperheight)\n"
        )
        latex_script += "\t\t\\raggedright " + text_proc + "\n"
        latex_script += "\t\\end{textblock*}\n"

    # Process watermarks
    # metavar=('file', 'anchor', 'hpos', 'vpos', 'scale', 'alpha')
    for i, wm in enumerate(args.watermark):
        file = os.path.normpath(os.path.join(previous_cwd, wm[0]))
        file = linuxize(file)
        anchor = wm[1]
        hpos = wm[2]
        vpos = wm[3]
        scale = wm[4]
        alpha = wm[5]
        if not os.path.isfile(file):
            printMsgAndExit(f"ERROR: File {file} does not exist", EXIT_FAIL)
        anchh, anchv = anchor2coords(anchor)
        # Get width of the text box
        latex_script += (
            "\t\\savebox{\\textbox}{\\includegraphics[width="
            + scale
            + "\\paperwidth]{"
            + file
            + "}}\n"
        )
        latex_script += "\t\\settowidth{\\textboxwidth}{\\usebox{\\textbox}}\n"
        # Insert image
        latex_script += "\t\\begin{textblock*}{\\textboxwidth}"
        latex_script += f"[{anchh},{anchv}]"
        latex_script += (
            "(" + str(hpos) + "\\paperwidth, " + str(vpos) + "\\paperheight)\n"
        )
        latex_script += "\t\t{\\transparent{" + alpha + "}\n"
        latex_script += (
            "\t\t\t\\includegraphics[width=" + scale + "\\paperwidth]{" + file + "}\n"
        )
        latex_script += "\t\t}"
        latex_script += "\t\\end{textblock*}\n"

    latex_script += "} %end of fancypagestyle\n"
    # End of fancy page style

    # BEGIN DOCUMENT
    latex_script += "\\begin{document}\n"
    if args.blackbg:
        latex_script += "\\pagecolor{black}\n"
    latex_script += "\t\\thispagestyle{empty}\n"

    # Insert input image files in latex script
    for filenum in range(len(input_img_files)):
        f = input_img_files[filenum]
        latex_script += (
            "\\begin{figure}"
            "\n\\includegraphics[width=\\textwidth]{" + linuxize(f) + "}"
            "\n\\end{figure}"
        )

    # Initialize arg.pages as list
    pagesl = [args.extract_pages] * len(input_pdf_files)
    rotmap = dict()
    page_count = None

    # Rotate pages
    # In this case, we add one page at a time
    if args.rotate_pages:
        if len(input_pdf_files) > 1:
            printMsgAndExit(
                "Page rotation is only supported with one input PDF file", EXIT_FAIL
            )
        rotmap = {
            str(page): int(angle)
            for pair in args.rotate_pages.split(";")
            for page, angle in [pair.split("=")]
        }
        page_count = getPageCount(input_pdf_files[0])
        pagesl = list(range(1, page_count + 1))
        pagesl = [str(x) for x in pagesl]
        input_pdf_files = [input_pdf_files[0]] * len(pagesl)

    # -Get size of the first page of the input pdf. Define \pdfwidth and \pdfheight
    if len(input_pdf_files) > 0:
        latex_script += (
            "%Get dimensions of pdf page"
            "\n\t\\savebox{\\mybox}{\\includegraphics{\\detokenize{"
            + linuxize(input_pdf_files[0])
            + "}}}"
            "\n\t\\settowidth{\\pdfwidth}{\\usebox{\\mybox}}"
            "\n\t\\settoheight{\\pdfheight}{\\usebox{\\mybox}} \n\t"
        )

    # Insert input PDF files in latex script
    for filenum, f in enumerate(input_pdf_files):
        # Update page_count only if we need too
        if (filenum == 0 and page_count is None) or (f != input_pdf_files[filenum - 1]):
            page_count = getPageCount(f)

        # Get pages parameter for this file
        pages = pagesl[filenum]

        # Swap pages
        if args.swap_pages:
            # Make a list of tuples. Each tuple contains the page pair to swap
            pairs = [pair.split(",") for pair in args.swap_pages.split(";")]
            pairs = [(int(a), int(b)) for a, b in pairs]
            # Generate a continuum list of items in the pair
            flat = [int(item) for t in pairs for item in t]
            # Make sure there are no repetitions
            assert len(set(flat)) == len(flat)
            assert min(flat) >= 1
            assert max(flat) <= page_count
            # Generate page sequence
            pagseq = list(range(min(flat), max(flat) + 1))
            # Actual swap
            for a, b in pairs:
                # Get indices
                aix = a - min(flat)
                bix = b - min(flat)
                pagseq[aix], pagseq[bix] = pagseq[bix], pagseq[aix]
            # Build pages argument
            pages = ""
            if min(flat) != 1:
                pages += "1-" + str(min(flat) - 1) + ","
            pages += ",".join([str(x) for x in pagseq])
            if max(flat) != page_count:
                pages += f",{max(flat)+1}-"

        # Delete pages
        if args.delete_pages:
            # Build list of pages to include
            pagesl = list(range(1, page_count + 1))
            for page_to_delete in args.delete_pages.split(","):
                page_to_delete = int(page_to_delete)
                pagesl.remove(page_to_delete)
            # Build pages string
            pages = ""
            pagesl.sort()
            page_start = pagesl[0]
            for ix, page in enumerate(pagesl):
                if ix == 0:
                    continue
                elif pagesl[ix - 1] == page - 1:
                    continue
                else:
                    pages += str(page_start) + "-" + str(pagesl[ix - 1]) + ","
                    page_start = page
            pages += str(page_start) + "-"

        # White page
        if args.add_white_pages:
            pagesl = list(range(1, page_count + 1))
            pages = ""
            for page in pagesl:
                pages += str(page) + ",{},"
            pages = pages[:-1]

        # Include the pdf
        include_pdf_str = "%Importing the pdf \n \t"
        include_pdf_str = "\\includepdf[keepaspectratio, pages={" + str(pages) + "}"

        if args.nup != [1, 1]:
            include_pdf_str += ",nup=" + str(args.nup[1]) + "x" + str(args.nup[0])

        if args.delta != ["0", "0"]:
            include_pdf_str += ",delta=" + arrayToString(args.delta)

        if args.offset != ["0", "0"]:
            include_pdf_str += ",offset=" + arrayToString(args.offset)

        if args.trim != ["0", "0", "0", "0"]:
            args.trim = [float(x) for x in args.trim]
            # Reverse trim is used with "split pages". `args.trim` contains the left page, reverse_trim contains the right page
            # if(args.split_pages):
            #    trim = [ 1-args.trim[2] , 1-args.trim[3] , 1-args.trim[0] , 1-args.trim[1] ]
            include_pdf_str += ",trim={" + trimArrayToStr(args.trim) + "}"

        if args.scale != 0:
            include_pdf_str += ",noautoscale, scale=" + str(args.scale)

        if args.width != 0:
            include_pdf_str += ",width=" + str(args.width[0]) + r"\paperwidth"

        if args.height != 0:
            include_pdf_str += ",height=" + str(args.height[0]) + r"\paperheight"

        include_pdf_str += r",pagecommand=\thispagestyle{mystyle}"

        # Boolean parameters for pdfpages package
        for boolpar in args.booleans:
            include_pdf_str += r"," + boolpar

        # Custom arguments for pdfpages package
        if args.custom:
            include_pdf_str += r"," + args.custom

        # Rotation Angle
        if pages in rotmap:
            include_pdf_str += r", angle=" + str(rotmap[pages])

        # Finalize with input filename
        include_pdf_str += "]{" + linuxize(f) + "} \n\t"
        # DO NOT PUT SPACES IN FILENAMES. THE FILENAME IS GET AS IT, VERY LITERALLY

        # Add include_pdf_str to latex_script
        latex_script += include_pdf_str

    # END OF FOR LOOP FOR MULTIPLE INPUT FILES

    # Post-include pdf
    latex_script += r"\end{document}"

    # Write latex file
    with open(latex_tex_fp, "w", encoding="utf8") as fh:
        fh.write(latex_script)

    # Compile
    if not args.debug_no_compile:
        for i in range(needed_comp_rounds):
            if args.verbose:
                print(
                    "Compilation round: " + str(i + 1) + "/" + str(needed_comp_rounds)
                )
            # Python 3.3 and higher support subprocess.DEVNULL to suppress output.
            # See (http://stackoverflow.com/questions/699325/suppress-output-in-python-calls-to-executables)
            latex_return = subprocess.run(
                [args.latex_engine, "--interaction=batchmode", linuxize(latex_tex_fp)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # Check if compilation was unsuccessful
            if (
                latex_return.returncode != 0
                or not os.path.isfile("latex_file.pdf")
                or os.path.getsize("latex_file.pdf") == 0
            ):
                if args.debug:
                    # We are currently into the temporary folder
                    zip_file = zipfile.ZipFile("report.zip", "w")
                    zip_file.write("latex_file.tex")
                    if os.path.isfile("latex_file.log"):
                        zip_file.write("latex_file.log")
                    zip_file.close()
                    printMsgAndExit(
                        "Latex failed to compile the file. Debug report was generated",
                        EXIT_FAIL,
                    )
                else:
                    printMsgAndExit(
                        "Latex failed to compile the file. "
                        "Please run again with --debug option, then report at "
                        "https://github.com/raffaem/pdftools/issues attaching ./temp/report.gz",
                        EXIT_FAIL,
                    )
        # ** End of all compilation rounds (for loop) **

        if args.replace_input:
            # Overwrite input file
            infp = input_pdf_files[0]
            backupfp = get_backup_path(infp)
            # Move input into backup
            shutil.move(infp, backupfp)
            # Move output into input
            shutil.move(latex_pdf_fp, infp)
            # Remove input
            os.unlink(backupfp)
        else:
            # Copy resulting pdf file from temporary folder to output directory
            shutil.copyfile(latex_pdf_fp, args.output)

    # We must change the cwd because the temporary folder will be deleted at the end of this function
    os.chdir(previous_cwd)

    # Cleanup temporary directory
    if not args.debug:
        shutil.rmtree(temp_dir)


def get_parser():
    # Get command line options
    # This formatter class prints default values in help
    # See: https://stackoverflow.com/questions/12151306/argparse-way-to-include-default-values-in-help
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Display version information
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    # LaTeX engine to use
    parser.add_argument(
        "--latex-engine",
        action="store",
        choices=["pdflatex","xelatex"],
        default="pdflatex",
        help="LaTeX engine to use. Defaults to pdflatex."
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "-if",
        "--input-file",
        action="append",
        default=[],
        dest="input_files",
        help="Input pdf file. Use this flag again to merge multiple pdf files into one.",
    )
    input_group.add_argument(
        "-id",
        "--input-dir",
        action="append",
        default=[],
        dest="input_dirs",
        help="Input a directory. All pdf files inside it will be merged together, sorted in alphabetical filename order.",
    )
    input_group.add_argument(
        "-rd",
        "--recursive-dir",
        action="store_true",
        default=False,
        dest="recursive",
        help="Process the PDFs inside a dir recursively.",
    )

    # A mutually exclusive group to specify the output file name OR a suffix to append to the first input file name
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("-o", "--output", help="Output filename")
    output_group.add_argument(
        "--out-suffix",
        help="Suffix to add to the first input filename to obtain the output filename",
        default="_pdfsak",
    )
    output_group.add_argument(
        "--replace-input",
        action="store_true",
        default=False,
        help="Replace first input PDF file with output PDF file.",
    )

    # Vector parameters
    parser.add_argument(
        "--paper",
        type=str,
        default=None,
        metavar=("PAPER_TYPE"),
        help="Specify output paper size. "
        "Can be: a4paper, letterpaper, a5paper, b5paper, executivepaper, legalpaper. "
        "The default is to use the same size as the input PDF",
    )

    # parser.add_argument('--fitpaper', action='append_const', const='fitpaper', dest='booleans', help=u'Adjusts the paper size to the one of the inserted document')

    parser.add_argument(
        "--scale",
        nargs=1,
        type=float,
        default=0,
        metavar=("SCALE_FACTOR"),
        help="Scales the image by the desired scale factor. "
        "E.g, 0.5 to reduce by half, or 2 to double. 0 means auto-scaling (default).",
    )
    parser.add_argument(
        "--width",
        nargs=1,
        type=float,
        default=0,
        metavar=("WIDTH"),
        help="Width of 1 input page (take care of this in case of n-upping) relative to output page width.",
    )
    parser.add_argument(
        "--height",
        nargs=1,
        type=float,
        default=0,
        metavar=("HEIGHT"),
        help="Height of 1 input page (take care of this in case of n-upping) relative to output page height.",
    )
    parser.add_argument(
        "--nup",
        nargs=2,
        type=int,
        default=[1, 1],
        metavar=("ROWS", "COLS"),
        help="N-up pages, follow with number of rows and columns",
    )

    parser.add_argument(
        "--offset",
        nargs=2,
        type=str,
        default=["0", "0"],
        metavar=("RIGHT", "TOP"),
        help="The inserted logical pages are being centered on the sheet of paper by default. "
        "Use this option, which takes two arguments, to displace them. "
        "E.g. --offset=10mm 14mm means that the logical pages are displaced by 10 mm in horizontal direction and by 14 mm in vertical direction. "
        "In oneside documents, positive values shift the pages to the right and to the top margin, respectively. "
        "In ‘twoside’ documents, positive values shift the pages to the outer and to the top margin, respectively.",
    )

    parser.add_argument(
        "--trim",
        nargs=4,
        type=str,
        default=["0", "0", "0", "0"],
        metavar=("Left", "Bottom", "Right", "Top"),
        help="Crop pdf page. "
        "You can use the following variables: \pdfwidth is the width of a pdf page, \pdfheight is the height of a pdf page. "
        "Both are calculated on the first page of the pdf. "
        'So for example "--trim 0 .5\pdfwidth .2\pdfheight 0" will trim the pages half from the right and 20 per cent from the bottom',
    )

    parser.add_argument(
        "--delta",
        nargs=2,
        type=str,
        default=["0", "0"],
        metavar=("X", "Y"),
        help="By default logical pages are being arranged side by side. "
        "To put some space between them, use the delta option, which takes two arguments.",
    )

    parser.add_argument("--custom", help="Custom pdfpages options")

    parser.add_argument(
        "--watermark",
        nargs=6,
        type=str,
        action="append",
        metavar=("file", "anchor", "hpos", "vpos", "scale", "alpha"),
        help="Add watermark image.",
    )

    parser.add_argument(
        "-t",
        "--text",
        nargs=4,
        type=str,
        action="append",
        metavar=("text_string", "anchor", "hpos", "vpos"),
        help="Add text to pdf file. "
        "'text_string' is the string to add, special variables can be passed, as well as LaTeX font sizes like \Huge. "
        "Pass --text-help for help on how to build this string. "
        "'anchor' sets the side of the text box (the box surrounding the text) where it is anchored (where its position is measured from):"
        "'tl' - top-left corner, "
        "'tm' - middle of the top edge, "
        "'tr' - top-right corner, "
        "'bl' - bottom-left corner, "
        "'bm' - middle of the bottom edge, "
        "'br' - bottom-right corner, "
        "all other parameters are invalid. "
        "'hpos' and 'vpos' are numbers between 0 and 1 that represent how far is 'anchor' from the top left corner of the page.",
    )

    parser.add_argument(
        "--text-help",
        action="store_true",
        help="Print help on how to build a text string for the -t/--text option",
    )

    parser.add_argument(
        "--font",
        action="store",
        help="Font to use for text in the document. This requires --latex-engine xelatex."
    )

    # Boolean parameters NOT for pdfpages
    parser.add_argument(
        "--skip-unrecognized-type",
        dest="skip_unreco_type",
        action="store_true",
        default=False,
        help="Skip unrecognized file types when scanning a directory. Otherwise, thrown an error",
    )
    parser.add_argument(
        "--natural-sorting",
        action="store_true",
        default=False,
        help="When scanning a folder, use natural sorting algorithm to sort the files inside it",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Overwrite output file if it exists already",
    )
    parser.add_argument(
        "--blackbg",
        action="store_true",
        default=False,
        help="Make the background black, for e.g. n-upping dark background slides.",
    )

    # Group to manage how pages are inserted
    pages_group = parser.add_mutually_exclusive_group()
    pages_group.add_argument(
        "--swap-pages",
        default="",
        help="A semi-colon separated list of colon-separated page pairs to swap. "
        'E.g. "1,5;6,9" will swap page 1 with page 5 and page 6 with page 9.',
    )
    pages_group.add_argument(
        "--rotate-pages",
        default="",
        help="A semi-colon separated list of page=angle pairs. "
        "Rotation angle is counterclockwise. "
        'E.g. "1=90;2=180" will rotate 1st page by 90 degress counterclockwise and 2nd page by 180 degrees.',
    )
    pages_group.add_argument(
        "--delete-pages",
        default="",
        help="A semi-colon separated list of pages to delete. ",
    )
    pages_group.add_argument(
        "--add-white-pages",
        action="store_true",
        default=False,
        help="Put a white page after every page.",
    )
    pages_group.add_argument(
        "--extract-pages",
        default="-",
        help="Selects pages to insert. "
        "The argument is a comma separated list, containing page numbers (e.g. 3,5,6,8), ranges of page numbers (e.g. 4-9) or any combination of the previous. "
        "To insert empty pages, use {}. "
        "Page ranges are specified by the following syntax: m-n. This selects all pages from m to n. "
        "Omitting m defaults to the first page; omitting n defaults to the last page of the document. "
        "Another way to select the last page of the document, is to use the keyword last."
        'E.g.: "--extract-pages 3,{},8-11,15" will insert page 3, an empty page, pages from 8 to 11, and page 15. '
        '"--extract-pages=-" will insert all pages of the document, '
        '"--extract-pages=last-1" will insert all pages in reverse order.',
    )

    # Options to simulate Adobe ClearSCan
    parser.add_argument(
        "--clearscan",
        action="store_true",
        default=False,
        help="Simulate Adobe Acrobat ClearScan",
    )
    parser.add_argument(
        "--clearscan-density",
        action="store",
        type=int,
        default=300,
        help="Density with which to convert PDF into bitmap.",
    )
    parser.add_argument(
        "--clearscan-opttolerance",
        action="store",
        type=float,
        default=0.2,
        help="Set the curve optimization tolerance. The default value is 0.2. Larger values allow more consecutive Bezier curve segments to be joined together in a single segment, at the expense of accuracy.",
    )
    parser.add_argument(
        "--clearscan-turnpolicy",
        action="store",
        type=str,
        default="minority",
        help="Specify how to resolve ambiguities in path decomposition. Must be one of black, white, right, left, minority, majority, or random. Default is minority. Turn policies can be abbreviated by an unambiguous prefix, e.g., one can specify min instead of minority.",
    )
    parser.add_argument(
        "--clearscan-alphamax",
        action="store",
        type=float,
        default=1,
        help="set the corner threshold parameter. The default value is 1. The smaller this value, the more sharp corners will be produced. If this parameter is 0, then no smoothing will be performed and the output is a polygon. If this parameter is greater than 4/3, then all corners are suppressed and the output is completely smooth. ",
    )
    parser.add_argument(
        "--clearscan-potrace-debug",
        action="store",
        type=int,
        default=0,
        help=argparse.SUPPRESS,
    )
    # ClearScan mkbitmap passage
    parser.add_argument(
        "--clearscan-skip-mkbitmap",
        action="store_true",
        default=False,
        help="Skip mkbitmap passage",
    )
    parser.add_argument(
        "--clearscan-filter-size",
        action="store",
        type=int,
        default=clearscan_filter_size_default,
        help="Pixel size of high-pass filter to pass to mkbitmap for clearscan. Requires mkbitmap.",
    )
    parser.add_argument(
        "--clearscan-upscaling-factor",
        action="store",
        type=int,
        default=clearscan_upscaling_factor_default,
        help="Upscale the image by this factor using mkbitmap before passing it to potrace. Requires mkbitmap.",
    )
    parser.add_argument(
        "--clearscan-threshold",
        action="store",
        type=float,
        default=clearscan_threshold_default,
        help="Threshold level. Requires mkbitmap.",
    )

    parser.add_argument(
        "--check-all",
        action="store_true",
        default=False,
        help="Check all dependencies (including optional ones)",
    )

    # Boolean parameters TO PASS TO PDFPAGES (AND ONLY FOR PDFPAGES)
    parser.add_argument(
        "--clip",
        action="append_const",
        const="clip",
        dest="booleans",
        help="Used togheter with trim, will actually remove the cropped part from the pdfpage. "
        "If false, the cropped part is present on the physical file, but the pdf reader is instructed to ignore it.",
    )
    parser.add_argument(
        "--rotateoversize",
        action="append_const",
        const="rotateoversize",
        dest="booleans",
        help="Rotate oversized pages. ",
    )
    parser.add_argument(
        "--landscape",
        action="append_const",
        const="landscape",
        dest="booleans",
        help="Output file is in landscape layer instead of portrait.",
    )
    parser.add_argument(
        "--frame",
        action="append_const",
        const="frame",
        dest="booleans",
        help="Put a frame around every logical page.",
    )

    parser.add_argument(
        "--textpos-showboxes",
        action="store_true",
        default=False,
        help="Call textpos package with the showboxes option, putting a frame around every textblock.",
    )

    # -Debug options-
    parser.add_argument(
        "--verbose", action="store_true", default=False, help=argparse.SUPPRESS
    )
    # Create temporary folder in the current working directory instead of system's default path for temporary files
    parser.add_argument(
        "--debug", action="store_true", default=False, help=argparse.SUPPRESS
    )
    # Print the result of parse_args' and exit
    parser.add_argument(
        "--debug-print", action="store_true", default=False, help=argparse.SUPPRESS
    )
    # Don't compile the resulting latex file
    parser.add_argument(
        "--debug-no-compile", action="store_true", default=False, help=argparse.SUPPRESS
    )
    # Specify debug folder
    parser.add_argument(
        "--debug-folder", type=str, default="temp", help=argparse.SUPPRESS
    )

    return parser


def runClearScan(args):
    if not checkImageMagick():
        printMsgAndExit(
            "Error: ClearScan requires ImageMagick, which is not in path. "
            "Please install it: https://imagemagick.org",
            EXIT_FAIL,
        )
    if not checkMKBitmap():
        printMsgAndExit(
            "Error: ClearScan requires mkbitmap, which is not in path. "
            "mkbitmap is distributed as part of the potrace package: http://potrace.sourceforge.net",
            EXIT_FAIL,
        )
    if not checkPotrace():
        printMsgAndExit(
            "Error: ClearScan requires potrace, which is not in path. "
            "Please install it: http://potrace.sourceforge.net",
            EXIT_FAIL,
        )
    if len(args.input_files) != 1:
        printMsgAndExit("Error: ClearScan requires exactly 1 input file", EXIT_FAIL)
    if not args.input_files[0].endswith(".pdf"):
        printMsgAndExit(
            "Error: ClearScan requires that input file ends with .pdf extension",
            EXIT_FAIL,
        )
    if not os.path.isfile(args.input_files[0]):
        printMsgAndExit("Error: Input file does not exist", EXIT_FAIL)
    if not args.output:
        printMsgAndExit("Error: Please specify an output file", EXIT_FAIL)
    if os.path.isfile(args.output):
        printMsgAndExit("Error: Output file already exist", EXIT_FAIL)
    if args.clearscan_skip_mkbitmap:
        if args.clearscan_filter_size != clearscan_filter_size_default:
            printMsgAndExit(
                "Error: --clearscan-skip-mkbitmap incompatible with --clearscan-filter-size",
                EXIT_FAIL,
            )
        if args.clearscan_upscaling_factor != clearscan_upscaling_factor_default:
            printMsgAndExit(
                "Error: --clearscan-skip-mkbitmap incompatible with --clearscan-upscaling-factor",
                EXIT_FAIL,
            )
        if args.clearscan_threshold != clearscan_threshold_default:
            printMsgAndExit(
                "Error: --clearscan-skip-mkbitmap incompatible with --clearscan-threshold",
                EXIT_FAIL,
            )
        print("Warning: Skipping mkbitmap step")

    # Copy input PDF file in temp folder
    fp1 = os.path.realpath(args.input_files[0])
    of = os.path.realpath(args.output)
    # Create temporary directory and chage to it
    # after we got the full path for the input file and output file
    # (which might be relative paths)
    temp_dir = createTempDir(args.debug, args.debug_folder)
    # Copy input file to temporary directory
    fp2 = os.path.join(temp_dir, os.path.basename(fp1))
    shutil.copy(src=fp1, dst=fp2)
    # Get page count of input file
    page_count = getPageCount(fp2)
    print(f"Input pages: {page_count}")
    os.makedirs("./pages", exist_ok=False)
    for page in tqdm(range(0, page_count)):
        # Extract PDF page to BMP
        cmd = [
            "magick",
            "convert",
            "-density",
            str(args.clearscan_density),
            fp2 + f"[{page}]",
        ]
        if args.clearscan_skip_mkbitmap:
            cmd.append(f"{page}.pbm")
        else:
            cmd.append(f"{page}.bmp")
        if args.verbose:
            print(f"Running: {cmd}")
        res = subprocess.run(cmd)
        if res.returncode != 0:
            printMsgAndExit("Error: ImageMagick failed", EXIT_FAIL)
        # Run mkbitmap
        if not args.clearscan_skip_mkbitmap:
            cmd = [
                "mkbitmap",
                "-f",
                str(args.clearscan_filter_size),
                "-s",
                str(args.clearscan_upscaling_factor),
                "-t",
                str(args.clearscan_threshold),
                f"{page}.bmp",
            ]
            if args.verbose:
                print(f"Running: {cmd}")
            res = subprocess.run(cmd)
            if res.returncode != 0:
                printMsgAndExit("Error: mkbitmap failed", EXIT_FAIL)
            # Remove PDF bitmap files
            os.unlink(f"{page}.bmp")
        # Run potrace
        cmd = [
            "potrace",
            "--backend",
            "pdf",
            "-t",
            str(args.clearscan_threshold),
            "--opttolerance",
            str(args.clearscan_opttolerance),
            "--turnpolicy",
            args.clearscan_turnpolicy,
            "--alphamax",
            str(args.clearscan_alphamax),
        ]
        if args.clearscan_potrace_debug != 0:
            cmd.append("--debug")
            cmd.append(str(args.clearscan_potrace_debug))
        cmd.append(f"{page}.pbm")
        cmd += ["--output", f"./pages/{page}.pdf"]
        if args.verbose:
            print(f"Running: {cmd}")
        res = subprocess.run(cmd)
        if res.returncode != 0:
            printMsgAndExit("Error: potrace failed", 1)
        # Remove mkbitmap output file
        os.unlink(f"{page}.pbm")

    # Merge PDF files
    print("Merging back...")
    cmd = ["--natural-sorting", "-id", "./pages", "-o", "merged.pdf"]
    if args.debug:
        cmd.append("--debug")
    p = Process(target=main, args=(cmd,))
    p.start()
    p.join()
    res = p.exitcode
    if res != 0:
        printMsgAndExit("Error: Failed to merge back", EXIT_FAIL)

    shutil.copyfile("./merged.pdf", of)

    # Exit
    printMsgAndExit("Success", 0)


def main(cmdargs=None, args=None):

    global temp_dir
    global debug
    global previous_cwd

    if cmdargs is None:
        cmdargs = sys.argv[1:]

    # Parse arguments
    if args is None:
        parser = get_parser()
        args = parser.parse_args(cmdargs)

    # If no options are passed, display help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        printMsgAndExit(None, EXIT_SUCCESS)

    debug = args.debug

    if args.check_all:
        checkAllCLI(args)

    if args.text_help:
        printTextHelp()
        printMsgAndExit(None, EXIT_SUCCESS)

    # Implement ClearScan and exit
    if args.clearscan:
        runClearScan(args)

    run(args)
    printMsgAndExit(None, 0)


if __name__ == "__main__":
    main()

