call pdftools --input-file ./pdfs/slides.pdf --output ./out/slides_W.pdf --white-page --fitpaper --overwrite
call pdftools --input-file ./out/slides_W.pdf --nup 2 2 --height 0.32 --delta 0mm 0mm --landscape --out-suffix _HANDOUT --frame --overwrite --paginate --paper a4paper -t $filename 0.4 0.01
