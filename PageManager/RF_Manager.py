import sys
import os
sys.path.append(os.getcwd())
from PageManager.PF_Manager import *
NO_HINT = 0
PAGE_SIZE = 4096
from PageManager.IX_Manager import *
class RM_Manager:
    def __init__(self, pfmanager:PF_Manager):
        self.pf_manager = pfmanager
        
        pass

    def __del__(self):
        pass 

    def CreateFile(self, fileName, recordSize):
        if recordSize > PAGE_SIZE:
            return 0
        attribute_length = 16
        attribute_format = '>ii4sf'
        self.pf_manager.CreateFile(fileName)
        pf_file_handle = self.pf_manager.OpenFile(fileName, attribute_length=attribute_length,
                             attribute_format=attribute_format)
        pf_file_handle.AllocatePage()
        pf_file_handle.ForcePages()

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
        self.header_page = self.pf_file_handle.GetFirstPage()

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
        slot = page.insert_record(record)
        self.pf_file_handle.MarkDirty(page.GetPageNum())
        self.pf_file_handle.MarkDirty(0)
        return RID(page.GetPageNum(), slot)

    def InsertRecs(self, records):
        page_slots = []
        header_page = self.pf_file_handle.GetFirstPage()
        i = 0
        page = self.pf_file_handle.FindFreePage()
        for i in range(len(records)):
            slot = page.insert_record(records[i]) 
            if slot == False:
                page_slots2 = self.InsertRecs(records[i:]) 
                page_slots += page_slots2
                break
            else:
                page_slots.append((page.GetPageNum, slot))
            header_page.record_nums += 1
        
        self.pf_file_handle.MarkDirty(page.GetPageNum())
        self.pf_file_handle.MarkDirty(0)
        return page_slots

    def DeleteRec(self, rid):
        header_page = self.pf_file_handle.GetFirstPage()
        pageNum = rid.GetPageNum
        slotNum = rid.getSlotNum
        page = self.pf_file_handle.GetThisPage(pageNum)
        page.delete_record(slotNum)
        header_page.record_nums -= 1
        self.pf_file_handle.MarkDirty(pageNum) 
        self.pf_file_handle.MarkDirty(0)

    def UpdateRec(self, rec):
        rid = rec.GetRid()
        record = rec.GetData()
        pageNum = rid.GetPageNum
        slotNum = rid.getSlotNum
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
        self.rm_fileHandle = fileHandle
        self.pf_fileHandle = self.rm_fileHandle.pf_file_handle
        self.pageNums = fileHandle.pf_file_handle.pageNum
        self.comop = comop
        self.value = value
        self.attrOffset = attrOffset
        self.attrType = attrType

    def GetNextRec(self):
        page = self.pf_fileHandle.GetNextPage()
        print(page)
        while(page):
            for record in page.GetData().values():
                if self.CheckRecord(record):
                    yield record
            page = self.pf_fileHandle.GetNextPage()

    def CheckRecord(self, record):
        attr = record[self.attrOffset]
        if self.comop == EQ_OP:
            if attr == self.value:
                return True
        if self.comop == GT_OP:
            if attr > self.value:
                return True
        if self.comop == LT_OP:
            if attr < self.value:
                return True
        if self.comop == GE_OP:
            if attr >= self.value:
                return True
        if self.comop == LE_OP:
            if attr <= self.value:
                return True
        if self.comop == NE_OP:
            if attr != self.value:
                return True
        return False

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



if __name__ == "__main__":
    fileName = 'student'
    indexNo = 1
    pf_manager = PF_Manager()
    rm_manager = RM_Manager(pf_manager)
    rm_manager.CreateFile(fileName, 10)

    rm_filehandle = rm_manager.OpenFile(fileName)

    ix_manager = IX_Manager().CreateIndex(fileName, indexNo, "int", 4)
    ix_indexhandle = ix_manager.OpenIndex(fileName, indexNo)

    relations = [[0, 1, 'Sun'.encode(), 2.5],
            [1, 2, 'Yes'.encode(), 3.5],
            [2, 3, 'NOP'.encode(), 4.5],
            [3, 4, 'You'.encode(), 4.3],
            [4, 5, 'Tim'.encode(), 2.3]]
    rid1 = RID(1, 0)
    rid2 = RID(1, 1)
    rid = rm_filehandle.InsertRec(relations[0])
    ix_indexhandle.InsertEntry(relations[0], rid)
    rid = rm_filehandle.InsertRec(relations[1])
    ix_indexhandle.InsertEntry(relations[1], rid)
    rid = rm_filehandle.InsertRec(relations[2])
    ix_indexhandle.InsertEntry(relations[2], rid)

    ix_indexhandle.ForcePages()

    ix_indexscan = IX_IndexScan()
    ix_indexscan.OpenScan(ix_indexhandle, NE_OP, 2)
    for rid in ix_indexscan.GetNextEntry():
        print (rid)

    rm_filescan = RM_FileScan()
    rm_filescan.OpenScan(rm_filehandle, 1, 4, 1, LE_OP, 2)
    l = rm_filescan.GetNextRec()
    rm_filehandle.ForcePages()
    pass    
    


