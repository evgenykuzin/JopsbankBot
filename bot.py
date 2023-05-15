import telebot
from telebot import types
from functools import lru_cache

import payments_service
import utils
import bank_users_service
import bot_keyboards
import botenv
from bot_keyboards import cancel_pay_inline_keyboard, cancel_registration_inline_keyboard
from models import BankUser
from utils import is_blank


class UserSession:
    session_id: int

    def __init__(self, session_id):
        self.session_id = session_id


class Registration(UserSession):
    first_name = None
    last_name = None
    phone = None
    username = None

    def __str__(self):
        return f"Registration(session=" \
               f"{self.session_id}, " \
               f"{self.first_name}, " \
               f"{self.last_name}, " \
               f"{self.phone}, " \
               f"{self.username})"


class PaymentPreparation(UserSession):
    sender: BankUser = None
    recipient: BankUser = None
    amount: int = None
    msg: str = None

    def __str__(self):
        return f"PaymentPreparation(session=" \
               f"{self.session_id}, " \
               f"{self.sender}, " \
               f"{self.recipient}, " \
               f"{self.amount}, " \
               f"{self.msg})"


bot = telebot.TeleBot(token=botenv.get_token())
print("Start bot Jopsbank...")


def run():
    bot.infinity_polling()


@bot.message_handler(content_types=['text'])
def start_message(message):
    if message.text == '/start':
        send_message(message.from_user.id, "Добро пожаловать в Jopsbank - первый в мире банк-бот. "
                                           "Тут все просто и удобно. Зарегистрируйся /reg "
                                           "или зарегистрируйся быстро /fast_reg")
        registration(message)
    else:
        bu = bank_users_service.get_user_by_telegram_id(message.from_user.id)
        if bu is not None:
            print(f"Пишет ("
                  f"id:{bu.bank_user_id}; "
                  f"name:{bu.first_name} {bu.last_name}; "
                  f"tg_username:{bu.username}; "
                  f"tg_id:{bu.telegram_id}; "
                  f"balance:{bu.balance})")
        else:
            print("from_id: " + str(message.from_user.id))
        print(message.text)
        if message.text == '/reg':
            registration(message)
        elif message.text == '/fast_reg':
            fast_registration(message)
        elif message.text == '/menu':
            menu(message)
        elif message.text == 'Оплатить':
            pay(message)
        elif message.text == 'Баланс':
            get_balance(message)
        elif message.text == 'Контакты':
            get_user_contacts(message)
        elif message.text == 'Все пользователи':
            get_all_users(message)
        elif message.text == 'Пополнить':
            get_money(message)
        elif message.text == 'Добавить в контакты или пригласить':
            add_to_contacts(message)
        else:
            send_message(message.from_user.id, 'Напиши /reg или /menu')


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'confirm_pay':
        send_message(call.message.chat.id, 'Отправка платежа')
        confirm_pay(call.message)
    elif call.data == 'cancel_pay':
        cancel_pay(call.message)
    elif call.data == 'cancel_reg':
        cancel_pay(call.message)
    elif call.data == 'cancel_get_money':
        send_message(call.message.chat.id, "Отмена пополнения")
        bot.clear_step_handler_by_chat_id(call.message.chat.id)
    elif str(call.data).__contains__('send_money'):
        username = str(call.data).split(":")[1]
        find_payment_preparation(call.message).recipient = bank_users_service.get_user_by_username(username)
        pay(call.message, call.message.chat.id)
    else:
        pass


