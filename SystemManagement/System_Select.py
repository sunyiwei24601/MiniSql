import sys
import os
sys.path.append(os.getcwd())
from SystemManagement.System_MetaData import *
from PageManager.RF_Manager import *
from PageManager.IX_Manager import *
from itertools import groupby
from operator import itemgetter
from SystemManagement.System_CMD import *
class Tuples:
    def __init__(self, records, attributes):
        self.records = records
        self.attributes = attributes

    def GetRecs(self):
        return self.records
    
    def GetAttributes(self):
        return self.attributes

class SelectExecutor():
    def  __init__(self, rm_manager, ix_manager, metadata_manager):
        self.rm_manager = rm_manager
        self.ix_manager = ix_manager
        self.rm_filescan = RM_FileScan()
        self.metadata_manager = metadata_manager
        pass 
    
    def SelectExecution(self, entity, conditions):
        if type(entity) == str:
            return self.SelectFromRelation(entity, conditions)
        elif type(entity) == Tuples:
            return self.SelectTuples(entity, conditions)
    
    def SelectFromRelation(self, relation_name, conditions):
        


        relation_metadata = self.metadata_manager.relation_data[relation_name]
        self.attribute_length = relation_metadata['attribute_total_length']
        self.attribute_format = relation_metadata['attribute_format']
        self.attributes = relation_metadata['attributes']
        self.relation_name = relation_name
        if conditions == None:
            key = list(self.attributes.keys())[0]
            conditions = {
                "type": "SEARCH",
                "op": NO_OP,
                "value": 0,
                "attribute": Attribute(relation_name, key)
            }

        self.rm_filehandle = self.rm_manager.OpenFile(relation_name, self.attribute_length, self.attribute_format)
        records = self.ExecuteConditions(conditions)
        attributes = [Attribute(relation_name, attribute) for attribute in self.attributes]
        return Tuples(records, attributes)
        
    def ExecuteConditions(self, conditions):

        if conditions["type"] in ("AND", "OR"):
            left_condition = conditions["left"]
            right_condition = conditions["right"]
            left_results = self.ExecuteConditions(left_condition)
            right_results = self.ExecuteConditions(right_condition)
            if conditions["type"] == "AND":
                return left_results & right_results
            elif conditions["type"] == "OR":
                return left_results | right_results
        elif conditions["type"] == "SEARCH":
            records = []
            #can be replaced later
            attribute = conditions['attribute'].attribute
            # attribute = conditions['attribute']
            op = conditions['op']
            value = conditions['value']
            offset = self.attributes[attribute]["offset"]
            ix_handle = self.ix_manager.OpenIndex(self.relation_name, offset)
            ix_indexscan = IX_IndexScan()
            ix_indexscan.OpenScan(ix_handle, op, value)
            for pageNum, slotNum in ix_indexscan.GetNextEntry():
                rm_record = self.rm_filehandle.GetRec(RID(pageNum, slotNum))
                record = rm_record.GetData()
                records.append(tuple(record))
            return set(records)

    def SelectTuples(self, tuples, conditions):
        records = tuples.GetRecs()
        self.attributes = tuples.GetAttributes()
        records = self.ExecuteTupleConditions(records, conditions)
        return Tuples(records, self.attributes)

    def ExecuteTupleConditions(self, records, conditions):
        if conditions["type"] in ("AND", "OR"):
            left_condition = conditions["left"]
            right_condition = conditions["right"]
            left_results = self.ExecuteTupleConditions(records, left_condition)
            right_results = self.ExecuteTupleConditions(records, right_condition)
            if conditions["type"] == "AND":
                return left_results & right_results
            elif conditions["type"] == "OR":
                return left_results | right_results
        elif conditions["type"] == "SEARCH":
            attribute = conditions['attribute']
            comop = conditions["op"]
            value = conditions['value']
            for i in range(len(self.attributes)):
                if self.attributes[i].relation_name == attribute.relation_name and \
                    self.attributes[i].attribute == attribute.attribute:
                    offset = i 
            records = self.check_records(records, offset, comop, value)
            return set(records)

    def check_records(self, records, offset, comop, value):
        results = []
        for record in records:
            target = record[offset]
            if comop == EQ_OP:
                if target == value:
                    results.append(record)
            elif comop == GT_OP:
                if target > value:
                    results.append(record)
            elif comop == LT_OP:
                if target < value:
                    results.append(record)
            elif comop == GE_OP:
                if target >= value:
                    results.append(record)
            elif comop == LE_OP:
                if target <= value:
                    results.append(record)
            elif comop == NE_OP:
                if target != value:
                    results.append(record)
        return results


