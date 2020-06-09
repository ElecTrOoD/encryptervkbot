import json
import time
from random import shuffle
from typing import List, Any

import vk_api
from config import *
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id


def mix(string_in):
    mixed_string = ""
    for i in range(len(key)):
        mixed_string += string_in[key[i]]
    return mixed_string


def sort(string_in):
    sorted_string = ""
    for i in range(len(string_in)):
        for j in range(len(string_in)):
            if key[j] == i:
                sorted_string += string_in[j]
                break
    return sorted_string


def slice_text(text_in):
    left_half = []
    right_half = []
    while len(text_in) % block_length != 0:
        text_in += "\x20"
    for i in range(0, len(text_in), block_length):
        left_half.append(text_in[i:i + int(block_length / 2)])
        right_half.append(text_in[i + int(block_length / 2):i + int(block_length)])
    return left_half, right_half


def transformation(text_in, multiplier):
    text_out = ""
    for i in range(len(text_in)):
        letter_number = alphabet.index(text_in[i]) * multiplier % len(alphabet)
        text_out += alphabet[letter_number]
    return text_out


def addition(string_1, string_2):
    text_out = ""
    for i in range(len(string_1)):
        text_out += alphabet[int((alphabet.index(string_1[i]) + alphabet.index(string_2[i])) % len(alphabet))]
        i += 1
    return text_out


def subtraction(string_1, string_2):
    text_out = ""
    for i in range(len(string_1)):
        text_out += alphabet[(int(alphabet.index(string_1[i])) - alphabet.index(string_2[i])) % len(alphabet)]
    return text_out


def crypt(text_in):
    left_half, right_half = slice_text(text_in)
    text_out = ""
    for i in range(len(right_half)):
        left_half_storage = []
        for j in range(3):
            left_half_storage.append(right_half[i])
            right_half[i] = addition(left_half[i], transformation(left_half_storage[j], multipliers[j]))
            left_half[i] = left_half_storage[j]
        left_half[i] = mix(left_half[i])
        right_half[i] = mix(right_half[i])
        text_out += str(left_half[i]) + str(right_half[i])
    return text_out


def decrypt(text_in):
    left_half: List[Any]
    left_half, right_half = slice_text(text_in)
    for i in range(len(right_half)):
        left_half[i] = sort(left_half[i])
        right_half[i] = sort(right_half[i])
    text_out = ""
    for i in range(len(right_half)):
        left_half_storage = []
        p = 0
        for j in range(3, 0, -1):
            left_half_storage.append(left_half[i])
            left_half[i] = subtraction(right_half[i], transformation(left_half_storage[p], multipliers[j - 1]))
            right_half[i] = left_half_storage[p]
            p += 1
        text_out += str(left_half[i]) + str(right_half[i])
    return text_out


def write_msg(user_id, message, keyboard_style, attachment):
    vk.method('messages.send',
              {'user_id': user_id,
               'message': message,
               'random_id': get_random_id(),
               'keyboard': keyboard_style,
               'attachment': attachment}
              )


def get_button(label, color, payload=''):
    return {
        'action': {
            'type': 'text',
            'payload': json.dumps(payload),
            'label': label
        },
        'color': color
    }


answer = 0
vk = vk_api.VkApi(token=TOKEN)
longpoll = VkLongPoll(vk)

keyboard = {
    'one_time': True,
    'buttons': [[
        get_button(label='Зашифровать', color='positive', payload='Зашифровать'),
        get_button(label='Дешифровать', color='primary', payload='Дешифровать')
    ], [
        get_button(label='FAQ', color='negative', payload='FAQ')
    ]]
}

keyboard = json.dumps(keyboard, ensure_ascii=False).encode('utf-8')
keyboard = str(keyboard.decode('utf-8'))

print('{clock}: Бот запущен.'.format(clock=time.strftime("%d-%m-%y %H.%M.%S", time.localtime())))

