# Здесь будут формироваться функции по управлению личным кабинетом пользователя бота, такие как
# создание карточки заказа, проверка баланса, оплата, статистика, формирование списка рассылки, рассылка рекламных сообщения, получение пароля для доступа через сайт

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update

from telegram.ext import CallbackContext

from state_machine_elements import *

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def profile(update: Update, context: CallbackContext) -> int:
    global state_machine
    user = update.message.from_user
    if state_machine != PROFILE:
        """Пользователь выбрал раздел "ПРОФИЛЬ". Выводим перечень доступных разделов"""
        logger.info("%s выбрала оформление сметы", user.first_name)
        reply_text = "Вы находитесь в личном кабинете. Выберите нужный раздел"
        reply_keyboard = [['Баланс', 'Оплата'], ['Карточка заказа', 'Статистика', 'Рассылка'], ['Вернуться назад']]
        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        state_machine = PROFILE
    elif state_machine == PROFILE and update.message.text == 'Карточка заказ':
        logger.info("%s выбрала раздел %s", user.first_name, update.message.text)
        context.user_data['last_msg'] = update.message.text
        reply_text = "Вы выбрали раздел 'Карточка заказа'. Что бы вы хотели сделать?"
        reply_keyboard = [['Вывести текущий шаблон', 'Редактировать шаблон'], ['Назад']]
        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    elif state_machine == PROFILE and context.user_data['last_msg'] == 'Карточка заказ' and update.message.text == 'Вывести текущий шаблон':
        logger.info("%s выбрала раздел %s", user.first_name, update.message.text)
        context.user_data['last_msg'] = update.message.text
        reply_text = "Вы выбрали раздел 'Карточка заказа'. Что бы вы хотели сделать?"
        reply_keyboard = [['Вывести текущий шаблон', 'Редактировать шаблон'], ['Назад']]
        update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    else:
        logger.info("%s выбрала раздел %s", user.first_name, update.message.text)
    return state_machine
