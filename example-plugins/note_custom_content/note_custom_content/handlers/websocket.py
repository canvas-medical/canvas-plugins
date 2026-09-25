from canvas_sdk.handlers.simple_api.websocket import WebSocketAPI


class NoteContentSocket(WebSocketAPI):
    """The socket a note's cards listen on for their counts.

    One channel per note, so a card only hears about the note it is rendered in.
    """

    def authenticate(self) -> bool:
        """Let a signed-in staff member listen, and nobody else."""
        user = self.websocket.logged_in_user

        return bool(user) and user.get("type") == "Staff"
