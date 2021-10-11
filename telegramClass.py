from telethon import TelegramClient, types, sync
from telethon.tl.functions.messages import GetHistoryRequest

class telegram:

    def __init__(self):
        self.telegramBaseGroupName = "fairlaunchnewstoday"
        self.telegramBaseUrl = "https://t.me/"

        self.getUpcomingCryptos()

    def getUpcomingCryptos(self):

        # You must get your own api_id and api_hash from https://my.telegram.org, under API Development.
        api_id = 8005184  #number
        api_hash = "0a1269bec27d33b56e5351aff08fff41" #string
        phone_number = "+34634553557"

        # Connect to telegram and get messages from there
        with TelegramClient('Marcos', api_id, api_hash) as client:

            if not client.is_user_authorized():
                client.send_code_request(phone_number)
                me = client.sign_in(phone_number, input('Enter code: '))

            channel_entity = client.get_entity(self.telegramBaseGroupName)

            posts = client(GetHistoryRequest(
                peer=channel_entity,
                limit=10,
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0
            ))
            # messages stored in 'posts.messages'

            for i, message in enumerate(posts.messages):
                message = str(message.message)

                if len(message) > 500:
                    self.getAllTelegramGroupsByMessage(message)
                    break

            exit()

    def getAllTelegramGroupsByMessage(self, message):

        telegramGroups = [word.replace(self.telegramBaseUrl, "") for word in message.split()
            if self.telegramBaseUrl in word and word != (self.telegramBaseUrl + self.telegramBaseGroupName)]
        print(telegramGroups)
    

telegram()