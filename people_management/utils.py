from people_management.models import Person

def get_person(user):
    try:
        return user.person
    except Person.DoesNotExist:
        return None

def get_role(user):
    person = get_person(user)
    return person.role if person else None

def is_hr_admin(user):
    return user.is_staff or get_role(user) == "hr_admin"

def is_manager(user):
    return get_role(user) == "manager"

def is_employee(user):
    return get_role(user) == "employee"
