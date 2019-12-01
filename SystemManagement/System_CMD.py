import os
import sys
sys.path.append(os.getcwd())
from SystemManagement.System_Create import *
from SystemManagement.System_Select import *
from prettytable import PrettyTable
class Interative_Component:
    def __init__(self):
        pass

    def input_command(self):
        prompt = "Please input SQL command"
        print(prompt)
        sql_statements = input()
        executions = parser(sql_statements)
        for execution in executions:
            if execution == "create":
                Create_Execution()

        self.input_command()

    def output_tuples(self, tuples, limit=10):
        attributes = tuples.attributes
        records = tuples.records
        header = [ i.relation_name + "." + i.attribute for i in attributes]
        table = PrettyTable(header)
        for record in records[:10]:
            table.add_row(record)
        print(table)
        print("Total output_records have {} rows and {} columns".format(len(records), len(attributes)))

