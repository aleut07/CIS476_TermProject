# Notification System using Observer Pattern
class NotificationManager:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def notify(self, event):
        for subscriber in self.subscribers:
            subscriber.update(event)

class ExpiryNotifier:
    def update(self, event):
        # Logic for sending notifications (e.g., password or card expiry)
        pass
