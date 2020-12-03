call pdftools -i ./pdfs/slides.pdf --output ./out/slides_W.pdf --white-page --fitpaper --overwrite
call pdftools -i ./out/slides_W.pdf --output ./out/slides_HANDOUT3x3.pdf --nup 3 2 --frame --overwrite --paginate --delta 0mm 5mm --width 0.45

