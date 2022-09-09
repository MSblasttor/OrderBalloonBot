#!/usr/bin/env python3
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import copy
import re

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from io import BytesIO

from mongodb import *

from settings import TG_TOKEN

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

START, CHANGE, FIO, TEL, FROM, DATE, LOCATION, ORDER, ORDER_CHANGE, ORDER_REMOVE, ORDER_EDIT, ORDER_SHOW, ORDER_ADD_ITEMS, LATEX, LATEX_SIZE, LATEX_COLOR, LATEX_COUNT, LATEX_PRICE, FOIL, FOIL_CHANGE, FOIL_FIG, FOIL_FIG_NAME, FOIL_FIG_COLOR, FOIL_FIG_PRICE, FOIL_NUM, FOIL_NUM_NAME, FOIL_NUM_COLOR, FOIL_NUM_PRICE, BUBL_COLOR, BUBL_INSERT, BUBL_PRICE, BUBL_SIZE, LABEL_NAME, LABEL_COLOR, LABEL_PRICE, STAND_NAME, STAND_PRICE, COMMENT = range(38)

state_machine = START
order_cnt = 0


def start(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    reply_keyboard = [['Заказ', 'Смета', 'Другое']]
    update.message.reply_text(
        'Привет! Меня зовут ШароБот. Я помогу тебе составить карточку заказа или расcчитать смету для заказчика '
        'Отправь /cancel что бы перестать разговаривать со мной\n\n'
        'Вы хотите оформить заказ или сделать смету?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Заказ или смета'
        ),
    )
    order_list=[]
    order_sheet = {'fio':0,'tel':0,'date':0,'location':0,'order_list':order_list, 'comment':0}
    context.user_data.update(order_sheet)
    print(user['id'])
    user = search_or_save_user(mdb, update.effective_user, update.message)  # получаем данные из базы данных
    print(user)
    #print(update.message.chat.id)
    global state_machine
    state_machine = CHANGE
    return CHANGE

def other(update: Update, context: CallbackContext) -> int:
    """Тестовая функция. Сюда пользователь попадает когда  нажимает в ответ боту - > Другое"""
    user = update.message.from_user
    logger.info(
        "Location of %s: %s", user.first_name, update.message.text 
    )
    keyboard = [
    [
            InlineKeyboardButton("Option 1", callback_data='1'),
            InlineKeyboardButton("Option 2", callback_data='2'),
        ],
        [InlineKeyboardButton("Option 3", callback_data='3')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
    'Данный раздел в разработке. Отправь команду /cancel чтобы начать сначала',
    reply_markup=reply_markup
    )
    with open("myevents.ics", 'rb') as tmp:
        obj = BytesIO(tmp.read())
        obj.name = 'myevents.ics'
        context.bot.send_document(update.message.from_user.id, document=obj, caption='myevents.ics')
    return ORDER_ADD_ITEMS

def change(update: Update, context: CallbackContext) -> int: # Сюда прилетают результаты выбора пользователя после старта
    global state_machine
    user = update.message.from_user
    if state_machine == CHANGE and  not update.message.text == 'Смета' :
            """Пользователь выбрал раздел заказ. Выводим предложение выбрать действие с заказом"""
            logger.info("%s приступил к оформлению -  %s", user.first_name, update.message.text)
            #update.message.reply_text('Отлично вы решил оформить заказ. Введите ФИО заказчика ') # Здесь написать операции с заказами
            reply_text="Так давай выберем что будем делать"
            reply_keyboard = [['Добавить новый заказ', 'Редактировать заказ', 'Удалить заказ'],['Вывести список заказов'],['Архив'],['Вернуться назад']]
            update.message.reply_text(
            reply_text,
            reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True 
            ),
            )
            state_machine = ORDER
    elif state_machine == CHANGE and update.message.text == 'Смета':
            """Пользователь приступил к оформлению сметы. Выводим предложение составить заказ"""
            logger.info("%s выбрала оформление сметы", user.first_name)
            reply_text="Отлично давай прикинем смету. Что будут заказывать?"
            reply_keyboard = [['Латекс', 'Фольга', 'Баблс'],['Стойка','Надпись','Другое'],['/end']]
            update.message.reply_text(
            reply_text,
            reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True 
            ),
            )
            state_machine = ORDER_ADD_ITEMS
    return state_machine

def order(update: Update, context: CallbackContext) -> int: # Здесь пользователь выбрал оформление заказа
    global state_machine
    user = update.message.from_user
    if state_machine == ORDER and  not update.message.text == 'Смета' :
            """Пользователь приступил к оформлению заказа. Выводим предложение ввести ФИО заказчика"""
            #Здесь необходимо прочитать крайнее значение номера заказа и увеличить его значение на 1 
            logger.info("%s приступил к оформлению -  %s", user.first_name, update.message.text)
            update.message.reply_text('Отлично вы решил оформить заказ. Введите ФИО заказчика ')
            state_machine = FIO
    elif state_machine == FIO:
            """Сохраняем фамилию имя отчество заказчика"""
            logger.info("ФИО Заказчика of %s: %s", user.first_name, update.message.text)
            # Сохраняем значение 
            key = 'fio'
            value = update.message.text
            context.user_data[key] = value
            update.message.reply_text(
                'ОК. Теперь введи номер телефона заказчика'
                'или отправь /skip если ты его не знаешь',
            )
            state_machine = TEL
    elif state_machine == TEL:
            """Сохраняем телефон заказчика"""
            logger.info("Номер телефона Заказчика of %s: %s", user.first_name, update.message.text)
            # Сохраняем значение 
            key = 'tel'
            value = update.message.text
            context.user_data[key] = value
            reply_text ='Хорошо. Теперь выберете откуда заказчик о вас узнал \n или отправь /skip если ты не знаешь'
            reply_keyboard = [['Инстаграм', 'Авито', 'ВКонтакте', 'Telegram', 'WhatshApp', 'Viber'],['Другое'], ['/skip']]
            update.message.reply_text(
            reply_text,
            reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True 
            ),
            )
            state_machine = FROM
    elif state_machine == FROM and (update.message.text == 'Инстаграм' or update.message.text == 'Авито' or update.message.text == 'ВКонтакте' or update.message.text == 'Telegram' or update.message.text == 'WhatshApp' or update.message.text == 'Viber'):
            """Сохраняем откуда заказчика"""
            logger.info("Заказчик пришел of %s: %s", user.first_name, update.message.text)
            # Сохраняем значение 
            key = 'from'
            value = update.message.text
            context.user_data[key] = value
            update.message.reply_text(
                'Отлично. Теперь введи дату и время когда планируется мероприятие (доставка)'
                'или отправь /skip если ты не знаешь или требует уточнения',
            )
            state_machine = DATE
    elif state_machine == FROM and update.message.text == 'Другое':
            """Сохраняем откуда заказчика"""
            logger.info("Заказчик пришел of %s: %s", user.first_name, update.message.text)
            update.message.reply_text(
                'Вы выбрали вариант \'Другое\'/n Укажите откуда заказчик'
                'или отправь /skip если ты не знаешь',
            )
            state_machine = FROM
    elif state_machine == FROM and not (update.message.text == 'Инстаграм' or update.message.text == 'Авито' or update.message.text == 'ВКонтакте' or update.message.text == 'Telegram' or update.message.text == 'WhatshApp' or update.message.text == 'Viber' or update.message.text == 'Другое'):
            """Сохраняем откуда заказчика"""
            logger.info("Заказчик пришел of %s: %s", user.first_name, update.message.text)
            # Сохраняем значение 
            key = 'from'
            value = update.message.text
            context.user_data[key] = value
            update.message.reply_text(
                'Отлично. Теперь введи дату и время когда планируется мероприятие (доставка)'
                'или отправь /skip если ты не знаешь или требует уточнения',
            )
            state_machine = DATE
    elif state_machine == DATE:
            """Сохраняем дату и время мероприятия заказчика"""
            logger.info("Дата проведения события %s: %s", user.first_name, update.message.text)
            # Сохраняем значение 
            key = 'date'
            value = update.message.text
            context.user_data[key] = value
            update.message.reply_text(
                'Отметь на карте геопозицию адреса доставки'
                'или отправь /skip заказ заберут самостоятельно',
                )
            state_machine = LOCATION
    elif state_machine == LOCATION:
            """Сохраняем место проведения мероприятия заказчика"""
            logger.info("Место проведения события %s: %s", user.first_name, update.message.text)
            # Сохраняем значение 
            key = 'location'
            value = update.message.text
            context.user_data[key] = value
            reply_text="Отлично давай прикинем смету. Что будут заказывать?"
            reply_keyboard = [['Латекс', 'Фольга', 'Баблс'],['Стойка','Надпись','Акссесуары'], ['Другое']]
            update.message.reply_text(
            reply_text,
            reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True 
            ),
            )
            state_machine = ORDER_ADD_ITEMS
    elif state_machine == ORDER and update.message.text == 'Смета':
            """Пользователь приступил к оформлению сметы. Выводим предложение составить заказ"""
            logger.info("%s выбрала оформление сметы", user.first_name)
            reply_text="Отлично давай прикинем смету. Что будут заказывать?"
            reply_keyboard = [['Латекс', 'Фольга', 'Баблс'],['Стойка','Надпись','Акссесуары'], ['Другое']]
            update.message.reply_text(
            reply_text,
            reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True 
            ),
            )
            state_machine = ORDER_ADD_ITEMS
    return state_machine