class JoinExecutor():
    def __init__(self, rm_manager, ix_manager, metadata_manager):
        self.rm_manager = rm_manager
        self.ix_manager = ix_manager
        self.metadata_manager = metadata_manager
        self.rm_filescan = RM_FileScan()

    def JoinExecution(self, left_component, right_component, on_attributes):
        if type(left_component) == Tuples and type(right_component) == Tuples:
            return self.Tuple_Join_Tuple(left_component, right_component, on_attributes)
        elif type(left_component) == Tuples or type(right_component) == Tuples:
            return self.Tuple_Join_Relation(left_component, right_component, on_attributes)
        else:
            return self.Relation_Join_Relation(left_component, right_component, on_attributes)

    def Relation_Join_Relation(self, left_relation, right_relation, on_attributes):
        left_record_nums, left_attributes, left_file_handle = self.OpenRelation(left_relation)
        right_record_nums, right_attributes, right_file_handle = self.OpenRelation(right_relation)
        if left_record_nums <= right_record_nums:
            attributes = [*right_attributes, *left_attributes]
            outer_offset = self.check_attribute_offset(on_attributes, right_attributes)
            inner_offset = self.check_attribute_offset(on_attributes, left_attributes)
            outer_file_handle, inner_file_handle = right_file_handle, left_file_handle
            inner_relation_name = left_relation
        else:
            attributes = [*left_attributes, *right_attributes]
            outer_offset = self.check_attribute_offset(on_attributes, left_attributes)
            inner_offset = self.check_attribute_offset(on_attributes, right_attributes)
            outer_file_handle, inner_file_handle = left_file_handle, right_file_handle
            inner_relation_name = right_relation
        # use file scan to get outer relation, use index scan to get inner relation
        index_handle = self.ix_manager.OpenIndex(inner_relation_name, inner_offset)
        file_scan = self.rm_filescan.OpenScan(outer_file_handle)
        records = []
        for rid, outer_record in file_scan.GetNextRec():
            on_value = outer_record[outer_offset]
            index_scan = IX_IndexScan().OpenScan(index_handle, EQ_OP, on_value)
            for pageNum, slotNum in index_scan.GetNextEntry():
                inner_record = inner_file_handle.GetRec(RID(pageNum, slotNum))
                records.append((*outer_record, *inner_record.GetData()))
        return Tuples(records, attributes)

    def Tuple_Join_Relation(self, left_component, right_component, on_attributes):
        if type(left_component) == str:
            relation = left_component
            tuples = right_component
        else:
            relation = right_component
            tuples = left_component
        record_nums, relation_attributes, inner_file_handle = self.OpenRelation(relation)
        attributes = [*tuples.attributes, *relation_attributes]
        outer_offset = self.check_attribute_offset(on_attributes, tuples.attributes)
        inner_offset = self.check_attribute_offset(on_attributes, relation_attributes)
        
        # group the records by on_attribute
        records = []
        tuple_records = sorted(tuples.records, key=lambda x: x[outer_offset])
        previous_tuple_record = [None for i in range(len(tuple_records[0]))]
        index_handle = self.ix_manager.OpenIndex(relation, inner_offset)
        for tuple_record in tuple_records:
            if tuple_record[outer_offset] != previous_tuple_record[outer_offset]:
                on_value = tuple_record[outer_offset]
                index_scan = IX_IndexScan().OpenScan(index_handle, EQ_OP, on_value)
                temp_inner_records = []
                for pageNum, slotNum in index_scan.GetNextEntry():
                    
                    temp_inner_records.append(tuple(inner_file_handle.GetRec(RID(pageNum, slotNum)).GetData()))

            for temp_inner_record in temp_inner_records:
                records.append((*tuple_record, *temp_inner_record))
        return Tuples(records, attributes)
            
    def Tuple_Join_Tuple(self, left_tuple, right_tuple, on_attributes):
        outer_attributes, inner_attributes = left_tuple.attributes, right_tuple.attributes
        outer_offset = self.check_attribute_offset(on_attributes, outer_attributes)
        inner_offset = self.check_attribute_offset(on_attributes, inner_attributes)
        outer_records = sorted(left_tuple.records, key=lambda x:x[outer_offset])
        inner_records = sorted(right_tuple.records, key=lambda x:x[inner_offset])
        attributes = (*outer_attributes, *inner_attributes)

        #merge join 
        previous_outer_record = [None for i in range(len(outer_records[0]))]
        temp_outer_record = []
        inner_search_start = 0
        records = []
        for outer_record in outer_records:
            if outer_record[outer_offset] != previous_outer_record[outer_offset]:
                
                if len(temp_outer_record) != 0:
                    on_value = temp_outer_record[0][outer_offset]
                    inner_search_start, temp_inner_records = self.SearchInnerTempRecords(
                                inner_search_start, inner_records, inner_offset, on_value)
                    records += self.CombineRecords(temp_outer_record, temp_inner_records)
                previous_outer_record = outer_record
                temp_outer_record = [outer_record]
            else:
                temp_outer_record.append(outer_record)

        return Tuples(records, attributes)
                
    def SearchInnerTempRecords(self, inner_search_start, inner_records, inner_offset, on_value):
        records = []
        position = inner_search_start
        for record in inner_records[inner_search_start:]:
            if record[inner_offset] == on_value:
                records.append(tuple(record))
                position += 1
            else:
                break 
        return position, records


    def CombineRecords(self, temp_outer_record, temp_inner_record):
        records = []
        for outer_record in temp_outer_record:
            for inner_record in temp_inner_record:
                records.append((*outer_record, *inner_record))
        return records

    def check_attribute_offset(self, on_attributes, attributes):
        
        for on_a in on_attributes:
            offset = 0
            for attr in attributes:
                if on_a == attr:
                    return offset
                offset += 1
    
    def OpenRelation(self, relation_name):
        relation_metadata = self.metadata_manager.relation_data[relation_name]
        attribute_length = relation_metadata['attribute_total_length']
        attribute_format = relation_metadata['attribute_format']
        attributes = relation_metadata['attributes']
        # sort according to offset
        keys = [ i[0] for i in sorted(attributes.items(), key=lambda x: x[1]["offset"])]
        attributes = [Attribute(relation_name, i) for i in keys]

        rm_filehandle = self.rm_manager.OpenFile(relation_name, attribute_length, attribute_format)
        record_nums = rm_filehandle.header_page.record_nums
        return record_nums, attributes, rm_filehandle

