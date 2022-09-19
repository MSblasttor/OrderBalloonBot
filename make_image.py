from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


font_path = "fonts/Steclo.otf"

def make_image_order(order):
    pagesize_w, pagesize_h = (744, 1052)
    im = Image.new('RGB', (pagesize_w, pagesize_h), color=('#FAACAC'))
    template = Image.open('img/order_templ.png')
    im.paste(template, (0, 0))
    template.close()
    #Заполняем поле номер заказа
    txt = str(order['order_cnt'])
    make_txt(im, 220, 80, txt, "centr", 60)
    #Заполняем поле ФИО
    txt = str(order['order']['fio'])
    make_txt(im, 220, 180, txt, "left")
    #Заполняем поле Телефон
    txt = str(order['order']['tel'])
    make_txt(im, 220, 210, txt, "left")
    #Заполняем поле Дата
    txt = str(order['order']['date'])
    make_txt(im, 220, 240, txt, "left")
    #Заполняем поле Дата
    txt = str(order['order']['location'])
    make_txt(im, 220, 270, txt, "left")
    count = 0
    message = ""
    summa = 0
    for element in order['order']['order_list']:
        result = order['order']['order_list'][count]['type']
        if result == 'latex':
            msg_str = 'Шар %(name)s %(size)s Цвет: %(color)s Кол-во - %(count)d шт. Цена %(price)d руб. \n' % \
                      order['order']['order_list'][count]
            # print (msg_str)
            message = '%d. ' % (count + 1)
            message += msg_str
        elif result == 'foil_fig' and not (
                order['order']['order_list'][count]["name"] == 'Сердце' or order['order']['order_list'][count][
            "name"] == 'Звезда' or order['order']['order_list'][count]["name"] == 'Круг'):
            msg_str = 'Фигура %(name)s Цена %(price)d руб. \n' % order['order']['order_list'][count]
            message = '%d. ' % (count + 1)
            message += msg_str
        elif result == 'foil_fig' and (
                order['order']['order_list'][count]["name"] == 'Сердце' or order['order']['order_list'][count][
            "name"] == 'Звезда' or order['order']['order_list'][count]["name"] == 'Круг'):
            msg_str = 'Фигура %(name)s Цвет: %(color)s Цена %(price)d руб. \n' % order['order']['order_list'][count]
            # print (msg_str)
            message = '%d. ' % (count + 1)
            message += msg_str
        elif result == 'foil_num':
            msg_str = 'Цифра %(name)s Цвет %(color)s Цена %(price)d руб. \n' % order['order']['order_list'][count]
            # print (msg_str)
            message = '%d. ' % (count + 1)
            message += msg_str
        elif result == 'bubl':
            msg_str = 'Баблс %(size)s с наполнением: %(name)s Цвет: %(color)s Цена %(price)d руб. \n' % \
                      order['order']['order_list'][count]
            # print (msg_str)
            message = '%d. ' % (count + 1)
            message += msg_str
        elif result == 'label':
            msg_str = 'Надпись %(name)s Цвет: %(color)s. \n' % order['order']['order_list'][count]
            # print (msg_str)
            message = '%d. ' % (count + 1)
            message += msg_str
        elif result == 'stand':
            msg_str = 'Стойка %(name)s Цена (Аренда) %(price)d руб. \n' % order['order']['order_list'][count]
            # print (msg_str)
            message = '%d. ' % (count + 1)
            message += msg_str
        elif result == 'other':
            msg_str = 'Другое: %(comment)s. Цена %(price)d руб. \n' % order['order']['order_list'][count]
            # print (msg_str)
            message = '%d. ' % (count + 1)
            message += msg_str
        summa += order['order']['order_list'][count]["summa"]
        count += 1
        print(count)
        make_txt(im, 50, 320+count*30, message, "left")
    count += 2
    if order['order']['comment'] != 0:
        message = 'Комментарий: %s' % order['order']['comment']
        count += 1
        make_txt(im, 50, 320 + count * 30, message, "left")
        #order['order']['summa'] = summa
    #print(count)
    message = 'Итого сумма заказа без учета доставки: %d руб.' % summa
    count += 1
    make_txt(im, 50, 320 + count * 30, message, "left")
    #print(count)
    if 'dostavka' in order['order']:
        message = 'Доставка: %d руб.' % order['order']['dostavka']
        #order['summa'] = summa + user_data['dostavka']
        #summa = order['summa']
        count += 1
        make_txt(im, 50, 320 + count * 30, message, "left")
        #print(count)
    if 'predoplata' in order['order']:
        if summa - order['order']['predoplata'] > 0:
            message = 'Предоплата: %d руб.' % order['order']['predoplata']
            message += '/nОсталось доплатить %d руб.' % (summa - order['order']['predoplata'])
        else:
            message = 'Все оплачено'
    else:
        message = 'Необходимая предоплата: %d руб.' % (summa // 2)
    count += 1
    make_txt(im, 50, 320 + count * 30, message, "left")
    #print(count)

    # Сохраняем изображение
    directory_order = Path('/root/OrderBalloonBot/img/' + str(order['user_id']))
    try:
        directory_order.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("Folder for pic: "+str(order['user_id'])+" already exists")
    else:
        print("Folder for pic: "+str(order['user_id'])+" was created")
    path_img ="/root/OrderBalloonBot/img/"+str(order['user_id'])+"/"+str(order['order_cnt'])+".png"
    im.save(path_img)
    print("Save pic order")
    return

def make_txt(image, x, y, txt, align="centr", font_size=30, font_path="fonts/Steclo.otf", fill='#1C0606'):
    font = ImageFont.truetype(font_path, font_size)
    draw_text = ImageDraw.Draw(image)
    left, top, right, bottom = font.getbbox(txt)
    #print (left, top, right, bottom)
    if align == "centr":
        txt_cord_w = x - right / 2
        txt_cord_h = y
    elif align == "left":
        txt_cord_w = x
        txt_cord_h = y
    #print(txt_cord_h)
    #print (txt_cord_w)
    draw_text.text(
        (txt_cord_w, txt_cord_h),
        txt,
        font=font,
        fill=fill
    )
    return

#order={'order_cnt':1024, 'user_id':123456789, 'order':{'fio':'Тест Тестович', 'tel':'89539729889', 'date':'20.09.22 15:00', 'location':'Тула, Санаторная 9 - 13', "comment":0, 'order_list':[{"type": "latex", "size":"12\"","color":"Черный", "name":"Латекс", "count":10, "price":105, "summa":1050}]}}
#make_image_order(order)