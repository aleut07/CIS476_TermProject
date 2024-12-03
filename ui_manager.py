# UI Component Communication using Mediator Pattern
class UIManager:
    def __init__(self):
        self.components = {}

    def register_component(self, name, component):
        """
        Register a UI component with the manager.
        :param name: Unique name of the component
        :param component: The component instance
        """
        self.components[name] = component
        component.set_mediator(self)

    def notify(self, sender, event, *args, **kwargs):
        """
        Notify other components about an event.
        :param sender: Name of the component sending the notification
        :param event: Event type
        """
        if sender in self.components:
            if event == "vault_item_created":
                self._on_vault_item_created(*args, **kwargs)
            elif event == "vault_item_deleted":
                self._on_vault_item_deleted(*args, **kwargs)
            elif event == "password_copied":
                self._on_password_copied(*args, **kwargs)

    def _on_vault_item_created(self, item):
        """
        Handle vault item creation event.
        :param item: The created vault item
        """
        print(f"UIManager: Vault item '{item.name}' of type '{item.item_type}' was created.")

    def _on_vault_item_deleted(self, item):
        """
        Handle vault item deletion event.
        :param item: The deleted vault item
        """
        print(f"UIManager: Vault item '{item.name}' was deleted.")

    def _on_password_copied(self, item, password):
        """
        Handle password copy event.
        :param item: The vault item containing the password
        :param password: The copied password
        """
        print(f"UIManager: Password for '{item.name}' was copied to clipboard.")

class UIComponent:
    def __init__(self, name):
        self.name = name
        self.mediator = None

    def set_mediator(self, mediator):
        """
        Assign a mediator to the component.
        :param mediator: Instance of UIManager
        """
        self.mediator = mediator

    def notify_mediator(self, event, *args, **kwargs):
        """
        Notify the mediator about an event.
        :param event: Event type
        """
        if self.mediator:
            self.mediator.notify(self.name, event, *args, **kwargs)


# Example components
class VaultComponent(UIComponent):
    def __init__(self):
        super().__init__('VaultComponent')

    def create_vault_item(self, item):
        # Logic to create a vault item
        print(f"VaultComponent: Creating vault item '{item.name}'")
        self.notify_mediator('vault_item_created', item=item)

    def delete_vault_item(self, item):
        # Logic to delete a vault item
        print(f"VaultComponent: Deleting vault item '{item.name}'")
        self.notify_mediator('vault_item_deleted', item=item)


class ClipboardComponent(UIComponent):
    def __init__(self):
        super().__init__('ClipboardComponent')

    def copy_password(self, item, password):
        # Logic to copy password to clipboard
        print(f"ClipboardComponent: Copying password for '{item.name}' to clipboard.")
        self.notify_mediator('password_copied', item=item, password=password)


# Example usage
if __name__ == "__main__":
    ui_manager = UIManager()

    vault_component = VaultComponent()
    clipboard_component = ClipboardComponent()

    # Register components with the mediator
    ui_manager.register_component('VaultComponent', vault_component)
    ui_manager.register_component('ClipboardComponent', clipboard_component)

    # Example vault item
    class VaultItem:
        def __init__(self, name, item_type):
            self.name = name
            self.item_type = item_type

    item = VaultItem(name="Google Account", item_type="Login")

    # Simulate UI interactions
    vault_component.create_vault_item(item)
    clipboard_component.copy_password(item, "securepassword123")
    vault_component.delete_vault_item(item)
