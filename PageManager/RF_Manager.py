import sys
import os
sys.path.append(os.getcwd())
from PageManager.PF_Manager import *
NO_HINT = 0
PAGE_SIZE = 4096
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

    def OpenFile(self, fileName):
        attribute_length = 16
        attribute_format = '>ii4sf'
        pf_file_handle = self.pf_manager.OpenFile(fileName, attribute_length=attribute_length,
                             attribute_format=attribute_format)
        return RM_FileHandle(pf_file_handle) 
         

class RM_FileHandle:
    def __init__(self, pf_file_handle:PF_FileHandle=None):
        self.pf_file_handle = pf_file_handle

    def __del__(self):
        pass 

    def GetRec(self, rid):
        pageNum = rid.pageNum
        slotNum = rid.slotNum
        page = self.pf_file_handle.GetThisPage(pageNum)
        record = page.GetData(slotNum)
        return RM_Record(record, rid)

    def InsertRec(self, record):
        header_page = self.pf_file_handle.GetFirstPage()
        header_page.record_nums += 1
        page = self.pf_file_handle.FindFreePage()
        page.insert_record(record)
        pf_file_handle.MarkDirty(page.GetPageNum)
        pf_file_handle.MarkDirty(0)
        
    def DeleteRec(self, rid):
        pageNum = rid.GetPageNum
        slotNum = rid.getSlotNum
        page = self.pf_file_handle.GetThisPage(pageNum)
        slotNum = rid.getSlotNum
        self.pf_file_handle.MarkDirty(pageNum) 

    def UpdateRec(self, rec):
        rid = rec.GetRid()
        record = rec.GetData()
        pageNum = rid.GetPageNum
        slotNum = rid.getSlotNum
        page = self.pf_file_handle.GetThisPage(pageNum)
        page = self.pf_file_handle.GetThisPage(pageNum)
        page.insert_record(record, slotNum)
        self.pf_file_handle.MarkDirty(pageNum) 
    
    def ForcePages(self, PageNum=None):
        if PageNum == None:
            PageNum = self.pf_file_handle.DirtyPool
        self.pf_file_handle.ForcePages(PageNum)

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

    def GetNextRec(self):
        pass 

    def CloseScan(self):
        pass

class RM_Record:
    def __init__(self, record, rid):
        self.record = record
        self.rid = rid

    def __del__(self):
        pass 

    def GetData(self):
        return self.record

    def GetRid(self):
        return self.rid

class RID:
    def __init__(self, pageNum=None, slotNum=None):
        self.pageNum = pageNum
        self.slotNum = slotNum 

    def __del__(self):
        pass 
    
    def getPageNum(self):
        return self.pageNum

    def getSlotNum(self):
        return self.slotNum


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
    fileName = 'student'
    pf_manager = PF_Manager()
    rm_manager = RM_Manager(pf_manager)
    rm_filehandle = rm_manager.OpenFile(fileName)

    rid1 = RID(1, 0)
    rid2 = RID(1, 1)
    r1 = rm_filehandle.GetRec(rid1)
    r2 = rm_filehandle.GetRec(rid2)

    


