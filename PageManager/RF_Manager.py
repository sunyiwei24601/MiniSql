from PageManager.PF_Manager import *
class RM_Manager:
    def __init__(self, pfmanager:PF_Manager):
        self.pf_manager = pfmanager
        
        pass

    def __del__(self):
        pass 

    def CreateFile(self, fileName, recordSize):
        if recordSize > PAGE_SIZE:
            return 0

        self.pf_manager.CreateFile(fileName)
        


    def DestroyFile(self, fileName):
        pass 

    def CloseFile(self, fileHandle):
        pass

    def OpenFile(self, fileName, fileHandle):
        pf_file_handle = self.pf_manager.OpenFile(fileName)
        fileHandle 
        pass 

class RM_FileHandle:
    def __init__(self):
        pass 

    def __del__(self):
        pass 

    def GetRec(self, rid, rec):
        pass 

    def InsertRec(self, pData, rid):
        pass 

    def DeleteRec(self, rid):
        pass 

    def UpdateRec(self, rec):
        pass 
    
    def ForcePages(self, PageNum=self.ALL_PAGES):
        pass

class RM_FileScan:
    def __init__(self):
        pass 

    def __del__(self):
        pass 

    def OpenScan(self, fileHandle,
                attrType, attrLengeth, attrOffset, 
                comop, value,
                pinHint=NO_HINT):
        pass 

    def GetNextRec(self, rec):
        pass 

    def CloseScan(self):
        pass

class RM_Record:
    def __init__(self):
        pass

    def __del__(self):
        pass 

    def GetData(self, pData):
        pass 

    def GetRid(self, rid):
        pass 

class RID:
    def __init__(self, pageNum=None, slotNum=None):
        pass 

    def __del__(self):
        pass 
    
    def getPageNum(self, pageNum):
        pass

    def getSlotNum(self, slotNum):
        pass 


def header_page():
    record_nums = 5
    relation_name = "sample"
    current_number_of_pages = 2
    first_free_page_num = 1
    location_of_pages = {0:0, 1:4096}
    information = {
        'record_nums': record_nums,
        'relation_name': relation_name,
        'current_number_of_pages': current_number_of_pages,
        "first_free_page_num" : first_free_page_num,
        "location_of_pages": location_of_pages,
        'record_size': 15,
    }
    return information

if __name__ == "__main__":
    relation_name = 'sample1'
    fileName = "temp\{}.db".format(relation_name)
    pf = PF_Manager()
    rm = RM_Manager(pf)
    

    # create relation
    rm.CreateFile(fileName, recordSize=15)
    information = header_page()
    



    relations = [[0, 1, 'Sun'.encode(), 2.5],
             [1, 2, 'Yes'.encode(), 3.5],
             [2, 3, 'NOP'.encode(), 4.5],
             [3, 4, 'You'.encode(), 4.3],
             [4, 5, 'Tim'.encode(), 2.3]]


