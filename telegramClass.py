from telethon import TelegramClient, types, sync
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import GetFullChannelRequest
import re
import datetime as dt
import bcolors
import asyncio
import asyncstdlib
import time

# --------------------------------------------------------------------------------

def printInfo(desc, color=""):
    print(f"{dt.datetime.now()} // {color}{desc}{bcolors.END}")

def findContractInTelegramMessages(message, pattern):

    pattern = r'(\w*%s\w*)' % pattern # Not thrilled about this line
    coincidences = re.findall(pattern, str(message).upper())

    #print(coincidences)

    if len(coincidences) == 0:
        return coincidences

    # Delete all previous characters before "0X"
    coincidences = [re.sub(r'^.*?0X', '0X', coincidence) for coincidence in coincidences]

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

    printInfo(coincidences, color)

    return coincidences

# --------------------------------------------------------------------------------

class telegram:

    def __init__(self):

        self.telegramBaseUrl = "https://t.me/"
        self.telegramBaseGroupName = "fairlaunchnewstoday"

        # Connect to Telegram. You must get your own api_id and api_hash from https://my.telegram.org, under API Development.
        self.api_id = 8005184  #number
        self.api_hash = "0a1269bec27d33b56e5351aff08fff41" #string
        self.phone_number = "+34634553557"

        # Papa credentials
        self.api_id2 = 8472425
        self.api_hash2 = "00790f70543b5a7f94547510d5ebbe84"
        self.phone_number2 = "+34635453357"

        self.core()

    @asyncstdlib.lru_cache()
    async def get_entity(client, group):
        return await client.get_entity(group)

    def getUpcomingCryptos(self, groupNamesList=None):

        if groupNamesList is None:
            groups = [self.telegramBaseGroupName]
        else:
            groups = groupNamesList
            upcomingCryptoContracts = {}

        # Connect to telegram and get messages from there
        with TelegramClient('Marcos123', self.api_id, self.api_hash) as client:

            if not client.is_user_authorized():
                client.send_code_request(self.phone_number2)
                me = client.sign_in(self.phone_number2, input('Enter code: '))

            for group in groups:

                try:

                    printInfo(group, bcolors.OK)

                    channel_entity = client.get_entity(group)

                    time.sleep(3)

                    # Default call, get group to search their contracts later
                    # if groupNamesList is None:

                    #     channel_info = client(GetFullChannelRequest(channel_entity))

                    #     pinned_msg_id = channel_info.full_chat.pinned_msg_id

                    #     printInfo(pinned_msg_id)

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
                        limit=1000,
                        offset_date=None,
                        offset_id=0,
                        max_id=0,
                        min_id=0,
                        add_offset=0,
                        hash=0
                    ))
                    # messages stored in 'posts.messages'

                    # We are trying to get all crypto groups
                    if groupNamesList is None:

                        for i, message in enumerate(posts.messages):
                            m = str(message.message)

                            if len(m) > 1000:
                                upcomingCryptos = self.getAllTelegramGroupsByMessage(message=m)
                                return upcomingCryptos

                    else: # Let's find all the contracts

                        # Convert all messages to strings
                        allMessages = [str(m) for m in posts.messages]

                        # Lists items to string
                        allMessagesJoined = " ".join(allMessages)

                        # Find all possible contracts
                        contracts = findContractInTelegramMessages(message=allMessagesJoined, pattern="0X")

                        if len(contracts) == 1:
                            upcomingCryptoContracts[group] = contracts[0]

                    printInfo("---------------------------------------------------", bcolors.UNDERLINE)

                except Exception as e:
                    printInfo(e, bcolors.ERRMSG)


        for g, contract in upcomingCryptoContracts.items():
            printInfo(f"{g} = {contract}", bcolors.OKMSG)

    def getAllTelegramGroupsByMessage(self, message):

        telegramGroups = []

        for word in message.split():
            if self.telegramBaseUrl in word and word != (self.telegramBaseUrl + self.telegramBaseGroupName):
                telegramGroups.append(word.replace(self.telegramBaseUrl, ""))

        printInfo(telegramGroups)
        return telegramGroups
    
    def core(self):
        upcomingCryptos = self.getUpcomingCryptos()
        contracts = self.getUpcomingCryptos(groupNamesList=upcomingCryptos)

telegram()