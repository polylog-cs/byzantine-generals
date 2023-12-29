from typing import Literal, Optional

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

    def __repr__(self):
        return f"ChatMessage({self.sender}, {self.message})"


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

        self.messages_group = VGroup()
        self.add(self.messages_group)

        # Includes even the ones that aren't displayed at the moment.
        self.all_messages: list[ChatMessage] = []

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
        if self.messages_group:
            position = (
                self.all_messages[-1].get_corner(DOWN + LEFT)
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

        self.all_messages.append(message_obj)

        if action == "animate":
            animation = FadeIn(message_obj, run_time=0.5)
            return AnimationGroup(animation)
        elif action == "add":
            self.messages_group.add(message_obj)
            return message_obj
        elif action == "nothing":
            return message_obj
        else:
            raise ValueError(f"Invalid action {action}")

    def copy_messages(
        self,
        messages_from: list[ChatMessage],
        background_color: Optional[ParsableManimColor] = None,
        keep_original: bool = True,
    ):
        """Copies the given messages to the chat window."""
        animations = []
        new_messages = []

        n_previous_messages = len(self.all_messages)

        for message_from in messages_from:
            new_background_color = background_color or message_from.background_color
            new_messages.append(
                self.add_message(
                    message_from.sender,
                    message_from.message,
                    background_color=new_background_color,
                    action="nothing",
                )
            )

        previous_bottom = self.all_messages[n_previous_messages - 1].get_corner(
            DOWN + LEFT
        )
        new_bottom = new_messages[-1].get_corner(DOWN + LEFT)
        shift = previous_bottom - new_bottom

        for i, message_to in enumerate(self.all_messages):
            if i < n_previous_messages:
                i_reversed = len(self.all_messages) - i - 1
                fade_strength = 0 if i_reversed < 5 else 1

                animations.append(
                    message_to.animate.shift(shift).fade_to(
                        ManimColor(util_general.BASE2), fade_strength
                    )
                )
            else:
                message_to.shift(shift)

                message_from = messages_from[i - n_previous_messages]

                if keep_original:
                    message_from = message_from.copy()
                animations.append(message_from.animate.become(message_to))

                # At this point, `message_to` is not actually displayed because it's not added
                # to any Manim group. Then using .become() we move `message_from` to the position
                # of the invisible `message_to`. Replace self.all_messages[i] with `message_from`
                # so that we use that in subsequent animations.
                # Otherwise, if we do copy_messages() again, we will .shift() the invisible
                # message, causing weird behavior.
                self.all_messages[i] = message_from

                # .become() doesn't update this custom property, so we do it manually.
                message_from.background_color = new_background_color

        return AnimationGroup(*animations)
