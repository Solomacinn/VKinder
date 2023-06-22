import sqlite3

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