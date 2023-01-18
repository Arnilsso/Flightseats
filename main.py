from flask import Flask, render_template
import requests
from lxml import etree
import re

app = Flask(__name__)

@app.route("/")
def index():
    hours = input("Enter the number of hours ahead you want to see flights for: ")
    url = f'https://flydata.avinor.no/XmlFeed.asp?TimeFrom=0&TimeTo={hours}&airport=TRD&direction=A'
    response = requests.get(url)
    root = etree.fromstring(response.content)

    flights = []
    for flight in root.findall('.//flight'):
        flight_id = flight.find('.//flight_id').text
        schedule_time = flight.find('.//schedule_time').text
        found = False
        with open("flight_data.txt", "r") as file:
            data = file.readlines()
        for line in data:
            if flight_id in line:
                flight_id, seat_count = line.strip().split(",")
                found = True
                flights.append({"flight_id": flight_id, "schedule_time": schedule_time, "seat_count": seat_count})
                break
        if not found:
            url = f"https://www.flightera.net/en/flight/{flight_id}"
            res = requests.get(url)
            if "seats" in res.text:
                seats_text = re.findall("(\d+) seats", res.text)
                seats_count = int(seats_text[0])
                flights.append({"flight_id": flight_id, "schedule_time": schedule_time, "seat_count": seats_count})
                with open("flight_data.txt", "a") as file:
                    file.write(f"{flight_id}, {seats_count}\n")
            else:
                flights
