from typing import Literal, Optional

from manim import *
from manim.mobject.types.vectorized_mobject import VMobject

from . import util_general
from .util_general import text_color


class CustomSVGMobject(SVGMobject):
    def interpolate_color(
        self, mobject1: VMobject, mobject2: VMobject, alpha: float
    ) -> None:
        attrs = [
            "fill_rgbas",
            "stroke_rgbas",
            "background_stroke_rgbas",
            # stroke_width was None, causing trouble in the original SVGMobject class
            # "stroke_width",
            "background_stroke_width",
            "sheen_direction",
            "sheen_factor",
        ]
        for attr in attrs:
            setattr(
                self,
                attr,
                interpolate(getattr(mobject1, attr), getattr(mobject2, attr), alpha),
            )
            if alpha == 1.0:
                setattr(self, attr, getattr(mobject2, attr))


class ChatMessage(VGroup):
    def __init__(
        self,
        sender: str,
        message: str,
        sender_color: ParsableManimColor = util_general.BASE00,
        background_color: ParsableManimColor = util_general.BASE02,
        tail_right: bool = False,  # x position of the bubble's tail
        tail_up: bool = False,  # y position of the bubble's tail
        with_verification: bool = False,
        *args,
        **kwargs,
    ):
        """A message in a chat stylized as a speech bubble."""
        super().__init__(*args, **kwargs)
        self.sender = sender
        self.message = message
        self.background_color = background_color

        self.message_text = Text(
            message, font="Helvetica", color=util_general.WHITE
        ).scale(0.8)
        self.sender_text = Text(sender, font="Helvetica", color=sender_color).scale(0.4)

        self.header_group = VGroup(self.sender_text)

        self.text_group = VGroup(self.header_group, self.message_text).arrange_in_grid(
            rows=2, cols=1, cell_alignment=LEFT, buff=SMALL_BUFF
        )

        self.add_verification()
        self.text_group.center()

        width = self.text_group.width + MED_LARGE_BUFF
        height = self.text_group.height + MED_LARGE_BUFF

        if not with_verification:
            # By removing after we've computed the width and height, we leave space
            # for the verification checkmark if we want to re-add it later.
            self.header_group.remove(self.verification)

        bubble_rectangle = RoundedRectangle(
            corner_radius=0.5 if sender != "" else 0.3,
            width=width,
            height=height,
            fill_color=background_color,
            fill_opacity=1,
            stroke_opacity=0,
        )

        tail = self.make_tail(bubble_rectangle, tail_right=tail_right, tail_up=tail_up)

        self.bubble = Union(
            bubble_rectangle,
            tail,
            fill_opacity=1,
            fill_color=background_color,
            stroke_opacity=0,
        )
        self.add(self.bubble)

        self.add(self.text_group)

    # Might not be needed in the end because moving the tail
    # can also be handled by .become().
    def make_tail(self, bubble_rectangle: Rectangle, tail_right: bool, tail_up: bool):
        tail_direction_x = RIGHT if tail_right else LEFT
        tail_direction_y = UP if tail_up else DOWN

        tail_corner = bubble_rectangle.get_corner(tail_direction_x + tail_direction_y)

        vertices = [
            tail_corner,
            tail_corner - 0.5 * tail_direction_x,
            tail_corner - 0.5 * tail_direction_y - 0.5 * tail_direction_x,
        ]

        # We'll be `Union()`-ing this with the rectangle later and Union
        # is sensitive to the vertex order. If they're in the wrong order,
        # we get a XOR of the tail and the bubble instead of a union.
        if int(tail_up) + int(tail_right) == 1:
            vertices.reverse()

        tail = Polygon(
            *vertices,
            stroke_opacity=0,
            fill_color=self.background_color,
            fill_opacity=1,
        )
        return tail

    def __repr__(self):
        return f"ChatMessage({self.sender}, {self.message})"

    def add_verification(self):
        self.verification = CustomSVGMobject("img/Twitter_Verified_Badge.svg").scale(
            0.15
        )
        self.verification.next_to(self.sender_text, RIGHT, buff=SMALL_BUFF)
        self.header_group.add(self.verification)
        return self.verification

    def has_verification(self):
        return self.verification in self.header_group

    def pop_header_group(self):
        """Remove and return the header group."""
        self.text_group.remove(self.header_group)
        return self.header_group


class ChatWindow(VGroup):
    SENDER_COLORS_ORDER = [
        util_general.ORANGE,
        util_general.GREEN,
        util_general.MAGENTA,
        util_general.BLUE,
        util_general.CYAN,
    ]
    SENDER_COLORS = {
        f"General #{i + 1}": color for i, color in enumerate(SENDER_COLORS_ORDER)
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Mobjects don't keep track of their scale, so when we scale the chat window
        # the newly created messages are *not* scaled. We keep track of the scale
        # ourselves.
        self.messages_scale = 1.0

        self.senders = []

        self.messages_group = VGroup()
        self.add(self.messages_group)

        # Includes even the ones that aren't displayed at the moment.
        self.all_messages: list[ChatMessage] = []

        # Even though we don't display the frame, we still need the window
        # because it affects methods like .get_center() - that doesn't work
        # if the group is empty.
        self.window = Rectangle(
            # Arbitrary but standardized. Changing width/height could break
            # positioning in existing animations
            width=6,
            height=4,
            color=text_color,
            stroke_opacity=0,  # vv: uncomment to show border
        )
        self.add(self.window)

    def add_message(
        self,
        message: ChatMessage,
        action: Literal["animate", "add", "nothing"] = "animate",
    ):
        # Format the message as "sender: message"

        # Position for the new message
        if self.all_messages:
            position = (
                self.all_messages[-1].get_corner(DOWN + LEFT)
                + DOWN * 0.9 * self.messages_scale
            )
        else:
            position = self.window.get_corner(UP + LEFT) + RIGHT * 0.2 + DOWN * 0.3

        if message.sender not in self.senders:
            self.senders.append(message.sender)

        # Make the message properties (color, scale, position) fit the ChatWindow
        sender_color = self.SENDER_COLORS[message.sender]
        message.sender_text.set_color(sender_color)
        message.scale(self.messages_scale).move_to(position, aligned_edge=LEFT)

        self.all_messages.append(message)

        if action == "animate":
            animation = FadeIn(message, run_time=0.5)
            return AnimationGroup(animation)
        elif action == "add":
            self.messages_group.add(message)
            return message
        elif action == "nothing":
            return message
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
                    ChatMessage(
                        sender=message_from.sender,
                        message=message_from.message,
                        background_color=new_background_color,
                        with_verification=message_from.has_verification(),
                    ),
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