def list_order_view(update: Update, context: CallbackContext) -> int:
    global state_machine
    list_order(update, context)
    state_machine = ORDER_CHANGE
    return state_machine
    
def list_order(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    #print(update.message.text)
    #print(state_machine)
    logger.info("Пользователь %s запросил список заказов", user.first_name)
    order_list = list_order_from_db(mdb, update)
    reply_keyboard = [[],[]]
    reply_text = "Вот список ваших заказов: \n"
    cnt = 0
    for order in order_list:
        cnt += 1
        reply_text += "%d\n" % order['order_cnt']
        reply_keyboard[0].append(str(order['order_cnt']))
    reply_keyboard[1].append('Вернуться назад')
    update.message.reply_text(reply_text,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return cnt

def show_list_order(update: Update, context: CallbackContext) -> int:
    global state_machine
    user = update.message.from_user
    list_order(update, context)
    if update.message.text == "Редактировать заказ" or state_machine != ORDER:
        logger.info("Пользователь %s запросил список заказов для редактирования", user.first_name)
        context.user_data['last_msg'] = update.message.text
        #print(context.user_data)
        state_machine = ORDER_CHANGE
        #print(state_machine)
    else:
        logger.info("Пользователь %s попал в else в функции show_list_order", user.first_name)
        context.user_data['last_msg'] = update.message.text
        state_machine = ORDER_CHANGE
    return state_machine

def select_order(update: Update, context: CallbackContext) -> int:
    global state_machine
    user = update.message.from_user
    if state_machine == ORDER_CHANGE and (update.message.text != 'Состав заказа' and update.message.text != 'Изменить заказ' and update.message.text != 'Удалить заказ' and update.message.text != 'В архив' and context.user_data['last_msg'] != "Редактировать заказ"):
        logger.info("Пользователь %s выбрал заказ %d", user.first_name, int(update.message.text))
        context.user_data['select_order'] = int(update.message.text)
        reply_keyboard = [['Состав заказа', 'Изменить заказ','Удалить заказ'],['В архив'],['Вернуться назад']]
        reply_text = "Выберите что сделать с заказом: \n"
        update.message.reply_text(reply_text,reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    elif state_machine == ORDER_CHANGE and update.message.text == 'Состав заказа':
        logger.info("Пользователь %s выбрал заказ %d чтобы посмотреть состав", user.first_name, context.user_data['select_order'])
        show_order(update, context)
    elif state_machine == ORDER_CHANGE and update.message.text == 'Изменить заказ':
        logger.info("Пользователь %s выбрал заказ %d чтобы изменить", user.first_name, context.user_data['select_order'])
        edit_order(update,context)
    elif state_machine == ORDER_CHANGE and update.message.text == 'Удалить заказ':
        logger.info("Пользователь %s выбрал заказ %d чтобы удалить", user.first_name, context.user_data['select_order'])
        remove_order(update, context)
    elif state_machine == ORDER_CHANGE and update.message.text == 'В архив':
        logger.info("Пользователь %s выбрал заказ %d чтобы отправить в архив", user.first_name, context.user_data['select_order'])
        #show_order(update, context)
    elif state_machine == ORDER_CHANGE and context.user_data['last_msg'] == "Редактировать заказ":
        context.user_data['select_order'] = int(update.message.text)
        logger.info("Пользователь %s выбрал заказ %d чтобы отредактировать", user.first_name, context.user_data['select_order'])
        edit_order(update, context)
    else:
        logger.info("Пользователь %s выбрал заказ %d чтобы отредактировать, но попал в else в этот момент был state_machine =%d", user.first_name, context.user_data['select_order'],state_machine)
    return state_machine

def show_order(update: Update, context: CallbackContext) -> int:
    global state_machine
    order = {}
    user = update.message.from_user
    if state_machine == ORDER_CHANGE:
        #state_machine = CHANGE
        # Сюда вставить функцию вывода состава заказа из БД
        order_num = context.user_data['select_order']
        order = show_order_user_from_db(mdb, update, order_num)
        #print(show_order_user_from_db(mdb, update, order_num))
        text = "Заказ № "+ str(context.user_data['select_order']) +":\n"
        text += "ФИО:"+ order['fio']+"\n"
        text += "Телефон:"+ order['tel']+"\n"
        text += "Дата:"+ order['date']+"\n"
        text += "Адрес:"+ order['location']+"\n"
        text += make_msg_order_list(order)
        update.message.reply_text(text)
        update.message.text = order_num
        select_order(update, context)
    #elif state_machine == ORDER_CHANGE:
        
    #else
        
    return state_machine

def edit_order(update: Update, context: CallbackContext) -> int:
    global state_machine
    user = update.message.from_user
    if (state_machine == ORDER or state_machine == ORDER_CHANGE) and (update.message.text != 'ФИО' and update.message.text != 'Телефон' and update.message.text != 'Дата и время' and update.message.text != 'Состав заказа' and update.message.text != 'Архив' and update.message.text != 'Оплата'):
        state_machine = ORDER_EDIT
        # Сюда вставить функцию редактирования заказа из БД
        logger.info("Пользователь %s выбрал заказ %d чтобы отредактировать", user.first_name, context.user_data['select_order'])
        reply_keyboard_edit_order = [['ФИО', 'Телефон','Дата и время', 'Адрес'],['Оплата'],['Состав заказа'],['В архив'],['Вернуться назад']]  #TODO: Сделать функцию по редактированию заказа в части оплаты и отправки заказов в архив.
        reply_text = "Выберите что изменить: \n"
        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard_edit_order, one_time_keyboard=True))
    elif state_machine == ORDER_EDIT and update.message.text == 'ФИО':
        logger.info("Пользователь %s выбрал заказ %d чтобы отредактировать ФИО", user.first_name, context.user_data['select_order'])
        context.user_data['last_msg'] = update.message.text
        text = "Введите новые ФИО"
        update.message.reply_text(text)
    elif state_machine == ORDER_EDIT and context.user_data['last_msg'] == 'ФИО':
        logger.info("Пользователь %s выбрал заказ %d и отредактировал %s", user.first_name, context.user_data['select_order'], context.user_data['last_msg'])
        #Сюда вставить функцию по изменению ФИО (Телефон, Дата, Место) в заказе
        edit_order_user_from_db(mdb, update, context.user_data['select_order'], 'fio', update.message.text)
        context.user_data['last_msg'] = update.message.text
        text = "В заказе №"+str(context.user_data['select_order'])+" фамилия изменена на "+update.message.text
        update.message.reply_text(text)
        state_machine = CHANGE
        change(update, context)
    elif state_machine == ORDER_EDIT and update.message.text == 'Телефон':
        logger.info("Пользователь %s выбрал заказ %d чтобы отредактировать Телефон", user.first_name, context.user_data['select_order'])
        context.user_data['last_msg'] = update.message.text
        text = "Введите новые телефон заказчика"
        update.message.reply_text(text)
    elif state_machine == ORDER_EDIT and context.user_data['last_msg'] == 'Телефон':
        if re.fullmatch(r'((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}', update.message.text):
            logger.info("Пользователь %s выбрал заказ %d и отредактировал %s", user.first_name, context.user_data['select_order'], context.user_data['last_msg'])
            #Сюда вставить функцию по изменению ФИО (Телефон, Дата, Место) в заказе
            edit_order_user_from_db(mdb, update, context.user_data['select_order'], 'tel', update.message.text)
            context.user_data['last_msg'] = update.message.text
            text = "В заказе №"+str(context.user_data['select_order'])+" телефон изменен на "+update.message.text
            update.message.reply_text(text)
            state_machine = CHANGE
            change(update, context)
        else:
            text = "Введите номер телефона в формате +7 999 123 44 55"
            update.message.reply_text(text)
    elif state_machine == ORDER_EDIT and update.message.text == 'Дата и время':
        logger.info("Пользователь %s выбрал заказ %d чтобы отредактировать дату и время", user.first_name, context.user_data['select_order'])
        context.user_data['last_msg'] = update.message.text
        text = "Введите новые дату и время"
        update.message.reply_text(text)
    elif state_machine == ORDER_EDIT and context.user_data['last_msg'] == 'Дата и время':
        if re.fullmatch(r'[0-3]?[0-9].[0-3]?[0-9].(?:[0-9]{2})?[0-9]{2} (?:[01][0-9]|2[0-3]):[0-5][0-9]', update.message.text):
            logger.info("Пользователь %s выбрал заказ %d и отредактировал %s", user.first_name, context.user_data['select_order'], context.user_data['last_msg'])
            #Сюда вставить функцию по изменению ФИО (Телефон, Дата, Место) в заказе
            edit_order_user_from_db(mdb, update, context.user_data['select_order'], 'date', update.message.text)
            context.user_data['last_msg'] = update.message.text
            text = "В заказе №"+str(context.user_data['select_order'])+" дата и время изменена на "+update.message.text
            update.message.reply_text(text)
            state_machine = CHANGE
            change(update, context)
        else:
            text = "Введите дату мероприятия в формате дд-мм-гг ЧЧ:ММ"
            update.message.reply_text(text)
    elif state_machine == ORDER_EDIT and update.message.text == 'Адрес':
        logger.info("Пользователь %s выбрал заказ %d чтобы отредактировать адрес", user.first_name, context.user_data['select_order'])
        context.user_data['last_msg'] = update.message.text
        text = "Введите новый адрес"
        update.message.reply_text(text)
    elif state_machine == ORDER_EDIT and context.user_data['last_msg'] == 'Адрес':
        logger.info("Пользователь %s выбрал заказ %d и отредактировал %s", user.first_name, context.user_data['select_order'], context.user_data['last_msg'])
        #Сюда вставить функцию по изменению ФИО (Телефон, Дата, Место) в заказе
        edit_order_user_from_db(mdb, update, context.user_data['select_order'], 'location', update.message.text)
        context.user_data['last_msg'] = update.message.text
        text = "В заказе №"+str(context.user_data['select_order'])+" адрес изменен на "+update.message.text
        update.message.reply_text(text)
        state_machine = CHANGE
        change(update, context)
    #else
    return state_machine

def remove_order(update: Update, context: CallbackContext) -> int:
    global state_machine
    user = update.message.from_user
    logger.info("Пользователь %s приступил к редактированию заказов. Удаление ", user.first_name)
    if state_machine == ORDER_REMOVE:
        state_machine = CHANGE
        # Сюда вставить функцию удаления заказа из БД
        text = "Заказ "+ update.message.text +" удален."
        update.message.reply_text(text)
        change(update, context)
    elif state_machine == ORDER_CHANGE:
        state_machine = CHANGE
        # Сюда вставить функцию удаления заказа из БД
        text = "Заказ "+ str(context.user_data['select_order']) +" удален."
        update.message.reply_text(text)
        change(update, context)
    else:
        context.user_data['order_cnt'] = list_order(update, context)
        state_machine = ORDER_REMOVE
        if context.user_data['order_cnt'] != 0:
            msg = 'Введите номер заказа который хотите УДАЛИТЬ'
            update.message.reply_text(msg)
        else:
            update.message.reply_text('Похоже нет заказов. Удалять нечего.')
    return state_machine

def order_insert(update: Update, context: CallbackContext) -> int:
    """Функция для добавления в заказ еще позиций"""
    global state_machine
    reply_text="Добавить в заказ ещё что-нибудь? Что-бы закончить отправь команду /end"
    reply_keyboard = [['Латекс', 'Фольга', 'Баблс'],['Стойка','Надпись','Акссесуары'], ['Другое'], ['/end']]
    update.message.reply_text(
    reply_text,
    reply_markup=ReplyKeyboardMarkup(
    reply_keyboard, one_time_keyboard=True 
    ),
    )
    state_machine = ORDER_ADD_ITEMS
    return state_machine

def remove_items_from_order(update: Update, context: CallbackContext) -> int:
    global state_machine
    #global order_list
    user = update.message.from_user
    logger.info("Пользователь %s приступил к редактированию заказа. Удаление ", user.first_name)
    if state_machine == ORDER_ADD_ITEMS and update.message.text != '/remove':
        """Usage: /remove № items"""
        # Seperate ID from command
        #key = int(context.args[0])
        key = int(update.message.text)
        if key <= len(context.user_data['order_list']):
            context.user_data['order_list'].pop(key - 1)
            state_machine = end(update, context)
        else:
            msg = 'Не верное значение! Введите номер позиции от 1 до %d' % len(context.user_data['order_list'])
            update.message.reply_text(msg)
    else:
        if len(context.user_data['order_list']) != 0:
            msg = 'Введите номер позиции от 1 до %d которую хотите убрать из заказа' % len(context.user_data['order_list'])
            update.message.reply_text(msg)
        else:
            update.message.reply_text('Похоже в вашем заказе пусто. Удалять нечего. \nДля продолжения введите одну из следующих команд:\n/add - чтобы добавить в заказ еще позиции\n/remove - чтобы удалить из списка заказа позицию\n/edit - чтобы откорректировать позицию из списка заказа\n/comment - добавить коментарий к заказу\n/finish - чтобы завершить оформление')
    return state_machine

def skip(update: Update, context: CallbackContext) -> int: # Здесь пользователь пропускает шаги
    """Skips the location and asks for info about the user."""
    user = update.message.from_user
    global state_machine
    if update.message.text == '/skip' and state_machine == TEL:
        state_machine = DATE
        logger.info("Пользователь %s не прислал номер телефона заказчика", user.first_name)
        reply_text='Плохо что нет номера заказчика, лучше уточнить на будушее. Теперь пришли дату мероприятия, или отправь /skip.'
        update.message.reply_text(reply_text)
    if update.message.text == '/skip' and state_machine == FROM:
        state_machine = DATE
        logger.info("Пользователь %s не прислал откуда заказчик", user.first_name)
        reply_text='Плохо что неизвестно откуда заказчик, лучше уточнить на будушее. Теперь пришли дату мероприятия, или отправь /skip.'
        update.message.reply_text(reply_text)
    elif update.message.text == '/skip' and state_machine == DATE:
        state_machine = LOCATION
        logger.info("Пользователь %s не прислал дату", user.first_name)
        reply_text='Неопределенность всегда плохо, лучше уточнить на будушее. Теперь пришли место проведения или доставки, или отправь /skip.'
        update.message.reply_text(reply_text)
    elif update.message.text == '/skip' and state_machine == LOCATION:
        state_machine = ORDER_ADD_ITEMS
        logger.info("Пользователь %s Заказ заберут самостоятельно", user.first_name)
        # Сохраняем значение 
        key = 'location'
        value = 'Самовывоз'
        context.user_data[key] = value
        reply_keyboard = [['Латекс', 'Фольга', 'Баблс'],['Стойка','Надпись','Другое']]
        reply_text="Отлично! заказ заберут самостоятельно. Давай теперь определимся что будут заказывать?"
        update.message.reply_text(
            reply_text,
            reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True))
    elif update.message.text == '/skip':
        logger.info("%s команда /skip", user.first_name)
        reply_text="Как ты сюда попал? Введи команду /cancel и попробуем снова"
        update.message.reply_text(reply_text)
    else:
        logger.info("%s не предоставил гелокацию доставки", user.first_name)
        reply_text="Ну это уже не в какие рамки. Что будут заказывать?"
        reply_keyboard = [['Латекс', 'Фольга', 'Баблс'],['Стойка','Надпись','Другое']]
        update.message.reply_text(
            reply_text,
            reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True 
            ),
        state_machine = ORDER_ADD_ITEMS
        )
    return state_machine

