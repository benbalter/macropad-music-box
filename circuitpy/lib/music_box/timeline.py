"""A tiny scheduler so lights and notes can be timed without blocking."""


class Timeline:
    def __init__(self):
        self._events = []

    def at(self, when, action):
        """Run `action()` once the clock reaches `when` (milliseconds)."""
        self._events.append((when, action))

    def tick(self, now):
        due = [e for e in self._events if e[0] <= now]
        if not due:
            return
        self._events = [e for e in self._events if e[0] > now]
        due.sort(key=lambda e: e[0])
        for _, action in due:
            action()

    def clear(self):
        self._events = []

    def __len__(self):
        return len(self._events)
