"""module session provides the logic for handling user sessions which are two
way conversations between the user and the application."""

from dataclasses import dataclass


@dataclass
class Session:
    """Session is a short-term conversation between the user and the
    application."""

    def commit(self):
        """commit the information gathered during the session to a permanent
        state. An example of this is performing changes to the database."""
