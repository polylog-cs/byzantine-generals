from manim import *
from .util_general import text_color


class ChatWindow(VGroup):
    def __init__(self, h=4, w=6, **kwargs):
        super().__init__(**kwargs)
        self.displayed_messages = VGroup()
        self.add(self.displayed_messages)
        self.window = Rectangle(height=h, width=w, color=text_color)
        self.add(self.window)

    def create_window(self):
        # Create a basic window frame for the chat
        animation = Create(self.window)
        return animation

    def add_message(self, sender, message):
        # Format the message as "sender: message"
        full_message = f"{sender}: {message}"

        # Position for the new message
        if self.displayed_messages:
            position = self.displayed_messages[-1].get_left() + DOWN * 0.4
        else:
            position = self.window.get_corner(UP + LEFT) + RIGHT * 0.2 + DOWN * 0.3

        # Create a text object for the message, positioned to the left
        message_obj = Text(full_message, font_size=24, color=text_color).move_to(
            position, aligned_edge=LEFT
        )
        self.displayed_messages.add(message_obj)

        # Animation: write each message letter by letter
        animation = Write(
            message_obj, run_time=len(full_message) * 0.1, rate_func=linear
        )

        # Return the animation
        return AnimationGroup(animation)
