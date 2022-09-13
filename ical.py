from icalendar import Calendar, Event, vCalAddress, vText
import pytz
from datetime import datetime
import os
from pathlib import Path

def make_ical_from_order(order):
    cal = Calendar()
    # Some properties are required to be compliant
    cal.add('prodid', '-//My calendar product//example.com//')
    cal.add('version', '2.0')
    cal.add('attendee', 'MAILTO:abc@example.com')

    # Add subcomponents
    event = Event()
    event.add('name', 'Awesome Meeting')
    event.add('description', 'Define the roadmap of our awesome project')
    event.add('dtstart', datetime(2022, 1, 25, 8, 0, 0, tzinfo=pytz.utc))
    event.add('dtend', datetime(2022, 1, 25, 10, 0, 0, tzinfo=pytz.utc))

    # Add the organizer
    organizer = vCalAddress('MAILTO:jdoe@example.com')

    # Add parameters of the event
    organizer.params['name'] = vText('John Doe')
    organizer.params['role'] = vText('CEO')
    event['organizer'] = organizer
    event['location'] = vText('New York, USA')

    event['uid'] = '2022125T111010/272356262376@example.com'
    event.add('priority', 5)
    attendee = vCalAddress('MAILTO:rdoe@example.com')
    attendee.params['name'] = vText('Richard Roe')
    attendee.params['role'] = vText('REQ-PARTICIPANT')
    event.add('attendee', attendee, encode=0)

    attendee = vCalAddress('MAILTO:jsmith@example.com')
    attendee.params['name'] = vText('John Smith')
    attendee.params['role'] = vText('REQ-PARTICIPANT')
    event.add('attendee', attendee, encode=0)

    # Add the event to the calendar
    cal.add_component(event)

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


