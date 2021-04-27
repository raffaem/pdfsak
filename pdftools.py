#!/usr/bin/env python3
# coding=utf8

# Copyright (c) 2021 Raffaele Mancuso

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

# To restore cwd at the end, otherwise we get a exception
previous_cwd = os.getcwd()
today = datetime.datetime.now()
# -Calculate needed rounds of compilation
needed_comp_rounds = 2
pdftk = True  # will be set to false if not found


def trimArrayToStr(timarr):
    #trim_str = "{"
    trim_str = ""
    trim_str += f"{timarr[0]:.2}" + "\\pdfwidth{} "
    trim_str += f"{timarr[1]:.2}" + "\\pdfheight{} "
    trim_str += f"{timarr[2]:.2}" + "\\pdfwidth{} "
    trim_str += f"{timarr[3]:.2}" + "\\pdfheight{} "
    #trim_str += "}"
    trim_str = re.sub(r"1.0\\pdf(width|height){}", "0.0", trim_str)
    return trim_str

# Return 'pdf' if it's a pdf file, 'img' if it's an image file, or 'unknown' if it is not recognized
def getFileType(filepath):
    curr_ext = os.path.splitext(filepath)[1]
    if curr_ext=='.pdf':
        return 'pdf'
    elif curr_ext=='.jpg' or curr_ext=='.jpeg' or curr_ext=='.gif' or curr_ext=='.png' or curr_ext=='.bmp':
        return 'img'
    else:
        return 'unknown'

# Natural sorting. See http://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def repairPdfFile(filepath):
    repaired_path = os.path.splitext(filepath)[0] + "_repaired.pdf"
    cmd = "pdftk \""+args.input[i]+"\" output \"" + repaired_path + "\""
    print("Running: \""+cmd+"\"")
    subprocess.call(cmd)
    return repaired_path

# Reads a list of pages to extract from a file. Used with the --extract-pages option
def readListFromFile(filename):
    filename = os.path.join(previous_cwd,filename)
    if not os.path.isfile(filename):
        exit_with_code("List file \"" + filename+"\" not found",1)
    f = open(filename,'r')
    l = list()
    for line in f:
        slt_list = line.split(' ')
        for slt in slt_list:
            l.append(int(slt))
    return l

# Check the presence of a single Latex package
def checkLatexPackageCLI(pkgname):
    res = checkLatexPackage(pkgname)
    if (res == False):
        print("Checking "+pkgname+": MISSING")
    else:
        print("Checking "+pkgname+": found")

