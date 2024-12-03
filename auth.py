# User Authentication using Singleton Pattern
class UserSession:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(UserSession, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.user = None

    def login(self, user):
        self.user = user

    def logout(self):
        self.user = None

    def is_authenticated(self):
        return self.user is not None
