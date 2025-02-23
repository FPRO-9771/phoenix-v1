from commands2 import Command

class AutonBlueLeft(Command):

    def __init__(self):
        super().__init__()
        # Add subsystem dependencies here if needed

    def initialize(self):
        print("Starting Auto B L")

    def execute(self):
        # Add movement logic (e.g., drive forward, turn, etc.)
        pass

    def isFinished(self):
        return True  # Modify based on your sequence duration

    def end(self, interrupted):
        print("Auto B L ended")


class AutonBlueRight(Command):

    def __init__(self):
        super().__init__()

    def initialize(self):
        print("Starting Auto B R")

    def execute(self):
        # Different movement logic from Auto 1
        pass

    def isFinished(self):
        return True

    def end(self, interrupted):
        print("Auto B R ended")
