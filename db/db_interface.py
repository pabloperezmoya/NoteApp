
from db import _db_classes

class Users(_db_classes.Tables):
    def __init__(self):
        super().__init__('users')

class Passwords(_db_classes.Tables):
    def __init__(self):
        super().__init__('passwords')

class Notes(_db_classes.Tables):
    def __init__(self):
        super().__init__('notes')