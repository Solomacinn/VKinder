import vk_api
from vk_api.utils import get_random_id
from vk_api.longpoll import VkLongPoll, VkEventType
import datetime
import sqlite3

# Авторизация в VK API
class VkClient(object):
    def __init__(self):
        self.vk = self.auth_vk()   
    def auth_vk(self):
        token = input("Enter your VK token: ")
        vk_session = vk_api.VkApi(token=token)
        return vk_session.get_api()

# Получение данных о пользователе
def get_user_info(self, user_id):
    user = self.vk.users.get(user_ids=user_id, fields=['sex', 'bdate', 'city', 'relation'])[0]
    user_info = {key: user[key] for key in ['id', 'first_name', 'last_name'] if key in user}
    user_info.update({key: user[key]['title'] for key in ['city'] if key in user})
    user_info.update({key: user[key] for key in ['sex', 'bdate', 'relation'] if key in user})
    return user_info

# Поиск подходящих людей
def find_people(self, user_info):
    search_params = {
        'sex': 1 if user_info['sex'] == 2 else 2,
        'status': 6 if user_info.get('relation') == 1 else 1,
        'age_from': calculate_age(user_info.get('bdate')) - 2,
        'age_to': calculate_age(user_info.get('bdate')) + 2
    }
    city = user_info.get('city')
    if city:
        city_id = self.vk.database.getCities(q=city, count=1)['items'][0]['id']
        search_params['city'] = city_id
    search_results = self.vk.users.search(count=1000, **search_params)
    return search_results['items']

# Рассчет возраста пользователя
from dateutil.relativedelta import relativedelta

def calculate_age(bdate):
    bdate = datetime.datetime.strptime(bdate, '%d.%m.%Y').date()
    today = datetime.date.today()
    age = relativedelta(today, bdate).years
    return age

def prompt_user():
    user_input = {}
    user_input['name'] = input("Enter the person's name or VK id: ")
    user_input['age'] = input("Enter the person's age: ")
    user_input['city'] = input("Enter the person's city: ")
    user_input['sex'] = input("Enter the person's sex: ")
    user_input['relation'] = input("Enter the person's relation: ")
    return user_input['name'], user_input['age'], user_input['city'], user_input['sex'], user_input['relation']

# Получение топ-3 фото профиля
def get_top_photos(self,user_id):
    self.vk = self.auth_vk()
    photo_params = {'owner_id': user_id, 'album_id': 'profile', 'extended': 1}
    photos = self.vk.photos.get(**photo_params)['items']
    photos.sort(key=lambda x: x['likes']['count'] + x['comments']['count'], reverse=True)
    top_photos = [{'url': p['sizes'][-1]['url'], 'likes': p['likes']['count'], 'comments': p['comments']['count']} for p in photos[:3]]
    return top_photos

# Отправка сообщения с найденным человеком и топ-3 фото

def send_message(self, user_id, person, top_photos):
    message = f"Мы нашли для вас человека, который может вам подойти!\nПользователь: {person['first_name']} {person['last_name']}\n"
    if 'city' in person:
        message += f"Город: {person['city']}\n"
    if 'bdate' in person:
        message += f"Возраст: {calculate_age(person['bdate'])}\n"
    message += f"Ссылка на профиль: https://vk.com/id{person['id']}\n\n"
    for i, photo in enumerate(top_photos):
        message += f"Топ-{i+1} фото:\nЛайки: {photo['likes']}\nКомментарии: {photo['comments']}\nСсылка на фото: {photo['url']}\n\n"
    self.vk.messages.send(user_id=user_id, message=message, random_id=get_random_id())
    
                                 

# Запись результатов в БД
class DBConnection:
    def __init__(self):
        self.conn = sqlite3.connect('vk.bot.db')
        self.cursor = self.conn.cursor()
    def _enter_(self):
        return self.cursor
    def _exit_(self):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

def save_result(user_id, people):
    with DBConnection() as c:
        c.execute('''CREATE TABLE IF NOT EXISTS search_results 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INT, person_id INT, 
                        first_name TEXT, last_name TEXT, city TEXT, age INT, likes INT, comments INT)''')
        for person in people:
            c.execute('''INSERT INTO search_results (user_id, person_id, first_name, last_name, city, age, likes, comments) 
                    VALUES(?,?,?,?,?,?,?,?)''', (user_id, person['id'], person['first_name'], person['last_name'], person['city'], person['age'], person['likes'], person['comments']))
    
       
 # Получение сохраненных результатов поиска
def get_saved_people(user_id):
    with sqlite3.connect('vk_bot.db') as conn:
        c = conn.cursor()
        c.execute("SELECT person_id FROM search_results WHERE user_id=?", (user_id,))
        saved_people = [result[0] for result in c.fetchall()]
    return saved_people
   
# Поиск и отправка сообщения подходящим людям
import logging
logger = logging.getLogger(__name__)

def start_search(user_id):
    user_info = get_user_info(user_id)
    people = find_people(user_info)
    saved_people = get_saved_people(user_id)
    new_people = [person for person in people if person['id'] not in saved_people]
    if new_people:
        for person in new_people:
            top_photos = get_top_photos(person['id'])
            send_message(user_id, person, top_photos)
        save_result(user_id, new_people)
        logger.info('Search completed successfully for user %s' % user_id)


# Запуск бота

class Bot:
    def __init__(self):
        self.vk = self.auth_vk()
        self.longpoll = VkLongPoll(self.vk)

    def run(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                try:
                    if event.text.strip().lower() == 'начать':
                        self.start_search(event.user_id)
                except Exception as e:
                    logger.error(f'Error occured: {e}') 