class ProjectionExecutor():
    def __init__(self, rm_manager, ix_manager, metadata_manager):
        self.rm_manager = rm_manager
        self.ix_manager = ix_manager
        self.metadata_manager = metadata_manager
        self.rm_filescan = RM_FileScan()
        pass

    def ProjectionExecution(self, tuples, select_attributes):
        records = tuples.records
        attributes = tuples.attributes
        attribute_offsets = [self.get_attribute_offset(i, attributes) for i in select_attributes]
        records = [[record[i] for i in attribute_offsets] for record in records]
        attributes = select_attributes
        return Tuples(records, attributes)

    def get_attribute_offset(self, select_attribute, attributes):
        offset = 0
        for attr in attributes:
            if select_attribute == attr:
                return offset
            offset += 1


class OrderExecutor():
    def __init__(self):
        pass 

    def OrderExecution(self, tuples, value, limit, sort):
        attributes = tuples.attributes
        offset = self.check_attribute_offset(attributes, value)
        if sort == "desc":
            reverse = True
        else:
            reverse = False
        records = sorted(tuples.records, key=lambda x: x[offset], reverse=reverse)
        if limit:
            records = records[:limit]
        return Tuples(records, attributes)

    def check_attribute_offset(self, attributes, sort_attribute):
        offset = 0 
        for attr in attributes:
            if sort_attribute == attr:
                return offset 
            offset += 1

