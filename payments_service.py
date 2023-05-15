from typing import Tuple, Optional

from models import Transaction, BankUser
import transaction


# def execute_transaction(transaction_data: Transaction):
#     sender_id = transaction_data.sender_id
#     recipient_id = transaction_data.recipient_id
#     amount = int(transaction_data.amount)
#     print(f"payment {amount} jopsbank from {sender_id} to {recipient_id} ")
#     try:
#         sender_acc = Account.get_by_id(sender_id)
#         recipient_acc = Account.get_by_id(recipient_id)
#         account_minus_balance(sender_acc, amount)
#         account_plus_balance(recipient_acc, amount)
#         # sender.save()
#         # recipient.save()
#         transaction_data.status = 'EXECUTED'
#         transaction_data.save()
#         transaction.commit()
#         print("payment success")
#     except Exception as e:
#         print(str(e))
#         transaction_data.status = 'ERROR'
#         transaction_data.save()
#         transaction.abort()


def execute_transaction_lite(transaction_data: Transaction) -> Optional[str]:
    sender_id = transaction_data.sender_id
    recipient_id = transaction_data.recipient_id
    amount = int(transaction_data.amount)
    try:
        sender = BankUser.get_by_id(sender_id)
        recipient = BankUser.get_by_id(recipient_id)
        if sender_id == recipient_id or sender.telegram_id == recipient.telegram_id or sender.username == recipient.username:
            raise Exception("Отправитель не может отправлять самому себе")
        print(f"payment {amount} bcr from ({sender.bank_user_id}:{sender.username}:{sender.telegram_id}) "
              f"to ({recipient.bank_user_id}:{recipient.username}:{recipient.telegram_id})")
        buser_minus_balance(sender, amount)
        buser_plus_balance(recipient, amount)
        # sender.save()
        # recipient.save()
        transaction_data.status = 'EXECUTED'
        transaction_data.save()
        transaction.commit()
        print("payment success")
        return None
    except Exception as e:
        print("error:")
        print(str(e))
        transaction_data.status = 'ERROR'
        transaction_data.save()
        transaction.abort()
        return str(e)


def create_transaction(sender_id: int, recipient_id: int, amount: int) -> Transaction:
    tr = Transaction.create(sender_id=sender_id, recipient_id=recipient_id, amount=amount, status='CREATED')
    tr.save()
    print("tr create:" + str(tr))
    return tr


def delete_transaction(transaction_id: int):
    tr: Transaction = Transaction.get_by_id(transaction_id)
    tr.status = 'DELETED'
    tr.save()
    print("tr delete: " + str(tr))


def pay(sender: BankUser, recipient: BankUser, amount: int) -> Tuple[Transaction.Status, str]:
    try:
        tr: Transaction = create_transaction(sender.bank_user_id, recipient.bank_user_id, int(amount))
        attempts = 0
        max_attempts = 10
        msg: str = 'Платеж в обработке'
        while tr.status == 'CREATED' or tr.status == 'ERROR' or tr.status == '' or tr.status is None:
            print("try to execute tr :" + str(tr))
            print(tr.status)
            msg = execute_transaction_lite(tr)
            attempts += 1
            if attempts >= max_attempts:
                break
        return tr.status, msg
    except Exception as e:
        print(str(e))
        return Transaction.Status.ERROR, str(e)


# def account_plus_balance(account: Account, amount: int):
#     credit = account.credit
#     if amount <= 0:
#         raise Exception
#     if credit < 0:
#         account.credit += amount
#     else:
#         account.balance += amount
#     account.save()
#
#
# def account_minus_balance(account: Account, amount: int):
#     if account.balance >= amount > 0:
#         account.balance -= amount
#         account.save()
#     else:
#         raise Exception


def buser_plus_balance(bu: BankUser, amount: int):
    credit = int(bu.credit)
    if amount <= 0:
        raise Exception(f"Ошибка: {amount} меньше нуля")
    if credit < 0:
        bu.credit = credit + amount
    else:
        bu.balance = int(bu.balance) + amount
    bu.save()


def buser_minus_balance(bu: BankUser, amount: int):
    if int(bu.balance) >= amount > 0:
        bu.balance = int(bu.balance) - amount
        bu.save()
    else:
        raise Exception(f"Ошибка: {bu.balance} Недостаточно средств")





