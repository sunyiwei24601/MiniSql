import collections
import json
import struct
from struct import Struct
import sys
import os
sys.path.append(os.getcwd())
from PageManager.PageHandle import *
PAGE_SIZE = 4096
PAGE_HEADER_FORMAT = ">iii"
PAGE_HEADER_LENGTH = 12
class PF_Manager:
    def __init__(self):
        pass 
    
    
    def CreateFile(self, fileName):
    #create an empty relation file
        f = open(fileName, "wb")
        
        f.close()
    
    def DestroyFile(self, fileName):
        pass

    def OpenFile(self, fileName, attribute_length=16, attribute_format=">ii4sf"):
    # open specific file, return a PF_FileHandle, relation name is the file name
        fileHandle = PF_FileHandle(fileName, attribute_length=attribute_length, attribute_format=attribute_format)
        return fileHandle

    def CloseFile(self, fileHandle):
        pass

    def AllocateBlock(self, buffer):
        pass 

    def DisposeBlock(self, buffer):
        pass 


class PF_FileHandle:
    def __init__(self, fileName, attribute_length=16, attribute_format=">ii4sf"):
    # initiate PF_FileHandle from given format and relation name
        self.fileName = fileName
        self.BufferPool = {}
        self.DirtyPool = []
        # current max page num
        self.pageNum = 0
        self.attribute_length = attribute_length
        self.attribute_format = attribute_format
        # current page pointing to, start from 0, GetNextPage will read from page1
        self.current_page_num = 0

    def GetFirstPage(self) -> PF_PageHeaderHandle:
        # get header page, if on bufferpool read it else read from data
        if 0 in self.BufferPool:
            return self.BufferPool[0]
        with open(self.fileName, 'rb') as f:
            page_bytes = f.read(PAGE_SIZE)
            headerPage = PF_PageHeaderHandle(self.fileName, self.attribute_length, 
                                            header_Data=page_bytes).read_from_Data()
        self.pageNum = headerPage.current_number_of_pages
        self.BufferPool[0] = headerPage
        
        return headerPage
    
    def GetLastPage(self, pageHandle) -> PF_PageHandle:
        pass 
    
    def GetNextPage(self, pageNum=None) -> PF_PageHandle:
        if pageNum == None:
            pageNum = self.current_page_num
        else:
            self.current_page_num = pageNum
        if self.current_page_num >= self.pageNum:
            return None
        self.current_page_num += 1
        return self.GetThisPage(pageNum + 1)

    def GetPreviousPage(self, pageNum=None) -> PF_PageHandle:
        if pageNum == None:
            pageNum = self.current_page_num
        else:
            self.current_page_num = pageNum
        if self.current_page_num <= 1:
            return None
        return self.GetThisPage(pageNum - 1)

    def GetThisPage(self, pageNum) -> PF_PageHandle:
        if pageNum in self.BufferPool:
            return self.BufferPool[pageNum]
        else:
            with open(self.fileName, 'rb+') as f:
                f.seek(pageNum * PAGE_SIZE)
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
            self.BufferPool[0].current_number_of_pages += 1
            self.BufferPool[0].location_of_pages[pageNum] = 4096 * pageNum
            

        self.BufferPool[pageNum] = new_page
        self.MarkDirty(pageNum)
        self.MarkDirty(0)
        return new_page
        
    def DisposePage(self, pageNum):
        pass 

    def MarkDirty(self, pageNum):
        if pageNum not in self.DirtyPool:
            self.DirtyPool.append(pageNum)

    def UnpinPage(self, pageNum):
    # move page from bufferpool
        if pageNum not in self.DirtyPool:
            self.BufferPool.pop(pageNum)
        else:
            self.ForcePages(pageNum=[pageNum])

    def ForcePages(self, pageNum=None):
    # write pages in dirtypool and remove them from dirty pool
        if pageNum == None:
            pageNum = self.DirtyPool
        with open(self.fileName, 'wb+') as f:
            for pagenum in pageNum:
                
                f.seek(4096 * pagenum)
                f.write(self.BufferPool[pagenum].convert_into_bytes())
                self.DirtyPool.pop(pagenum)
            f.close()
    
    def FindFreePage(self, record_nums=1):
    # scan all the pages, check it free nums, if not , allocate a new page
        for pageNum in range(1, self.pageNum + 1):
            page = self.GetThisPage(pageNum)
            if page.check_free() > record_nums:
                return page
        return self.AllocatePage()


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
    # first_page.insert_record(relations[0])
    # first_page.insert_record(relations[1])
    
    # write file
    file_handle.ForcePages()
    
    # read file
    head_page = file_handle.GetFirstPage()
    first_page = file_handle.GetThisPage(1)
    pass