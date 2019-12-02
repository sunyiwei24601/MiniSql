import win32com.client 
import json
import base64
metadata_filename = "metadata.json"
class UserSystem:
    def __init__(self):
        with open(metadata_filename) as f:
            try:
                self.j = json.load(f)
                self.user_information = self.j[2]
            except:
                self.j = [{},{}, {}]
                self.user_information = {}
        self.key = "database"
        pass

    def save_user_keys(self, user_name, key):
        user_name = self.encrypt(self.key, user_name)
        key = self.encrypt(self.key, key)
        self.user_information[user_name] = key 
        self.j[2] = self.user_information
        with open(metadata_filename, "w") as f:
            json.dump(self.j, f)
        
    def check_username(self, user_name):
        user_name = self.encrypt(self.key,user_name)
        if user_name in self.user_information:
            return True 
        else:
            return False
    
    def check_key(self, user_name, key):
        user_name = self.encrypt(self.key, user_name)
        key = self.encrypt(self.key, key)
        if self.user_information[user_name] == key:
            return True
        else:
            return False

    def encrypt(self, key, content): # key:密钥,content:明文   
        return  str(base64.encodestring(content.encode())  )
        
    def decrypt(self, key, content): # key:密钥,content:密文   
        EncryptedData = win32com.client.Dispatch('CAPICOM.EncryptedData')   
        EncryptedData.Algorithm.KeyLength = 5   
        EncryptedData.Algorithm.Name = 2   
        EncryptedData.SetSecret(key)   
        EncryptedData.Decrypt(content)   
        str = EncryptedData.Content   
        return str   

if __name__ == "__main__":
    user_system = UserSystem()
    user_system.save_user_keys("ys", "123456")
    user_system.save_user_keys("database", "111111")