def registration(message):
    user = message.from_user
    existed_user = bank_users_service.get_user_by_telegram_id(user.id)
    if existed_user is not None:
        send_message(message.from_user.id, "Вы уже зарегистрированы!")
        return
    reg = find_registration(message)
    if reg.username is None and user.username is None:
        print(f"input username")
        send_message(message.from_user.id, "Введите ваш никнейм",
                     reply_markup=cancel_registration_inline_keyboard())
        bot.register_next_step_handler(message, get_username)
        return
    elif reg.username is None:
        print(f"set default username {user.username}")
        # username = utils.tg_username_formatter(user.username)
        reg.username = utils.tg_username_without_at(user.username)
    if reg.first_name is None and user.first_name is None:
        print(f"input first_name")
        send_message(message.from_user.id, "Введите ваше имя, либо /skip",
                     reply_markup=cancel_registration_inline_keyboard())
        bot.register_next_step_handler(message, get_first_name)
        return
    elif reg.first_name is None:
        print(f"set default first_name {user.first_name}")
        reg.first_name = user.first_name
    if reg.last_name is None and user.last_name is None:
        print(f"input last_name")
        send_message(message.from_user.id, "Введите вашу фамилию, либо /skip",
                     reply_markup=cancel_registration_inline_keyboard())
        bot.register_next_step_handler(message, get_last_name)
        return
    elif reg.last_name is None:
        print(f"set default last_name {user.last_name}")
        reg.last_name = user.last_name
    if reg.phone is None:
        send_message(message.from_user.id, "Введите ваш номер телефона, либо /skip",
                     reply_markup=cancel_registration_inline_keyboard())
        bot.register_next_step_handler(message, get_phone)
        return
    print("user creating...")
    bank_users_service.register_user(
        telegram_id=message.from_user.id,
        username=reg.username,
        first_name=reg.first_name,
        last_name=reg.last_name,
        phone=reg.phone
    )
    send_message(message.from_user.id, 'Вы зарегистрированы!')
    menu(message)


def fast_registration(message):
    user = message.from_user
    existed_user = bank_users_service.get_user_by_telegram_id(user.id)
    if existed_user is not None:
        send_message(message.from_user.id, "Вы уже зарегистрированы!")
        return
    reg = find_registration(message)
    if reg.username is None:
        print(f"set default username {user.username}")
        # username = utils.tg_username_formatter(user.username)
        reg.username = utils.tg_username_without_at(user.username)
    if reg.first_name is None:
        print(f"set default first_name {user.first_name}")
        reg.first_name = user.first_name
    if reg.last_name is None:
        print(f"set default last_name {user.last_name}")
        reg.last_name = user.last_name
    print("user creating...")
    bank_users_service.register_user(
        telegram_id=message.from_user.id,
        username=reg.username,
        first_name=reg.first_name,
        last_name=reg.last_name,
        phone=reg.phone
    )
    send_message(message.from_user.id, 'Вы зарегистрированы!')
    menu(message)


def get_username(message):
    find_registration(message).username = message.text
    registration(message)


def get_first_name(message):
    if message.text != '/skip':
        find_registration(message).first_name = message.text
    else:
        find_registration(message).first_name = ''
        send_message(message.from_user.id, 'Ок, без имени(((')
    registration(message)


def get_last_name(message):
    if message.text != '/skip':
        find_registration(message).last_name = message.text
    else:
        find_registration(message).last_name = ''
        send_message(message.from_user.id, 'Ок, без фамилии(((')
    registration(message)


def get_phone(message):
    if message.text != '/skip':
        find_registration(message).phone = message.text
    else:
        find_registration(message).phone = ''
        send_message(message.from_user.id, 'Ок, без телефона(((')
    registration(message)


def menu(message):
    send_message(message.from_user.id, text='Главное меню', reply_markup=bot_keyboards.menu_keyboard())


def pay_get_recipient(message):
    # username = utils.tg_username_formatter(message.text)
    recipient = bank_users_service.get_user_by_username(utils.tg_username_without_at(message.text))
    if recipient is None:
        send_message(message.from_user.id, "Некорректный никнейм, либо он не зарегистрирован!"
                                           " Отправьте правильный никнейм")
        bot.register_next_step_handler(message, pay_get_recipient)
        return
    find_payment_preparation(message).recipient = recipient
    send_message(chat_id=message.from_user.id, text='Введите сумму', reply_markup=cancel_pay_inline_keyboard())
    bot.register_next_step_handler(message, pay_get_amount)