def latex(update: Update, context: CallbackContext) -> int: # Здесь пользователь выбрал добавить в заказ латекс
    global state_machine
    user = update.message.from_user
    if state_machine == ORDER_ADD_ITEMS:
        """Пользователь выбрал шар латекс"""
        #Добавляем во внутрь словаря пользователя новый словарь с карточкой заказа
        key = 'order_dict'
        order_dict = {'type':0,'size':0,'color':0,'name':0,'count':0,'price':0,'summa':0,'comment':0}
        value = order_dict
        context.user_data[key] = value
        # Сохраняем значение типа 
        key = 'type'
        value = 'latex'
        context.user_data['order_dict'][key] = value
        key = 'name'
        value = update.message.text
        context.user_data['order_dict'][key] = value
        logger.info("%s: %s", user.first_name, update.message.text)
        reply_keyboard = [['5"', '12"', '18"'],['14"', '24"', '36"']]
        update.message.reply_text(
        'Укажи размер шара',
        reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder='Размер ...'
        ),
        )
        state_machine = LATEX_SIZE
    elif state_machine == LATEX_SIZE:
        """Пользователь выбрал размер шара латекс"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем значение размера
        key = 'size'
        value = update.message.text
        context.user_data['order_dict'][key] = value
        reply_keyboard = [['Серебро', 'Золото'], ['Розовое золото хром', 'Розовое золото'], ['Красный', 'Синий', 'Зеленый'], ['Белый', 'Черный', 'Жёлтый'], ['Белый песок', 'Эвкалипт', 'Бирюза'], ['Конфетти'], ['/end']]
        update.message.reply_text(
        'Укажи цвет шара\n (выберите из списка или введите вручную)',
        reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder='Цвет фигуры ...'
        ),
        )
        state_machine = LATEX_COLOR
    elif state_machine == LATEX_COLOR:
        """Пользователь выбрал цвет шара латекс"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем значение цвета
        key = 'color'
        value = update.message.text
        context.user_data['order_dict'][key] = value # order_dict[key] = value
        update.message.reply_text('Укажи количество шаров')
        state_machine = LATEX_COUNT
    elif state_machine == LATEX_COUNT:
        """Пользователь выбрал кол-во шаров латекс"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем значение количества
        key = 'count'
        value = int(update.message.text)
        context.user_data['order_dict'][key] = value        # order_dict[key] = value
        update.message.reply_text('Укажи цену шара')
        state_machine = LATEX_PRICE
    elif state_machine == LATEX_PRICE:
        """Пользователь указал цену шара латекс"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем значение цены
        key = 'price'
        value = int(update.message.text)
        context.user_data['order_dict'][key] = value
        key = 'count'
        value_cnt = context.user_data['order_dict'][key] 
        summa = value * value_cnt
        key = 'summa'
        context.user_data['order_dict'][key] = summa
        print(context.user_data)
        dict2=copy.deepcopy(context.user_data['order_dict'])
        order_list = context.user_data['order_list']
        order_list.append(dict2)
        print(order_list)
        context.user_data['order_list'] = order_list
        state_machine = order_insert(update, context)
    else:
        """Сюда попадаем если не подошло не одно из значений"""
        #logger.info("%s команда /skip", user.first_name)
        reply_text="Как ты сюда попал? Введи команду /cancel и попробуем снова"
        update.message.reply_text(reply_text)
    return state_machine

