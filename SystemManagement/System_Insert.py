import sys
sys.setrecursionlimit(10000)
import os
sys.path.append(os.getcwd())
from SystemManagement.System_MetaData import *
from PageManager.PF_Manager import *
from PageManager.IX_Manager import *
from PageManager.RF_Manager import *
from SystemManagement.System_Create import *
class InsertExecutor:
    def __init__(self, rm_manager, ix_manager, relation_name):
        self.rm_manager = rm_manager
        self.ix_manager = ix_manager
        self.rm_filehandle = self.rm_manager.OpenFile(relation_name)

    def InsertTuples(self, relation_name, records):
        rm_filehandle = self.rm_manager.OpenFile(relation_name)
        index_lists = []
        for i in range(len(records[0])):
            ix_indexhandle = self.ix_manager.OpenIndex(relation_name, i)
            index_lists.append(ix_indexhandle)
        
        rids = rm_filehandle.InsertRecs(records)
        for record, rid in zip(records, rids):
            for offset in range(len(record)):
                index_lists[offset].InsertEntry(record, rid)
        for index in index_lists:
            index.ForcePages()
        rm_filehandle.ForcePages()
    
    def InsertTuple(self, relation_name, record):
        index_lists = []
        rid = self.rm_filehandle.InsertRec(record)
        for offset in range(len(record)):
            ix_indexhandle = self.ix_manager.OpenIndex(relation_name, offset)
            ix_indexhandle.InsertEntry(record, rid)
        ix_indexhandle.ForcePages()

if __name__ == "__main__":
    relations = [[i, 1] for i in range(100000)]
    attributes = ["NO", "VAL"]
    attribute_types = ["int", "int"]
    relation_name = "R_1_100000"
    domains = [[], []]
    metadata_filename = "metadata.json"
    pf_manager = PF_Manager()
    rm_manager = RM_Manager(pf_manager)
    ix_manager = IX_Manager()
    createExecutor = CreateExecutor(metadata_filename, rm_manager, ix_manager)
    createExecutor.create_relation(relation_name, attributes, attribute_types, domains)

    insertExecutor = InsertExecutor(rm_manager, ix_manager, relation_name)
    insertExecutor.InsertTuples(relation_name, relations)
    pf_filehandle = insertExecutor.rm_filehandle.pf_file_handle
    pf_filehandle.GetThisPage(1)
    pass


            