class Attribute:
    def __init__(self, relation_name, attribute, name=None):
        self.relation_name = relation_name
        self.attribute = attribute
        if name == None:
            self.name = relation_name + "." + attribute
        else:
            self.name = name

    def __eq__(self, att):
        if att.relation_name == self.relation_name and \
            att.attribute == self.attribute:
            return True
        else:
            return False

if __name__ == "__main__":
    select_conditions = {
        "type": "OR",
        "left": {
            "type": "AND",
            "left": {
                "type": "SEARCH",
                "attribute": Attribute("Rel_i_1_10000", "NO"),
                "op": GE_OP,
                "value": 10,
            },
            "right":{
                "type": "SEARCH",
                "attribute": Attribute("Rel_i_1_10000", "NO"),
                "op": LE_OP,
                "value": 100,
            }
        },
        "right":{
            "type":"SEARCH",
            "attribute": Attribute("Rel_i_1_10000", "VAL"),
            "op": GE_OP,
            "value": 1,
        }
    }


    tuple_conditions = {
        "type": "AND",
        "left": {
            "type": "Search",
            "attribute": Attribute("A", "NO"),
            "op": GE_OP,
            "value": 10,
        },
        "right":{
            "type": "Search",
            "attribute": Attribute("B", "VAL"),
            "op": LE_OP,
            "value": 1,
        }
    }
    attributes = [
        Attribute("A", "NO"),
        Attribute("A", "VAL"),
        Attribute("B", "NO"),
        Attribute("B", "VAL")
    ]

    pf_manager = PF_Manager()
    rm_manager = RM_Manager(pf_manager)
    ix_manager = IX_Manager()
    metadata_manager = MetaDataManager("metadata.json")
    select_executor = SelectExecutor(rm_manager, ix_manager, metadata_manager)
    join_executor = JoinExecutor(rm_manager, ix_manager, metadata_manager)
    project_executor = ProjectionExecutor(rm_manager, ix_manager, metadata_manager)
    io = Interative_Component()
    one_conditions ={
        "type": "SEARCH",
        "value": 100,
        "op": LE_OP,
        "attribute": Attribute("Rel_i_1_10000", "NO")
        
    }


    records = {(i, 1) for i in range(100)}
    left_tuples = Tuples(records, attributes[:2])
    # t = select_executor.SelectFromRelation("R_1_10000", select_conditions )
    # t = select_executor.SelectExecution(tuples, conditions=tuple_conditions)
    records = {(i,i) for i in range(50)}
    right_tuples = Tuples(records, attributes[2:])
    t = join_executor.JoinExecution(left_tuples, right_tuples, [Attribute("A", "NO"),Attribute("B", "VAL")])
    on_attributes = [Attribute("Rel_i_1_1000", "NO"), Attribute("B", "NO")]
    t = join_executor.JoinExecution("Rel_i_1_1000", right_tuples, on_attributes)
    project_attributes = [Attribute("Rel_i_1_1000", "VAL"), Attribute("B", "NO") ]
    p = project_executor.ProjectionExecution(t, project_attributes)
    io.output_tuples(p)
    
    pass
