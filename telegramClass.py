import commonFunctions
import sqliteClass

from telethon import TelegramClient, types, sync
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import GetFullChannelRequest
import re
import datetime as dt
import bcolors
import asyncio
import time
import pandas as pd
import os

# --------------------------------------------------------------------------------

def findContractInTelegramMessages(message, pattern):

    pattern = r'(\w*%s\w*)' % pattern # Not thrilled about this line
    coincidences = re.findall(pattern, str(message).upper())

    #print(coincidences)

    if len(coincidences) == 0:
        return coincidences

    # Delete all previous characters before "0X"
    coincidences = [re.sub(r'^.*?0X', "0X", coincidence) for coincidence in coincidences]

    # Remove duplicates
    coincidences = list(dict.fromkeys(coincidences))

    # Filter list elements below 42 characters long
    coincidences = [coincidence for coincidence in coincidences if len(coincidence) == 42]

    _len = len(coincidences)

    if _len <= 0:
        color = ""
    elif _len >= 2:
        color = bcolors.WARN
    else:
        color = bcolors.OKMSG

    commonFunctions.printInfo(coincidences, color)

    return coincidences

# --------------------------------------------------------------------------------

class telegram:

    def __init__(self, bscContractCsv, tradingType=2):
        self.bscContractCsv = bscContractCsv
        self.tradingType = tradingType

        # ------------------------------------------------

        self.telegramGroupNameDesc = "telegramGroupName"
        self.newTelegramGroupNameDesc = "newTelegramGroupName"

        # id,symbol,symbolName,slug,bscContract
        self.idDesc = "id"
        self.symbolDesc = "symbol"
        self.symbolNameDesc = "symbolName"
        self.slugDesc = "slug"
        self.bscContractDesc = "bscContract"

        self.newCryptosInCsvDf = sqliteClass.db().executeQuery(f"""
            SELECT
                id, symbol, symbolName, slug, contract
            FROM dimCryptos
            WHERE FK_typeId = {self.tradingType}
            """
        )

        # Do we need to write headers in the .csv file?
        if os.path.exists(self.bscContractCsv):
            self.newCryptosInCsvDf = pd.read_csv(self.bscContractCsv)
            self.writeNewCryptosCsvHeaders = False
        else:
            self.newCryptosInCsvDf = pd.DataFrame()
            self.writeNewCryptosCsvHeaders = True

        self.telegramBaseUrl = "https://t.me/"
        self.telegramBaseGroupName = "fairlaunchnewstoday"

        self.telegramGroupsMessageText = "Note: Any tokens can be honeypot, scam, so please Always Do Your Own Research before you jump into the Pools!"

        # Connect to Telegram. You must get your own api_id and api_hash from https://my.telegram.org, under API Development.
        self.api_id = 8005184  #number
        self.api_hash = "0a1269bec27d33b56e5351aff08fff41" #string
        self.phone_number = "+34634553557"

        # Papa credentials
        self.api_id2 = 8472425
        self.api_hash2 = "00790f70543b5a7f94547510d5ebbe84"
        self.phone_number2 = "+34635453357"

        # Let's start the code
        self.core()

    # --------------------------------------------------------------------------------

    def getNewCryptos(self, groupNamesList=None):

        if groupNamesList is None:
            groups = [self.telegramBaseGroupName]
        else:
            groups = groupNamesList
            newCryptoContracts = {}

        # Connect to telegram and get messages from there
        with TelegramClient('Marcos', self.api_id, self.api_hash) as client:

            if not client.is_user_authorized():
                client.send_code_request(self.phone_number)
                #me = client.sign_in(self.phone_number, input('Enter code: '))

            for group in groups:

                try:

                    commonFunctions.printInfo(group, bcolors.OK)

                    channel_entity = client.get_entity(group)

                    time.sleep(3)

                    # Default call, get group to search their contracts later
                    # if groupNamesList is None:

                    #     channel_info = client(GetFullChannelRequest(channel_entity))

                    #     pinned_msg_id = channel_info.full_chat.pinned_msg_id

                    #     commonFunctions.printInfo(pinned_msg_id)

                    # if groupNamesList is None and pinned_msg_id is not None:
                    #     posts = client(GetHistoryRequest(
                    #         channel_entity,
                    #         limit=1,
                    #         offset_date=None,
                    #         offset_id=pinned_msg_id + 1,
                    #         max_id=0,
                    #         min_id=0,
                    #         add_offset=0,
                    #         hash=0
                    #     ))

                    # else:
                    posts = client(GetHistoryRequest(
                        peer=channel_entity,
                        limit=100000,
                        offset_date=None,
                        offset_id=0,
                        max_id=0,
                        min_id=0,
                        add_offset=0,
                        hash=0
                    ))

                    commonFunctions.printInfo(f"posts.messages lenght = {len(posts.messages)}", bcolors.WARN)
                    # messages stored in 'posts.messages'

                    # We are trying to get all crypto groups
                    if groupNamesList is None:

                        newCryptos = []

                        for i, message in enumerate(posts.messages):
                            m = str(message.message)

                            # If the message contains a certain text, it's the right one (not 100% reliable...) 
                            if self.telegramGroupsMessageText in m:
                                print(m)
                                newCryptos = self.getAllTelegramGroupsByMessage(message=m)
                                break
                        
                        return newCryptos

                    else: # Let's find all the contracts

                        # Convert all messages to strings
                        allMessages = [str(m) for m in posts.messages]

                        # Lists items to a single string
                        allMessagesJoined = " ".join(allMessages)

                        # Find all possible contracts
                        contracts = findContractInTelegramMessages(message=allMessagesJoined, pattern="0X")

                        if len(contracts) == 1:
                            newCryptoContracts[group] = contracts[0]

                    commonFunctions.printInfo("---------------------------------------------------")

                except Exception as e:
                    commonFunctions.printInfo(e, bcolors.ERRMSG)

        # Print all valid contracts (if we only found 1 distinct contract in a group) of the Telegram groups
        for g, contract in newCryptoContracts.items():
            commonFunctions.printInfo(f"{g} = {contract}", bcolors.OKMSG)

        # Dict to pd.DataFrame() --> list(df.items()) is required for Python 3.x
        df = pd.DataFrame(list(newCryptoContracts.items()), columns=[self.newTelegramGroupNameDesc, self.bscContractDesc])

        # Check
        print(df)

        # The .csv file exists
        if not self.writeNewCryptosCsvHeaders:

            # Full join between the .csv pd.DataFrame() and the one obtained from the Telegram group
            newCryptosToInsert = self.newCryptosInCsvDf.set_index(self.bscContractDesc).combine_first(df.set_index(self.bscContractDesc)).reset_index()

            print(newCryptosToInsert)

            # Drop duplicates
            newCryptosToInsert.drop_duplicates(inplace=True)

            print(newCryptosToInsert)
            
            # Filter out the already existing contracts in the .csv file to insert only the new ones
            newCryptosToInsert = newCryptosToInsert[
                newCryptosToInsert[self.idDesc].isnull()
            ]

            print(newCryptosToInsert)

            # Select the only columns we need
            newCryptosToInsert = newCryptosToInsert[[self.newTelegramGroupNameDesc, self.bscContractDesc]]

            print(newCryptosToInsert)

        else: # The .csv file does not exists
            newCryptosToInsert = df

        print(newCryptosToInsert)

        # Don't insert or delete anything if there is not new cryptos to insert
        if len(newCryptosToInsert) == 0:
            commonFunctions.printInfo(f"No hay nuevas cryptos a insertar", bcolors.WARN)
            return

        # Create columns to union the data with the .csv later
        newCryptosToInsert[self.idDesc] = -1
        newCryptosToInsert[self.symbolDesc] = newCryptosToInsert[self.newTelegramGroupNameDesc]
        newCryptosToInsert[self.symbolNameDesc] = newCryptosToInsert[self.newTelegramGroupNameDesc]
        newCryptosToInsert[self.slugDesc] = newCryptosToInsert[self.newTelegramGroupNameDesc]

        # Union data
        newCryptosToInsert = pd.concat([self.newCryptosInCsvDf, newCryptosToInsert])

        print(newCryptosToInsert)

        # Drop duplicates by bscContract column
        newCryptosToInsert.drop_duplicates(subset=[self.bscContractDesc], inplace=True)

        # Reassign index
        newCryptosToInsert[self.idDesc] = newCryptosToInsert.reset_index().index

        print(newCryptosToInsert)

        # Select and reorder columns to insert in the .csv
        newCryptosToInsert = newCryptosToInsert[[self.symbolDesc, self.symbolNameDesc, self.slugDesc, self.bscContractDesc]]

        print(newCryptosToInsert)

        # Delete .csv file if exists
        if os.path.exists(self.bscContractCsv):
            os.remove(self.bscContractCsv)

        # Create file and insert data
        newCryptosToInsert.to_csv(self.bscContractCsv, index=False, columns=list(newCryptosToInsert), mode="a", header=True)


    # Scrap all Telegram groups in the message
    def getAllTelegramGroupsByMessage(self, message):

        #commonFunctions.printInfo(message)
        #message = message.split("𝗢𝗡𝗚𝗢𝗜𝗡𝗚 𝗪𝗛𝗜𝗧𝗘𝗟𝗜𝗦𝗧:")[0]
        #commonFunctions.printInfo(message)

        telegramGroups = []

        for word in message.split():
            if self.telegramBaseUrl in word and word != (self.telegramBaseUrl + self.telegramBaseGroupName):
                telegramGroups.append(word.replace(self.telegramBaseUrl, ""))

        # Remove duplicates
        telegramGroups = list(dict.fromkeys(telegramGroups))

        commonFunctions.printInfo(telegramGroups)

        return telegramGroups


    # ----------------------------------------------------------------------------------------

    # Main function of this class, we only need to call this one to execute the full code
    # What this code does is get all telegram groups from one group message and then access all the others to get all crypto contracts
    def core(self):
        newCryptos = self.getNewCryptos()
        self.getNewCryptos(groupNamesList=newCryptos)
