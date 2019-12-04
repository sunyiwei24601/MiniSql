import os
import sys
sys.path.append(os.getcwd())
from SystemManagement.System_Create import *
from SystemManagement.System_Login import *
from QueryManager.carl_parser import *
from prettytable import PrettyTable
class Interactive_Component:
    def __init__(self):
        pass

    def input_command(self):
        # self.login()
        parser = Parser()
        while(True):
            prompt = "Please input SQL command:\n"
            sql_statement = input(prompt)
            result = parser.parse(sql_statement)
            self.output_tuples(result)


    def output_tuples(self, tuples, limit=102):
        attributes = tuples.attributes
        records = list(tuples.records)
        header = [ i.name for i in attributes]
        table = PrettyTable(header)
        for record in records[:10]:
            table.add_row(record)
        print(table)
        print("Total output_records have {} rows and {} columns".format(len(records), len(attributes)))

    def login(self):
        user_system = UserSystem()
        while(True):
            user_name = input("Please input username:")
            if user_system.check_username(user_name):
                
                key = input("Please input password:")
                if user_system.check_key(user_name, key):
                    break 
                else:
                    print("Password Error!")
                    continue
            else:
                print("Username Undetected")
        return True

if __name__ == "__main__":
    Interactive = Interactive_Component()
    Interactive.input_command()