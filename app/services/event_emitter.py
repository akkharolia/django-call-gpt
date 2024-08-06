class EventEmitter:
    def __init__(self):
        self.events = {}

    def on(self, event, callback):
        if event not in self.events:
            self.events[event] = []
        self.events[event].append(callback)

    def emit(self, event, *args, **kwargs):
        if event in self.events:
            for callback in self.events[event]:
                callback(*args, **kwargs)
            return True
        print(f"No listeners for event '{event}'")
        return False
