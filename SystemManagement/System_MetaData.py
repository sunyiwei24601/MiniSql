from PageManager.IX_Manager import *
import json
class MetaDataManager:
    def __init__(self, fileName):
        with open(fileName) as f:
            try:
                self.data = json.load(f)
            except:
                self.data = [{}, {}, {}]
            self.relation_data = self.data[0]
            self.index_data = self.data[1]
            self.user_data = self.data[2]
        self.fileName = fileName

    def set_primary_key(self, relation_name, attributes):
        self.relation_data[relation_name]['primary_key'] = attributes
        
    def create_relation_data(self, relation_name, attributes, attribute_types, domains):
        if self.relation_data.get(relation_name, None) == None:
            self.relation_data[relation_name] = {}
            #maybe update if we get new attributes once at all 
            self.attribute_total_length = 0
            self.number_of_attributes = len(attributes)
            self.attribute_format = ""
        for offset in range(len(attributes)):
            attribute = attributes[offset]
            attribute_type = attribute_types[offset]
            domain = domains[offset]
            self.create_attribute_data(self, relation_name, attribute, attribute_type, domain, offset)
    
    def create_attribute_data(self, relation_name, attribute, attribute_type, domain, offset):
        relation = self.relation_data[relation_name]
        relation[attribute] = {}
        relation[attribute]["type"] = attribute_type
        relation[attribute]['length'] = self.get_attribute_length([attribute_type])
        relation[attribute]['offset'] = offset
        relation[attribute]['domain'] = domain

    def get_attribute_length(self, attribute_types):
        length = 0
        for attribute_type in attribute_types:
            if attribute_type == "int":
                length += 4
            if attribute_type == "float":
                length += 4
            if attribute_type == "long":
                length += 4
            if attribute_type[:6] == "string":
                length += int(attribute_type[6:])+1
        return length

    def get_attribute_format(self, attribute_types):
        fmt = ">"
        for attribute_type in attribute_types:
            if attribute_type == "int":
                fmt += "i"
            if attribute_type == "float":
                fmt += "f"
            if attribute_type == "long":
                fmt += "l"
            if attribute_type[:6] == "string":
                l = int(attribute_type[6:]) +1
                fmt += str(l) + "s"
        return fmt

    def create_index_data(self, relation_name, attribute, offset):
        if relation_name in self.index_data:
            if attribute not in self.index_data[relation_name]:
                self.index_data[relation_name][attribute] = offset
        else:
            self.index_data[relation_name] = {}
            self.index_data[relation_name][attribute] = offset

    def force_metadata(self):
        data = [self.relaiton_data, self.index_data, self.user_data]
        with open(self.fileName, 'w') as f:
            json.dump(data,f)
        

relaiton_data = {
    "student" : {
        "number_of_attributes": 4,
        "attribute_total_length": 16,
        "attribute_format": ">ii4sf",
        "attributes":{
            "NO": {
                "type": "int",
                "length": 4,
                "offset": 0,
                "domain": [
                    (GE_OP, 0)
                ]

            },
            "NUM":{
                "type": "int",
                "length": 4,
                "offset": 1,
                "domain": [
                    (GE_OP, 0)
                ]
            },
            "NAME":{
                "type": "string3",
                "length": 4,
                "offset": 2,
                "domain": [
                    (GE_OP, 0)
                ]
            },
            "GRADE":{
                "type": "float",
                "length": 4,
                "offset": 3,
            }
        },
        "primary_key":["NO"]
    }
}

index_data = {
    "student":{"NO":0, "GRADE":3 }
}

user_data = {
    "user1": "12345",
    "user2": "23456"
}