def pay_get_amount(message):
    amountstr: str = message.text
    if not amountstr.isnumeric() or int(amountstr) <= 0:
        send_message(message.from_user.id, "Сумма некорректна. Отправьте сумму еще раз.")
        bot.register_next_step_handler(message, pay_get_amount)
        return
    amount = int(amountstr)
    find_payment_preparation(message).amount = amount
    send_message(
        chat_id=message.from_user.id,
        text="Введите сообщение к переводу, либо отправить без текста: /skip_pay_msg",
        reply_markup=cancel_pay_inline_keyboard()
    )
    bot.register_next_step_handler(message, pay_get_msg)


def pay_get_msg(message):
    msg: str = message.text
    find_payment_preparation(message).msg = msg
    keyboard = types.InlineKeyboardMarkup()
    key_confirm_pay = types.InlineKeyboardButton(text='Оплатить', callback_data='confirm_pay')
    keyboard.add(key_confirm_pay)
    keyboard.add()
    key_cancel_pay = types.InlineKeyboardButton(text='Отмена', callback_data='cancel_pay')
    keyboard.add(key_cancel_pay)
    send_message(
        chat_id=message.from_user.id,
        text="Данные получены! "
             "Теперь нажмите 'Оплатить', чтобы подтвердить платеж, "
             "либо 'Отмена', чтобы отменить платеж",
        reply_markup=keyboard
    )


def pay(message, chat_id=None):
    chat_id = message.from_user.id if chat_id is None else chat_id
    sender = bank_users_service.get_user_by_telegram_id(chat_id)
    if check_user_registered(message, bank_user_ext=sender):
        return
    pp = find_payment_preparation(message)
    pp.sender = sender
    if pp.recipient is None:
        send_message(chat_id, 'Введите никнейм получателя', reply_markup=cancel_pay_inline_keyboard())
        bot.register_next_step_handler(message, pay_get_recipient)
    else:
        send_message(chat_id=chat_id, text='Введите сумму', reply_markup=cancel_pay_inline_keyboard())
        bot.register_next_step_handler(message, pay_get_amount)


def confirm_pay(message):
    print("pay")
    pp = find_payment_preparation(message)
    try:
        status, msg = payments_service.pay(pp.sender, pp.recipient, int(pp.amount))
        print("pay status: " + str(status))
        if status == 'EXECUTED':
            send_message(message.chat.id, 'Платеж проведен успешно :)')
            sender = pp.sender
            name = f'{sender.first_name} {sender.last_name}' \
                if not is_blank(sender.first_name) \
                else utils.tg_username_with_at(sender.username)
            pay_msg = f' \nСообщение: {pp.msg}' if pp.msg is not None else ''
            send_message(pp.recipient.telegram_id, f'Перевод {pp.amount} руб. от {name}.{pay_msg}')
        elif status == 'DELETED':
            send_message(message.chat.id, 'Платеж отменен :.(')
        elif status == 'ERROR':
            send_message(message.chat.id, f'Ошибка проведения платежа :.( \n{msg}')
        else:
            send_message(message.chat.id, 'Ошибка создания платежа :.(')
    except Exception as e:
        raise e
    finally:
        clear_payment_preparation(pp)


def cancel_pay(message):
    print("cancel pay")
    pp = find_payment_preparation(message)
    clear_payment_preparation(pp)
    pp.sender = None
    pp.recipient = None
    pp.amount = None
    pp.session_id = None
    send_message(message.chat.id, 'Платеж отменен(((')


def cancel_reg(message):
    print("cancel pay")
    reg = find_registration(message)
    clear_registration(reg)
    send_message(message.chat.id, 'Отменена регистрации(((')


def add_to_contacts(message):
    if check_user_registered(message):
        return
    send_message(message.from_user.id, "Введите никнейм пользователя")
    bot.register_next_step_handler(message, add_to_contacts_username)


