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
sumqueue = Queue()     #本轮剩余红包数量队列

groupinfoque = Queue()
# userqueue = queue.Queue() #本轮已经抢过红包队列

#数据库读写
from pymongo import MongoClient

luckytextpre3 = "触币-基于区块链的数字资产交易平台。全民签到领CHU币活动中。\
                每天9、12、18时准时发送红包，一共三次签到机会。签到已更新，大家快来签到吧！"
luckytextpre = "触币-基于区块链的数字资产交易平台。全民签到领CHU币活动中（每天签到3次，9、12、18时准时更新签到）。\
签到已更新，大家快来签到吧！"

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

def start(bot,update):
    logger.info("starting the bot for getting the group info %s" % update)

    if not groupinfoque.full():
        groupinfoque.put(update.message.chat.id)

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
    # create(bot,update)


def gethongbao(bot,query):

    if not gqueue.empty():

        
        client = MongoClient('localhost', 27017)
        db = client.test_database
        
        luckyuser = db.posts.find_one({'userid':query.from_user.id})

        luckychu = 0
        sumleft = 0
        if luckyuser is None:

            #get the random 
            luckychu = gqueue.get()
            
            if not sumqueue.empty():
                sumleft = sumqueue.get()
                sumleft -=  int(luckychu)
                sumqueue.put(sumleft)

            #----------------------------------------------------------
            print("hi {}, you are getting the locky money".format(query.from_user.first_name))
            db.posts.insert_one({'userid':query.from_user.id,'chunum':luckychu,'luckynum':luckychu,'isregister':False,'isGetCHU':True})

            bot.edit_message_text(text="hi {} {}, 抢到{}个CHU币".format(query.from_user.first_name,query.from_user.last_name,int(luckychu)),
                    chat_id=query.message.chat_id,
                    message_id=query.message.message_id)

        elif 'isGetCHU' in luckyuser and luckyuser['isGetCHU'] is False:

            #get the random 
            luckychu = gqueue.get()
            #left random lucky money
            if not sumqueue.empty():
                sumleft = sumqueue.get()
                sumleft -=  int(luckychu)
                sumqueue.put(sumleft)

            #----------------------------------------------------------

            luckyuser['chunum'] += luckychu
            luckyuser['luckynum'] = luckychu
            luckyuser['isGetCHU'] = True
            db.posts.replace_one({'userid':query.from_user.id},luckyuser)
            
            
            print("get the lucky coin : %s for %s " % (luckychu,query))
            bot.edit_message_text(text="hi {} {}, 抢到{}个CHU币".format(query.from_user.first_name,query.from_user.last_name,int(luckychu)),
                            chat_id=query.message.chat_id,
                            message_id=query.message.message_id)
        else:
            logger.info("current the sumleft is {}".format(sumleft))
            gsumleft = sumqueue.get()
            bot.edit_message_text(  text="hi {} {},你已抢过红包,已获得{}个CHU币,请3小时后再来,目前红包剩余{}/20，剩余CHU币{}个".format(query.from_user.first_name,query.from_user.last_name,int(luckyuser['luckynum']), gqueue.qsize(), gsumleft),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)       
            sumqueue.put(gsumleft)
        client.close()
        
    else:
        bot.edit_message_text(  text="hi {} {},当前不是发红包的时间，请3小时后再来".format(query.from_user.first_name,query.from_user.last_name),
                        chat_id=query.message.chat_id,
                        message_id=query.message.message_id)

def checkin(bot,query):
    client = MongoClient('localhost', 27017)
    db = client.test_database
    useritem = db.posts.find_one({'userid':query.from_user.id})
    
    print("useritem is {}".format(useritem))
    if useritem == None:

        db.posts.insert_one({'userid':query.from_user.id,'chunum':20,'isregister':True,'isGetCHU':False})
        bot.edit_message_text(  text="hi {} {},签到成功,已获得20个CHU币".format(query.from_user.first_name,query.from_user.last_name),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)

    elif 'isregister' in useritem and useritem['isregister'] is False:

        useritem["chunum"] += 20
        useritem['isregister'] = True
        
        db.posts.replace_one({'userid':query.from_user.id},useritem)
        bot.edit_message_text(  text="hi {} {},签到成功,已获得20个CHU币".format(query.from_user.first_name,query.from_user.last_name),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
    else:
        bot.edit_message_text(  text="hi {} {},今天已签过到".format(query.from_user.first_name,query.from_user.last_name),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)

    client.close()
    
def getthechuinfo(bot,query):
    client = MongoClient('localhost', 27017)
    db = client.test_database
    infoitem = db.posts.find_one({'userid':query.from_user.id})
    
    if infoitem is None:
        bot.edit_message_text(  text="hi {} {},未查到你任何信息，今天可以签到或者抢红包".format(query.from_user.first_name,query.from_user.last_name),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
    elif 'chunum' in infoitem:
        bot.edit_message_text(  text="hi {} {},共获得chu币总数为:{}".format(query.from_user.first_name,query.from_user.last_name,int(infoitem['chunum'])),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
    else:
        bot.edit_message_text(  text="hi {} {},未能查到任何信息，请与客服联系".format(query.from_user.first_name,query.from_user.last_name),
                                chat_id=query.message.chat_id,
                                message_id=query.message.message_id)
    print("query is")
    client.close()

def generate_random_integers(_sum, n):  
    mean = _sum / n
    variance = int(1 * mean)

    min_v = mean - variance
    max_v = 200 #mean + variance
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
    command_handler = CommandHandler("CHU币",create)
    command_start_handler = CommandHandler("start",start) #
    dispatcher.add_handler(echo_handler)
    dispatcher.add_handler(command_handler)
    dispatcher.add_handler(command_start_handler)
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
    listforgroupid = []
    while True:
        time.sleep(300)  #LUCKYINTERVAL

        #updater.bot.edit_message_text(  text="hi {},今天已签过到".format(query.from_user.first_name),
        #                         chat_id=query.message.chat_id,
        #                         message_id=query.message.message_id)
        while groupinfoque.qsize() != 0:

            groupchatid = groupinfoque.get()
            listforgroupid.append(groupchatid)
            logger.info("sending the info to chat {}".format(groupchatid))

            for tmid in range(3):
                logger.info("sending the info to chat {}".format(listforgroupid))
                updater.bot.send_message(chat_id=groupchatid, text = luckytextpre)

        for backtoqueue in listforgroupid:
            groupinfoque.put(backtoqueue)
            
        listforgroupid.clear()
            
                                
        rannum = generate_random_integers(500,20)

        client = MongoClient('localhost', 27017)
        db = client.test_database
        infoitem = db.posts.update_many({"isGetCHU":True},{'$set':{"isGetCHU":False}})
        client.close()

        while not gqueue.empty():
            gqueue.get()

        for i in rannum:
            print("put random number into gqueue %s" % i)
            gqueue.put(i)

        for gid in listforgroupid:
            logger.info("group id is {}".format(gid))
            groupinfoque.put(gid)

        while sumqueue.qsize() != 0:
            sumqueue.get()
                
        sumqueue.put(500)

def dailylucky():
    logger.info("starting change the database")
    client = MongoClient('localhost', 27017)
    db = client.test_database
    infoitem = db.posts.update_many({"isregister":True},{'$set':{"isregister":False}})
    client.close()

def runtimer():
    print("working on it", file=open("output.txt", "a"))

def scheduler():
    schedule.every().day.at("01:00").do(dailylucky)
    schedule.every().day.at("02:12").do(dailylucky)
    schedule.every().day.at("04:00").do(dailylucky)
    schedule.every().day.at("07:00").do(dailylucky)
    

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
         
        