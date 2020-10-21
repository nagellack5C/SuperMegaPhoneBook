import re
import argparse
from peewee import *
import db_ops

PHONE_MASK = r'^\+?\d{1,11}$' # all phone numbers entered must match this mask
MAX_NAME_LEN = 60


@db_ops.connector
def add_entry(name, phone):
    """
    Add a single new entry to the Phonebook.
    :param name: name of the contact
    :param phone: phone number of the contact
    :return:
    """
    try:
        return db_ops.Person(name=name, phone=phone).save(force_insert=True)
    except IntegrityError:
        return False


@db_ops.connector
def remove_entry(phone):
    """
    Remove a single entry from the Phonebook.
    :param phone: phone of the person to remove.
    :return:
    """
    try:
        return db_ops.Person.get(db_ops.Person.phone == phone).delete_instance()
    except db_ops.DoesNotExist:
        return False


@db_ops.connector
def list_all_entries():
    """
    List all entries from the Phonebook.
    :return: list of all entries
    """
    return [(person.name, person.phone) for person in db_ops.Person.select()]


@db_ops.connector
def search_entries_by_name(name):
    """
    Search a name in the Phonebook.
    :param name:
    :return: list of all entries where name includes the name parameter passed
    into the function.
    """
    return [(person.name, person.phone) for person in
            db_ops.Person.select().where(db_ops.Person.name % f'*{name}*')]


def validate(name=None, phone=None):
    """
    Service function for name and phone validation. Uses the constants
    defined on top of the file for easier control.
    :param name: name to validate
    :param phone: phone to validate
    :return: True if no parameters passed OR all parameters passed are valid,
    False otherwise.
    """
    valid = True
    if name is not None:
        if len(name) < 1 or len(name) > MAX_NAME_LEN:
            print('Invalid name length!')
            valid = False
    if phone is not None:
        if not re.match(PHONE_MASK, phone):
            print('Bad number! Please make sure you enter '
                  'an 11-digit number starting with + symbol.')
            valid = False
    return valid


@db_ops.connector
def check_persons():
    persons = []
    for person in db_ops.Person.select():
        per_repr = {
            'name': person.name,
            'phone': person.phone
        }
        persons.append(per_repr)
    return persons


def get_args():
    """
    Service function for setting up CLI arguments. Allows for one option only.
    :return: namedtuple of all arguments.
    """
    help = '''This is a phonebook!
    You can use only one of the --interactive, --add-entry, --remove-entry, --list-all, --search commands at a time.'''
    parser = argparse.ArgumentParser(description=help)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--interactive', action='store_true', help='turn interactive mode on')
    group.add_argument('--add-entry', action='store_true', help='add name and phone number to the phonebook REQUIRES --name, --phone')
    group.add_argument('--remove-entry', action='store_true', help='remove a record from the phonebook by numberREQUIRES, --phone')
    group.add_argument('--list-all', action='store_true', help='list all records')
    group.add_argument('--search', action='store_true', help='search records by name REQUIRES --name')

    parser.add_argument('--name', dest='name', default='', help='name to add or search for')
    parser.add_argument('--phone', dest='phone', default='', help='phone number to add or delete')

    group.add_argument('--reset', action='store_true', help='clear phonebook')

    return parser.parse_args()


def args_flow(args):
    """
    First variant of user flow, using shell arguments only.
    :param args: arguments parsed from the shell
    :return:
    """
    if args.add_entry and validate(args.name, args.phone):
        if add_entry(args.name, args.phone):
            print('Success!')
        else:
            print('This number is already in the PhoneBook.')
    if args.remove_entry and validate(args.phone):
        if remove_entry(args.phone):
            print('Success!')
        else:
            print('Cannot find this number.')
    if args.list_all:
        for entry in list_all_entries():
            print(entry[0], entry[1])
    if args.search and validate(args.name):
        for entry in search_entries_by_name(args.name):
            print(entry[0], entry[1])
    if args.reset:
        db_ops.init_db()


def interactive_flow():
    """
    Second variant of user flow, where the app continues to ask for user input
    until user decides to exit. Was hard to test so I decided to leave this as
    an option only.
    """
    user_input = None
    print('Hi! I am a phone book. what would you like to do?')

    while user_input != '0':
        print('1 - add record')
        print('2 - remove record')
        print('3 - list all records')
        print('4 - search for records')
        print('0 - exit')

        user_input = input('Your choice: ')

        print('-' * 15)

        if user_input not in ('0', '1', '2', '3', '4'):
            print('Wrong input! Please repeat!')
            continue

        if user_input == '1':
            name = input('Please enter a name: ')
            phone = input('Please enter a phone number: ')
            if not validate(name=name, phone=phone):
                continue
            add_entry(name, phone)
        if user_input == '2':
            phone = input('Please enter a phone number to delete: ')
            if not validate(phone=phone):
                continue
            remove_entry(phone)
        if user_input == '3':
            print('Your Phone Book:')
            for entry in list_all_entries():
                print(entry[0], entry[1])
        if user_input == '4':
            name = input('Please enter a name to search: ')
            if not validate(name=name):
                continue
            for entry in search_entries_by_name(name):
                print(entry[0], entry[1])

        print('-' * 15)

    print('Thanks, bye!')


args = get_args()
if args.interactive:
    interactive_flow()
else:
    args_flow(args)
