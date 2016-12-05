# coding: utf8

'''
This code is about the graph we build - edges and nodes   (nodes are called Blocks)

JL Meunier
March 3rd, 2016


Copyright Xerox 2016

'''

from common.trace import trace, traceln

import Block

DEBUG=0
DEBUG=1


class Edge:
        
    def __init__(self, A, B):
        """
        An edge from A to B
        """
        self.A = A
        self.B = B
       
 
    # ------------------------------------------------------------------------------------------------------------------------------------        
    #specific code for the CRF graph
    def computeEdges(cls, lPrevPageEdgeBlk, lPageBlk, bShortOnly=False):
        """
        we will compute the edge between those nodes, some being on previous "page", some on "current" page.
        
        if bShortOnly, we filter intra-page edge and keep only "short" ones
        """
        lAllEdge = list()
        
        #--- horizontal and vertical neighbors
        lHEdge, lVEdge = Block.Block.findPageNeighborEdges(lPageBlk, bShortOnly)
        lAllEdge.extend(lHEdge)
        lAllEdge.extend(lVEdge)
        if DEBUG: 
            cls.dbgStorePolyLine("neighbors", lHEdge)
            cls.dbgStorePolyLine("neighbors", lVEdge)
        
        #--- overlap with previous page
        if lPrevPageEdgeBlk:
            lConseqOverEdge = Block.Block.findConsecPageOverlapEdges(lPrevPageEdgeBlk, lPageBlk)
            lAllEdge.extend(lConseqOverEdge) 
            
        return lAllEdge
    computeEdges = classmethod(computeEdges)

    def dbgStorePolyLine(cls, sAttr, lEdge):
        """
        Store a polyline in the given attribute
        """
        for e in lEdge:
            xA, yA = e.A.getCenter()
            xB, yB = e.B.getCenter()
            ndA = e.A.node
            sPolyLine = "%.1f,%.1f,%.1f,%.1f,%.1f,%.1f"%(xA,yA,xB,yB,xA,yA)
            if ndA.hasProp(sAttr):
                ndA.setProp(sAttr, ndA.prop(sAttr) + "," + sPolyLine)
            else:
                ndA.setProp(sAttr,                         sPolyLine)
        return
    dbgStorePolyLine = classmethod(dbgStorePolyLine)
    
class HorizontalEdge(Edge): pass    
    
class VerticalEdge(Edge): pass    

class CrossPageEdge(Edge): pass    

class VirtualEdge(Edge): pass    
    
    