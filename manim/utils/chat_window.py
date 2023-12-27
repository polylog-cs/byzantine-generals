from manim import *
from .util_general import text_color, BASE00


class ChatMessage(VGroup):
    def __init__(self, sender: str, message: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        width = 5
        height = 1.5
        self.add(
            RoundedRectangle(
                corner_radius=0.5,
                width=width,
                height=height,
                fill_color=BASE00,
                fill_opacity=1,
                stroke_opacity=0,
            )
        )

        bottom_left_corner = width / 2 * LEFT + height / 2 * DOWN

        self.add(
            Polygon(
                bottom_left_corner,
                bottom_left_corner + 0.5 * RIGHT,
                bottom_left_corner + 0.5 * UP + 0.5 * RIGHT,
                stroke_opacity=0,
                fill_color=BASE00,
                fill_opacity=1,
            )
        )

        sender_text = Text(sender).scale(0.4)
        sender_text.align_to(self, direction=LEFT + UP)
        sender_text.shift(0.3 * RIGHT + 0.3 * DOWN)
        self.add(sender_text)

        message = Text(message).scale(0.8)
        self.add(message)


class ChatWindow(VGroup):
    def __init__(self, h=4, w=6, **kwargs):
        super().__init__(**kwargs)
        self.displayed_messages = VGroup()
        self.add(self.displayed_messages)
        self.window = Rectangle(
            height=h,
            width=w,
            color=text_color,
            stroke_opacity=0,  # vv: uncomment to show border
        )
        self.add(self.window)

    def create_window(self):
        # Create a basic window frame for the chat
        animation = Create(self.window)
        return animation

    def add_message(self, sender: str, message: str):
        # Format the message as "sender: message"
        full_message = f"{sender}: {message}"

        # Position for the new message
        if self.displayed_messages:
            position = self.displayed_messages[-1].get_corner(DOWN + LEFT) + DOWN * 0.9
        else:
            position = self.window.get_corner(UP + LEFT) + RIGHT * 0.2 + DOWN * 0.3

        # Create a text object for the message, positioned to the left
        message_obj = ChatMessage(sender, message).move_to(position, aligned_edge=LEFT)
        self.displayed_messages.add(message_obj)

        # Animation: write each message letter by letter
        # Surprisingly, Write also works with non-Text objects. I guess it calls Create.
        # to animate the other components.
        animation = Write(
            message_obj, run_time=len(full_message) * 0.1, rate_func=linear
        )

        # Return the animation
        return AnimationGroup(animation)
