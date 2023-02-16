from PIL import Image, ImageDraw, ImageFont
import pathlib

from math import ceil

font_path = "/root/OrderBalloonBot/fonts/Steclo.otf"
def make_template_image(user):
    pagesize_w, pagesize_h = (744, 1052)
    color = user['color_bg'] if user['color_bg'] == None else '#FFFFFF'
    im = Image.new('RGB', (pagesize_w, pagesize_h), color='#FAACAC')
    logosize_w, logosize_h = (250, 250)
    try:
        # for Debug uncomment next line
        # logo_img = Image.open('/img/' + str(order['user_id']) + '/order_logo_' + str(order['user_id']) + '.png')
        logo_img = Image.open('/root/OrderBalloonBot/img/' + str(user['user_id']) + '/order_logo_' + str(user['user_id']) +'.png')
        logo_img.thumbnail(size=(logosize_w, logosize_h))
    except:
        # for Debug uncomment next line
        # logo_img = Image.open('C:/Users/GladkihAA/PycharmProjects/OrderBalloonBot/img/logo_for_order.png') for
        logo_img = Image.open('/root/OrderBalloonBot/img/order_logo_templ.png')
    im.paste(logo_img, (pagesize_w-logosize_w-10, 10))
    logo_img.close()
    txt = "Карточка заказа"
    make_txt(im, 93, 25, txt, "left", 60)
    # Заполняем поле номер заказа
    txt = "№ _________"
    make_txt(im, 150, 80, txt, "left", 60)
    txt_mass = ["ФИО Заказчика:", "Телефон:", "Дата и время:", "Адрес:"]
    i = 0
    for txt in txt_mass:
        make_txt(im, 45, 180+i*30, txt, "left")
        i += 1
    # Состав заказа
    txt = "Состав заказа"
    make_txt(im, pagesize_w/2, 180+i*30, txt, "centr", 45)
    # Сохраняем изображение

    # for Debug uncomment next line
    # directory_order = pathlib.Path('C:/Users/GladkihAA/PycharmProjects/OrderBalloonBot/img/' + str(order['user_id']))
    directory_order = pathlib.Path('/root/OrderBalloonBot/img/' + str(user['user_id']))
    try:
        directory_order.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("Folder for pic: " + str(user['user_id']) + " already exists")
    else:
        print("Folder for pic: " + str(user['user_id']) + " was created")
    # for Debug uncomment next line
    # path_img = "C:/Users/GladkihAA/PycharmProjects/OrderBalloonBot/img/" + str(order['user_id']) + "/order_templ_test" + str(
    #    order['user_id']) + ".png"
    path_img = "/root/OrderBalloonBot/img/" + str(user['user_id']) + "/order_templ_test" + str(user['user_id']) + ".png"
    im.save(path_img)
    print("Save pic order")
    return