def foil(update: Update, context: CallbackContext) -> int: # Здесь пользователь выбрал добавить в заказ фольгу
    global state_machine

    user = update.message.from_user
    if state_machine == ORDER_ADD_ITEMS:
        """Пользователь выбрал фольгу"""
        #Добавляем во внутрь словаря пользователя новый словарь с карточкой заказа
        key = 'order_dict'
        order_dict = {'type':0,'size':0,'color':0,'name':0,'count':0,'price':0,'summa':0,'comment':0}
        value = order_dict
        context.user_data[key] = value
        logger.info("%s: %s", user.first_name, update.message.text)
        reply_keyboard = [['Фигура', 'Цифра']]
        update.message.reply_text(
        'Выберите тип шара',
        reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder='Тип шара ...'
        ),
        )
        state_machine = FOIL_CHANGE
    elif state_machine == FOIL_CHANGE and update.message.text == 'Фигура':
        """Пользователь выбрал тип шара ФИГУРА"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # clear_ORDER_ADD_ITEMS_sheet() #Очищаем карточку товара перед заполнением
        # Сохраняем значение типа 
        key = 'type'
        value = 'foil_fig'
        context.user_data['order_dict'][key] = value        # order_dict[key] = value
        reply_keyboard = [['Сердце', 'Звезда', 'Круг', 'Другое']]
        update.message.reply_text(
        'Выберите тип шара',
        reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder='Тип шара ...'
        ),
        )
        state_machine = FOIL_FIG_NAME
    elif state_machine == FOIL_FIG_NAME and (update.message.text == 'Сердце' or update.message.text == 'Звезда' or update.message.text == 'Круг'):
        """Пользователь указал название ФИГУРЫ"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем название фигуры 
        key = 'name'
        value = update.message.text
        context.user_data['order_dict'][key] = value        # order_dict[key] = value
        reply_keyboard = [['Серебро'], ['Золото'], ['Розовое золото'], ['Красная'], ['Синяя'], ['Зеленая'], ['Радужная'], ['Черная'], ['/end']]
        update.message.reply_text(
        'Укажи цвет фигуры\n (выберите из списка или введите вручную)',
        reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder='Цвет фигуры ...'
        ),
        )
        state_machine = FOIL_FIG_COLOR
    elif state_machine == FOIL_FIG_NAME and update.message.text == 'Другое':
        """Пользователь указал название ФИГУРЫ"""
        logger.info("%s: %s", user.first_name, update.message.text)
        update.message.reply_text('Укажи название фигуры')
        state_machine = FOIL_FIG_NAME
    elif state_machine == FOIL_FIG_NAME and not (update.message.text == 'Сердце' or update.message.text == 'Звезда' or update.message.text == 'Круг'or update.message.text == 'Другое'):
        """Пользователь указал название ФИГУРЫ"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем название фигуры 
        key = 'name'
        value = update.message.text
        context.user_data['order_dict'][key] = value        # order_dict[key] = value
        update.message.reply_text('Укажи стоимость фигуры')
        state_machine = FOIL_FIG_PRICE
    elif state_machine == FOIL_FIG_COLOR:
        """Пользователь указал цвет ФИГУРЫ"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем название фигуры 
        key = 'color'
        value = update.message.text
        context.user_data['order_dict'][key] = value
        update.message.reply_text('Укажи цену фигуры')
        state_machine = FOIL_FIG_PRICE
    elif state_machine == FOIL_FIG_PRICE:
        """Пользователь указал цену ФИГУРЫ"""
        logger.info("%s: %s", user.first_name, update.message.text)
        key = 'price'
        value = int(update.message.text)
        context.user_data['order_dict'][key] = value
        key = 'count'
        context.user_data['order_dict'][key] = 1
        key = 'summa'
        context.user_data['order_dict'][key] = value
        print(context.user_data)
        dict2=copy.deepcopy(context.user_data['order_dict'])
        order_list = context.user_data['order_list']
        order_list.append(dict2)
        print(order_list)
        context.user_data['order_list'] = order_list
        # Здесь необходимо сохранить словарь по данной ФИГУРЕ
        state_machine = order_insert(update, context)
    elif state_machine == FOIL_CHANGE and update.message.text == 'Цифра':
        """Пользователь выбрал тип шара ЦИФРА"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем значение типа 
        key = 'type'
        value = 'foil_num'
        context.user_data['order_dict'][key] = value
        reply_keyboard = [['0'], ['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'], ['/end']]
        update.message.reply_text(
        'Укажи цифру',
        reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder='Цифра ...'
        ),
        )
        state_machine = FOIL_NUM_NAME
    elif state_machine == FOIL_NUM_NAME:
        """Пользователь указал значение ЦИФРЫ"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем значение цифры 
        key = 'name'
        value = update.message.text
        context.user_data['order_dict'][key] = value
        reply_keyboard = [['Серебро'], ['Золото'], ['Розовое золото'], ['Красная'], ['Синяя'], ['Зеленая'], ['Радужная'], ['/end']]
        update.message.reply_text(
        'Укажи цвет цифры\n (выберите из списка или введите вручную)',
        reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder='Цвет цифры ...'
        ),
        )
        state_machine = FOIL_NUM_COLOR
    elif state_machine == FOIL_NUM_COLOR:
        """Пользователь указал цвет ЦИФРЫ"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем цвет цифры 
        key = 'color'
        value = update.message.text
        context.user_data['order_dict'][key] = value
        update.message.reply_text('Укажи стоимость цифры')
        state_machine = FOIL_NUM_PRICE
    elif state_machine == FOIL_NUM_PRICE:
        """Пользователь указал стоимость ЦИФРЫ"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем цену цифры 
        key = 'price'
        value = int(update.message.text)
        context.user_data['order_dict'][key] = value
        key = 'count'
        context.user_data['order_dict'][key] = 1
        key = 'summa'
        context.user_data['order_dict'][key] = value
        dict2=copy.deepcopy(context.user_data['order_dict'])
        order_list = context.user_data['order_list']
        order_list.append(dict2)
        context.user_data['order_list'] = order_list
        # Здесь необходимо сохранить словарь по данной ЦИФРЕ
        state_machine = order_insert(update, context)
    else:
        """Сюда попадаем если не подошло не одно из значений"""
        #logger.info("%s команда /skip", user.first_name)
        reply_text="Как ты сюда попал? Введи команду /cancel и попробуем снова"
        update.message.reply_text(reply_text)
    return state_machine

