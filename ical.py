from icalendar import Calendar, Event, vCalAddress, vText, vDatetime, Alarm
import pytz
from datetime import datetime, timedelta
import os
from pathlib import Path

def make_ical_from_order(order, msg):
    cal = Calendar()
    # Some properties are required to be compliant
    cal.add('prodid', '-//My calendar product//example.com//')
    cal.add('version', '2.0')
    #cal.add('attendee', 'MAILTO:abc@example.com')


    # Add subcomponents
    event = Event()
    event.add('name', 'Заказ №'+str(order['order_cnt']))
    event.add('summary', 'Заказ №' + str(order['order_cnt']))
    event.add('description', msg)
    print(order['order']['date'])
    #event.add('dtstart', datetime(2022, 1, 25, 8, 0, 0, tzinfo=pytz.utc))
    #event.add('dtend', datetime(2022, 1, 25, 10, 0, 0, tzinfo=pytz.utc))
    if order['order']['date'] != '0':
        try:
            start_time = datetime.strptime(order['order']['date'], '%d.%m.%y %H:%M')
        except ValueError:
            print("Формат даты не соответствует образцу")
            start_time = datetime.strptime(order['order']['date'], '%d.%m.%Y %H:%M')
    else:
        start_time = datetime.strptime('01.01.20 12:00', '%d.%m.%y %H:%M')
    event.add('dtstart', vDatetime(start_time))
    event.add('dtend', vDatetime(start_time))
    event['location'] = vText(order['order']['location'])
    # Add the event to the calendar
    cal.add_component(event)

    alarm = Alarm()
    alarm.add('trigger', timedelta(hours=-2))
    #alarm.add('trigger', timedelta(days=-2))
    alarm.add('action', 'display')
    #desc = " in 5 minutes"
    #alarm.add('description', desc)
    event.add_component(alarm)

    alarm = Alarm()
    #alarm.add('trigger', timedelta(hours=-2))
    alarm.add('trigger', timedelta(days=-2))
    alarm.add('action', 'display')
    # desc = " in 5 minutes"
    # alarm.add('description', desc)
    event.add_component(alarm)



    # Write to disk
    directory = Path.cwd() / Path(str(order['user_id']))
    try:
        directory.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("Folder already exists")
    else:
        print("Folder was created")
    print("ics file will be generated at ", directory)
    f = open(os.path.join(directory, str(order['order_cnt'])+".ics"), 'wb')
    f.write(cal.to_ical())
    f.close()

    #from pathlib import Path

    directory_flask = Path('/var/www/html/flask_project/'+str(order['user_id']))
    try:
        directory_flask.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("Folder already exists")
    else:
        print("Folder was created")
    dest = directory_flask / Path(str(order['order_cnt'])+".ics")
    src = directory / Path(str(order['order_cnt'])+".ics")
    dest.write_bytes(src.read_bytes())  # for binary files
    print("ics file will be copy at ", directory_flask)
    #dest.write_text(src.read_text())  # for text files


