from telethon import TelegramClient, sync

# These example values won't work. You must get your own api_id and
# api_hash from https://my.telegram.org, under API Development.
api_id = 346229
api_hash = 'b2d844fcd8cd5827457f3426dbd77513'

client = TelegramClient('session_name', api_id, api_hash)
client.start()

print(client.get_me().stringify())
messages = client.get_messages('@EOSCN',limit = 10)
for i in range(len(messages)):
    print ("%s,%s"%(i+1,messages[i].message))
#print("hello mesg %s, one is %s" % (messages,messages[0].message))
