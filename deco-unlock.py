import pikepdf
import sys
import os
import re
from xfaTools import XfaObj
from bs4 import BeautifulSoup


def soupCopy(soup):
    return BeautifulSoup(str(soup),'xml').findChild()

if(len(sys.argv) == 1 or re.match(r'(^-+h)',sys.argv[1]) ):
    print(f'''
USAGE: 

    python {os.path.basename(sys.argv[0])} 'PATH_TO_PDF.pdf' [... MORE_PDFS.pdf ]
  
        Output will be saved to PATH_TO_PDF_unlocked.pdf in the current working directory
    ''')
    quit()

fileNames = sys.argv
# starting from 1 because the 0th arg is the file name of this script
for fileName in fileNames[1:]:
    with pikepdf.Pdf.open(fileName) as pdfData:
        xfaDict = XfaObj(pdfData)

        templateSoup = BeautifulSoup(xfaDict['template'],'xml')

        # shifting the radio button controls to a nicer spot.
        yOffset = 0
        for tag in templateSoup.find_all('exclGroup'):
            tag['x'] = "0mm" 
            tag['y'] = f'{yOffset}mm'
            yOffset += 20

            tag['access'] = 'open'
            tag['presence'] = 'visible'
        


        # tags to check for personal data that should be deleted on conversion
        personalDataTagRegex = r'(Narrative)|(MemberFullName)|(Sign.*\d+)'
        personalDataTags = []
        
        #copy the event/script that hides the various font size boxes, and change the copy to trigger on mouse clicks
        newEvent = soupCopy(templateSoup.find('event'))
        newEvent['activity'] = 'click'
        
        for tag in templateSoup.find_all('field'):
            # check to see if the field should be marked for data clearing later
            if(tag.find('textEdit')):
                if(re.match(personalDataTagRegex,tag['name'])):
                    personalDataTags.append(tag['name'])
            
            # make the field visible and editable
            tag['access'] = 'open'
            tag['presence'] = 'visible'
            # add an event listener to trigger on mouse click
            tag.append(soupCopy(newEvent))

            # shifting some remaining controls to nicer spot
            if(tag['name'] == "PreviewGraphic" or tag['name'] == 'PrintGraphic'):
                tag['x'] = "0mm" 
                tag['y'] = f'{yOffset}mm'
                yOffset += 5

        # editing the form input data and clearing any personal information    
        dataSoup = BeautifulSoup(xfaDict['datasets'],'xml')
        for tagName in personalDataTags:
            tag = dataSoup.find(tagName)
            if(tag):
                # clear out any data in the tag
                tag.contents = []
        
        # Applying XML changes to the actual PDF
        ## findchild() hotfix is needed to omit <?xml version=...> tag at beginning of document
        xfaDict['template'] = str(templateSoup.findChild())
        xfaDict['datasets'] = str(dataSoup.findChild())

        # Saving to disk
        newFileName = re.sub(r'\.pdf$', '', os.path.basename(fileName)) + '_unlocked.pdf'
        pdfData.save(newFileName)
        



