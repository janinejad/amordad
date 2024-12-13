import os
from django.utils.text import slugify
import random
import string

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)
    return name, ext


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug,
            randstr=random_string_generator(size=4)
        )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug

def is_valid_national_code(code):
    national_code = ""
    if not code:
        return False
    if not code.isnumeric():
        return False
    if len(code) == 10:
        national_code = code
    else:
        return False
    division = 0
    for i in range(len(national_code) - 1):
        division += int(national_code[i])
    if division / 9 == int(national_code[9]):
        return False
    total = (int(national_code[8]) * 2) + (int(national_code[7]) * 3) + (int(national_code[6]) * 4) + (
            int(national_code[5]) * 5) + (int(national_code[4]) * 6) + (int(national_code[3]) * 7) + (
                    int(national_code[2]) * 8) + (
                    int(national_code[1]) * 9) + (int(national_code[0]) * 10)
    mod = total % 11
    if mod < 2:
        if mod == int(national_code[9]):
            return True
        else:
            return False
    elif mod >= 2:
        if 11 - mod == int(national_code[9]):
            return True
        else:
            return False

def delete_tasks(task_name):
    from background_task.models import Task
    tasks = Task.objects.filter(task_name=task_name)
    for task in tasks:
        task.delete()