from typing import Optional

from models import BankUser, ContactRelationship


def register_user(
        telegram_id: int,
        username='',
        first_name='',
        last_name='',
        phone=''
):
    bank_user = BankUser.create(
        telegram_id=telegram_id,
        # account_id=account.account_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        balance=100,
        credit=0,
        phone=phone
    )
    # Account.create(bank_user=bank_user)


def get_user_by_username(username) -> Optional[BankUser]:
    try:
        return BankUser.get(BankUser.username == username)
    except Exception as e:
        print(e)
        # return BankUser(bank_user_id=1, telegram_id=0, username='jekajops', phone='89523663611', balance=100, credit=0, deleted=False)
        return None


def get_user_by_telegram_id(telegram_id) -> Optional[BankUser]:
    try:
        return BankUser.get(BankUser.telegram_id == telegram_id)
    except Exception as e:
        print(e)
        # return BankUser(bank_user_id=1, telegram_id=0, username='jekajops', phone='89523663611', balance=100, credit=0, deleted=False)
        return None


# def get_account_of_user(id: int) -> Account:
#     try:
#         return Account.get_by_id(id)
#     except Exception as e:
#         print(e)
#         return Account(bank_user=get_user_by_telegram_id(id), balance=100, credit=0, deleted=False)


def get_all_bank_users():
    # print([f'Account(bank_user: {acc.bank_user}, balance: {acc.balance}, credit: {acc.credit})' for acc in Account.select()])
    return BankUser.select()


def get_money(telegram_id, amount):
    bu = get_user_by_telegram_id(telegram_id)
    cbalance = int(bu.balance)
    bu.balance = str(cbalance + int(amount))
    bu.save()


def add_to_contacts(from_user: BankUser, to_user: BankUser):
    ContactRelationship.create(from_user=from_user, to_user=to_user)


def get_contacts_of_user(bank_user: BankUser):
    return [contact.to_user
            for contact in ContactRelationship.get(
                ContactRelationship.from_user.bank_user_id == bank_user.bank_user_id
            )]
