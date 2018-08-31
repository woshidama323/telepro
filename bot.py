# -*- coding: utf-8 -*-
from telegram.ext import Updater
from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove,InlineKeyboardMarkup,InlineKeyboardButton)
import logging
import random,time

import asyncio

#解决一般函数不能用异步的方式的问题
from multiprocessing import Pool, Queue
# import queue
import schedule


#全局变量==== 定时发红包时间
LUCKYINTERVAL = 3600*3

#全局队列
gqueue = Queue()     #红包生成queue
# userqueue = queue.Queue() #本轮已经抢过红包队列

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

    keyboard = [[InlineKeyboardButton("抢红包", callback_data='1')],   #,InlineKeyboardButton("发红包", callback_data='2')

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
    # elif(query.data == '2'):
    #     print("发红包=================")
    #     print("get the data 2")
        # checkin(bot,query)
    elif(query.data == '3'):
        print("签到=================")
        checkin(bot,query)
    elif(query.data == '4'):
        print("chu币排行=================")
        getthechuinfo(bot,query)
    create(bot,update)



def gethongbao(bot,query):


    if not gqueue.empty():

        client = MongoClient('localhost', 27017)
        db = client.test_database
        
        luckyuser = db.posts.find_one({'userid':query.from_user.id})
        luckychu = gqueue.get()

        if luckyuser is None:
            print("hi {}, you are getting the locky money".format(query.from_user.first_name))
            db.posts.insert_one({'userid':query.from_user.id,'chunum':luckychu,'isregister':False,'isGetCHU':True})

            bot.edit_message_text(text="hi {}, 你已经抢到过CHU币".format(query.from_user.first_name),
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id)

        elif 'isGetCHU' in luckyuser and luckyuser['isGetCHU'] is False:
            luckyuser['chunum'] += luckychu
            luckyuser['isGetCHU'] = True
            db.posts.replace_one({'userid':query.from_user.id},luckyuser)
            
            
            print("get the lucky coin : %s for %s " % (luckychu,query))
            bot.edit_message_text(text="hi {}, 抢到{}个CHU币".format(query.from_user.first_name,int(luckychu)),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)
        else:
            bot.edit_message_text(  text="hi {},你已抢过红包,已获得{}个CHU币,请3小时后再来".format(query.from_user.first_name,int(luckyuser['chunum'])),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)       
                        
        client.close()
        
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

        db.posts.insert_one({'userid':query.from_user.id,'chunum':20,'isregister':True,'isGetCHU':False})
        bot.edit_message_text(  text="hi {},签到成功,已获得20个CHU币".format(query.from_user.first_name),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)

    elif 'isregister' in useritem and useritem['isregister'] is False:

        useritem["chunum"] += 20
        useritem['isregister'] = True
        
        db.posts.replace_one({'userid':query.from_user.id},useritem)
        bot.edit_message_text(  text="hi {},签到成功,已获得20个CHU币".format(query.from_user.first_name),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
    else:
        bot.edit_message_text(  text="hi {},今天已签过到".format(query.from_user.first_name),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)

    client.close()
    
def getthechuinfo(bot,query):
    client = MongoClient('localhost', 27017)
    db = client.test_database
    infoitem = db.posts.find_one({'userid':query.from_user.id})
    
    if infoitem is None:
        bot.edit_message_text(  text="hi {},未查到你任何信息，今天可以签到或者抢红包".format(query.from_user.first_name),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
    elif 'chunum' in infoitem:
        bot.edit_message_text(  text="hi {},共获得chu币总数为:{}".format(query.from_user.first_name,int(infoitem['chunum'])),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
    else:
        bot.edit_message_text(  text="hi {},未能查到任何信息，请与客服联系".format(query.from_user.first_name),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
    print("query is")
    client.close()

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
    print("sending random number to the gqueue")
    import time
    while True:
        time.sleep(LUCKYINTERVAL)

        rannum = generate_random_integers(500,20)

        client = MongoClient('localhost', 27017)
        db = client.test_database
        infoitem = db.posts.update_many({"isGetCHU":True},{'$set':{"isGetCHU":False}})
        client.close()

        # with gqueue.mutex:
        #     gqueue.queue.clear()
        for i in rannum:
            print("put random number into gqueue %s" % i)
            gqueue.put(i)

def dailylucky():
    client = MongoClient('localhost', 27017)
    db = client.test_database
    infoitem = db.posts.update_many({"isregister":True},{'$set':{"isregister":False}})
    client.close()

def runtimer():
    print("working on it", file=open("output.txt", "a"))

def scheduler():
    schedule.every().day.at("16:00").do(dailylucky)

    while True:
        schedule.run_pending()
        time.sleep(60)
        print("working======")

    
if __name__ == '__main__':
    # queue = Queue()

    with Pool(processes=3) as pool:         # start 4 worker processes
        
        result1 = pool.apply_async(testprint)
        
        result2 = pool.apply_async(scheduler)
        
        result3 = pool.apply(teleupdate) 
         
        