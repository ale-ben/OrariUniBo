import json
from datetime import datetime
from pathlib import Path

from custom_utils import sanitize_path
import requests, uuid


def getCurricula():
	curriculaResponse  = requests.get("https://corsi.unibo.it/magistrale/informatica/orario-lezioni/@@available_curricula").json()
	
	return {curriculum['value']: curriculum['label'] for curriculum in curriculaResponse}

def getClassesForYear(curricula, year):

	classes = {}
	print("[INFO] Populating classes JSON")

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
					'curriculum': key,
					'uuid': f"{uuid.uuid4()}"
				}
	return classes

def populate_lessons():
	base_git_url = "https://raw.githubusercontent.com/ale-ben/OrariUniBo/master/out/"
	directory = Path.cwd().joinpath('out')

	if not directory.exists():
		directory.mkdir()

	curricula = getCurricula()

	print(curricula)
	json_object = json.dumps(curricula, indent=None, separators=(',', ':'))
	with open(directory.joinpath("curricula.json"), "w") as outfile:
		outfile.write(json_object)

	classes1 = getClassesForYear(curricula, "1")
	print(classes1)

	json_object = json.dumps(classes1, indent=None, separators=(',', ':'))
	with open(directory.joinpath("year_1.json"), "w") as outfile:
		outfile.write(json_object)

	classes2 = getClassesForYear(curricula, "2")
	print(classes2)

	json_object = json.dumps(classes2, indent=None, separators=(',', ':'))
	with open(directory.joinpath("year_2.json"), "w") as outfile:
		outfile.write(json_object)

	with open(Path.cwd().joinpath("README.md"), "w") as readme:
		readme.write('# OrariUniBo\n\n')
		readme.write('## Year 1\n')
		for lesson in sorted(classes1.items(), key=lambda item: item[1]['title']):
			file_url = sanitize_path(f"{lesson[1]['title']}-{lesson[1]['cod_modulo']}")
			file_url = f"{base_git_url}year_1/{file_url}.ics"
			readme.write(f"- {lesson[1]['title']} ({lesson[1]['cod_modulo']}) [link]({file_url})\n")

		readme.write('\n## Year 2\n')
		for lesson in sorted(classes2.items(), key=lambda item: item[1]['title']):
			file_url = sanitize_path(f"{lesson[1]['title']}-{lesson[1]['cod_modulo']}")
			file_url = f"{base_git_url}year_2/{file_url}.ics"
			readme.write(f"- {lesson[1]['title']} ({lesson[1]['cod_modulo']}) [link]({file_url})\n")

if __name__ == '__main__':
	populate_lessons()