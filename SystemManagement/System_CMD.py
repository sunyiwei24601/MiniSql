import os
import sys
sys.path.append(os.getcwd())
from SystemManagement.System_Create import *


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

    def Create_Execution(self):
        pass

    def Insert_Execution(self):
        pass

    def Delete_Execution(self):
        pass 

    def Select_Execution(self):
        pass

    def Projection_Execution(self):
        pass

    def Join(self, Execution):
        pass

