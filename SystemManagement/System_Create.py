from SystemManagement.System_MetaData import *
from PageManager.PF_Manager import *
from PageManager.IX_Manager import *
from PageManager.RF_Manager import *
class CreateExecutor:
    def __init__(self, metadata_file_name, rm_manager, ix_manager):
        self.metadata_manager = MetaDataManager(metadata_file_name)
        self.rm_manager = rm_manager
        self.ix_manager = ix_manager

    def create_relation(self, relation_name, attributes, attribute_types, domains):
        self.metadata_manager.create_relation_data(relation_name, attributes, attribute_types, domains)
        for offset in range(len(attribute_types)):
            attribute = attributes[offset]
            attribute_type = attribute_types[offset]
            attribute_length = 4
            self.ix_manager.CreateIndex(relation_name, offset, attribute_type, attribute_length)
            self.metadata_manager.create_index_data(relation_name, attribute, offset)
        attribute_format = self.metadata_manager.get_attribute_format(attribute_types)
        attribute_length = self.metadata_manager.get_attribute_length(attribute_types)
        
        self.rm_manager.CreateFile(relation_name, 10, attribute_length, attribute_format)
        self.metadata_manager.force_metadata()

relation_name = "R_1_10000"
attributes = ["NO", "VAL"]
attribute_types = ["int", "int"]
    

    