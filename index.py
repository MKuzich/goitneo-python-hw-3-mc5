from collections import UserDict, defaultdict
from datetime import datetime
import pickle

class NotValidPhoneNumber(ValueError):
    pass

class NotValidDate(ValueError):
    pass

class PhoneIsNumber(ValueError):
    pass

class NameIsString(ValueError):
    pass

class NoContacts(Exception):
    pass

class NoBirthdays(Exception):
    pass

class NoBirthday(KeyError):
    pass

def error_handler(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotValidPhoneNumber:
            return "Phone number should contain only 10 digits."
        except IndexError:
            return "Phone not found."
        except NotValidDate:
            return "Date should be in format DD.MM.YYYY"
        except:
            return "Something went wrong."
    return inner

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        self.value = value

class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise NotValidPhoneNumber
        self.value = value

class Birthday(Field):
    def __init__(self, value):
        try:
            day, month, year = map(int, value.split('.'))
            self.value = datetime(year, month, day)
        except:
            raise NotValidDate

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []

    def find_idx(self, phone):
        for i in range(len(self.phones)):
            if self.phones[i].value == phone:
                return i
        raise IndexError

    @error_handler
    def add_phone(self, phone):
        self.phones.append(Phone(phone))
        return 'Phone added.'

    @error_handler
    def remove_phone(self, phone):
        idx = self.find_idx(phone)
        self.phones.pop(idx)
        return 'Phone removed.'

    @error_handler
    def edit_phone(self, phone, new_phone):
        idx = self.find_idx(phone)
        self.phones[idx].value = new_phone
        return 'Phone edited.'

    @error_handler
    def find_phone(self, phone):
        idx = self.find_idx(phone)
        return self.phones[idx]
    
    @error_handler
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)
        return 'Birthday added.'
        
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{', birthday: ' + self.birthday.value.strftime('%d %B, %Y') if hasattr(self, 'birthday') else ''}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
        return 'Contact added.'
    
    def find(self, name):
        contact = self.data.get(name)
        if not contact:
            raise KeyError
        return contact

    def delete(self, name):
        contact = self.data.pop(name, None)
        if not contact:
            raise KeyError
        return contact
    
    def get_birthdays_per_week(self):
        today = datetime.now().date()
        birthdays = defaultdict(list)
        users = [{"name": user.name.value, "birthday": user.birthday.value} for user in self.data.values() if hasattr(user, 'birthday')]
        def sort_by_date(user):
            return user['birthday'].date()
        users.sort(key=sort_by_date)
        
        for user in users:
            name = user['name']
            birthday = user['birthday'].date()
            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)
            
            delta_days = (birthday_this_year - today).days

            if delta_days < 7:
                if birthday_this_year.weekday() > 4: 
                    if today.weekday() != 0 and today.weekday() < 5:
                        birthdays['Monday'].append(name)
                else:
                    birthdays[birthday_this_year.strftime('%A')].append(name)
        return birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotValidDate:
            return "Date should be in format DD.MM.YYYY"
        except PhoneIsNumber:
            return "Phone number should contain only 10 digits."
        except NameIsString:
            return "Name should contain only letters."
        except ValueError:
            return "Give me name and phone please."
        except NoBirthday:
            return "No birthday for this contact."
        except IndexError:
            return "Contact not found."
        except KeyError:
            return "Contact not found."
        except NoContacts: 
            return "No contacts in phonebook."
        except NoBirthdays:
            return "No birthdays in the next 7 days."
        except:
            return "Something went wrong."
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, contacts):
    name, phone = args
    if not phone.isdigit() or len(phone) != 10:
        raise PhoneIsNumber
    if not name.isalpha():
        raise NameIsString
    
    record = Record(name)
    record.add_phone(phone)
    contacts.add_record(record)
    return "Contact added."

@input_error
def change_contact(args, contacts):
    name, phone = args
    if name not in contacts:
        raise KeyError
    if not phone.isdigit() or len(phone) != 10:
        raise PhoneIsNumber
    if not name.isalpha():
        raise NameIsString
    
    record = contacts.find(name)
    record.edit_phone(record.phones[0].value, phone)
    return "Contact phone changed."


@input_error
def show_contact(args, contacts):
    name = args[0]
    if not name.isalpha():
        raise NameIsString
    return contacts.find(name)

@input_error
def all(contacts):
    if not contacts:
        raise NoContacts
    all_contacts = []
    for i in contacts.data.values():
        all_contacts.append(str(i))
    
    return '\n'.join(all_contacts)

@input_error
def birthdays(contacts):
    birthdays = contacts.get_birthdays_per_week()
    if not birthdays:
        raise NoBirthdays
    res = []
    for key, val in birthdays.items():
        res.append(f'{key}: {", ".join(val)}')
    return '\n'.join(res)

@input_error
def add_birthday(args, contacts):
    name, birthday = args
    if not name.isalpha():
        raise NameIsString

    record = contacts.find(name)
    if birthday.count('.') != 2 or len(birthday) != 10 or not birthday.replace('.', '').isdigit():
        raise NotValidDate

    record.add_birthday(birthday)
    return "Birthday added."

@input_error
def show_birthday(args, contacts):
    name = args[0]
    if not name.isalpha():
        raise NameIsString
    record = contacts.find(name)
    if not hasattr(record, 'birthday'):
        raise NoBirthday
    return record.birthday.value.strftime("%d %B, %Y")

file_name = 'data.bin'

def save_data(data):
    global file_name
    with open(file_name, "wb") as fh:
        pickle.dump(data, fh)

def load_data():
    global file_name
    with open(file_name, "rb") as fh:
        return pickle.load(fh)

def main():
    contacts = AddressBook()
    try:
        contacts = load_data()
    except:
        pass
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(contacts)
            break
        elif command == "hello":
            print("How can I help you?")
        elif command in ["add"]:
            print(add_contact(args, contacts))
        elif command in ["change"]:
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_contact(args, contacts))
        elif command == "all":
            print(all(contacts))
        elif command == "birthdays":
            print(birthdays(contacts))
        elif command == "add-birthday":
            print(add_birthday(args, contacts))
        elif command == "show-birthday":
            print(show_birthday(args, contacts))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
