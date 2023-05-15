from enum import Enum

from peewee import *

conn = SqliteDatabase('Chinook_Sqlite.sqlite')


# Определяем базовую модель о которой будут наследоваться остальные
class BaseModel(Model):
    class Meta:
        database = conn  # соединение с базой, из шаблона выше

    # @classmethod
    # def create_table(cls, *args, **kwargs):
    #     for field in cls._meta.get_fields:
    #         if hasattr(field, "pre_field_create"):
    #             field.pre_field_create(cls)
    #
    #     cls._meta.database.create_table(cls)
    #
    #     for field in cls._meta.get_fields():
    #         if hasattr(field, "post_field_create"):
    #             field.post_field_create(cls)


class EnumField(Field):
    db_field = "enum"

    def pre_field_create(self, model):
        field = "e_%s" % self.name

        self.get_database().get_conn().cursor().execute(
            "DROP TYPE IF EXISTS %s;" % field
        )

        query = self.get_database().get_conn().cursor()

        tail = ', '.join(["'%s'"] * len(self.choices)) % tuple(self.choices)
        q = "CREATE TYPE %s AS ENUM (%s);" % (field, tail)
        query.execute(q)

    def post_field_create(self, model):
        self.db_field = "e_%s" % self.name

    def coerce(self, value):
        if value not in self.choices:
            raise Exception("Invalid Enum Value `%s`", value)
        return str(value)

    def get_column_type(self):
        return "enum"

    def __ddl_column__(self, ctype):
        return SQL("e_%s" % self.name)


class BankUser(BaseModel):
    bank_user_id = PrimaryKeyField(null=False)
    telegram_id = IntegerField(column_name='telegram_id')
    # account_id = TextField(column_name='account_id', null=True)
    first_name = TextField(column_name='first_name', null=True)
    last_name = TextField(column_name='last_name', null=True)
    username = TextField(column_name='username', null=True)
    phone = TextField(column_name='phone', null=True)
    balance = IntegerField(column_name="balance")
    credit = IntegerField(column_name="credit")
    deleted = BooleanField(column_name='deleted', default=False)
    timestamp = TimestampField(null=True)

    # @property
    # def account(self):
    #     return self.account_id

    class Meta:
        table_name = 'BankUser'


class Transaction(BaseModel):
    transaction_id = AutoField(column_name='transaction_id')
    sender_id = IntegerField(column_name='sender_id')
    recipient_id = IntegerField(column_name='recipient_id')
    amount = IntegerField(column_name='amount')
    deleted = BooleanField(column_name='deleted', default=False)
    status = EnumField(column_name='status', choices=['CREATED', 'EXECUTED', 'DELETED', 'ERROR'], default='CREATED')
    timestamp = TimestampField(null=True)

    class Meta:
        table_name = 'Transaction'

    class Status(Enum):
        CREATED = 1
        EXECUTED = 2
        DELETED = 3
        ERROR = 4

    def __str__(self):
        return super().__str__()


class ContactRelationship(BaseModel):
    contact_relationship_id = AutoField(column_name='contact_relationship_id')
    from_user: BankUser = ForeignKeyField(BankUser)
    to_user: BankUser = ForeignKeyField(BankUser)
    timestamp = TimestampField(null=True)

    class Meta:
        table_name = 'ContactRelationship'
        indexes = (
            # Specify a unique multi-column index on from/to-user.
            (('from_user', 'to_user'), True),
        )


# class Account(BaseModel):
#     # account_id = AutoField()
#     bank_user = ForeignKeyField(BankUser, primary_key=True)
#     balance = TextField(column_name='balance', default=0)
#     credit = TextField(column_name='credit', default=0)
#     deleted = BooleanField(column_name='deleted', default=False)
#     timestamp = TimestampField()
#
#     class Meta:
#         table_name = 'Account'


# Создаем курсор - специальный объект для запросов и получения данных с базы
cursor = conn.cursor()


def initialize_db():
    conn.connect()
    conn.create_tables([BankUser, Transaction, ContactRelationship], safe=True)
    conn.close()

# ТУТ БУДЕТ НАШ КОД РАБОТЫ С БАЗОЙ ДАННЫХ


# Не забываем закрыть соединение с базой данных
conn.close()