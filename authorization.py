import vk_api
from vk_api.utils import get_random_id

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
