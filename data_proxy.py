# Mask/Unmask Sensitive Data using Proxy Pattern
class SensitiveDataProxy:
    def __init__(self, sensitive_data):
        self._sensitive_data = sensitive_data
        self._masked = True

    def get_data(self):
        if self._masked:
            return "****" * (len(self._sensitive_data) // 4)
        return self._sensitive_data

    def toggle_mask(self):
        self._masked = not self._masked
