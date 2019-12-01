from BTrees.OOBTree import OOBTree as Tree
import pickle
import json
import sys
import os
sys.path.append(os.getcwd())
from PageManager.RF_Manager import *
EQ_OP, LT_OP, GT_OP, LE_OP, GE_OP, NE_OP, NO_OP = 1,2,3,4,5,6,7
class IX_Manager:
    def __init__(self):
        pass 

    def CreateIndex(self, fileName, indexNo, atrrType, attrLength):
        with open(fileName + "." + str(indexNo), "w", encoding="utf-8") as f:
            tree = Tree()
            tree_dict = dict(tree.items())
            json.dump(tree_dict, f)
        return self
        

    def DestroyIndex(self, fileName, indexNo):
        pass

    def OpenIndex(self, fileName, indexNo):
        indexhandle = IX_IndexHandle(fileName, indexNo)
        return indexhandle 

    def CloseIndex(self, indexHandle):
        pass

class IX_IndexHandle:
    def __init__(self, fileName, indexNo):
        self.filename = fileName + '.' + str(indexNo)
        self.indexNo = indexNo
        self.fileName = fileName
        with open(self.filename, "r", encoding="utf-8") as f:
            tree_dict = json.load(f)
            
            keys = list(map(int, tree_dict.keys()))
            values = list(tree_dict.values())
            new_tree_dict = dict(zip(keys, values))
            self.tree = Tree()
            self.tree.update(new_tree_dict)

        pass 

    def __del__(self):
        pass 

    def InsertEntry(self, record, rid):
        key = record[self.indexNo]
        l = self.tree.get(key)
        pageNum = rid.getPageNum()
        slotNum = rid.getSlotNum()
        if l:
            l.append((pageNum, slotNum))
        else:
            self.tree[key] = [(pageNum, slotNum)]
        
    def DeleteEntry(self, record, rid):
        key = record[self.indexNo]
        l = self.tree.get(key)
        pageNum = rid.getPageNum()
        slotNum = rid.getSlotNum()
        if l:
             l.remove((pageNum, slotNum))
        else:
            return False

    def ForcePages(self):
        with open(self.filename, "w", encoding="utf-8") as f:

            tree_dict = dict(self.tree.items())
            json.dump(tree_dict, f) 
            
    
class IX_IndexScan:
    def __init__(self):
        pass 

    def __del__(self):
        pass 

    def OpenScan(self, indexHandle, comOp, value, pinHint=NO_HINT):
        tree = indexHandle.tree
        if comOp == EQ_OP:
            t = tree.values(max=value, min=value)
        if comOp == LT_OP:
            t = tree.values(max=value, excludemax=True)
        if comOp == GT_OP:
            t = tree.values(min=value, excludemin=True)
        if comOp == LE_OP:
            t = tree.values(max=value)
        if comOp == GE_OP:
            t = tree.values(min=value)
        if comOp == NE_OP:
            t1 = list(tree.values(min=value, excludemin=True))
            t2 = list(tree.values(max=value, excludemax=True))
            t = t1 + t2
        if comOp == NO_OP:
            t = tree.values()
        self.t = t

        return self

    def GetNextEntry(self):
        for sets in self.t :
            for rid in sets:
                pageNum = rid[0]
                slotNum = rid[1]
                yield pageNum, slotNum

    def CloseScan(self):
        pass