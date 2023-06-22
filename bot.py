from vk_api.longpoll import VkLongPoll, VkEventType
import logging


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