def bubl(update: Update, context: CallbackContext) -> int: # Здесь пользователь выбрал добавить в заказ баблс
    global state_machine
    user = update.message.from_user
    if state_machine == ORDER_ADD_ITEMS:
        """Пользователь выбрал баблс"""
        #Добавляем во внутрь словаря пользователя новый словарь с карточкой заказа
        key = 'order_dict'
        order_dict = {'type':0,'size':0,'color':0,'name':0,'count':0,'price':0,'summa':0,'comment':0}
        value = order_dict
        context.user_data[key] = value
        # Сохраняем значение типа 
        key = 'type'
        value = 'bubl'
        context.user_data['order_dict'][key] = value        # order_dict[key] = value
        logger.info("%s: %s", user.first_name, update.message.text)
        reply_keyboard = [['Перья'], ['Конфети'],['Снег']]
        update.message.reply_text(
        'Выберите наполнитель для баблса из списка или введи вручную',
        reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder='Наполнитель ...'
        ),
        )
        state_machine = BUBL_INSERT
    elif state_machine == BUBL_INSERT:
        """Пользователь выбрал наполнитель для БАБЛС"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем тип наполнителя для баблса 
        key = 'name'
        value = update.message.text
        context.user_data['order_dict'][key] = value        # order_dict[key] = value
        update.message.reply_text("Укажи цвет наполнителя")
        state_machine = BUBL_COLOR
    elif state_machine == BUBL_COLOR:
        """Пользователь выбрал цвет наполнителя для БАБЛС"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем цвет наполнителя для баблса 
        key = 'color'
        value = update.message.text
        context.user_data['order_dict'][key] = value        # order_dict[key] = value
        reply_keyboard = [['18"', '24"', '36"']]
        update.message.reply_text(
        'Укажите размер баблса',
        reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder='Размер ...'
        ),
        )
        state_machine = BUBL_SIZE
    elif state_machine == BUBL_SIZE:
        """Пользователь выбрал размер БАБЛС"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем размер баблса 
        key = 'size'
        value = update.message.text
        context.user_data['order_dict'][key] = value        # order_dict[key] = value
        update.message.reply_text("Укажи стоимость баблс")
        state_machine = BUBL_PRICE
    elif state_machine == BUBL_PRICE:
        """Пользователь указал цену БАБЛС"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем цену баблса
        key = 'price'
        value = int(update.message.text)
        context.user_data['order_dict'][key] = value
        key = 'count'
        context.user_data['order_dict'][key] = 1
        key = 'summa'
        context.user_data['order_dict'][key] = value
        dict2=copy.deepcopy(context.user_data['order_dict'])
        order_list = context.user_data['order_list']
        order_list.append(dict2)
        print(order_list)
        context.user_data['order_list'] = order_list
        # Здесь необходимо сохранить словарь по данной ЦИФРЕ
        state_machine = order_insert(update, context)
    else:
        """Пользователь попадает сюда когда ни одно из условий не подошло"""
        #logger.info("%s команда /skip", user.first_name)
        reply_text="Как ты сюда попал? Введи команду /cancel и попробуем снова"
        update.message.reply_text(reply_text)
    return state_machine

