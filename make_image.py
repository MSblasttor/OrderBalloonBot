from PIL import Image, ImageDraw, ImageFont


font_path = "fonts/Steclo.otf"

def make_image_order(order):
    pagesize_w, pagesize_h = (744, 1052)
    im = Image.new('RGB', (pagesize_w, pagesize_h), color=('#FAACAC'))
    template = Image.open('img/order_templ.png')
    im.paste(template, (0, 0))
    template.close()
    #Заполняем поле номер заказа
    txt = str(order['order_cnt'])
    make_txt(im, 260, 80, txt, "centr", 60)
    #Заполняем поле ФИО
    txt = str(order['order']['fio'])
    make_txt(im, 260, 180, txt)
    #Заполняем поле Телефон
    txt = str(order['order']['tel'])
    make_txt(im, 260, 210, txt)
    #Заполняем поле Дата
    txt = str(order['order']['date'])
    make_txt(im, 260, 240, txt)
    #Заполняем поле Дата
    txt = str(order['order']['location'])
    make_txt(im, 260, 270, txt)
    count = 0
    message = ""
    summa = 0
    for element in order['order']['order_list']:
        result = order['order']['order_list'][count]['type']
        if result == 'latex':
            msg_str = 'Шар %(name)s %(size)s Цвет: %(color)s Кол-во - %(count)d шт. Цена %(price)d руб. \n' % \
                      order['order']['order_list'][count]
            # print (msg_str)
            message += '%d. ' % (count + 1)
            message += msg_str
        elif result == 'foil_fig' and not (
                order['order']['order_list'][count]["name"] == 'Сердце' or order['order']['order_list'][count][
            "name"] == 'Звезда' or order['order']['order_list'][count]["name"] == 'Круг'):
            msg_str = 'Фигура %(name)s Цена %(price)d руб. \n' % order['order']['order_list'][count]
            message += '%d. ' % (count + 1)
            message += msg_str
        elif result == 'foil_fig' and (
                order['order']['order_list'][count]["name"] == 'Сердце' or order['order']['order_list'][count][
            "name"] == 'Звезда' or order['order']['order_list'][count]["name"] == 'Круг'):
            msg_str = 'Фигура %(name)s Цвет: %(color)s Цена %(price)d руб. \n' % order['order']['order_list'][count]
            # print (msg_str)
            message += '%d. ' % (count + 1)
            message += msg_str
        elif result == 'foil_num':
            msg_str = 'Цифра %(name)s Цвет %(color)s Цена %(price)d руб. \n' % order['order']['order_list'][count]
            # print (msg_str)
            message += '%d. ' % (count + 1)
            message += msg_str
        elif result == 'bubl':
            msg_str = 'Баблс %(size)s с наполнением: %(name)s Цвет: %(color)s Цена %(price)d руб. \n' % \
                      order['order']['order_list'][count]
            # print (msg_str)
            message += '%d. ' % (count + 1)
            message += msg_str
        elif result == 'label':
            msg_str = 'Надпись %(name)s Цвет: %(color)s. \n' % order['order']['order_list'][count]
            # print (msg_str)
            message += '%d. ' % (count + 1)
            message += msg_str
        elif result == 'stand':
            msg_str = 'Стойка %(name)s Цена (Аренда) %(price)d руб. \n' % order['order']['order_list'][count]
            # print (msg_str)
            message += '%d. ' % (count + 1)
            message += msg_str
        elif result == 'other':
            msg_str = 'Другое: %(comment)s. Цена %(price)d руб. \n' % order['order']['order_list'][count]
            # print (msg_str)
            message += '%d. ' % (count + 1)
            message += msg_str
        summa += order['order']['order_list'][count]["summa"]
        count += 1
        make_txt(im, 50, 320+count*30, message, "left")
    # Сохраняем изображение
    print("Save pic order")
    im.save('img/order/new_pic1.png')

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

#order={'order_cnt':1024, 'order':{'fio':'Тест Тестович', 'tel':'89539729889', 'date':'20.09.22 15:00', 'location':'Тула, Санаторная 9 - 13', "comment":0, 'order_list':[{"type": "latex", "size":"12\"","color":"Черный", "name":"Латекс", "count":10, "price":105, "summa":1050}]}}
#make_image_order(order)