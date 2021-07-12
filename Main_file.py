import pandas as pd
from telethon import TelegramClient, utils
from telethon.tl.types import InputPhoneContact
from telethon import functions, types
import random
import numpy as np
import asyncio
import time
from telethon.errors import FloodWaitError, PeerFloodError
import json
class Telegram_Marketing():
    def __init__(self, api_id, api_hash, phone, file_path,message ,  database_encryption_key='15035'):

        self.api_hash = api_hash
        self.api_id = api_id
        self.phone = phone
        self.file_path = file_path
        self.exit = False
        self.message = message
    async def login(self):
        try:
            self.client = TelegramClient('Main_script_Session', self.api_id, self.api_hash)
            await self.client.start()
            print('LOGGED IN SUCCESSFULLY')
        except Exception as e:
            print("ERROR LOGGING IN -> ERROR CODE:", e)

    async def add_contact(self, user_mobile, user_name):
        contact = InputPhoneContact(random.randint(0, 9999999), '+91' + user_mobile, user_name, "q")
        contacts = await self.client(functions.contacts.ImportContactsRequest([contact]))
        time.sleep(100)
        try:

            a1 = contacts.to_dict()['users'][0]['username']
            a2 = contacts.to_dict()['users'][0]['phone']
            a3 = contacts.to_dict()['users'][0]['id']
            return [a1, a2, a3]
        except PeerFloodError:
            self.exit = True
            print("ERROR IN ADDING CONTACT -> ERROR CODE: ", "PeerFloodError")
            return False
        except FloodWaitError:
            self.exit = True
            print("ERROR IN ADDING CONTACT -> ERROR CODE: ", "FloodWaitError")
            return False
        except Exception as e:
            print("ERROR IN ADDING CONTACT -> ERROR CODE: ",e)
            return False

    async def send_invite(self , number):
        try:
            contact = await self.client.get_entity('+91' + number)

            peer = utils.get_input_user(contact)
            result = await self.client(functions.messages.SendMessageRequest(peer, self.message))
            print("Message Send to:", number , "Message Details: ", self.message)
        except FloodWaitError:
            self.exit = True
            print("ERROR IN ADDING CONTACT -> ERROR CODE: ", "FloodWaitError")
        except PeerFloodError:
            self.exit = True
            print("ERROR IN ADDING CONTACT -> ERROR CODE: ", "PeerFloodError")

    def read_file(self):
        try:
            self.Data = pd.read_csv(self.file_path)
            if 'ADDED_TO_LIST' not in self.Data.columns:
                self.Data['ADDED_TO_LIST'] = False
                self.Data['Username'] = None
                self.Data['phone'] = None
                self.Data['chat_id'] = None
                self.Data['message'] = None
                print(self.Data)
                self.Data.to_csv(self.file_path, index=False)

        except Exception as e:
            print("ERROR IN READ_FILE -> ERROR CODE:", e)

    def launch_script(self):
        for index, row in self.Data.iterrows():
            if not row['ADDED_TO_LIST']:
                self.Data.at[index, 'ADDED_TO_LIST'] = True
                print("scanning:",row['Mobile'])
                temp = asyncio.get_event_loop().run_until_complete(self.add_contact(str(row['Mobile']), str(row['Company'])))

                if temp:
                    print("CONTACT ADDED: ", row['Mobile']," NAME: ", row['Company'])
                    a1, a2, a3 = temp[0], temp[1], temp[2]
                    asyncio.get_event_loop().run_until_complete(self.send_invite(str(row['Mobile'])))
                    time.sleep(300)
#                    #temp_list.append([row['Company'], row['Mobile'], a1, a2, a3])
                    self.Data.at[index, 'Username'], self.Data.at[index, 'phone'], self.Data.at[index, 'chat_id'], self.Data.at[index, 'message'] = a1, a2, a3, True
                self.Data.to_csv(self.file_path, index=False)

                if self.exit:
                    print("FLOOD ERROR GOING TO SLEEP")
                    break




def main():
    with open('configurations.json', 'r')as f:
        config = json.loads(f.read())

    api_hash = str(config['api_hash'])
    api_id = int(config['api_id'])
    phone = str(config['phone'])
    file_path = str(config['File Path'])
    message = str(config['message'])

    tb_object = Telegram_Marketing(api_id=api_id, api_hash=api_hash, phone=phone, file_path=file_path, message=message)
    asyncio.get_event_loop().run_until_complete(tb_object.login())
    tb_object.read_file()
    tb_object.launch_script()


main()