# -*- coding: utf-8 -*-
"""

    XML object class 
    
    Herv� D�jean
    cpy Xerox 2009
    
    a class for object from a XMLDocument

"""

from XMLObjectClass import XMLObjectClass
from config import ds_xml_def as ds_xml

class  XMLDSObjectClass(XMLObjectClass):
    """
        DS object class
        this is a 2D object
    """
    orderID = 0
    name = None
    def __init__(self):
        XMLObjectClass.__init__(self)
#         XMLDSObjectClass.id += 1
#         self._orderedID =  XMLObjectClass.id
#         self._domNode = None
        # needed for mapping dataobject to layoutObject
        self._lElements = []
        self._page  = None
        self._id= None
        
        
        self.Xnearest=[[],[]]  # top bottom
        self.Ynearest=[[],[]]  # left right        
        
    def getPage(self): return self._page
    def setPage(self,p): self._page= p 
    
    def getID(self): return self._id
    
#     def getElements(self): return self._lElements
#     def addElement(self,e): self._lElements.append(e)
    

    def getX(self): return float(self.getAttribute('x'))
    def getY(self): return float(self.getAttribute('y'))
    def getX2(self): return float(self.getAttribute('x'))+self.getWidth()
    def getY2(self): return float(self.getAttribute('y'))+self.getHeight()        
    def getHeight(self): return float(self.getAttribute('height'))
    def getWidth(self): return float(self.getAttribute('width'))    
    
    
    def resizeMe(self,objectType):
        assert len(self.getAllNamedObjects(objectType)) != 0
        
        minbx = 9e9
        minby = 9e9
        maxbx = 0
        maxby = 0
        for elt in self.getAllNamedObjects(objectType):
#            if len(elt.getContent()) > 0 and elt.getHeight()>4 and elt.getWidth()>4:
                if elt.getX() < minbx: minbx = elt.getX()
                if elt.getY() < minby: minby = elt.getY()
                if elt.getX() + elt.getWidth() > maxbx: maxbx = elt.getX() + elt.getWidth()
                if elt.getY() + elt.getHeight()  > maxby: maxby = elt.getY() + elt.getHeight()
        assert minby != 9e9
        self.addAttribute('x', minbx)
        self.addAttribute('y', minby)
        self.addAttribute('width', maxbx-minbx)
        self.addAttribute('height', maxby-minby)
        self.addAttribute('x2', maxbx)
        self.addAttribute('y2', maxby)

        
        self._BB = [minbx,minby,maxby-minby,maxbx-minbx]    
    
    def fromDom(self,domNode):
        
        ## if domNode in mappingTable:
        ## -> ise the fromDom of the specific object
        
        self.setName(domNode.name)
        self.setNode(domNode)
        # get properties
        prop = domNode.properties
        while prop:
            self.addAttribute(prop.name,prop.getContent())
            # add attributes
            prop = prop.next
        child = domNode.children
        try: 
            self._id = self.getAttribute('id')
        except:pass
        ## if no text: add a category: text, graphic, image, whitespace
        while child:
            if child.type == 'text':
                if self.getContent() is not None:
                    self.addContent(child.getContent().decode("UTF-8"))
                else:
                    self.setContent(child.getContent().decode("UTF-8"))
                pass
            elif child.type =="comment":
                pass
            elif child.type == 'element':
                from XMLDSLINEClass import XMLDSLINEClass
                from XMLDSTEXTClass import XMLDSTEXTClass
                from XMLDSBASELINEClass import XMLDSBASELINEClass
                if child.name  == ds_xml.sLINE_Elt:
                    myObject= XMLDSLINEClass(child)
                    # per type?
                    self.addObject(myObject)
                    myObject.setPage(self)
                    myObject.fromDom(child)
                elif child.name  == ds_xml.sTEXT:
                    myObject= XMLDSTEXTClass(child)
                    # per type?
                    self.addObject(myObject)
                    myObject.setPage(self)
                    myObject.fromDom(child)
                elif child.name == ds_xml.sBaseline:
                    myObject= XMLDSBASELINEClass(child)
                    self.addObject(myObject)
                    myObject.setPage(self)
                    myObject.fromDom(child)      
                else:
                    myObject= XMLDSObjectClass()
                    myObject.setNode(child)
                    # per type?
                    self.addObject(myObject)
                    myObject.setPage(self)
                    myObject.fromDom(child)   
                
                
                
            child = child.next
         
         
         
    def clipMe(self,clipRegion,lSubObject=[]):
        """
        
            DOES NOT WORK !!!
        
            return the list of new subobjects considering the clip region
            -->  if subobjects is not 'clippable' ? how to cut a TOKEN????
            
            recursive: if a sub object is cut: go down and take only clipped) subobj if the zones
            -> text/token
            
            
            region: a XMLDSObjectClass!!
            
            create new objects?  YES::
            
        """
        ## if self has no subojects: need to be inserted in the region???
        
        ## current object
        if self.overlap(clipRegion):
            myNewObject =  XMLDSObjectClass()
