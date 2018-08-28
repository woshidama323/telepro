# -*- coding: utf-8 -*-
from telegram.ext import Updater
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove,InlineKeyboardMarkup,InlineKeyboardButton)
import logging
import random

import asyncio

#解决一般函数不能用异步的方式的问题
from concurrent.futures import ThreadPoolExecutor
_executor = ThreadPoolExecutor(1)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

updater = Updater(token='570841543:AAGnlNIz7eTb-nmJ6QmiZ13cNVsIsGKR1HQ')

dispatcher = updater.dispatcher

def hello(bot,update):
    logger.info("Gender of %s: %s", update.message.from_user.first_name, update.message.text)
    #bot.send_message(chat_id=update.message.chat_id, text = update.message.text)
    #bot.send_message(chat_id='@helloeasy', text = update.message.text)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

def create(bot,update):
    print("hello update %s" % update)

    keyboard = [[InlineKeyboardButton("抢红包", callback_data='1'),
                 InlineKeyboardButton("发红包", callback_data='2')],

                [InlineKeyboardButton("签到", callback_data='3'),
                 InlineKeyboardButton("chu币排行", callback_data='4')]
               ]

    bot.send_message(chat_id='@helloeasy',
        text = '需要我做什么？',
        reply_markup=InlineKeyboardMarkup(keyboard))
    print("hello output, %s" % update.message)
    bot.send_message(chat_id='@helloeasy', text = 'my lord')
    
def button(bot, update):
    query = update.callback_query
    print("callback is %s" % query)
    if(query.data == '1'):
        print("get the data 1")
        gethongbao(bot,query)
    elif(query.data == '2'):
        print("get the data 2")
    create(bot,update)

def gethongbao(bot,query):
    from pymongo import MongoClient
    client = MongoClient('localhost', 27017)
    db = client.test_database
    print("hello is %s" % db)
    db.posts.insert_one({'what':'are your'})
    generate_random_integers(500,20)
    bot.edit_message_text(text="Selected option: {}".format(query.data),
                          chat_id=query.message.chat_id,
                          message_id=query.message.message_id)



def generate_random_integers(_sum, n):  
    mean = _sum / n
    variance = int(0.5 * mean)

    min_v = mean - variance
    max_v = mean + variance
    array = [min_v] * n

    diff = _sum - min_v * n
    while diff > 0:
        a = random.randint(0, n - 1)
        if array[a] >= max_v:
            continue
        array[a] += 1
        diff -= 1
    print(array)

def teleupdate():
    from telegram.ext import MessageHandler,Filters,CommandHandler,CallbackQueryHandler
    echo_handler = MessageHandler(Filters.text,hello)
    command_handler = CommandHandler("老单",create)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(command_handler)
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


async def asyncteleupdate():
    await loop.run_in_executor(_executor, teleupdate())

async def timerthread():
    import threading
    timethreading = threading.Timer(10,runtimer)
    print(timethreading)
    timethreading.start()


def runtimer():
    print("working on it", file=open("output.txt", "a"))

loop=asyncio.get_event_loop()
tasks=[timerthread(),asyncteleupdate()]
loop.run_until_complete(asyncio.gather(
                                    timerthread(),
                                    asyncteleupdate())
                       )
loop.close()