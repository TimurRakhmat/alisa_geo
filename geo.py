import requests, sys
from math import sin, cos, sqrt, atan2, radians


def full_info(home, org):
    toponym_to_find = home

    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {"geocode": toponym_to_find, "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        print("Ошибка не найден объект")
        sys.exit(1)
    json_response = response.json()
    # Получаем первый топоним из ответа геокодера.
    toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
    # Координаты центра топонима:
    toponym_coodrinates = toponym["Point"]["pos"]
    # Долгота и широта:
    toponym_longitude, toponym_lattitude = toponym_coodrinates.split(" ")

    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

    address_ll = ",".join([toponym_longitude, toponym_lattitude])

    search_params = {
        "apikey": api_key,
        "text": org,
        "lang": "ru_RU",
        "ll": address_ll,
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)
    if not response:
        pass
    json_response = response.json()

    # Получаем первую найденную организацию.
    organization = json_response["features"][0]
    # Название организации.
    org_name = organization["properties"]["CompanyMetaData"]["name"]
    # Адрес организации.
    org_address = organization["properties"]["CompanyMetaData"]["address"]

    org_time = organization["properties"]["CompanyMetaData"]["Hours"]["text"]

    # Получаем координаты ответа.
    point = organization["geometry"]["coordinates"]
    org_point = "{0},{1}".format(point[0], point[1])

    #сниппет
    snip = {
        'Адрес': org_address,
        'Название': org_name,
        'Часы работы': org_time,
        'ссылка': (address_ll, org_point),
        'Растояние в метрах': get_distance(list(map(lambda x: float(x), (point[0], point[1]))), list(map(lambda x: float(x), toponym_coodrinates.split())))
    }
    return snip


def get_distance(p1, p2):

    R = 6373.0

    lon1 = radians(p1[0])
    lat1 = radians(p1[1])
    lon2 = radians(p2[0])
    lat2 = radians(p2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return round(distance * 1000)