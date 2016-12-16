# -*- coding: utf-8 -*-
"""

    DS2PageXml.py
    some functionality to handle pageXML files (add regions,...)

    Copyright Xerox(C) 2016 H. Déjean


    
    Developed  for the EU project READ. The READ project has received funding 
    from the European Union’s Horizon 2020 research and innovation programme 
    under grant agreement No 674943.
    
"""
import sys, os
import libxml2

try: #to ease the use without proper Python installation
    import TranskribusDU_version
except ImportError:
    sys.path.append( os.path.dirname(os.path.dirname( os.path.abspath(sys.argv[0]) )) )
    import TranskribusDU_version
    
from common.Component import Component
from xml_formats.PageXml import PageXml
from ObjectModel.xmlDSDocumentClass import XMLDSDocument

from util.unitConversion import convertDot2Pixel

class DS2PageXMLConvertor(Component):
    """
        conversion from DSXML to PageXML
    """
    #DEFINE the version, usage and description of this particular component
    usage = "" 
    version = "v.01"
    description = "description: DS2PageXml conversion"

    
        
    #--- INIT -------------------------------------------------------------------------------------------------------------    
    def __init__(self):
        """
        """
        Component.__init__(self, "DS2PageXml", self.usage, self.version, self.description) 
    
        self.dpi = 300

        self.xrce_id=10000        
        self.dTagNameMapping = {'PAGE':'Page','TEXT':'TextLine', 'BLOCK':'TextRegion','GRAPHELT':'LineDrawingRegion'} 

        self.pageXmlNS = None

    def getCoord(self,DSObject):
        """
            create Coords value (polylines) from BoundingBox
            if object has @points: return points
        """
        
        if DSObject.hasAttribute('points'):
            return DSObject.getAttribute('points')
        else:
            return self.BB2Polylines(DSObject.getX(), DSObject.getY(),DSObject.getHeight(), DSObject.getWidth())
        
    def BB2Polylines(self,x,y,h,w):
        lx= map(lambda x:1.0*x*self.dpi/72.0, ( x,y, x+w,y, x+w,y+h, x,y+h, x,y))
        myPoints = ' '.join(["%d,%d"%(xa,ya) for xa,ya  in zip(lx[0::2], lx[1::2])])
        return myPoints    
        
    def convertDSObject(self,DSObject,pageXmlParentNode):
        """
            convert DSObject and add it as child to pageXmlParentNode
             
             <TextLine id="line_1472550984091_215" custom="readingOrder {index:0;}">
                <Coords points="218,65 280,65 280,100 218,100"/>
                <Baseline points="218,95 280,95"/>
                <TextEquiv>
                    <Unicode>10.</Unicode>
                </TextEquiv>
            </TextLine>            
            
        """
        try:
            pageXmlName= self.dTagNameMapping[DSObject.getName()]
        except KeyError: pass
                    
        domNode= PageXml.createPageXmlNode(pageXmlName,self.pageXmlNS)
        if DSObject.getID():
            domNode.setProp("id", "xrce_%s"%DSObject.getID())
        else: self.addXRCEID(domNode)
        pageXmlParentNode.addChild(domNode)
        
        coordsNode = libxml2.newNode('Coords')
        coordsNode.setNs(self.pageXmlNS)
        coordsNode.setProp('points', self.BB2Polylines(DSObject.getX(),DSObject.getY(), DSObject.getHeight(),DSObject.getWidth()))        

        domNode.addChild(coordsNode)       
        
        
    def addXRCEID(self,node):
        node.setProp("id", "xrce_%d"%self.xrce_id)  
        self.xrce_id += 1
        
    def convertDSPage(self,OPage,pageXmlPageNODE):
        """
            populate pageXml with OPage
        """
        from ObjectModel.XMLDSGRAHPLINEClass import XMLDSGRAPHLINEClass
        from ObjectModel.XMLDSTEXTClass import XMLDSTEXTClass

        # TextRegion needed: create a fake one with BB zone?
        regionNode= PageXml.createPageXmlNode("TextRegion",self.pageXmlNS)
        pageXmlPageNODE.addChild(regionNode)
        self.addXRCEID(regionNode)
                
        coordsNode = libxml2.newNode('Coords')
        coordsNode.setNs(self.pageXmlNS)
        coordsNode.setProp('points', self.BB2Polylines(0,0, OPage.getHeight(),OPage.getWidth()))
        regionNode.addChild(coordsNode)     
        
        # get textual elements
        lElts= OPage.getAllNamedObjects(XMLDSTEXTClass)
        for DSObject in lElts:
            self.convertDSObject(DSObject,regionNode)

#         # get graphelt elements
        lElts= OPage.getAllNamedObjects(XMLDSGRAPHLINEClass)
        for DSObject in lElts:
            self.convertDSObject(DSObject,pageXmlPageNODE)
        
        # get table elements
        
    def run(self,domDoc):
        """
            conversion
        """
        ODoc =XMLDSDocument()
        ODoc.loadFromDom(domDoc)
        lPageXmlDoc=[]
        lPages= ODoc.getPages()   
        for inumpage,page in enumerate(lPages[:1]):
            pageXmlDoc,pageNode = PageXml.createPageXmlDocument(creatorName='XRCE', filename = page.getAttribute('imageFilename'), imgW = int(round(page.getWidth(),0)), imgH = int(round(page.getHeight(),0)))
            self.pageXmlNS = pageXmlDoc.getRootElement().ns()
            self.convertDSPage(page,pageNode)
            #store pageXml
            lPageXmlDoc.append(pageXmlDoc)
#             print pageXmlDoc.serialize('UTF-8', 1)
            res= PageXml.validate(pageXmlDoc.doc)
            print "document is valid:", res 
            self.outputFileName = os.path.dirname(self.inputFileName)+os.sep+os.path.basename(page.getAttribute('imageFilename'))+"_%.4d"%(inumpage+1) + ".xml"
            print "output:[%s]",self.outputFileName
            self.writeDom(pageXmlDoc, bIndent=True)
        
if __name__ == "__main__":
    
    
    docM = DS2PageXMLConvertor()

    #prepare for the parsing of the command line
    docM.createCommandLineParser()
        
    #parse the command line
    dParams, args = docM.parseCommandLine()
    
    #Now we are back to the normal programmatic mode, we set the componenet parameters
    docM.setParams(dParams)
    
    doc = docM.loadDom()
    docM.run(doc)
    if doc and docM.getOutputFileName() != "-":
        docM.writeDom(doc, True)

    