def checkLatexPackage(pkgname):
    latex_file_name = "check.tex"
    latex_script = "\\documentclass{article} \
    \n\\usepackage{"+pkgname+"} \
    \n\\begin{document}\
    \nHello\
    \n\\end{document}"
    # Write latex file
    latex_file = open(latex_file_name,"w")
    latex_file.write(latex_script)
    latex_file.close()
    # Compile latex file
    latex_return = subprocess.call( ["pdflatex","--interaction=batchmode",""+latex_file_name] , stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    removeFile("check.tex")
    removeFile("check.pdf")
    removeFile("check.aux")
    removeFile("check.log")
    if latex_return != 0:
        return False
    return True

# Check that the current Latex installation has all the required packages
def checkLatexInstallation():
    checkLatexPackageCLI("pdfpages")
    checkLatexPackageCLI("lastpage")
    checkLatexPackageCLI("grffile")
    checkLatexPackageCLI("forloop")
    checkLatexPackageCLI("fancyhdr")
    checkLatexPackageCLI("textpos")
    checkLatexPackageCLI("changepage")
    checkLatexPackageCLI("graphicx")
    checkLatexPackageCLI("THIS_PACKAGE_DOES_NOT_EXIST")

def removeFile(filename):
    # see: https://stackoverflow.com/questions/10840533/most-pythonic-way-to-delete-a-file-which-may-not-exist
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

# Open a file with the OS default application
# Credit: http://stackoverflow.com/questions/434597/open-document-with-default-application-in-python
def openFile(filepath):
    if sys.platform.startswith('darwin'):
        subprocess.call(('open', filepath))
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        filepath = filepath.replace('"', '')
        subprocess.call( ["xdg-open", filepath] )

def exit_with_code(msg, code):
    # Avoid a permission error exception caused by the fact Python wants to delete the temporary folder
    os.chdir(previous_cwd)
    if msg != "":
        print(msg)
    exit(code)

# Convert an array into a string
# Used to convert command line passed arrays, like "delta", "offset" options
def arrayToString(arr, ldelim = "", rdelim=""):
    ostr = ""
    for i in range(0, len(arr)):
        ostr += ldelim + str(arr[i]) + rdelim + " "
    return ostr

def linuxize(str):
    return str.replace("\\","/")

def printTextHelp():
    # text_proc = Template(text[0]).substitute(day=today.day, month=today.month, year=today.year, page=r'\thepage', pages=r'\pageref{LastPage}', filename=file_basename)
    print("Prepend these variables with a $ sign (e.g. $day). \
        Notice that on bash the $ sign must be escape (\\$): \
        \nday = day of today \
        \nmonth = today month \
        \nyear = today year \
        \npage = current page \
        \npages = total number of pages \
        \nfilename = input pdf filename (without path and without extension} ")

# The core of the software
def run(args):
    pre_include_pdf = ""
    post_include_pdf = ""

    if(args.check_latex):
        checkLatexInstallation()
        exit_with_code("Exiting",1)
    if(args.debug_print):
        print(args)
        exit_with_code("debug mode exit", 1)

    # debug-no-compile implies debug
    if args.debug_no_compile or args.debug_folder != 'temp':
        args.debug = True

    if(args.repair and pdftk==False):
        exit_with_code("ERROR: You need pdftk to repair files")

    # ****Process options got from command line****

    # 1. Check PDF input files
    input_pdf_files = []
    input_img_files = []

    # -Process directory, walk through every file in it-
    for indir in args.input_dirs:
        if not os.path.isdir(indir):
            exit_with_code(f"ERROR: {indir} is not a directory ", 1)
        for root, dirs, files in os.walk(indir):
            if args.natural_sorting:
                print("Using natural sorting algorithm...")
                files.sort(key=natural_keys)
            else:
                files.sort()
            for file in files:
                filefp = os.path.join(root, file)
                args.input_files.append(filefp)


    # -Process files-
    for infile in args.input_files:
        if not os.path.isfile(infile):
            exit_with_code(f"ERROR: Input file {infile} doesn't exist.", 1)

        type = getFileType(infile)
        if type=='pdf' and args.repair:
            infile = repairPdfFile(infile)

        infileabs = os.path.abspath(infile)

        if type=='pdf':
            input_pdf_files.append(infileabs)
            if args.verbose == True:
                print(f"Adding PDF file: '{infile}'")
        elif type=='img':
            input_img_files.append(infileabs)
            if args.verbose == True:
                print(f"Adding image file: '{infile}'")
        else:
            exit_with_code(f"ERROR: unrecognized file type for '{infile}'", 1)


    # 2. Check output file
    # If no output file was specified, append "args.out_suffix" to the first input file name
    if(args.output==None):
        args.output = os.path.splitext(input_pdf_files[0])[0] + args.out_suffix + ".pdf"
    args.output = os.path.abspath(args.output) #To make shutil.copy happy
    if(os.path.isfile(args.output)==True): #Check that output pdf file doesn't exist yet
        if args.overwrite:
            os.remove(args.output)
        else:
            exit_with_code("FATAL ERROR: File \""+args.output+"\" already exists. Use --overwrite if you want to overwrite it", 1)

    # 3. Create temporary directory
    temp_dir = ''
    def_temp_dir = tempfile.TemporaryDirectory(prefix='pdftools') #avoid out of scope
    # If NOT in debug, temporary directory is created in system temporary folder
    if not args.debug:
        temp_dir = def_temp_dir.name
    # If in debug mode, temporary directory is created in current working directory
    else:
        temp_dir = os.path.join(os.getcwd(), args.debug_folder)
        if not os.path.isdir(temp_dir):
            os.mkdir(temp_dir)
    os.chdir(temp_dir) #Change working directory to the temp folder. In this way, latex temporary files are created there

    # 4. ******* Pre-compiling **********

    # -Latex input and pdf output file
    latex_file_name = "latex_file.tex" #Relative path
    latex_pdf_name = os.path.join(temp_dir,"latex_file.pdf")
    if(os.path.isfile(latex_file_name)): #Check for existence of the LaTeX file and remove it. Useful in debug mode.
        os.remove(latex_file_name)

    # -In landscape mode, rows and columns number for nup are swapped
    if 'landscape' in args.booleans:
        args.nup[0], args.nup[1] = args.nup[1], args.nup[0]

    # -Process offset and delta strings
    args.offset[0] = args.offset[0].replace(r'_',r'-')
    args.offset[1] = args.offset[1].replace(r'_',r'-')
    args.delta[0] = args.delta[0].replace(r'_',r'-')
    args.delta[1] = args.delta[1].replace(r'_',r'-')

    # -Get size of the first page of the input pdf. Define \pdfwidth and \pdfheight
    pre_include_pdf += "%Get dimensions of pdf page" \
    "\n\t\\savebox{\\mybox}{\\includegraphics{latex_pdf_filename}}" \
    "\n\t\\settowidth{\\pdfwidth}{\\usebox{\\mybox}}" \
    "\n\t\\settoheight{\\pdfheight}{\\usebox{\\mybox}} \n\t"

    # -Loop to include pages one at a time. Use 'latex_pdf_filename' variable
    if(args.white_page or args.split_pages):
        #-Insert a white page after every pdf page
        if(args.white_page):
            args.pages = r"{\theit,{}}"
        if(args.split_pages):
            args.pages = r"{\theit}"

        pre_include_pdf += "%Loop adding one single page at a time"\
        "\n\t\\newcounter{it}"\
        "\n\t\\forloop{it}{1}{\\value{it} < \\numexpr \\thepdfpagenum+1} {\n\t"
        post_include_pdf += "} \n"

    # -Keep last page even
    if(args.last_page_even):
        post_include_pdf += "\\clearpage"\
        "\n\t\\checkoddpage"\
        "\n\t\\ifoddpage"\
        "\n\t\\else"\
        "\n\t\\hbox{}"\
        "\n\t\\newpage"\
        "\n\t\\fi\n\t"

    # ********** 5. Create latex script **********
    latex_script = r"\documentclass"
    if(args.paper is not None):
        latex_script += '[' + args.paper + ']'
    latex_script += "{article}"\
    "\n\\usepackage[utf8x]{inputenc}" \
    "\n\\usepackage{grffile} %To avoid problems with pdf filenames. N.B. MUST BE BEFORE PDFPAGES TO AVOID BUG!"\
    "\n\\usepackage{pdfpages, lastpage, fancyhdr, forloop, geometry, calc, graphicx}"\
    "\n\\usepackage[absolute]{textpos}"\
    "\n\\usepackage{changepage} %Implement check to get if current page is odd or even"\
    "\n\\strictpagecheck"\
    "\n\\newcounter{pdfpagenum}"\
    "\n\\newsavebox{\\mybox}"\
    "\n\\newlength{\\pdfwidth}"\
    "\n\\newlength{\\pdfheight}\n"

    # Generate variables to hold the text boxes and the text boxes' widths
    #for i in range(len(args.text)):
    #    latex_script += "\\newsavebox{\\textbox"+str(i)+"}\n"
    #    latex_script += "\\newlength{\\textbox"+str(i)+"width}\n"
    latex_script += "\\newsavebox{\\textbox}\n"
    latex_script += "\\newlength{\\textboxwidth}\n"

    # File loop
    for filenum in range(len(input_pdf_files)):

        file_basename = os.path.basename(input_pdf_files[filenum])

        # Create a fancy pagestyle for each input files
        latex_script += "\\fancypagestyle{file""" + str(filenum) + "}"
        latex_script += "{\n\t\\fancyhf{} % Start with clearing everything in the header and footer"
        latex_script += "\n\t\\renewcommand{\\headrulewidth}{0pt}% No header rule"
        latex_script += "\n\t\\renewcommand{\\footrulewidth}{0pt}% No footer rule\n\t"

        # Process add text
        for texti, text in enumerate(args.text):

            # Process text string
            text_proc = Template(text[0]).substitute(day=today.day, month=today.month, year=today.year, page=r'\thepage', pages=r'\pageref{LastPage}', filename=file_basename)
            text_proc = text_proc.replace(r' ',r'~') #otherwise spaces will get ignored
            text_proc = text_proc.replace(r'_',r'\_') #otherwise error occurs

            # Position template
            if text[1] == "tl":
                anchh, anchv = 0, 0
            elif text[1] == "tr":
                anchh, anchv = 1, 0
            elif text[1] == "bl":
                anchh, anchv = 0, 1
            elif text[1] == "br":
                anchh, anchv = 1, 1
            else:
                print(f"Argument {text[1]} not valid")

            # The default position of textpos is the top left page corner.
            # In landscape mode this become the top right corner (rotation of 90 degress clockwise)
            # But we want the units always expressed related to the top left corner. So we convert them.
            if 'landscape' in args.booleans:
                text[2], text[3] = text[3], text[2] #swap them
                text_proc = "\\rotatebox{90}{"+text_proc+"}"

            # Get the size of the text box
            #latex_script += "\\savebox{\\textbox"+str(texti)+"}{"+text_proc+"}\n\t"
            #latex_script += "\\settowidth{\\textbox"+str(texti)+"width}{\\usebox{\\textbox"+str(texti)+"} }\n\t"
            latex_script += "\\savebox{\\textbox}{"+text_proc+"}\n"
            latex_script += "\t\\settowidth{\\textboxwidth}{\\usebox{\\textbox} }\n"

            # Use textpos package: https://ctan.mirror.garr.it/mirrors/ctan/macros/latex/contrib/textpos/textpos.pdf
            # textblock wants the position of the upper left corner of the text box.
            # Starred version requires positions expressed as length (not relative to TPHorizModule)
            #latex_script += "\\begin{textblock*}{\\textbox"+str(texti)+"width}"
            latex_script += "\t\\begin{textblock*}{\\textboxwidth}"
            latex_script += f"[{anchh},{anchv}]"
            latex_script += "("+str(text[2])+"\\paperwidth, "+str(text[3])+"\\paperheight)\n"
            latex_script += "\t\t\\raggedright "+text_proc+"\n"
            latex_script += "\t\\end{textblock*}\n"

        latex_script += "} %end of fancypagestyle\n"

    latex_script += "\\begin{document}\n\t";

    # Insert input image files in latex script
    for filenum in range(len(input_img_files)):
        f = input_img_files[filenum]
        f = linuxize(f)
        latex_script += "\\begin{figure}"\
        "\n\\includegraphics[width=\\linewidth]{"+f+"}"\
        "\n\\end{figure}"

    # Insert input PDF files in latex script
    for filenum, f in enumerate(input_pdf_files):

        latex_pdf_filename_detokenize = r"\detokenize{"+linuxize(f)+"}"

        pagestyle = "file"+str(filenum)

        # Page numbers are needed on some pre include scripts (e.g. white pages)
        latex_script += "%Get the number of pdf pages"\
        "\n\t\\pdfximage{"""+latex_pdf_filename_detokenize+"}"\
        "\n\t\\setcounter{pdfpagenum}{\\pdflastximagepages}\n\t"

        # Pre-include script (e.g. insert a white page after every logical page).
        # Substitute latex_pdf_filename variable
        latex_script += pre_include_pdf.replace(r"latex_pdf_filename", latex_pdf_filename_detokenize)

        # Include the pdf
        include_pdf_str = "%Importing the pdf \n \t"
        include_pdf_str = "\\includepdf[keepaspectratio, pages=$pages"

        if(args.nup != [1,1]):
            include_pdf_str += ",nup="+str(args.nup[1])+"x"+str(args.nup[0])

        if(args.delta != ['0','0']):
            include_pdf_str += ",delta="+arrayToString(args.delta)

        if(args.offset != ['0','0']):
            include_pdf_str += ",offset="+arrayToString(args.offset)

        if(args.trim != ['0','0','0','0']):
            include_pdf_str += ",trim={$trimarray}" #we use this syntax to allow "split pages"

        if (args.scale != 0):
            include_pdf_str += ",noautoscale, scale="+str(args.scale)
        if (args.width != 0):
            include_pdf_str += ",width="+str(args.width[0])+r"\paperwidth"
        if (args.height != 0):
            include_pdf_str += ",height="+str(args.height[0])+r"\paperheight"
        include_pdf_str += r",pagecommand=\thispagestyle{" + pagestyle + "}"

        # Boolean parameters for pdfpages package
        for boolpar in args.booleans:
            include_pdf_str += r"," + boolpar

        # Custom arguments for pdfpages package
        if args.custom != None and args.custom != "":
            include_pdf_str += r"," + args.custom

        # Finalize with input filename
        include_pdf_str += "]{" + latex_pdf_filename_detokenize + "} \n\t";
        # DO NOT PUT SPACES IN FILENAMES. THE FILENAME IS GET AS IT, VERY LITERALLY

        # Swap pages
        if(args.swap_pages):
            pag_list = list()
            for p in args.pages.split(","):
                pag_list.append(int(p))
            # Find maximum value
            maxv = max(pag_list)
            pages = list()
            for n in range(1,maxv+1): #right limit is excluded
                pages.append(n)

            for p in range(0,len(pag_list),2):
                pages[pag_list[p]-1], pages[pag_list[p+1]-1] = pag_list[p+1], pag_list[p]
            pages.append(maxv+1)
            for p in pages:
                if(p is not pages[0]):
                    args.pages += ","
                args.pages += str(p)
            args.pages+="-"

        # Extract pages
        if(args.extract_pages):
            print("Reading pages to extract from: {}".format(args.extract_pages))
            pag_list = readListFromFile(args.extract_pages)
            pag_list.sort()
            print("Extracting the following pages: {}".format(','.join([str(a) for a in pag_list])))
            for p in pag_list:
                if(p is not pag_list[0]):
                    args.pages += ","
                args.pages += str(p)

        # -Adjust pages syntax
        if(args.pages[0] != "{"): #Avoids to get page={{{{-}}}} when merging multiple pdf files together
            args.pages = "{" + args.pages + "}"

        # Add include_pdf_str to latex_script
        inc_pdf_temp = Template(include_pdf_str)
        # \includegraphics[trim=left bottom right top, clip]{file}

        args.trim = [float(x) for x in args.trim]
        inc_pdf_fin1 = inc_pdf_temp.safe_substitute(trimarray=trimArrayToStr(args.trim), pages=args.pages)
        latex_script += inc_pdf_fin1

        # Split pages
        if(args.split_pages):
            # -Reverse trim is used with "split pages". args.trim contains the left page, reverse_trim contains the right page
            reverse_trim = [ 1-args.trim[2] , 1-args.trim[3] , 1-args.trim[0] , 1-args.trim[1] ]
            latex_script += inc_pdf_temp.safe_substitute(trimarray=trimArrayToStr(reverse_trim), pages=args.pages)

        latex_script += post_include_pdf

    # END OF FOR LOOP FOR MULTIPLE INPUT FILES

    # Post-include pdf
    latex_script += r'\end{document}'

    # Write latex file
    latex_file = open(latex_file_name,"w")
    latex_file.write(latex_script)
    latex_file.close()

    # Compile
    if not args.debug_no_compile:
        for i in range(needed_comp_rounds):
            if(args.verbose):
                print("Compilation round: " + str(i+1) + "/" + str(needed_comp_rounds))
            # Python 3.3 and higher support subprocess.DEVNULL to suppress output.
            # See (http://stackoverflow.com/questions/699325/suppress-output-in-python-calls-to-executables)
            latex_return = subprocess.call( ["pdflatex","--interaction=batchmode",latex_file_name],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if latex_return != 0 or \
               not os.path.isfile('latex_file.pdf') or \
               os.path.getsize('latex_file.pdf')==0:
                if args.debug:
                    # We are currently into the temporary folder
                    zip_file = zipfile.ZipFile('report.zip', 'w')
                    zip_file.write('latex_file.tex')
                    if(os.path.isfile('latex_file.log')):
                        zip_file.write('latex_file.log')
                    zip_file.close()
                    return exit_with_code("Latex failed to compile the file. Debug report was generated", 1)
                else:
                    exit_with_code("Latex failed to compile the file. Please run again with --debug option, then report at https://github.com/raffamaiden/pdftools/issues attaching ./temp/report.gz", 1)
        # ** End of all compilation rounds (for loop) **
        # Copy resulting pdf file from temporary folder to output directory
        shutil.copyfile(latex_pdf_name, args.output)

    # Open output pdf
    if args.open:
        openFile("\""+args.output+"\"")

    # We must change the cwd becuase the temporary folder will be deleted at the end of this function
    os.chdir(previous_cwd)

def main(cmdargs):

    # Check for pdflatex to be in path
    try:
        pdflatex_return = subprocess.call( ['pdflatex','--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        exit_with_code("Pdflatex is not in path. Please install a Latex distribution and make sure pdflatex is in path", 1)

    # Check for pdftk to be in path
    try:
        pdftk_return = subprocess.call( ['pdftk','--version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        #print("Warning: pdftk was not found (only needed if you want to repair pdf files)")
        pdftk=False

    # Get command line options
    # This formatter class prints default values in help
    # See: https://stackoverflow.com/questions/12151306/argparse-way-to-include-default-values-in-help
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-if', '--input-file', action='append', default=[],
    dest='input_files', required=False, help=u'Input pdf file. '\
    'Use this flag again to merge multiple pdf files into one. ' )

    parser.add_argument('-id', '--input-dir', action='append', default=[],
    dest='input_dirs', required=False, help=u'Input a directory. '
    'all pdf files inside it are merged togheter, sorted in alphabetical filename order. ' )

    # A mutually exclusive group to specify the output file name OR a suffix to append to the first input file name
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('-o', '--output', help=u'Output filename')
    output_group.add_argument('--out-suffix', help=u'Suffix to add to the first input filename to obtain the output filename', default='_pdftools')

    #Vector parameters

    parser.add_argument('--paper', type=str, default=None, metavar=('PAPER_TYPE'), help=u'Specify output paper size. Can be: a4paper, letterpaper,'\
        'a5paper, b5paper, executivepaper, legalpaper. The default is to use the same size as the input PDF')
    #parser.add_argument('--fitpaper', action='append_const', const='fitpaper', dest='booleans', help=u'Adjusts the paper size to the one of the inserted document')

    parser.add_argument('--scale', nargs=1, type=float, default=0, metavar=('SCALE_FACTOR'), help=u'Scales the image by the desired scale factor. ' \
        'E.g, 0.5 to reduce by half, or 2 to double. 0 means auto-scaling (default)')
    parser.add_argument('--width', nargs=1, type=float, default=0, metavar=('WIDTH'), help=u'Width of 1 input page (take care of this in case of n-upping) '
        'relative to output page width.')
    parser.add_argument('--height', nargs=1, type=float, default=0, metavar=('HEIGHT'), help=u'Height of 1 input page (take care of this in case of n-upping)' \
        'relative to output page height.')
    parser.add_argument('--nup', nargs=2, type=int,   default=[1,1], metavar=('ROWS', 'COLS'), help=u'Nup pages, follow with number of rows and columns')

    parser.add_argument('--offset', nargs=2, type=str, default=['0','0'], metavar=('RIGHT', 'TOP'), help=u'The inserted logical pages are being centered ' \
        'on the sheet of paper by default. To displace them use the offset option, which argument should be two dimensions. E.g. offset=10mm 14mm means that the logical' \
        'pages are displaced by 10 mm in horizontal direction and by 14 mm in vertical direction. In oneside documents, positive values shift the pages to the right and to' \
        'the top margin, respectively, whereas in ‘twoside’ documents, positive values shift the pages to the outer and to the top margin, respectively.')

    parser.add_argument('--trim', nargs=4, type=str, default=['0','0','0','0'], metavar=('Left', 'Bottom', 'Right', 'Top'), help=u'Crop pdf page. ' \
        'You can use the following variables: \pdfwidth is the width of a pdf page, \pdfheight is the height of a pdf page. Both are calculated on the first page of the pdf. So for example "--trim 0 .5\pdfwidth .2\pdfheight 0" will trim the pages half from the right and 20 per cent from the bottom')
    parser.add_argument('--delta',  nargs=2, type=str, default=['0','0'], metavar=('X', 'Y'), help=u'By default logical pages are being arranged side by side.' \
        'To put some space between them, use the delta option, whose argument should be two dimensions.')
    parser.add_argument('--custom', help=u'Custom pdfpages options')
    parser.add_argument('--pages', default="-", help=u'Selects pages to insert. The argument is a comma separated list, containing page numbers '\
        '(e.g. --pages 3,5,6,8), ranges of page numbers (e.g. --pages 4-9) or any combination fo the previous.'\
        'To insert empty pages use {}. '\
        'Page ranges are specified by the following syntax: m-n. This selects'\
        'all pages from m to n. Omitting m defaults to the first page; omitting'\
        'n defaults to the last page of the document. Another way to select' \
        'the last page of the document, is to use the keyword last.' \
        'E.g.: "--pages 3,{},8-11,15" will insert page 3, an empty page, pages from 8 to 11, and page 15. '\
        '"--pages=-" will insert all pages of the document, and "--pages=last-1"' \
        'will insert all pages in reverse order.')

    parser.add_argument('-t', '--text', nargs=4, type=str, action='append',
    metavar=('text_string', 'anchor', 'hpos', 'vpos'),
    help="Add text to pdf file. \n" \
    "'text_string' is the string to add, special variables can be passed, as well as LaTeX font sizes like \Huge. " \
    "Call --text-help for help on how to build this string. " \
    "'anchor' is the point of the text box (the box surrounding the text) to position: " \
    "'tl' will position the top-left corner, " \
    "'tr' will position the top-right corner, " \
    "'bl' will position the bottom-left corner, " \
    "'br' will position the bottom-right corner, " \
    "all other parameters are invalid. \n" \
    "'hpos' and 'vpos' are numbers between 0 and 1 that represent " \
    "how far is 'anchor' from the top left corner of the page.")

    parser.add_argument('--text-help', action='store_true', help=u'Print the help to build a text string to pass to the -t/--text option')

    parser.add_argument('--extract-pages', type=str, metavar=('file_name'), help=u'Read pages to extract from a text file. In the text file pages can be separated by newline character or by space (or mixed)')

    #Boolean parameters NOT for pdfpages
    parser.add_argument('--natural-sorting', action='store_true', default=False, help=u'When scanning a folder, use natural sorting algorithm to sort the files inside it')
    parser.add_argument('--overwrite', action='store_true', default=False, help=u'Overwrite output file if it exists already')
    parser.add_argument('--open', action='store_true', default=False, help=u'Open output PDF file')
    parser.add_argument('--white-page', action='store_true', default=False, help=u'Put a white page after every pdf page')
    parser.add_argument('--repair', action='store_true', default=False, help=u'Try to repair the input PDF files. You need pdftk for this')
    parser.add_argument('--check-latex', action='store_true', default=False, help=u'Check LaTeX installation')
    parser.add_argument('--split-pages', action='store_true', default=False, help=u'Split every input page in 2 equal output pages. '\
        'Use it, for example, if you have a pdf which consists of 2 physical pages in 1 pdf page and you want to split them. Use it on conjuction with trim,'\
        'with which you will specify the left page. If you specify --trim L B R T, the left page will be obtained by trimming with {L B R T}, '\
        'while the right page will be obtained by trimming with {R f L B} (note the swap in left-right and in top-bottom). Use \pdfwidth and \pdfheight '\
        'paramenters in trim option to specify trim relative to page size')
    parser.add_argument('--swap-pages', action='store_true', default=False, help=u'--pages-list specify a text file with a space-separated list of pages to swap')

    parser.add_argument('--last-page-even', action='store_true', default=False, help=u'Last page of every included pdf must be even.'\
        'If it is odd, add a white page')

    #Boolean parameters TO PASS TO PDFPAGES (AND ONLY FOR PDFPAGES)
    parser.add_argument('--clip', action='append_const', const='clip', dest='booleans', help=u'Used togheter with trim, will actually remove the cropped '\
        'part from the pdfpage. If false, the cropped part is present on the physical file, but the pdf reader is instructed to ignore it')
    parser.add_argument('--landscape', action='append_const', const='landscape', dest='booleans', help=u'Output file is in landscape layer instead of portrait')
    parser.add_argument('--frame', action='append_const', const='frame', dest='booleans', help=u'Put a frame around every logical page')

    #-Debug options-
    #Create temporary folder in the current working directory instead of system's default path for temporary files
    parser.add_argument('--verbose', action='store_true', default=False, help=argparse.SUPPRESS)
    parser.add_argument('--debug', action='store_true', default=False, help=argparse.SUPPRESS)
    #Print the result of parse_args' and exit
    parser.add_argument('--debug-print', action='store_true', default= False, help=argparse.SUPPRESS)
    #Don't compile the resulting latex file
    parser.add_argument('--debug-no-compile', action='store_true', default= False, help=argparse.SUPPRESS)
    #Specify debug folder
    parser.add_argument('--debug-folder', type=str, default='temp', help=argparse.SUPPRESS)

    # If no options were passed, display help
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        exit_with_code("",1)

    #Parse arguments
    args = parser.parse_args(cmdargs)

    if(args.verbose):
        print(args)

    if(args.text_help):
        printTextHelp()
        exit_with_code("",0)

    #Build args.text as list if not defined, otherwise crash/we need to make a test every time
    if(args.text is None):
        args.text=list()

    if(args.booleans is None):
        args.booleans=list()

    # If the --paper option is not specified, we pass "fitpaper" to pdfpages by default
    if(args.paper is None):
        args.booleans.append("fitpaper")

    if(args.split_pages):
        args.booleans.append("clip")

    run(args)

if __name__ == "__main__":
    main(sys.argv[1:])
