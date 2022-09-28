from pymongo import MongoClient

# Create the client
client = MongoClient('localhost', 27017)

# Connect to our database
mdb = client['orderballoonbot']

#from settings import client, mdb
# Fetch our series collection
series_collection = mdb['user_id']

# Imports truncated for brevity

def insert_document(collection, data):
    """ Function to insert a document into a collection and
    return the document's id.
    """
    return collection.insert_one(data).inserted_id

# Imports and previous code truncated for brevity

def find_document(collection, elements, multiple=False):
    """ Function to retrieve single or multiple documents from a provided
    Collection using a dictionary containing a document's elements.
    """
    if multiple:
        results = collection.find(elements)
        return [r for r in results]
    else:
        return collection.find_one(elements)

# Imports and previous code truncated for brevity

def update_document(collection, query_elements, new_values):
    """ Function to update a single document in a collection.
    """
    collection.update_one(query_elements, {'$set': new_values})

# Imports and previous code truncated for brevity

def delete_document(collection, query):
    """ Function to delete a single document from a collection.
    """
    collection.delete_one(query)

def search_or_save_user(mdb, effective_user, message):
    user = mdb.users.find_one({"user_id": effective_user.id})  # поиск в коллекции users по user.id
    if not user:  # если такого нет, создаем словарь с данными
        user = {
            "user_id": effective_user.id,
            "first_name": effective_user.first_name,
            "last_name": effective_user.last_name,
            "chat_id": message.chat.id,
			"order_cnt": 1000
        }
        mdb.users.insert_one(user)  # сохраняем в коллекцию users
    return user

def save_user_order(mdb, update, user_data):
    if 'select_order' in user_data and user_data['select_order'] != 0:
        #print(user_data['select_order'])
        user = search_or_save_user(mdb, update.effective_user, update.message)
        #order = mdb.orders.find_one({'user_id': user['user_id'], 'order_cnt': user_data['select_order']})
        result_order_list = user_data['order_list']
        #print(result_order_list)
        finish = mdb.orders.update_one(
            {'user_id': user['user_id'], 'order_cnt': user_data['select_order']},
            {'$set': {'order.order_list' : result_order_list}})
        #print(finish)
        order = mdb.orders.find_one({'user_id': user['user_id'], 'order_cnt': user_data['select_order']})
    else:
        print('save fail')
        if user_data['summa'] != 0:
            user = search_or_save_user(mdb, update.effective_user, update.message)  # получаем данные из базы данных
            mdb.users.update_one(
                {'_id': user['_id']},
                {'$set': {'order_cnt': (user['order_cnt'] + 1) }}
            )
            order = mdb.orders.find_one({"user_id": user['user_id']})   # поиск в коллекции orders по user.id
            if not order:  # если такого нет, создаем словарь с данными
                order = {
                    'order_cnt': user['order_cnt'] + 1,
                    'user_id': user['user_id'],
                    'order': {
                        "fio": user_data['fio'],
                        "tel": user_data['tel'],
                        "from": user_data['from'],
                        "date": user_data['date'],
                        "location": user_data['location'],
                        "order_list": user_data['order_list'],
                        "comment": user_data['comment'],
                        "summa": user_data['summa']
                    }
                }
                mdb.orders.insert_one(order)   # сохраняем в коллекцию orders
            else:
                order = {
                    'order_cnt': user['order_cnt'] + 1,
                    'user_id': user['user_id'],
                    'order': {
                        "fio": user_data['fio'],
                        "tel": user_data['tel'],
                        "from": user_data['from'],
                        "date": user_data['date'],
                        "location": user_data['location'],
                        "order_list": user_data['order_list'],
                        "comment": user_data['comment'],
                        "summa": user_data['summa']
                    }
                }
                mdb.orders.insert_one(order)   # сохраняем в коллекцию orders
        else:
            order = 0
    return order

def list_order_from_db(mdb, update):
    user = search_or_save_user(mdb, update.effective_user, update.message)
    order_list = mdb.orders.find({'user_id': user['user_id']})
    return order_list

def list_archive_from_db(mdb, update):
    user = search_or_save_user(mdb, update.effective_user, update.message)
    order_list = mdb.archives.find({'user_id': user['user_id']})
    return order_list
def show_order_user_from_db(mdb, update, order_num):
    user = search_or_save_user(mdb, update.effective_user, update.message)
    order = mdb.orders.find_one({'user_id': user['user_id'], 'order_cnt': order_num})
    print(order)
    return order['order']

def show_archive_user_from_db(mdb, update, order_num):
    user = search_or_save_user(mdb, update.effective_user, update.message)
    archive = mdb.archives.find_one({'user_id': user['user_id'], 'order_cnt': order_num})
    #print(order)
    return archive['order']

def edit_order_user_from_db(mdb, update, order_num, param, value):
    user = search_or_save_user(mdb, update.effective_user, update.message)
    finish = mdb.orders.update_one(
        {'user_id': user['user_id'], 'order_cnt': order_num},
        {'$set': {'order.'+param: value}})
    print(finish)

# сохраняем - обновляем результаты анкеты и возвращаем результат
def save_user_anketa(mdb, user, user_data):
    mdb.users.update_one(
        {'_id': user['_id']},
        {'$set': {'anketa': {'name': user_data['name'],
                             'age': user_data['age'],
                             'evaluation': user_data['evaluation'],
                             'comment': user_data['comment']
                             }
                  }
         }
    )
    return user

def move_to_archive_from_orders(mdb, update, order_num):
    user = search_or_save_user(mdb, update.effective_user, update.message)
    archive = mdb.orders.find_one({'user_id': user['user_id'], 'order_cnt': order_num})
    mdb.archives.insert_one(archive)  # сохраняем в коллекцию archives
    mdb.orders.delete_one({'user_id': user['user_id'], 'order_cnt': order_num}) # удаляем заказ из колекции orders
    return

def move_to_trash_from_orders(mdb, update, order_num):
    user = search_or_save_user(mdb, update.effective_user, update.message)
    trash = mdb.orders.find_one({'user_id': user['user_id'], 'order_cnt': order_num})
    mdb.trash.insert_one(trash)  # сохраняем в коллекцию archives
    mdb.orders.delete_one({'user_id': user['user_id'], 'order_cnt': order_num}) # удаляем заказ из колекции orders
    return

def recovery_from_archive_to_orders(mdb, update, order_num):
    user = search_or_save_user(mdb, update.effective_user, update.message)
    order = mdb.archives.find_one({'user_id': user['user_id'], 'order_cnt': order_num})
    mdb.orders.insert_one(order)  # сохраняем в коллекцию orders
    mdb.archives.delete_one({'user_id': user['user_id'], 'order_cnt': order_num}) # удаляем заказ из колекции orders
    return