def add_to_contacts_username(message):
    username = utils.tg_username_without_at(message.text)
    current_tg_user = bank_users_service.get_user_by_telegram_id(message.from_user.id)
    if check_user_registered(message, bank_user_ext=current_tg_user):
        return
    bank_user_to_invite = bank_users_service.get_user_by_username(username)
    if bank_user_to_invite is None:
        send_message(message.from_user.id, "Этот пользователь еще не зарегистрирован в сервисе Jopsbank. "
                                           "Перешлите ему приглашение:")
        send_message(message.from_user.id, f"Привет! Присоединяйся к новому платежному сервису "
                                           f"Jopsbank @bcr_test_bot\nНапиши ему /reg, чтобы зарегистрироваться")
    else:
        bank_users_service.add_to_contacts(current_tg_user, bank_user_to_invite)


def get_user_contacts(message):
    bank_user = bank_users_service.get_user_by_telegram_id(message.from_user.id)
    if check_user_registered(message, bank_user_ext=bank_user):
        return
    contacts = bank_users_service.get_contacts_of_user(bank_user)
    for bu in contacts:
        msg = f'Имя: {bu.first_name} {bu.last_name};\n Никнейм: {utils.tg_username_with_at(bu.username)};'
        send_message(message.from_user.id, msg, reply_markup=bot_keyboards.send_money_inline_keyboard(bu))


def get_all_users(message):
    bank_users = bank_users_service.get_all_bank_users()
    for bu in bank_users:
        msg = f'Имя: {bu.first_name} {bu.last_name};\n Никнейм: {utils.tg_username_with_at(bu.username)};'
        send_message(message.from_user.id, msg, reply_markup=bot_keyboards.send_money_inline_keyboard(bu))


def get_balance(message):
    bank_user = bank_users_service.get_user_by_telegram_id(message.from_user.id)
    if check_user_registered(message, bank_user_ext=bank_user):
        return
    # account: Account = bank_users_service.get_account_of_user(bank_user.bank_user_id)
    send_message(message.from_user.id, f"Ваш текущий баланс: {bank_user.balance}. Кредит: {bank_user.credit}")


def get_money(message):
    if check_user_registered(message):
        return
    send_message(message.from_user.id, "Введите сумму пополнения",
                 reply_markup=bot_keyboards.cancel_get_money_inline_keyboard())
    bot.register_next_step_handler(message, get_money_amount)


def get_money_amount(message):
    amountstr: str = message.text
    if not amountstr.isnumeric() or int(amountstr) <= 0:
        send_message(message.from_user.id, "Сумма некорректна. Отправьте сумму еще раз.")
        bot.register_next_step_handler(message, get_money_amount)
        return
    amount = int(amountstr)
    bank_users_service.get_money(message.from_user.id, amount)
    send_message(message.from_user.id, f"Баланс пополнен на {amount} руб.")
    get_balance(message)


def check_user_registered(message, bank_user_ext=None) -> bool:
    if message is not None and bank_user_ext is None:
        bank_user = bank_users_service.get_user_by_telegram_id(message.from_user.id)
    elif bank_user_ext is not None:
        bank_user = bank_user_ext
    else:
        bank_user = None
    if bank_user is None:
        send_message(message.from_user.id, "Вы еще не зарегистрированы! Нажмите /reg или /fast_reg")
        return True
    return False


def find_registration(message) -> Registration:
    c = find_registration_cache(message.from_user.id)
    print("cache reg: " + str(c))
    return c


def find_payment_preparation(message) -> PaymentPreparation:
    c = find_payment_preparation_cache(message.chat.id)
    print("cache payment: " + str(c))
    return c


def clear_payment_preparation(pp: PaymentPreparation):
    pp.sender = None
    pp.recipient = None
    pp.amount = None
    pp.session_id = None
    pp = None


def clear_registration(reg: Registration):
    reg.first_name = None
    reg.last_name = None
    reg.username = None
    reg.phone = None
    reg.session_id = None
    reg = None

@lru_cache
def find_registration_cache(from_user_id) -> Registration:
    return Registration(from_user_id)


@lru_cache
def find_payment_preparation_cache(from_user_id) -> PaymentPreparation:
    return PaymentPreparation(from_user_id)


def send_message(chat_id=None, text=None, reply_markup=bot_keyboards.menu_keyboard()):
    print(f"Bot send to {chat_id} '{text}' \n keyboard: {reply_markup}")
    return bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)
