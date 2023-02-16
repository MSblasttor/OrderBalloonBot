# Здесь будут формироваться функции по управлению личным кабинетом пользователя бота, такие как
# создание карточки заказа, проверка баланса, оплата, статистика, формирование списка рассылки, рассылка рекламных сообщения, получение пароля для доступа через сайт

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update

from telegram.ext import CallbackContext

from bot_balloon import state_machine


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def profile(update: Update, context: CallbackContext) -> int:
    global state_machine
    user = update.message.from_user
    """Пользователь выбрал раздел "ПРОФИЛЬ". Выводим перечень доступных разделов"""
    logger.info("%s выбрала оформление сметы", user.first_name)
    reply_text = "Вы находитесь в личном кабинете. Выберите нужный раздел"
    reply_keyboard = [['Баланс', 'Оплата'], ['Карточка заказа', 'Статистика', 'Рассылка'], ['Вернуться назад']]
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    state_machine = PROFILE
    return state_machine
