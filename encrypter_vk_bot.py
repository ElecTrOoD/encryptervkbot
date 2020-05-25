import json
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from random import shuffle
from typing import List, Any
import time
from config import *


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


def slicetext(text_in):
    lefthalf = []
    righthalf = []
    while len(text_in) % block_length != 0:
        text_in += "\x20"
    for i in range(0, len(text_in), block_length):
        lefthalf.append(text_in[i:i + int(block_length / 2)])
        righthalf.append(text_in[i + int(block_length / 2):i + int(block_length)])
    return lefthalf, righthalf


def function(text_in, multiplier):
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
    lefthalf: List[Any]
    lefthalf, righthalf = slicetext(text_in)
    text_out = ""
    for i in range(len(righthalf)):
        lefthalf_storage = []
        for j in range(3):
            lefthalf_storage.append(righthalf[i])
            righthalf[i] = addition(lefthalf[i], function(lefthalf_storage[j], multipliers[j]))
            lefthalf[i] = lefthalf_storage[j]
        lefthalf[i] = mix(lefthalf[i])
        righthalf[i] = mix(righthalf[i])
        text_out += str(lefthalf[i]) + str(righthalf[i])
    return text_out


def decrypt(text_in):
    lefthalf: List[Any]
    lefthalf, righthalf = slicetext(text_in)
    for i in range(len(righthalf)):
        lefthalf[i] = sort(lefthalf[i])
        righthalf[i] = sort(righthalf[i])
    text_out = ""
    for i in range(len(righthalf)):
        lefthalf_storage = []
        p = 0
        for j in range(3, 0, -1):
            lefthalf_storage.append(lefthalf[i])
            lefthalf[i] = subtraction(righthalf[i], function(lefthalf_storage[p], multipliers[j - 1]))
            righthalf[i] = lefthalf_storage[p]
            p += 1
        text_out += str(lefthalf[i]) + str(righthalf[i])
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


# noinspection SpellCheckingInspection
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
        # noinspection PyBroadException
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
            # noinspection PyUnboundLocalVariable
            write_msg(event.user_id, 'Произошла ошибка, попробуйте ещё раз.', keyboard, '')
            print('{clock}: Зашифровано неуспешно'.format(clock=time.strftime("%d-%m-%y %H.%M.%S", time.localtime())))
    # noinspection PyBroadException
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
                    # noinspection PyUnboundLocalVariable
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
