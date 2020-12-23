import pikepdf
import sys
import os
import re
from xfaTools import XfaObj

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



