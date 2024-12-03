# Master Password Recovery using Chain of Responsibility
class Handler:
    def __init__(self, successor=None):
        self.successor = successor

    def handle(self, request):
        if self.successor:
            return self.successor.handle(request)

class SecurityQuestionHandler(Handler):
    def __init__(self, question, answer, successor=None):
        super().__init__(successor)
        self.question = question
        self.answer = answer

    def handle(self, request):
        user_answer = request.get(self.question)
        if user_answer == self.answer:
            return super().handle(request)
        else:
            return False  # Terminate chain

# Build chain
def create_recovery_chain(questions_answers):
    chain = None
    for question, answer in reversed(questions_answers):
        chain = SecurityQuestionHandler(question, answer, chain)
    return chain
