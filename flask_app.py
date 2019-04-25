from flask import Flask, request
import logging
import json
from geo import full_info

app = Flask(__name__)

sessionStorage = {}

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s %(levelname)s %(name)s %(message)s')

@app.route('/post', methods=['POST'])
def main():

    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(response, request.json)

    logging.info('Request: %r', response)

    return json.dumps(response)


def handle_dialog(res, req):

    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,  # здесь будет храниться имя
            'home': None,  # адресс пользователя
            'org': None
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            res['response']['text'] = f'{first_name.title()}. Я Алиса. Я могу показать ближайшую организацию, сказать расстояние между вами и организацией и показать ее на карте! Скажи организацию, которую хочешь найти (например аптека или кафе)'
    else:
        first_name = sessionStorage[user_id]['first_name']
        if 'показать организацию на карте' in req['request']['original_utterance']:
            res['response']['text'] = f'{first_name.title()}, давай найдем что нибудь еще! Скажи ближайшую организию которую хочешь найти (например аптека или кафе)'

        elif sessionStorage[user_id]['org'] is None:
            sessionStorage[user_id]['org'] = get_org(req)
            if sessionStorage[user_id]['home'] is None:
                res['response']['text'] = f'{first_name.title()}, стоп скажи, где ты находишься'
            else:
                snip = full_info(sessionStorage[user_id]['home'], sessionStorage[user_id]['org'])
                url = snip['ссылка']
                res['response']['text'] = '{}, {} находится по адрессу {}, часы работы {}, растояние {}метров'.format(first_name, snip['Название'], snip['Адрес'], snip['Часы работы'], snip['Растояние в метрах'])
                res['response']['buttons'] = [
                    {
                        'title': 'показать организацию на карте',
                        'hide': True,
                        'url': 'https://static-maps.yandex.ru/1.x/?l=map&pt={},pmgrs~{},flag'.format(url[0], url[1])
                    }
                ]
                sessionStorage[user_id]['org'] = None

        elif sessionStorage[user_id]['home'] is None:
            home = get_home(req)
            if home:
                sessionStorage[user_id]['home'] = home
                snip = full_info(home, sessionStorage[user_id]['org'])
                url = snip['ссылка']
                res['response']['text'] = '{}, {} находится по адрессу {}, часы работы {}, растояние {}метров'.format(first_name, snip['Название'], snip['Адрес'], snip['Часы работы'], snip['Растояние в метрах'])
                res['response']['buttons'] = [
                    {
                        'title': 'показать организацию на карте',
                        'hide': True,
                        'url': 'https://static-maps.yandex.ru/1.x/?l=map&pt={},pmgrs~{},flag'.format(url[0], url[1])
                    }
                ]
                sessionStorage[user_id]['org'] = None
            else:
                res['response']['text'] = f'{first_name.title()}, не расслышала адресс. Повтори, пожалуйста!'


def get_org(req):
    return req['request']['original_utterance']


def get_home(req):

    home = []

    for entity in req['request']['nlu']['entities']:

        if entity['type'] == 'YANDEX.GEO':
            for keys in entity['value']:
                home.append(entity['value'][keys])
    return ' '.join(home)


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name', то возвращаем её значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    app.run()