import collections
import json
import struct
from struct import Struct

class PF_PageHeaderHandle:
    def __init__(self, relation_name, attribute_length, header_Data=None):
        self.record_nums = 0
        self.relation_name = relation_name
        self.current_number_of_pages = 1
        self.location_of_pages = {0:0}
        self.attribute_length = attribute_length
        self.header_Data = header_Data

    def convert_into_bytes(self):
        information = {
            'record_nums': self.record_nums,
            'relation_name': self.relation_name,
            'current_number_of_pages': self.current_number_of_pages,
            #"first_free_page_num" : first_free_page_num,
            "location_of_pages": self.location_of_pages,
            'attribute_length': self.attribute_length,
        }
        
        byte = json.dumps(information).encode()
        return extend_to_a_page(byte)

    def read_from_Data(self):
        information = json.loads(self.header_Data.decode("utf-8"))
        self.record_nums = information['record_nums']
        self.relation_name = information['relation_name']
        self.current_number_of_pages = information['current_number_of_pages']
        self.location_of_pages = information['location_of_pages']
        self.attribute_length = information['attribute_length']

class PF_PageHandle:
    def __init__(self, pageNum, attribute_length, attribute_format, pData=None):
        self.pageNum = pageNum
        self.attribute_length = attribute_length
        self.attribute_format = attribute_format
        if pData == None:
            self.page_records_nums = 0
        self.pData = pData
        self.records = {}
        self.max_record_nums = (PAGE_SIZE - 4) // attribute_length
    
    def __del__(self):
        pass 

    def GetData(self, start=None):
        if start == None:
            return self.records
        return self.records[start]
    
    def ReadData(self):
        l = self.attribute_length
        self.records = collections.defaultdict(list)
        self.pageNum, self.page_records_nums = struct.unpack(self.pData[:8])
        slot_num = 0

        structer = Struct(self.attribute_format)
        for i in range(8, 4096, l):
            record_bytes = self.pData[i:i+l]
            if record_bytes[0] == 32:
                record = []
            else:
                record = list(structer.unpack(record_bytes))
            self.records[slot_num] = record
            slot_num += 1
        return self

    def GetPageNum(self):
        return self.pageNum

    def convert_into_bytes(self):
        page_bytes = struct.pack('>ii', self.pageNum, self.page_records_nums) 
        structer = Struct(self.attribute_format)
        
        records = sorted(self.records.items(), key= lambda x:x[0])
        for record in records:
            if len(record[1]) == 0 :
                page_bytes += ' ' * self.attribute_length
            else:
                page_bytes += structer.pack(*record[1])
        return extend_to_a_page(page_bytes)
    
    def search_first_free_slot(self):
        slots = self.records.keys()
        
        first_free_slot = 0
        if len(slots) == 0:
            return first_free_slot
        
        
        slots = sorted(slots)
        for i in slots:
            if i != first_free_slot:
                return first_free_slot
            first_free_slot += 1
        
        return first_free_slot
    
    def check_free(self):
        if len(self.records.keys()) == self.max_record_nums:
            if self.search_first_free_slot() >= self.max_record_nums:
                return False
        else:
            return self.max_record_nums - len(self.records)

    def insert_record(self, record):
        slot = self.search_first_free_slot()
        if slot != None:
            self.records[slot] = record
            self.page_records_nums += 1
            return True
        else:
            print("this Page is Full")
            return False

    def delete_record(self, slot):
        self.records[slot] = []
        self.record_nums -= 1
