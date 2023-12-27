from typing import Literal

from manim import *

from . import util_general
from .util_general import text_color


class ChatMessage(VGroup):
    def __init__(
        self,
        sender: str,
        message: str,
        sender_color: ParsableManimColor = util_general.WHITE,
        background_color: ParsableManimColor = util_general.BASE02,
        tail_right: bool = False,  # x position of the bubble's tail
        tail_up: bool = False,  # y position of the bubble's tail
        *args,
        **kwargs,
    ):
        """A message in a chat stylized as a speech bubble."""
        super().__init__(*args, **kwargs)
        self.sender = sender
        self.message = message
        self.background_color = background_color

        message_text = Text(message, font="Helvetica").scale(0.8)
        sender_text = Text(sender, color=sender_color, font="Helvetica").scale(0.4)

        self.text_group = VGroup(sender_text, message_text).arrange_in_grid(
            rows=2, cols=1, cell_alignment=LEFT, buff=SMALL_BUFF
        )

        width = self.text_group.width + MED_LARGE_BUFF
        height = self.text_group.height + MED_LARGE_BUFF

        self.bubble = RoundedRectangle(
            corner_radius=0.5,
            width=width,
            height=height,
            fill_color=background_color,
            fill_opacity=1,
            stroke_opacity=0,
        )

        self.add(self.bubble)

        self.tail = None
        self.set_tail_direction(tail_right=tail_right, tail_up=tail_up)

        self.add(self.text_group)

    # Might not be needed in the end because moving the tail
    # can also be handled by .become().
    def set_tail_direction(self, tail_right: bool, tail_up: bool):
        if self.tail:
            self.remove(self.tail)

        tail_direction_x = RIGHT if tail_right else LEFT
        tail_direction_y = UP if tail_up else DOWN

        tail_corner = self.bubble.get_corner(tail_direction_x + tail_direction_y)

        self.tail = Polygon(
            tail_corner,
            tail_corner - 0.5 * tail_direction_x,
            tail_corner - 0.5 * tail_direction_y - 0.5 * tail_direction_x,
            stroke_opacity=0,
            fill_color=self.background_color,
            fill_opacity=1,
        )
        self.add(self.tail)


class ChatWindow(VGroup):
    def __init__(self, width=6, height=4, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height
        # Mobjects don't keep track of their scale, so when we scale the chat window
        # the newly created messages are *not* scaled. We keep track of the scale
        # ourselves.
        self.messages_scale = 1.0

        self.sender_colors = [
            util_general.ORANGE,
            util_general.RED,
            util_general.MAGENTA,
            util_general.BLUE,
            util_general.CYAN,
        ]
        self.senders = []

        self.displayed_messages = VGroup()
        self.add(self.displayed_messages)
        self.window = Rectangle(
            height=height,
            width=width,
            color=text_color,
            stroke_opacity=0,  # vv: uncomment to show border
        )
        self.add(self.window)

    def create_window(self):
        # Create a basic window frame for the chat
        animation = Create(self.window)
        return animation

    def add_message(
        self,
        sender: str,
        message: str,
        background_color: ParsableManimColor = util_general.BASE02,
        action: Literal["animate", "add", "nothing"] = "animate",
    ):
        # Format the message as "sender: message"

        # Position for the new message
        if self.displayed_messages:
            position = (
                self.displayed_messages[-1].get_corner(DOWN + LEFT)
                + DOWN * 0.9 * self.messages_scale
            )
        else:
            position = self.window.get_corner(UP + LEFT) + RIGHT * 0.2 + DOWN * 0.3

        # Create a text object for the message, positioned to the left
        if sender not in self.senders:
            self.senders.append(sender)
        sender_color = self.sender_colors[self.senders.index(sender)]

        message_obj = (
            ChatMessage(
                sender,
                message,
                sender_color=sender_color,
                background_color=background_color,
            )
            .scale(self.messages_scale)
            .move_to(position, aligned_edge=LEFT)
        )

        if action == "animate":
            animation = FadeIn(message_obj, run_time=0.5)
            return AnimationGroup(animation)
        elif action == "add":
            self.displayed_messages.add(message_obj)
            return message_obj
        elif action == "nothing":
            return message_obj
        else:
            raise ValueError(f"Invalid action {action}")
