import collections
import json
import struct
from struct import Struct
from PageManager.PageHandle import *
PAGE_SIZE = 4096
PAGE_HEADER_FORMAT = ">ii"
class PF_Manager:
    def __init__(self):
        pass 
    
    def CreateFile(self, fileName):
        f = open(fileName, "wb")
        
        f.close()
    
    def DestroyFile(self, fileName):
        pass

    def OpenFile(self, fileName):
        fileHandle = PF_FileHandle(fileName)
        return fileHandle

    def CloseFile(self, fileHandle):
        pass

    def AllocateBlock(self, buffer):
        pass 

    def DisposeBlock(self, buffer):
        pass 


class PF_FileHandle:
    def __init__(self, fileName, attribute_length=15, attribute_format=">ii4sf", 
                fileHandle=None):
        self.fileName = fileName
        self.BufferPool = {}
        self.DirtyPool = []
        self.pageNum = -1
        self.attribute_length = attribute_length
        self.attribute_format = attribute_format
        self.current_page_num = -1

    def GetFirstPage(self) -> PF_PageHeaderHandle:
        with open(self.fileName, 'rb') as f:
            page_bytes = f.read(PAGE_SIZE)
            headerPage = PF_PageHeaderHandle(self.fileName, self.attribute_length, 
                                            header_Data=page_bytes).read_from_Data()
            return headerPage
    
    def GetLastPage(self, pageHandle):
        pass 
    
    def GetNextPage(self, pageNum=None):
        if pageNum == None:
            pageNum = self.current_page_num
        else:
            self.current_page_num = pageNum
        self.current_page_num += 1
        return self.GetThisPage(pageNum + 1)

    def GetPreviousPage(self, pageNum=None):
        if pageNum == None:
            pageNum = self.current_page_num
        else:
            self.current_page_num = pageNum
        return self.GetThisPage(pageNum - 1)

    def GetThisPage(self, pageNum):
        if pageNum in self.BufferPool:
            return self.BufferPool[pageNum]
        else:
            with open(self.fileName, 'rb+') as f:
                f.peek(pageNum * PAGE_SIZE)
                pData = f.read(PAGE_SIZE)
            page = PF_PageHandle(pageNum, self.attribute_length, self.attribute_format,
                             pData=pData).ReadData()
            self.BufferPool[pageNum] = page 
            return page

    def AllocatePage(self)-> PF_PageHandle:
        pageNum = self.pageNum + 1
        self.pageNum += 1
        # create headfile
        if pageNum == 0:
            new_page = PF_PageHeaderHandle(relation_name = self.fileName, attribute_length=self.attribute_length)
        else:
            new_page = PF_PageHandle(pageNum, attribute_length=self.attribute_length, attribute_format=self.attribute_format)
        self.BufferPool[pageNum] = new_page
        self.DirtyPool.append(pageNum)
        return new_page
        
    def DisposePage(self, pageNum):
        pass 

    def MarkDirty(self, pageNum):
        if pageNum not in self.DirtyPool:
            self.DirtyPool.append(pageNum)

    def UnpinPage(self, pageNum):
        if pageNum not in self.DirtyPool:
            self.BufferPool.pop(pageNum)
        else:
            self.ForcePages(pageNum=[pageNum])

    def ForcePages(self, pageNum=None):
        if pageNum == None:
            pageNum = self.DirtyPool
        with open(self.fileName, 'wb+') as f:
            for pagenum in pageNum:
                f.peek(4096 * pagenum)
                f.write(self.BufferPool[pagenum].convert_into_bytes())
            f.close()
    
    def FindFreePage(self, record_nums=1):
        for pageNum in range(self.pageNum):
            page = self.GetThisPage(pageNum)
            if page.check_free > record_nums:
                return page




def extend_to_a_page(s, page_size=PAGE_SIZE):
    if len(s) >= PAGE_SIZE:
        print("bigger than a page!")
        return False
    else:
        return s + b" " * (page_size - len(s))

if __name__ == "__main__":
    fileName = 'student'
    pf_mgr = PF_Manager()
    pf_mgr.CreateFile(fileName)
    file_handle = pf_mgr.OpenFile(fileName)
   
   # create file
    header_page = file_handle.AllocatePage()
    first_page = file_handle.AllocatePage()
    relations = [[0, 1, 'Sun'.encode(), 2.5],
             [1, 2, 'Yes'.encode(), 3.5],
             [2, 3, 'NOP'.encode(), 4.5],
             [3, 4, 'You'.encode(), 4.3],
             [4, 5, 'Tim'.encode(), 2.3]]
    first_page.insert_record(relations[0])
    first_page.insert_record(relations[1])
    
    # write file
    file_handle.ForcePages()
    
    # read file
    head_page = file_handle.GetFirstPage()
    first_page = file_handle.GetThisPage(1)
    pass