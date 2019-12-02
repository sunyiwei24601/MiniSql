class Symbol:
    def __init__(self, symbol_name, reference):
        self.symbol_name = symbol_name
        self.reference = reference

    def get_symbol_name(self):
        return self.symbol_name

    def get_reference(self):
        return self.reference


class Relation:
    def __init__(self, _name, attr_l):
        self._name = _name
        self.attr_l = attr_l

    def get_relation_name(self):
        return self._name

    def get_attributes(self):
        return self.attr_l

    def add_attr(self, attr):
        self.attr_l.append(attr)


class Attribute:
    def __init__(self, name, typ, relation):
        self._name = name
        self._typ = typ
        self._relation = relation

    def get_name(self):
        return self._name

    def get_typ(self):
        return self._typ

    def get_relation(self):
        return self._relation


def analysis_db(metadata):
    tab_l = []
    for key, value in metadata.items():
        tab_name = key
        attr_l = []
        for value_k, value_v in value.items():
            col_name = value_k
            col_typ = value_v
            attr = Attribute(col_name, col_typ, tab_name)
            attr_l.append(attr)
        tab_l.append(Relation(tab_name, attr_l))

    return tab_l


# if __name__ == '__main__':
#     R1_value = {'x': 'INT', 'y': 'INT', 'z': 'CHAR'}
#     R2_value = {'y': 'INT', 'm': 'INT', 'n': 'INT'}
#     db = {'R1': R1_value, 'R2': R2_value}
#     s = analysis_db(db)
#
#     tab_list = s[0]
#     attr_list = s[1]
#     for tab in tab_list:
#         print('table name is: ' + tab.get_relation_name())
#
#     for att in attr_list:
#         print('attribute name is: ' + att.get_name())
#         print('attribute type is: ' + att.get_typ())
