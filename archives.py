from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import CallbackContext
from mongodb import *
from bot_balloon import state_machine, ARCHIVE, ORDER, make_msg_order_list
import logging


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
def archive(update: Update, context: CallbackContext) -> int:
    global state_machine
    user = update.message.from_user
    if state_machine == ARCHIVE and (update.message.text != 'Состав заказа' and update.message.text != 'Восстановить'):
        logger.info("Пользователь %s выбрал заказ %d из архива", user.first_name, int(update.message.text))
        context.user_data['select_order'] = int(update.message.text)
        reply_keyboard = [['Состав заказа', 'Восстановить'], ['Вернуться назад']]
        reply_text = "Выберите что сделать с заказом из архива: \n"
        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    elif state_machine == ARCHIVE and update.message.text == 'Состав заказа':
        logger.info("Пользователь %s выбрал заказ %d из архива чтобы посмотреть состав", user.first_name,
                    context.user_data['select_order'])
        show_archive(update, context)
    elif state_machine == ARCHIVE and update.message.text == 'Восстановить':
        logger.info("Пользователь %s выбрал заказ %d из архива чтобы восстановить", user.first_name,
                    context.user_data['select_order'])
        recovery_from_archive(update, context)

    return state_machine
def move_to_archive(update, context):
    move_to_archive_from_orders(mdb, update, context.user_data['select_order'])
    reply_keyboard = [['Вернуться назад']]
    reply_text = "Заказ №" + str(context.user_data['select_order']) + " отправлен в АРХИВ"
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return
def recovery_from_archive(update, context):
    recovery_from_archive_to_orders(mdb, update, context.user_data['select_order'])
    reply_keyboard = [['Вернуться назад']]
    reply_text = "Заказ №" + str(context.user_data['select_order']) + " восстановлен из АРХИВА"
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return

def show_archive(update: Update, context: CallbackContext) -> int:
    global state_machine
    user = update.message.from_user
    list_archive_order(update, context)
    if update.message.text == "Состав заказа" or state_machine != ORDER:
        logger.info("Пользователь %s запросил список заказов из архива отображения состава", user.first_name)
        context.user_data['last_msg'] = update.message.text
        # print(context.user_data)
        show_archive_order(update, context)
        state_machine = ARCHIVE
        # print(state_machine)
    else:
        logger.info("Пользователь %s попал в else в функции show_archive", user.first_name)
        context.user_data['last_msg'] = update.message.text
        state_machine = ARCHIVE
    return state_machine

def list_archive_order(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Пользователь %s запросил список заказов из архива", user.first_name)
    order_list = list_archive_from_db(mdb, update)
    reply_keyboard = [[], []]
    reply_text = "Вот список ваших заказов находящихся в архиве: \n"
    cnt = 0
    for order in order_list:
        cnt += 1
        reply_text += "%d\n" % order['order_cnt']
        reply_keyboard[0].append(str(order['order_cnt']))
    reply_keyboard[1].append('Вернуться назад')
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return cnt

def show_archive_order(update: Update, context: CallbackContext) -> int:
    global state_machine
    order = {}
    user = update.message.from_user
    if state_machine == ARCHIVE:
        # Сюда вставить функцию вывода состава заказа из БД
        order_num = context.user_data['select_order']
        archive = show_archive_user_from_db(mdb, update, order_num)
        # print(show_order_user_from_db(mdb, update, order_num))
        text = "Заказ № " + str(context.user_data['select_order']) + ":\n"
        text += "ФИО:" + archive['fio'] + "\n"
        text += "Телефон:" + archive['tel'] + "\n"
        text += "Дата:" + archive['date'] + "\n"
        text += "Адрес:" + archive['location'] + "\n\n"
        text += make_msg_order_list(archive)
        update.message.reply_text(text)

    return state_machine
