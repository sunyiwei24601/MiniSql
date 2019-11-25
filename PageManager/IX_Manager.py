class IX_Manager:
    def __init__(self, pfm):
        pass 

    def CreateIndex(self, fileName, indexNo, atrrType, attrLength):
        pass 

    def DestroyIndex(self, fileName, indexNo):
        pass

    def OpenIndex(self, fileName, indexNo, indexHandle):
        pass 

    def CloseIndex(self, indexHandle):
        pass

class IX_IndexHandle:
    def __init__(self):
        pass 

    def __del__(self):
        pass 

    def InsertEntry(self, pData, rid):
        pass

    def DeleteEntry(self, pData, rid):
        pass 

    def ForcePages(self):
        pass 


class IX_IndexScan:
    def __init__(self):
        pass 

    def __del__(self):
        pass 

    def OpenScan(self, indexHandle, comOp, value, pinHint=NO_HINT):
        pass 

    def GetNextEntry(self, rid):
        pass

    def CloseScan(self):
        pass