#             print self.getAttributes()           
            ## ID missing! - > use self id and extend?
            newX = max(clipRegion.getX(),self.getX())
            newY = max(clipRegion.getY(),self.getY())
            newW = min(self.getX2(),clipRegion.getX2()) - newX
            newH = min(self.getY2(),clipRegion.getY2()) - newY
            
            myNewObject.addAttribute('x',newX)
            myNewObject.addAttribute('y',newY)
            myNewObject.addAttribute('height',newH)
            myNewObject.addAttribute('width',newW)            
            
#             print self.getID(),self.getName(),self.getContent()
#             print '\tnew dimensions',myNewObject.getX(),myNewObject.getY(),myNewObject.getWidth(),myNewObject.getHeight()
            
            if lSubObject == []:
                lSubObject= self.getObjects()
        
            for subObject in lSubObject:
                ## get clipped dimensions
                newSub= subObject.clipMe(clipRegion)
                if newSub:
                    myNewObject.addObject(newSub)
            else:
                return None
            return myNewObject 
        
         
         
         
    def overlap(self,zone):
        return self.overlapX(zone) and self.overlapY(zone)
    
    def overlapX(self,zone):
        
    
        [a1,a2] = self.getX(),self.getX()+ self.getWidth()
        [b1,b2] = zone.getX(),zone.getX()+ zone.getWidth()
        return min(a2, b2) >=   max(a1, b1) 
        
    def overlapY(self,zone):
        [a1,a2] = self.getY(),self.getY() + self.getHeight()
        [b1,b2] = zone.getY(),zone.getY() + zone.getHeight()
        return min(a2, b2) >=  max(a1, b1)   
        
    def getAllSetOfFeatures(self,TH):
        """
            Generate a set of features for self.
            
            
        """
        from spm.feature import featureObject,sequenceOfFeatures, emptyFeatureObject
     
        if self._lBasicFeatures and len(self._lBasicFeatures.getSequences()) > 0:
            lR=sequenceOfFeatures()
            for f in self._lBasicFeatures.getSequences():
                if f.isAvailable():
                    lR.addFeature(f)
            return lR     
   
        else:

            lFeatures = []
            for attributeName in self.getAttributes():
                if (self._lFeatureList is not None and attributeName in self._lFeatureList) or self._lFeatureList is None:
                    try:
                        fvalue = float(self.getAttribute(attributeName))
                        ftype= featureObject.NUMERICAL
                    except ValueError:
                        ftype = featureObject.EDITDISTANCE
                        fvalue = self.getAttribute(attributeName)
                        
                    feature = featureObject()
                    feature.setName(attributeName)
                    feature.setTH(TH)
                    feature.addNode(self)
                    feature.setObjectName(self.getName())
                    feature.setValue(fvalue)
                    feature.setType(ftype)
                    lFeatures.append(feature)
      
            
        if lFeatures == []:
            feature = featureObject()
            feature.setName('EMPTY')
            feature.setTH(TH)
            feature.addNode(self)
            feature.setObjectName(self.getName())
            feature.setValue(True)
            feature.setType(featureObject.BOOLEAN)
            lFeatures.append(feature)            

        seqOfF = sequenceOfFeatures()
        for f in lFeatures:
            seqOfF.addFeature(f)
        self._lBasicFeatures=seqOfF
        return seqOfF