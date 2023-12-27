from manim import *
from .util_general import text_color, BASE00
from . import util_general


class ChatMessage(VGroup):
    def __init__(
        self,
        sender: str,
        message: str,
        sender_color: ParsableManimColor = util_general.WHITE,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        message_text = Text(message, font="Helvetica").scale(0.8)
        sender_text = Text(sender, color=sender_color, font="Helvetica").scale(0.4)

        text_group = VGroup(sender_text, message_text).arrange_in_grid(
            rows=2, cols=1, cell_alignment=LEFT, buff=SMALL_BUFF
        )

        width = text_group.width + MED_LARGE_BUFF
        height = text_group.height + MED_LARGE_BUFF

        self.add(
            RoundedRectangle(
                corner_radius=0.5,
                width=width,
                height=height,
                fill_color=util_general.BASE02,
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
                fill_color=util_general.BASE02,
                fill_opacity=1,
            )
        )

        # sender_text.align_to(self, direction=LEFT + UP)
        # sender_text.shift(0.3 * RIGHT + 0.2 * DOWN)

        self.add(text_group)


class ChatWindow(VGroup):
    def __init__(self, width=6, height=4, **kwargs):
        super().__init__(**kwargs)
        self.width = width
        self.height = height

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

    def add_message(self, sender: str, message: str, animate: bool = True):
        # Format the message as "sender: message"

        # Position for the new message
        if self.displayed_messages:
            position = self.displayed_messages[-1].get_corner(DOWN + LEFT) + DOWN * 0.9
        else:
            position = self.window.get_corner(UP + LEFT) + RIGHT * 0.2 + DOWN * 0.3

        # Create a text object for the message, positioned to the left
        if sender not in self.senders:
            self.senders.append(sender)
        sender_color = self.sender_colors[self.senders.index(sender)]

        message_obj = ChatMessage(sender, message, sender_color=sender_color).move_to(
            position, aligned_edge=LEFT
        )
        self.displayed_messages.add(message_obj)

        if animate:
            animation = FadeIn(message_obj, run_time=0.5)
            return AnimationGroup(animation)
        else:
            self.add(message_obj)
            return None