def make_image_order(order):
    pagesize_w, pagesize_h = (744, 1052)
    im = Image.new('RGB', (pagesize_w, pagesize_h), color='#FAACAC')
    #print(order['user_id'])
    try:
        template = Image.open('/root/OrderBalloonBot/img/' + str(order['user_id']) + '/order_templ_' + str(order['user_id']) + '.png')
    except:
        template = Image.open('/root/OrderBalloonBot/img/order_templ.png')
    im.paste(template, (0, 0))
    template.close()
    # print(order)
    # Заполняем поле номер заказа
    txt = str(order['order_cnt'])
    make_txt(im, 260, 80, txt, "centr", 60)
    # Заполняем поле ФИО
    txt = str(order['order']['fio'])
    make_txt(im, 220, 180, txt, "left")
    # Заполняем поле Телефон
    txt = str(order['order']['tel'])
    make_txt(im, 220, 210, txt, "left")
    # Заполняем поле Дата
    txt = str(order['order']['date'])
    make_txt(im, 220, 240, txt, "left")
    # Заполняем поле Дата
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
                order['order']['order_list'][count]["name"] == 'Сердце' or
                order['order']['order_list'][count]["name"] == 'Звезда' or
                order['order']['order_list'][count]["name"] == 'Круг'):
            msg_str = 'Фигура %(name)s Цена %(price)d руб. \n' % order['order']['order_list'][count]
            message = '%d. ' % (count + 1)
            message += msg_str
        elif result == 'foil_fig' and (
                order['order']['order_list'][count]["name"] == 'Сердце' or
                order['order']['order_list'][count]["name"] == 'Звезда' or
                order['order']['order_list'][count]["name"] == 'Круг'):
            msg_str = 'Фигура %(name)s Цвет: %(color)s Кол-во - %(count)d шт. Цена %(price)d руб. \n' % order['order']['order_list'][count]
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
        elif result == 'accessories':
            if order['order']['order_list'][count]['comment'] != 0:
                msg_str = '%(name)s Кол-во - %(count)d шт. Цена %(price)d руб. Комментарий: %(comment)s \n' % order['order']['order_list'][count]
            else:
                msg_str = '%(name)s Кол-во - %(count)d шт. Цена %(price)d руб. \n' % order['order']['order_list'][count]
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
        make_txt(im, 50, 320+count*30, message, "left")
    count += 1
    if order['order']['comment'] != 0:
        message = 'Комментарий: %s' % order['order']['comment']
        count += 1
        make_txt(im, 50, 320 + count * 30, message, "left")
    message = 'Итого сумма заказа без учета доставки: %d руб.' % summa
    count += 1
    make_txt(im, 50, 320 + count * 30, message, "left")
    if 'dostavka' in order['order'] and order['order']['dostavka'] != 0:
        print(order['order']['dostavka'])
        message = 'Доставка: %d руб.' % order['order']['dostavka']
        summa = summa + order['order']['dostavka']
        count += 1
        make_txt(im, 50, 320 + count * 30, message, "left")
    else:
        print("Not dostavka")
    if 'predoplata' in order['order']:
        if summa - order['order']['predoplata'] > 0:
            message = 'Предоплата: %d руб.' % order['order']['predoplata']
            message += '\nОсталось доплатить %d руб.' % (summa - order['order']['predoplata'])
        else:
            message = 'Все оплачено'
    else:
        message = 'Необходимая предоплата: %d руб.' % (summa // 2)
    count += 1
    make_txt(im, 50, 320 + count * 30, message, "left")
    count += 1
    if 'reference' in order['order'] and order['order']['reference'] != 0:
        count += 2
        message = "Референсы"
        make_txt(im, pagesize_w/2, 320 + count * 30, message, "centr", font_size=45)
        count += 1
        max_pic_inline = 4
        row = ceil(order['order']['reference'] / max_pic_inline)
        cells = order['order']['reference'] if order['order']['reference'] <= max_pic_inline else max_pic_inline
        # В случае наличия картинок референсов необходимо вычислить допустимую максимальную ширину и высоту картинок с учетом отступа
        max_width_pic_ref = (pagesize_w - 50 - 25 * (cells-1)) / cells
        max_height_pic_ref = (pagesize_h - 25 - (320 + 30 + count * 30) - 25 * (row - 1)) / row
        print(max_width_pic_ref)
        print(max_height_pic_ref)

        for i in range(order['order']['reference']):
            reference_path = str(pathlib.Path.cwd()) + "/orders/" + str(order['user_id']) + "/" + str(order['order_cnt']) + "/reference/" + str(i + 1) + ".jpg"
            reference = Image.open(reference_path)
            reference.thumbnail(size=(int(max_width_pic_ref), int(max_height_pic_ref)))
            if order['order']['reference'] == 1:
                width, height = reference.size
                cord_x_ref = (pagesize_w - width) // 2
            else:
                cord_x_ref = int(max_width_pic_ref * i)+25*i+25 if i <= 3 else int(max_width_pic_ref * (i-4))+25*(i-4)+25
            step = max_height_pic_ref * (ceil((i + 1) / max_pic_inline) - 1) + 25 * (ceil((i + 1) / max_pic_inline) - 1)
            cord_y_ref = 320 + 30 + count * 30 + int(step)
            im.paste(reference, (cord_x_ref, cord_y_ref))
            reference.close()

    # Сохраняем изображение
    directory_order = pathlib.Path('/root/OrderBalloonBot/img/' + str(order['user_id']))
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

def make_txt(image, x, y, txt, align="centr", font_size=30, font_path="/root/OrderBalloonBot/fonts/Steclo.otf", fill='#1C0606'):
    font = ImageFont.truetype(font_path, font_size)
    draw_text = ImageDraw.Draw(image)
    left, top, right, bottom = font.getbbox(txt)
    if align == "centr":
        txt_cord_w = x - right / 2
        txt_cord_h = y
    elif align == "left":
        txt_cord_w = x
        txt_cord_h = y
    draw_text.text(
        (txt_cord_w, txt_cord_h),
        txt,
        font=font,
        fill=fill
    )
    return


order={'order_cnt': 1024, 'user_id': 123456789, 'order': {'fio': 'Тест Тестович', 'tel': '89539729889', 'date': '20.09.22 15:00', 'location': 'Тула, Санаторная 9 - 13', "comment": 0, "reference": 2, 'order_list': [{"type": "latex", "size": "12\"", "color": "Черный", "name": "Латекс", "count": 10, "price": 105, "summa": 1050}]}}
# make_image_order(order)
make_template_image(order)