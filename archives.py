def move_to_archive(update, context):
    move_to_archive_from_orders(mdb, update, context.user_data['select_order'])
    reply_keyboard = [['Вернуться назад']]
    reply_text = "Заказ №" + str(context.user_data['select_order']) + " отправлен в АРХИВ"
    update.message.reply_text(reply_text, reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return

def show_archive(update: Update, context: CallbackContext) -> int:
    global state_machine
    user = update.message.from_user
    list_archive_order(update, context)
    if update.message.text == "Редактировать заказ" or state_machine != ORDER:
        logger.info("Пользователь %s запросил список заказов для редактирования", user.first_name)
        context.user_data['last_msg'] = update.message.text
        # print(context.user_data)
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
        # state_machine = CHANGE
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
