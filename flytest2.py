from datetime import datetime
import requests
from lxml import etree
import re
import pytz


url = f'https://flydata.avinor.no/XmlFeed.asp?TimeFrom=1&TimeTo=4&airport=TRD&direction=A'
response = requests.get(url)
root = etree.fromstring(response.content)

for flight in root.findall('.//flight'):
    flight_id = flight.find('.//flight_id').text #find flight id in the xml response
    schedule_time = flight.find('.//schedule_time').text #find schedueled time in the XML, it will be listed in UTC
    schedule_time = datetime.strptime(schedule_time, "%Y-%m-%dT%H:%M:%SZ")
    gmt_1 = pytz.timezone("Europe/Oslo")
    schedule_time = schedule_time.replace(tzinfo=pytz.utc).astimezone(gmt_1) #Change time to gmt+1
    from_airport = flight.find('.//airport').text
    found = False
    #search text file first
    with open("flight_data.txt", "r") as file:
        data = file.readlines()
    for line in data:
        if flight_id in line:
            flight_id, seat_count = line.strip().split(",")
            found = True
            print(f"Seat count for flight {flight_id} from {from_airport} scheduled at {schedule_time} is: {seat_count}")
            break
    if not found:
        #if flight id is not found in text file, get the seat numbers from the flightera website
        url = f"https://www.flightera.net/en/flight/{flight_id}"
        res = requests.get(url)
        if "seats" in res.text:
            seats_text = re.findall("(\d+) seats", res.text)
            seats_count = int(seats_text[0])
            print(f"Flight {flight_id} from {from_airport} scheduled at {schedule_time} has a total seat numbers on this flight is: {seats_count}")
            with open("flight_data.txt", "a") as file:
                file.write(f"{flight_id}, {seats_count}\n")
        else:
            print(f"Flight {flight_id} from {from_airport} scheduled at {schedule_time}, was unfortunately unable to find seat numbers for this flight")
