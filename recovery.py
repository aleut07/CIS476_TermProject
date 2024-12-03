# Master Password Recovery using Chain of Responsibility
class RecoveryHandler:
    def __init__(self):
        self.chain = None

    def set_chain(self, handler):
        if self.chain is None:
            self.chain = handler
        else:
            current = self.chain
            while current.next_handler:
                current = current.next_handler
            current.next_handler = handler

    def recover(self, user, user_answers):
        if not self.chain:
            raise Exception("No recovery chain set up.")
        return self.chain.handle(user, user_answers)


class SecurityQuestionHandler:
    def __init__(self):
        self.next_handler = None

    def handle(self, user, user_answers):
        # Retrieve security questions and answers from the user relationship
        security_answers = {q.question: q.answer.lower() for q in user.security_questions}

        for answer, question in zip(user_answers, security_answers.keys()):
            if answer.lower() != security_answers[question]:
                return False

        if self.next_handler:
            return self.next_handler.handle(user, user_answers)

        return True

