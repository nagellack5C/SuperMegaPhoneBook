import subprocess
import csv
import pytest


def run_app(args: list):
    """
    Run the app with provided arguments and return the results.
    :param args: list of arguments to pass to the app
    :return: stdout, stderr from the app run
    """
    proc = subprocess.Popen(['python3', 'phonebook.py'] + args,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, universal_newlines=True
                            )
    stdout, stderr = proc.communicate()
    return stdout, stderr


def add_contact(name, phone):
    """
    Wrapper for the add entry function of the app.
    :param name: name of new contact
    :param phone: phone number of new contact
    :return: stdout, stderr from the app run
    """
    return run_app(['--add-entry', '--name', name, '--phone', phone])


def remove_contact(phone):
    """
    Wrapper for the removal function of the app.
    :param phone: phone number of contact to delete
    :return: stdout, stderr from the app run
    """
    return run_app(['--remove-entry', '--phone', phone])


def list_all():
    """
    Wrapper for the list-all function of the app.
    :return: list of contacts returned by the app
    """
    all_records, _ = run_app(['--list-all'])
    return all_records.split('\n')


@pytest.fixture(scope='session')
def phonebook_setup(request):
    """
    Load test contacts into the phonebook to simulate a non-empty phonebook.
    """
    with open('contacts.csv') as contacts_file:
        reader = csv.DictReader(contacts_file)
        test_contacts = [(record['name'], record['phone']) for record in reader]
    for contact in test_contacts:
        x, _ = add_contact(contact[0], contact[1])

    def resource_teardown():
        """
        Delete all records from the phonebook.
        """
        run_app(['--reset'])

    request.addfinalizer(resource_teardown)


@pytest.mark.parametrize('name,phone', [
    ('Vasily Pupkin', '+79643776772'),
    ('I am a test user', '+89643776772'),
    ('DROP TABLE Person;', '+123')
])
def test_add_and_remove_record(name, phone, phonebook_setup):
    """
    Try to load various valid contacts into the app.
    :param name: name to add
    :param phone: phone number to add
    """
    stdout, stderr = add_contact(name, phone)
    assert stdout == 'Success!\n'
    assert f'{name} {phone}' in list_all()
    stdout, stderr = remove_contact(phone)
    assert stdout == 'Success!\n'
    assert f'{name} {phone}' not in list_all()


@pytest.mark.parametrize('name,phone,expected_results', [
    ('', '', ['Invalid name length', 'Bad number']),
    ('', '+12345678901', ['Invalid name length']),
    ('John Doe'*30, '+12345678901', ['Invalid name length']),
    ('Mister X', '', ['Bad number']),
    ('', '+123456789012', ['Bad number']),
    ('', 'John Doe', ['Bad number'])
])
def test_bad_inputs(name, phone, expected_results, phonebook_setup):
    """
    Try to load invalid records into the app, assert the app won't add them.
    :param name: name to add
    :param phone: phone to add
    :param expected_results: substrings to look for in the output to assert it
    returns a proper response
    :return:
    """
    stdout, stderr = add_contact(name, phone)
    assert all([result in stdout for result in expected_results])


def test_amendment_scenario(phonebook_setup):
    """
    Simulate a scenario where user adds a record to the phonebook, then decides
    to change the number of the contact, then decides to change the name of the
    contact.
    """
    name1 = 'Billy Butcher'
    phone1 = '+777666'
    add_contact(name1, phone1)
    remove_contact(phone1)
    phone2 = '+777667'
    add_contact(name1, phone2)
    remove_contact(phone2)
    name2 = 'Billy Kitty'
    add_contact(name2, phone2)
    results = list_all()
    assert f'{name2} {phone2}' in results
    for record in results:
        assert name1 not in record
        assert phone1 not in record