def stand(update: Update, context: CallbackContext) -> int: # Здесь пользователь выбрал добавить в заказ стойка
    global state_machine
    user = update.message.from_user
    if state_machine == ORDER_ADD_ITEMS:
        """Пользователь выбрал СТОЙКА"""
        key = 'order_dict'
        order_dict = {'type':0,'size':0,'color':0,'name':0,'count':0,'price':0,'summa':0,'comment':0}
        value = order_dict
        context.user_data[key] = value
        # Сохраняем значение типа 
        key = 'type'
        value = 'stand'
        context.user_data['order_dict'][key] = value
        logger.info("%s: %s", user.first_name, update.message.text)
        reply_keyboard = [['Арка 1,5х2,0 м'], ['Квадрат 1,5х1,5 м'], ['Прямоугольник 1,5х2,0 м'], ['Куб 1,5х1,5 м'], ['Куб 1,5х2,0 м'], ['Сетка 1,0х1,8 м']]
        update.message.reply_text(
        'Выберите тип стойки',
        reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder='Тип сетки ...'
        ),
        )
        state_machine = STAND_NAME
    elif state_machine == STAND_NAME:
        """Пользователь ввел тип стойки"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем надпись 
        key = 'name'
        value = update.message.text
        context.user_data['order_dict'][key] = value
        update.message.reply_text("Укажи стоимость аренды стойки")
        state_machine = STAND_PRICE
    elif state_machine == STAND_PRICE:
        """Пользователь указал цену стойки"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем стоимость стойки
        key = 'price'
        value = int(update.message.text)
        context.user_data['order_dict'][key] = value
        key = 'count'
        context.user_data['order_dict'][key] = 1
        key = 'summa'
        context.user_data['order_dict'][key] = value
        dict2=copy.deepcopy(context.user_data['order_dict'])
        order_list = context.user_data['order_list']
        order_list.append(dict2)
        print(order_list)
        context.user_data['order_list'] = order_list
        state_machine = order_insert(update, context)
    return state_machine

def label(update: Update, context: CallbackContext) -> int: # Здесь пользователь выбрать добавить в заказ надпись
    global state_machine
    user = update.message.from_user
    if state_machine == ORDER_ADD_ITEMS:
        """Пользователь выбрал НАДПИСЬ"""
        # Сохраняем значение типа 
        key = 'type'
        value = 'label'
        context.user_data['order_dict'][key] = value
        logger.info("%s: %s", user.first_name, update.message.text)
        update.message.reply_text("Введите надпись")
        state_machine = LABEL_NAME
    elif state_machine == LABEL_NAME:
        """Пользователь ввел НАДПИСЬ"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем надпись 
        key = 'name'
        value = update.message.text
        context.user_data['order_dict'][key] = value
        update.message.reply_text("Укажи цвет надписи")
        state_machine = LABEL_COLOR
    elif state_machine == LABEL_COLOR:
        """Пользователь указал цвет НАДПИСИ"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем цвет надписи
        key = 'color'
        value = update.message.text
        context.user_data['order_dict'][key] = value
        dict2=copy.deepcopy(context.user_data['order_dict'])
        order_list = context.user_data['order_list']
        order_list.append(dict2)
        print(order_list)
        context.user_data['order_list'] = order_list
        state_machine = order_insert(update, context)
    return state_machine

def comment(update: Update, context: CallbackContext) -> int: # Здесь пользователь выбрать добавить в заказ комментарий
    global state_machine
    user = update.message.from_user
    if state_machine == ORDER_ADD_ITEMS:
        """Пользователь выбрал КОММЕНТАРИЙ"""
        # Сохраняем значение типа 
        logger.info("%s: %s", user.first_name, update.message.text)
        update.message.reply_text("Введите коментарий к заказу")
        state_machine = COMMENT
    elif state_machine == COMMENT:
        """Пользователь ввел КОММЕНТАРИЙ"""
        logger.info("%s: %s", user.first_name, update.message.text)
        # Сохраняем комментарий 
        key = 'comment'
        value = update.message.text
        context.user_data[key] = value
        state_machine = end(update, context)
    return state_machine

