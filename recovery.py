# Master Password Recovery using Chain of Responsibility
class RecoveryStep:
    def __init__(self, next_step=None):
        self.next_step = next_step

    def handle(self, user_input):
        if self.next_step:
            return self.next_step.handle(user_input)
        return False


class SecurityQuestionStep(RecoveryStep):
    def __init__(self, question, expected_answer, next_step=None):
        super().__init__(next_step)
        self.question = question
        self.expected_answer = expected_answer

    def handle(self, user_input):
        if user_input.get(self.question) != self.expected_answer:
            return False
        return super().handle(user_input)


class RecoveryHandler:
    def __init__(self, user_security_questions):
        self.chain = None
        for question, answer in reversed(user_security_questions):
            self.chain = SecurityQuestionStep(question, answer, self.chain)

    def recover(self, user_input):
        if self.chain.handle(user_input):
            return "Recovery Successful"
        return "Recovery Failed"
