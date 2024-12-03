# Password Generator using Builder Pattern
import random
import string

class PasswordBuilder:
    def __init__(self):
        self.length = 8
        self.complexity = 'medium'

    def set_length(self, length):
        self.length = length
        return self

    def set_complexity(self, complexity):
        self.complexity = complexity
        return self

    def build(self):
        pool = string.ascii_letters
        if self.complexity == 'high':
            pool += string.digits + string.punctuation
        elif self.complexity == 'medium':
            pool += string.digits
        return ''.join(random.choices(pool, k=self.length))
