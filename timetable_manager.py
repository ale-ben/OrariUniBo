import json
from pathlib import Path
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import requests
from populate_lesson_json import populate_lessons
from custom_utils import sanitize_path
import pytz
import uuid


def get_timetable_for_class(lesson, year, delta_days=14):
    timetable = Calendar()
    timetable.add("calscale", "GREGORIAN")
    timetable.add("name", f'{lesson["title"]} - {lesson["cod_modulo"]}')
    timetable.add("X-WR-CALNAME", f'{lesson["title"]} - {lesson["cod_modulo"]}')
    timetable.add("X-WR-TIMEZONE", "Europe/Rome")
    timetable.add("REFRESH-INTERVAL;VALUE=DURATION", "P1D")
    timetable.add("uid", lesson["uuid"])
    timetable.add("last-modified", datetime.now().astimezone(pytz.UTC))
    timetable.add("prodid", "-//Unibo Timetable//Timetable Manager//")
    timetable.add("version", "2.0")

    start_date = datetime.now()
    end_date = start_date + timedelta(days=delta_days)

    payload = {
        "start": start_date.strftime("%Y-%m-%d"),
        "end": end_date.strftime("%Y-%m-%d"),
        "anno": year,
        "curricula": lesson["curriculum"],
        "insegnamenti": lesson["ext_code"],
    }
    timetable_response = requests.get(
        "https://corsi.unibo.it/magistrale/informatica/orario-lezioni/@@orario_reale_json",
        params=payload,
    )

    if timetable_response.status_code != 200:
        print(
            "Error while getting classes for year "
            + year
            + ", curriculum "
            + lesson["curriculum"]
            + " and class "
            + lesson["cod_modulo"]
            + " "
            + lesson["title"]
            + ". Url: "
            + timetable_response.url
        )
        return None

    for lesson_event in timetable_response.json():
        event = Event()
        event.add("summary", lesson_event["title"])
        event.add("uid", uuid.uuid4())
        event.add("dtstamp", datetime.now().astimezone(pytz.UTC))
        event.add(
            "dtstart",
            datetime.strptime(lesson_event["start"], "%Y-%m-%dT%H:%M:%S").astimezone(
                pytz.UTC
            ),
        )
        event.add(
            "dtend",
            datetime.strptime(lesson_event["end"], "%Y-%m-%dT%H:%M:%S").astimezone(
                pytz.UTC
            ),
        )
        event.add("location", lesson_event["aule"][0]["des_indirizzo"])
        event.add(
            "description",
            f"{lesson_event['cod_modulo']} - {lesson_event['docente']}\n{lesson_event['aule'][0]['des_edificio']} - {lesson_event['aule'][0]['des_piano']}\n{lesson_event['aule'][0]['des_indirizzo']}\n----autogenerated----",
        )
        timetable.add_component(event)

    return {
        "title": lesson["title"],
        "class_code": lesson["cod_modulo"],
        "year": year,
        "timetable": timetable,
    }


def save_timetable_for_class(timetable_dict):
    # Write to disk
    directory = Path.cwd() / "out" / f'year_{timetable_dict["year"]}'

    if not directory.exists():
        directory.mkdir(parents=True)

    file_name = f"{timetable_dict['title']}-{timetable_dict['class_code']}"
    file_name = sanitize_path(file_name)

    with open(directory.joinpath(f"{file_name}.ics"), "wb") as f:
        f.write(timetable_dict["timetable"].to_ical())


def main():

    directory = Path.cwd().joinpath("out")
    if not directory.exists():
        populate_lessons()

    year_1 = {}
    with open(directory.joinpath("year_1.json"), "r") as f:
        year_1 = json.load(f)

    year_2 = {}
    with open(directory.joinpath("year_2.json"), "r") as f:
        year_2 = json.load(f)

    for lesson_code in year_1:
        timetable = get_timetable_for_class(year_1[lesson_code], "1")
        if timetable is not None:
            save_timetable_for_class(timetable)

    for lesson_code in year_2:
        timetable = get_timetable_for_class(year_2[lesson_code], "2")
        if timetable is not None:
            save_timetable_for_class(timetable)


if __name__ == "__main__":
    main()
