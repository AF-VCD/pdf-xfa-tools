import pikepdf
import sys
import os
import re
from xfaTools import XfaObj


if(len(sys.argv) == 1 or re.match(r'(^-+h)',sys.argv[1]) ):
    print(f'''
USAGE: 

    python {os.path.basename(sys.argv[0])} 'PATH_TO_PDF.pdf' [... MORE_PDFS.pdf ]
  
        Output will be saved to a folder called PATH_TO_PDF (for each pdf) in the current working directory
    ''')
    quit()

fileNames = sys.argv

# starting from 1 because the 0th arg is the file name of this script
for fileName in fileNames[1:]:
    with pikepdf.Pdf.open(fileName) as pdfData:
        xfaDict = XfaObj(pdfData)

        folderName = re.sub(r'\.pdf$', '', os.path.basename(fileName))
        
        os.makedirs(f'./{folderName}', exist_ok=True)
        
        for key in xfaDict.keys():
            outFile = re.sub(r'[<>: ]','',key) 
            outFile = re.sub('/','END',outFile)
            fullPath = f'./{folderName}/{outFile}.xml'
            with open(fullPath, 'w', encoding="utf-8") as f:
                data = xfaDict[key]
                f.write(data)



