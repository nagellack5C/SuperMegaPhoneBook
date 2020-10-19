>Write an architecture document explaining the choices you have made to implement this application.

## General Architecture (big words, small scale)

I have decided to implement all 4 basic functions as they were explained in the task.

To simplify setup, I am using an SQLite database for storage (it can be handled from Python with no additional packages required). However, I am using Peewee as an ORM for simpler and cleaner database operations.

The general architecture is very unsophisticated:
- There is a single table in the SQLite database file called Person. It has 2 custom fields: name (VARCHAR with length 60)
and phone (unique VARCHAR with length 12).
- The app itself resides in the phonebook.py file. It has 4 basic functions for adding. deletion,
record listing and search. The script is executed by the python using `python phonebook.py $ARGS`
see `python phonebook.py -h for proper instructions`. There is also an `--interactive` option for this file
but it's untested (I decided that it would be too complicated to test such an app that loops in the shell).
- All inputs and outputs will be in the user shell.

There are several constraints that I decided to enforce:

- As mentioned above, the max length of a contact name is 60 and max length of phone number is 12
- I do not validate names, only check the length (what if your friend's name is `DROP DATABASE Person;`?)
Well, apparently this won't break the app.
- The phones are validated: they should contain from 1 to 11 digits and an optional `+` sign.
- Search function returns names that _include_ the name searched, rather than full matches only.

## Installation Instructions

The app uses Python 3. Also it probably won't run on Windows (should work fine on Unix-based OS or MacOS)
due to shell and Unicode issues.

Run pip install -r requirements.txt (you will need `pytest` and `peewee`)

You're ready to use the app!

## Test Plan

We need to make sure that:

- the user can add proper records
- the user cannot add invalid records
- the user can remove records by number
- the user can find added records in the app output
- the user can search for particular records by name

## Test Automation

The tests are automated using pytest. All test code is in the `test_phonebook.py` file.

Run `pytest` in the app directory to run all tests, or run `pytest -k "TEST_NAME"` to run particular test(s).

I have automated adding and removal cases, several negative adding cases, and also a case where user makes amendments to an added record by adding and
removing a single record several times.

The results are validated by searching for substrings in the app output and also by checking all records from the app's "list all" function.

The tests utilize a setup fixture that loads a set of data into the app (I thought I would use this data
for search scenario but then decided I won't implement it), several helper functions and the `parametrize` feature of `pytest`.

The app itself is run using the `subprocess` Python library.

The tests do not use the app's code directly for the sake of purity (they interact with the app exactly as the user would do).
