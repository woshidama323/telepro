# -*- coding: utf-8 -*-
from telegram.ext import Updater
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove,InlineKeyboardMarkup,InlineKeyboardButton)
import logging
import random

import asyncio

#解决一般函数不能用异步的方式的问题
from multiprocessing import Pool
import queue


#全局变量==== 定时发红包时间
LUCKYINTERVAL = 3600*3

#全局队列
gqueue = queue.Queue()     #红包生成queue
userqueue = queue.Queue() #本轮已经抢过红包队列

#数据库读写
from pymongo import MongoClient



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
    # bot.send_message(chat_id='@helloeasy', text = 'my lord')
    
def button(bot, update):
    query = update.callback_query
    print("callback is %s" % query)
    if(query.data == '1'):
        print("抢红包=================")
        print("get the data 1")
        gethongbao(bot,query)
    elif(query.data == '2'):
        print("发红包=================")
        print("get the data 2")
        # checkin(bot,query)
    elif(query.data == '3'):
        print("签到=================")
        checkin(bot,query)
    elif(query.data == '4'):
        print("chu币排行=================")
        getthechuinof(bot,query)
    create(bot,update)



def gethongbao(bot,query):

    if query.from_user.id in userqueue.queue:
        bot.edit_message_text(text="hi {}, 你已经抢到过CHU币".format(query.from_user.first_name),
                chat_id=query.message.chat_id,
                message_id=query.message.message_id)
    else:
        if not gqueue.empty():
            
            print("hi {}, you are getting the locky money".format(query.from_user.first_name))
            luckychu = gqueue.get()
            client = MongoClient('localhost', 27017)
            db = client.test_database
            db.posts.insert_one({'userid':query.from_user.id,'chunum':luckychu})
            client.close()
            
            print("get the lucky coin : %s for %s " % (luckychu,query))
            bot.edit_message_text(text="hi {}, 抢到{}个CHU币".format(query.from_user.first_name,int(luckychu)),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)
        else:
            bot.edit_message_text(  text="hi {},当前不是发红包的时间，请3小时后再来".format(query.from_user.first_name),
                                    chat_id=query.message.chat_id,
                                    message_id=query.message.message_id)

def checkin(bot,query):
    client = MongoClient('localhost', 27017)
    db = client.test_database
    useritem = db.posts.find_one({'userid':query.from_user.id})
    
    print("useritem is {}".format(useritem))
    if useritem == None:

        db.posts.insert_one({'userid':query.from_user.id,'chunum':20})
        bot.edit_message_text(  text="hi {},签到成功,已获得20个CHU币".format(query.from_user.first_name),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)

    else:
        useritem["chunum"] += 20
        
        db.posts.replace_one({'userid':query.from_user.id},{'userid':query.from_user.id,'chunum':useritem["chunum"]})
        bot.edit_message_text(  text="hi {},签到成功,已获得20个CHU币".format(query.from_user.first_name),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)

    client.close()
    
def getthechuinof(bot,query):
    print("query is")

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
    return array

def teleupdate():
    from telegram.ext import MessageHandler,Filters,CommandHandler,CallbackQueryHandler
    echo_handler = MessageHandler(Filters.text,hello)
    command_handler = CommandHandler("老单",create)
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(command_handler)
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()


def timerthread():
    import threading
    timethreading = threading.Timer(10,runtimer)
    print(timethreading)
    timethreading.start()

def testprint():
    print("we have no ability to figure something out")
    import time
    while True:
        time.sleep(90)

        rannum = generate_random_integers(500,20)

        with gqueue.mutex:
            gqueue.clear()
        for i in rannum:
            print("put random number into gqueue %s" % i)
            gqueue.put(i)
    
        # client = MongoClient('localhost', 27017)
        # db = client.test_database
        # print("hello is %s" % db)
        # db.posts.insert_one({'what':'are your'})
        
        print("hello man time ")


def runtimer():
    print("working on it", file=open("output.txt", "a"))


if __name__ == '__main__':
    # queue = Queue()

    with Pool(processes=4) as pool:         # start 4 worker processes
        result = pool.apply_async(testprint)
        result = pool.apply(teleupdate) 
         
        