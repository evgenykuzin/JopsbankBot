from telebot import types

from models import BankUser


def menu_keyboard():
    keyboard = types.ReplyKeyboardMarkup()
    key_pay = types.KeyboardButton(text='Оплатить')
    keyboard.add(key_pay)
    key_balance = types.KeyboardButton(text='Баланс')
    keyboard.add(key_balance)
    # key_contacts = types.KeyboardButton(text='Контакты')
    # keyboard.add(key_contacts)
    key_allcontacts = types.KeyboardButton(text='Все пользователи')
    keyboard.add(key_allcontacts)
    key_getmoney = types.KeyboardButton(text='Пополнить')
    keyboard.add(key_getmoney)
    key_addcontact = types.KeyboardButton(text='Добавить в контакты или пригласить')
    keyboard.add(key_addcontact)
    return keyboard


def cancel_pay_inline_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    key = types.InlineKeyboardButton(text='Отмена', callback_data='cancel_pay')
    keyboard.add(key)
    return keyboard


def cancel_registration_inline_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    key = types.InlineKeyboardButton(text='Отмена', callback_data='cancel_reg')
    keyboard.add(key)
    return keyboard


def cancel_get_money_inline_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    key = types.InlineKeyboardButton(text='Отмена', callback_data='cancel_get_money')
    keyboard.add(key)
    return keyboard


def send_money_inline_keyboard(bank_user: BankUser):
    keyboard = types.InlineKeyboardMarkup()
    key = types.InlineKeyboardButton(text='Отправить деньги', callback_data=f'send_money:{bank_user.username}')
    keyboard.add(key)
    return keyboard
