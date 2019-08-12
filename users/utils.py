import re


def normalize_phone(phone):
    phone = re.sub(r'[+\s()-]', '', phone.strip())
    phone = '380' + phone[-9:]
    return phone


def normalize_email(email):
    return email.lower()


def valid_phone(phone):
    if not re.match(r'^[\d]{12}$', phone) or not phone.startswith('38'):
        return False
    return True
