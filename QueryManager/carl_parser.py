import json 
import os
import sys
sys.path.append(os.getcwd())
from SystemManagement.System_Select import *
from moz_sql_parser import parse 
from PageManager.RF_Manager import *
from PageManager.IX_Manager import *
class Parser:
    def __init__(self):
        self.alias = {}
        pf_manager = PF_Manager()
        rm_manager = RM_Manager(pf_manager)
        ix_manager = IX_Manager()
        metadata_manager = MetaDataManager("metadata.json")
        self.select_executor = SelectExecutor(rm_manager, ix_manager, metadata_manager)
        self.join_executor = JoinExecutor(rm_manager, ix_manager, metadata_manager)
        self.project_executor = ProjectionExecutor(rm_manager, ix_manager, metadata_manager)
        self.order_executor = OrderExecutor()
        pass

    def parse(self, statements):
        self.alias = {}
        statements = parse(statements)
        from_statement = statements["from"]
        select_statement = statements["select"]
        where_statement = statements.get("where")
        order_statement = statements.get("orderby")
        limit = statements.get("limit")
        #join/from execution
        self.identify_alias(from_statement)
        from_execution = self.from_parse(from_statement)
        if from_execution[0] == "Relation":
            results = from_execution[1]
        elif from_execution[0] == "JOIN":
            left_component, right_componenet, on_attributes = from_execution[1:]
            results = self.join_executor.JoinExecution(left_component, right_componenet, on_attributes)

        #where execution
        if where_statement != None:
            conditions = self.where_parse(where_statement)
            results = self.select_executor.SelectExecution(results, conditions)
        elif type(results) == str:
            conditions = None
            results = self.select_executor.SelectExecution(results, conditions)
        
        #order_by
        if order_statement != None:
            sort, value = self.order_parse(order_statement)
            results = self.order_executor.OrderExecution(results, value, limit, sort)

            
        # projection execution
        if select_statement != "*":
            project_attributes = self.select_parse(select_statement)[1]
            results = self.project_executor.ProjectionExecution(results, project_attributes)
        

        return results


    def from_parse(self, statement):
        if type(statement) == str:
            return "Relation", statement
        elif type(statement) == dict:
            return "Relation", statement['value']
        elif len(statement) == 2:
            left_component = self.identify_relation(statement[0])
            right_componenet = self.identify_relation(statement[1]['join'])
            on_attributes = statement[1]['on']['eq']
            on_attributes = [self.attribute_parse(attribute) for attribute in on_attributes]
            
            return "JOIN", left_component, right_componenet, on_attributes

    def select_parse(self, statement):
        l = []
        if type(statement) == dict:
            l.append(self.attribute_parse(statement['value'], statement.get('name')))
        else:
            for i in statement:
                l.append(self.attribute_parse(i["value"], i.get('name')))
        select_attributes = l
        return "PROJECTION", select_attributes

    def where_parse(self, statement):
        result = {}
        for t in statement:
            if t == 'or':
                result["type"] = "OR"
                result['left'] = self.where_parse(statement[t][0])
                result['right'] = self.where_parse(statement[t][1])
                continue
            elif t == "and":
                result["type"] = "AND"
                result['left'] = self.where_parse(statement[t][0])
                result['right'] = self.where_parse(statement[t][1])
                continue 
            
            result["type"] = "SEARCH"
            result["op"] = self.identify_comop(t)
            result["attribute"] = self.attribute_parse(statement[t][0])
            result['value'] = statement[t][1]
            
            

        return result
                
    def identify_alias(self, from_statement):
        if type(from_statement) == dict:
            name = from_statement.get("name")
            value = from_statement.get("value")
            if name and value:
                self.alias[name] = value
            else:
                statement = from_statement.get("join")
                self.identify_alias(statement)
        if type(from_statement) == list:
            for statement in from_statement:
                self.identify_alias(statement)
        pass

    def attribute_parse(self,  attr , name=None):
        relation, attribute = attr.split(".")
        relation = self.alias.get(relation, relation)
        return Attribute(relation, attribute, name)
    
    def order_parse(self, order):
        sort = order.get("sort", "aesc")
        value = self.attribute_parse(order.get("value"))
        return sort, value
    
    def identify_relation(self, statement):
        if type(statement) == str:
            return statement
        else:
            return statement['value']

    def identify_comop(self, op):
        if op == "eq":
            return EQ_OP
        elif op == "lt":
            return LT_OP
        elif op == "gt":
            return GT_OP
        elif op == "lte":
            return LE_OP
        elif op == "gte":
            return GE_OP
        elif op == "neq":
            return NE_OP

if __name__ == "__main__":
    
    # s = """select Rel_i_1_1000.NO, Rel_i_i_1000.VAL from Rel_i_1_1000 join Rel_i_i_1000 on Rel_i_1_1000.NO =  Rel_i_i_1000.VAL where (Rel_i_1_1000.NO > 10 and Rel_i_i_1000.VAL <=100) and Rel_i_1_1000.VAL = 1 """
    s = """ select a.NO as NO, b.VAL from Rel_i_1_1000 as a join  Rel_i_i_1000 as b on a.NO = b.VAL"""
    parser = Parser()
    t = parser.parse(s)
    for i in t.attributes:
        print(i.name)
    pass