while True:
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            request = event.text
            if request.lower() == 'начать' or request.lower() == 'faq':
                write_msg(event.user_id,
                          "Привет, меня создал техномаг и моя основная задача шифровать/дешифровать сообщения, "
                          "чтобы злые ФСБ'шники не узнали что ты делал этим летом.\nМаксимальная длина сообщения – "
                          "4000 символов.\nПоддерживаются цифры, латинские и кириллические буквы, а так же спец "
                          "символы: + - – . , … ! ? : ; ( ) / \ \nПеренос строк не поддерживается!\nДля использования "
                          "моих функций воспользуйся меню. ",
                          keyboard, '')
                print('{clock}: FAQ.'.format(clock=time.strftime("%d-%m-%y %H.%M.%S", time.localtime())))
            elif request.lower() == 'зашифровать':
                write_msg(event.user_id, 'Введите текст который хотите зашифровать', '', '')
                print('{clock}: Шифруем.'.format(clock=time.strftime("%d-%m-%y %H.%M.%S", time.localtime())))
                answer = 1
                break
            elif request.lower() == 'дешифровать':
                write_msg(event.user_id, 'Введите ключ дешифровки.', '', '')
                print('{clock}: Дешифруем.'.format(clock=time.strftime("%d-%m-%y %H.%M.%S", time.localtime())))
                answer = 2
                break
            elif request.lower() != 'начать' and request.lower() != 'faq':
                write_msg(event.user_id, 'Воспользуйтесь меню.', keyboard, '')
                print('{clock}: Пользователь неопределился.'.format(
                    clock=time.strftime("%d-%m-%y %H.%M.%S", time.localtime())))
    if answer == 1:
        try:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                    request = event.text
                    user_key = ''
                    key = [i for i in range(0, int(block_length / 2))]
                    shuffle(key)
                    multipliers = []
                    for i in range(3):
                        multipliers.append((key[i] + key[i + 3] + key[i + 6]) ** (i + 2) % len(alphabet))
                    for i in range(len(key)):
                        user_key += str(key[i])
                    write_msg(event.user_id, '↓↓↓ Ваш ключ дешифровки ↓↓↓', '', '')
                    write_msg(event.user_id, user_key, '', '')
                    write_msg(event.user_id, '↓↓↓ Ваш зашифрованный текст ↓↓↓', '', '')
                    write_msg(event.user_id, crypt(request), keyboard, '')
                    print('{clock}: Зашифровано успешно!'.format(
                        clock=time.strftime("%d-%m-%y %H.%M.%S", time.localtime())))
                    break
        except:
            write_msg(event.user_id, 'Произошла ошибка, попробуйте ещё раз.', keyboard, '')
            print('{clock}: Зашифровано неуспешно'.format(clock=time.strftime("%d-%m-%y %H.%M.%S", time.localtime())))
    try:
        if answer == 2:
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                    request = str(event.text)
                    secret_key = request
                    key = []
                    for i in range(len(request)):
                        key.append(int(request[i]))
                    multipliers = []
                    for i in range(3):
                        multipliers.append((key[i] + key[i + 3] + key[i + 6]) ** (i + 2) % len(alphabet))
                    write_msg(event.user_id, 'Введите текст, который хотите дешифровать.', '', '')
                    break
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                    request = event.text
                    if secret_key == '0123456789' and request.lower() == 'секретные материалы':
                        write_msg(event.user_id, '', keyboard, 'photo-195601257_457239020')
                        print('{clock}: Шалун решил поглядеть на секретные материалы.'.format(
                            clock=time.strftime("%d-%m-%y %H.%M.%S", time.localtime())))
                    else:
                        write_msg(event.user_id, '↓↓↓ Ваш расшифрованный текст ↓↓↓', '', '')
                        write_msg(event.user_id, decrypt(request), keyboard, '')
                        print('{clock}: Дешифровано успешно!'.format(
                            clock=time.strftime("%d-%m-%y %H.%M.%S", time.localtime())))
                    break
    except:
        write_msg(event.user_id, 'Произошла ошибка, попробуйте ещё раз.', keyboard, '')
        print('{clock}: Дешифровано неуспешно.'.format(clock=time.strftime("%d-%m-%y %H.%M.%S", time.localtime())))