def cancel(update: Update, context: CallbackContext) -> int: # Здесь прекращается общение с ботом.
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("Пользователь %s отменил заполнение форм", user.first_name)
    update.message.reply_text(
        'Пока! Я надеюсь тебе все понравилось и ты вернешься в следующий раз', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def end(update: Update, context: CallbackContext) -> int: # Здесь обрабатываются смета и выводится предварительный состав заказ
    """Пользователь завершил заполнение формы"""
    user = update.message.from_user
    logger.info("Пользователь %s завершил заполнение форм", user.first_name)
    msg = make_msg_order_list(context.user_data)
    
    update.message.reply_text('Итак давай посмотрим что получается')
    update.message.reply_text(msg)
    update.message.reply_text('Введите одну из следующих команд:\n/add - чтобы добавить в заказ еще позиции\n/remove - чтобы удалить из списка заказа позицию \n/edit - чтобы откорректировать позицию из списка заказа\n/comment - добавить коментарий к заказу\n/finish - чтобы завершить оформление')
    return ORDER_ADD_ITEMS

def make_msg_order_list(user_data) -> str:

    #Создаем сообщение с выводом состава заказа
    count = 0
    summa = 0
    message = ''
    for element in user_data['order_list']:
        result = user_data['order_list'][count]["type"]
        if result == 'latex':
            msg_str = 'Шар %(name)s %(size)s Цвет: %(color)s \nКол-во - %(count)d шт. Цена %(price)d руб. \n' % user_data['order_list'][count]
            #print (msg_str)
            message += '%d. ' % (count+1)
            message += msg_str
        elif result == 'foil_fig' and not (user_data['order_list'][count]["name"] == 'Сердце' or user_data['order_list'][count]["name"] == 'Звезда' or user_data['order_list'][count]["name"] == 'Круг'):
            msg_str = 'Фигура %(name)s Цена %(price)d руб. \n' % user_data['order_list'][count]
            message += '%d. ' % (count+1)
            message += msg_str
        elif result == 'foil_fig' and (user_data['order_list'][count]["name"] == 'Сердце' or user_data['order_list'][count]["name"] == 'Звезда' or user_data['order_list'][count]["name"] == 'Круг'):
            msg_str = 'Фигура %(name)s Цвет: %(color)s Цена %(price)d руб. \n' % user_data['order_list'][count]
            #print (msg_str)
            message += '%d. ' % (count+1)
            message += msg_str
        elif result == 'foil_num':
            msg_str = 'Цифра %(name)s Цвет %(color)s Цена %(price)d руб. \n' % user_data['order_list'][count]
            #print (msg_str)
            message += '%d. ' % (count+1)
            message += msg_str
        elif result == 'bubl':
            msg_str = 'Баблс %(size)s с наполнением: %(name)s Цвет: %(color)s Цена %(price)d руб. \n' % user_data['order_list'][count]
            #print (msg_str)
            message += '%d. ' % (count+1)
            message += msg_str
        elif result == 'label':
            msg_str = 'Надпись %(name)s Цвет: %(color)s. \n' % user_data['order_list'][count]
            #print (msg_str)
            message += '%d. ' % (count+1)
            message += msg_str
        elif result == 'stand':
            msg_str = 'Стойка %(name)s Цена (Аренда) %(price)d руб. \n' % user_data['order_list'][count]
            #print (msg_str)
            message += '%d. ' % (count+1)
            message += msg_str
        elif result == 'other':
            msg_str = 'Другое: %(comment)s. Цена %(price)d руб. \n' % user_data['order_list'][count]
            #print (msg_str)
            message += '%d. ' % (count+1)
            message += msg_str
        summa +=user_data['order_list'][count]["summa"]
        count += 1
        print(result)
    if message == '':
        message = 'Похоже в заказе пусто'
        user_data['summa'] = 0
    else:
        if user_data['comment'] != 0:
            message +='\n\nКомментарий: %s' % user_data['comment']
        user_data['summa'] = summa
        message +='\n\nИтого сумма заказа без учета доставки: %d руб.' % summa
        message +='\nНеобходимая предоплата: %d руб.' % (summa // 2)
    print(message)
    return message

def finish(update: Update, context: CallbackContext) -> int: # Здесь финализируется каточка заказа и сохраняется в базу данных MongoDB
    global state_machine
    user = update.message.from_user
    logger.info("Пользователь %s завершил оформление заказ", user.first_name)
    order = save_user_order(mdb, update, context.user_data) # Сохраняем заказ в базу данных
    if order !=0:
        text = """Заказ сохранён!
            Его номер: <b>%d</b>
            Я надеюсь тебе все понравилось и ты вернешься в следующий раз""" % (order['order_cnt'])
    else:
        text = "Заказ не сохранен так как нечего сохранять. Попробуй заново /start"
    update.message.reply_text(text, parse_mode=ParseMode.HTML)  # текстовое сообщение с форматированием HTML
    #update.message.reply_text("Спасибо!", reply_markup=get_keyboard())  # отправляем сообщение и возвращаем осн. клаву
    state_machine = ConversationHandler.END  # выходим из диалога
    return state_machine

def error_input(update: Update, context: CallbackContext) -> int: # Здесь обрабатываются недопустимые значения вводимые пользователем при заполнении форм
    """Пользователь ввел не правильные значения формы"""
    global state_machine
    user = update.message.from_user
    logger.info("Пользователь %s ввел не допустимые значения формы", user.first_name)
    if state_machine == TEL:
        update.message.reply_text('Введите номер телефона в формате +7 999 123 44 55')
    elif state_machine == DATE:
        update.message.reply_text('Введите дату мероприятия в формате дд-мм-гг ЧЧ:ММ')
    elif state_machine == LATEX_COUNT:
        update.message.reply_text('Введите колличество шаров ЦИФРАМИ')
    elif state_machine == LATEX_PRICE or state_machine == FOIL_NUM_PRICE or state_machine == FOIL_FIG_PRICE or state_machine == BUBL_PRICE or state_machine == STAND_PRICE:
        update.message.reply_text('Введите стоимость ЦИФРАМИ')
    elif state_machine == START or state_machine == ConversationHandler.END:
        update.message.reply_text('Чтобы начать разговор введите команду /start')
        state_machine = ConversationHandler.END

    return state_machine

def callback_button_pressed(update: Update, context: CallbackContext) -> None:
    global state_machine
    query = update.callback_query  # данные которые приходят после нажатия кнопки
    #print(query)
    data = int(query.data)  # получаем данные нажатой кнопки (1 или -1)
    if state_machine == ORDER_REMOVE:
        print("Заказ номер будет удален")
        print(data)
        msg = "Заказ № %d удалён" % data
        #query.answer(text="Проверка",show_alert=True)
        query.answer(text=msg)
        """
        reply_text="Так давай выберем что будем делать дальше"
        reply_keyboard = [[InlineKeyboardButton('Добавить новый заказ', callback_data="1"),
                          InlineKeyboardButton('Редактировать заказ', callback_data="2"),
                          InlineKeyboardButton('Удалить заказ', callback_data="3"),
                          InlineKeyboardButton('Вывести список заказов', callback_data="4"),
                          InlineKeyboardButton('Вернуться назад', callback_data="5")]]
        update.callback_query.message.edit_text(
            text=reply_text,
            reply_markup=InlineKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True 
        )
        )
        # update.message.reply_text(
            # reply_text,
            # reply_markup=ReplyKeyboardMarkup(
            # reply_keyboard, one_time_keyboard=True 
        # ),
        # )
        """
        state_machine = CHANGE
        change(update, context)
    #return state_machine

def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    
    updater = Updater(TG_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(callback_button_pressed))
    
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text & ~Filters.command, error_input), CommandHandler('start', start)],
        states={
            CHANGE: [MessageHandler(Filters.regex('^(Заказ|Смета)$'), change), MessageHandler(Filters.regex('^(Другое)$'), other)], # Обрабатываем выбор пользователя
            #Блок получение данных для заполнения карточки заказа
            FIO: [MessageHandler(Filters.text & ~Filters.command, order), CommandHandler('skip', skip)],
            TEL: [MessageHandler(Filters.regex('^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$') & ~Filters.command, order), MessageHandler(Filters.text & ~Filters.command, error_input), CommandHandler('skip', skip)],
            FROM: [MessageHandler(Filters.text & ~Filters.command, order), CommandHandler('skip', skip)],
            DATE: [MessageHandler(Filters.regex('[0-3]?[0-9].[0-3]?[0-9].(?:[0-9]{2})?[0-9]{2} (?:[01][0-9]|2[0-3]):[0-5][0-9]') & ~Filters.command, order),MessageHandler(Filters.text & ~Filters.command, error_input), CommandHandler('skip', skip)],
            LOCATION: [
                MessageHandler(Filters.location | (Filters.text & ~Filters.command), order),
                CommandHandler('skip', skip),
            ],
            #Блок получения данных для формирования состава заказа
            ORDER: [MessageHandler(Filters.regex('^(Добавить новый заказ)$'), order), MessageHandler(Filters.regex('^(Редактировать заказ)$'), show_list_order), MessageHandler(Filters.regex('^(Удалить заказ)$'), remove_order),  MessageHandler(Filters.regex('^(Вывести список заказов)$'), show_list_order), MessageHandler(Filters.regex('^(Вернуться назад)$'), start)], # Выбор манипуляций с заказом
            ORDER_CHANGE: [MessageHandler(Filters.regex('^[1-9][0-9]*$'), select_order), MessageHandler(Filters.regex('^(Состав заказа|Изменить заказ|Удалить заказ|В архив)$'), select_order ), MessageHandler(Filters.regex('^(Вернуться назад)$'), start)], # Выбор манипуляций с заказом
            ORDER_REMOVE: [MessageHandler(Filters.regex('^(Добавить новый заказ)$'), order), MessageHandler(Filters.regex('^(Редактировать заказ)$'), order), MessageHandler(Filters.regex('^(Удалить заказ)$'), remove_order), MessageHandler(Filters.regex('^[1-9][0-9]*$'), remove_order), MessageHandler(Filters.regex('^(Вывести список заказов)$'), show_list_order), MessageHandler(Filters.regex('^(Вернуться назад)$'), start)], # Выбор манипуляций с заказом
            ORDER_EDIT: [MessageHandler(Filters.regex('^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$') & ~Filters.command, edit_order), MessageHandler(Filters.regex('^[1-9][0-9]*$'), edit_order), MessageHandler(Filters.regex('^(ФИО|Телефон|Дата и время|Адрес|Состав заказа)$'), edit_order),  MessageHandler(Filters.regex('^(Вернуться назад)$'), start)], # Выбор манипуляций с заказом  # TODO: внести изменение чтобы функция отрабатывала комманду "в архив"
            ORDER_SHOW: [MessageHandler(Filters.regex('^(Добавить новый заказ)$'), order), MessageHandler(Filters.regex('^(Редактировать заказ)$'), order), MessageHandler(Filters.regex('^(Удалить заказ)$'), remove_order), MessageHandler(Filters.regex('^[1-9][0-9]*$'), remove_order), MessageHandler(Filters.regex('^(Вывести список заказов)$'), show_list_order), MessageHandler(Filters.regex('^(Вернуться назад)$'), start)], # Выбор манипуляций с заказом
            ORDER_ADD_ITEMS: [MessageHandler(Filters.regex('^(Латекс)$'), latex), MessageHandler(Filters.regex('^(Фольга)$'), foil), MessageHandler(Filters.regex('^(Баблс)$'), bubl), MessageHandler(Filters.regex('^(Надпись)$'), label), MessageHandler(Filters.regex('^(Стойка)$'), stand), CommandHandler('end', end), CommandHandler('add', order_insert), CommandHandler('remove', remove_items_from_order), MessageHandler(Filters.regex('^[1-9][0-9]*$'), remove_items_from_order), CommandHandler('finish', finish), CommandHandler('comment', comment)], # Выбор продукции для заказа

            LATEX_SIZE: [MessageHandler(Filters.text & ~Filters.command, latex), CommandHandler('skip', skip)], # Шары из латекса
            LATEX_COLOR: [MessageHandler(Filters.text & ~Filters.command, latex), CommandHandler('skip', skip)],
            LATEX_COUNT: [MessageHandler(Filters.regex('^\d+$') & ~Filters.command, latex), MessageHandler(Filters.text & ~Filters.command, error_input), CommandHandler('skip', skip)],
            LATEX_PRICE: [MessageHandler(Filters.regex('^\d+$') & ~Filters.command, latex), MessageHandler(Filters.text & ~Filters.command, error_input), CommandHandler('skip', skip)],

            FOIL: [MessageHandler(Filters.text & ~Filters.command, foil), CommandHandler('skip', skip)],
            FOIL_CHANGE: [MessageHandler(Filters.regex('^(Фигура|Цифра)$'), foil), CommandHandler('skip', skip)],

            FOIL_FIG_NAME: [MessageHandler(Filters.text & ~Filters.command, foil), CommandHandler('skip', skip)], #Фигуры из фольги
            FOIL_FIG_COLOR: [MessageHandler(Filters.text & ~Filters.command, foil), CommandHandler('skip', skip)],
            FOIL_FIG_PRICE: [MessageHandler(Filters.regex('^\d+$') & ~Filters.command, foil), MessageHandler(Filters.text & ~Filters.command, error_input), CommandHandler('skip', skip)],

            FOIL_NUM_NAME: [MessageHandler(Filters.text & ~Filters.command, foil), CommandHandler('skip', skip)], #Цифры из фольги
            FOIL_NUM_COLOR: [MessageHandler(Filters.text & ~Filters.command, foil), CommandHandler('skip', skip)],
            FOIL_NUM_PRICE: [MessageHandler(Filters.regex('^\d+$') & ~Filters.command, foil), MessageHandler(Filters.text & ~Filters.command, error_input), CommandHandler('skip', skip)],

            BUBL_INSERT: [MessageHandler(Filters.text & ~Filters.command, bubl), CommandHandler('skip', skip)], # Баблс
            BUBL_SIZE: [MessageHandler(Filters.text & ~Filters.command, bubl), CommandHandler('skip', skip)],
            BUBL_COLOR: [MessageHandler(Filters.text & ~Filters.command, bubl), CommandHandler('skip', skip)],
            BUBL_PRICE: [MessageHandler(Filters.regex('^\d+$') & ~Filters.command, bubl), MessageHandler(Filters.text & ~Filters.command, error_input), CommandHandler('skip', skip)],

            LABEL_NAME: [MessageHandler(Filters.text & ~Filters.command, label), CommandHandler('skip', skip)], # Надпись
            LABEL_COLOR: [MessageHandler(Filters.text & ~Filters.command, label), CommandHandler('skip', skip)], 
            LABEL_PRICE: [MessageHandler(Filters.regex('^\d+$') & ~Filters.command, label), MessageHandler(Filters.text & ~Filters.command, error_input), CommandHandler('skip', skip)],

            STAND_NAME: [MessageHandler(Filters.text & ~Filters.command, stand), CommandHandler('skip', skip)], # Стойка
            STAND_PRICE: [MessageHandler(Filters.regex('^\d+$') & ~Filters.command, stand), MessageHandler(Filters.text & ~Filters.command, error_input), CommandHandler('skip', skip)],

            COMMENT: [MessageHandler(Filters.text & ~Filters.command, comment), CommandHandler('skip', skip)], # Комментарий
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
