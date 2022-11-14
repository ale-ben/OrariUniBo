import json
from datetime import datetime
from pathlib import Path

import requests


def getCurricula():
	curriculaResponse  = requests.get("https://corsi.unibo.it/magistrale/informatica/orario-lezioni/@@available_curricula").json()
	
	return {curriculum['value']: curriculum['label'] for curriculum in curriculaResponse}

def getClassesForYear(curricula, year):

	classes = {}

	start_date = datetime.now()
	if start_date.month >= 8:
		end_date = datetime(start_date.year, 12, 31)
	else:
		end_date = datetime(start_date.year, 8, 1)

	for key in curricula:
		payload = {'start': start_date.strftime("%Y-%m-%d"), 'end': end_date.strftime("%Y-%m-%d"), 'anno': year, 'curricula': key}
		classesResponse = requests.get('https://corsi.unibo.it/magistrale/informatica/orario-lezioni/@@orario_reale_json', params=payload)
		
		if classesResponse.status_code != 200:
			print("Error while getting classes for year " + year + " and curriculum " + key)
			return None

		for classJson in classesResponse.json():
			if classJson['cod_modulo'] not in classes:
				classes[classJson['cod_modulo']] = {
					'title': classJson['title'],
					'ext_code': classJson['extCode'],
					'docente': classJson['docente'],
					'crediti': classJson['cfu'],
					'cod_modulo': classJson['cod_modulo'],
					'curriculum': key
				}
	return classes

def populate_lessons():
	directory = Path.cwd().joinpath('out')

	if not directory.exists():
		directory.mkdir()

	curricula = getCurricula()

	print(curricula)
	json_object = json.dumps(curricula, indent=None, separators=(',', ':'))
	with open(directory.joinpath("curricula.json"), "w") as outfile:
		outfile.write(json_object)

	classes = getClassesForYear(curricula, "2")
	print(classes)

	classes = getClassesForYear(curricula, "1")
	print(classes)

	json_object = json.dumps(classes, indent=None, separators=(',', ':'))
	with open(directory.joinpath("year_1.json"), "w") as outfile:
		outfile.write(json_object)

	classes = getClassesForYear(curricula, "2")
	print(classes)

	json_object = json.dumps(classes, indent=None, separators=(',', ':'))
	with open(directory.joinpath("year_2.json"), "w") as outfile:
		outfile.write(json_object)

if __name__ == '__main__':
	populate_lessons()