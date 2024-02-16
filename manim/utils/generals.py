from collections import namedtuple
from typing import List, Optional, Tuple

from manim import *

import utils.chat_window

from .util_general import *

GENERAL_RADIUS = 0.5

GENERAL_CIRCLE_SIZE = 2.2
GENERAL_THINKING_BUFFER_RADIUS = 3.5
GENERAL_RECEIVE_BUFFER_RADIUS = 1.3

MESSAGE_RADIUS = 0.05

MESSAGE_BUFFER_COLUMNS = 2
MESSAGE_BUFFER_HORIZONTAL_OFFSET = 0.45
MESSAGE_BUFFER_VERTICAL_OFFSET = 0.3

# Messages are received in a circle with this radius
RECEIVE_BUFFER_CIRCULAR_RADIUS = 0.23

MessageToSend = namedtuple("MsgType", ["sender_id", "receiver_id", "message"])
WHOOSH_OFFSET = 0.5
CLICK_OFFSET = 0.1
EXPLOSION_OFFSET = 0.1


class Message(Group):
    def __init__(self, message: str, clipart=False):
        super().__init__()
        self.message = message
        self.color = RED if message == "N" else GREEN
        self.icon = Circle(
            radius=MESSAGE_RADIUS,
            color=self.color,
            stroke_width=2,
            fill_color=self.color,
            fill_opacity=1,
        )
        self.add(self.icon)
        if clipart:
            # Note that the scale gets overwritten in SendMessage
            self.clipart = ImageMobject("img/envelope_2.png").scale(0.2)
            self.add(self.clipart)


# NOTE(vv): An older version of the crown. To be removed, but a lot of the animations are already
#   rendered with this version so we keep it in case we only need to do minor changes.
class BlackCrown(SVGMobject):
    def __init__(self, parent: Mobject):
        super().__init__("img/crown.svg")
        self.scale(parent.width / self.width)

        self.set_z_index(100)  # Make sure the crown is always on top


class Crown(ImageMobject):
    def __init__(self, parent: Mobject):
        super().__init__("img/crown_2.png")
        self.scale(0.28)

        self.set_z_index(100)  # Make sure the crown is always on top


class LeaderMessage(Message):
    def __init__(self, message: str):
        super().__init__(message)
        self.crown = BlackCrown(self)
        self.add(self.crown)


class MessageBuffer(Group):
    def __init__(self):
        super().__init__()
        self.messages = []
        self.icon = Rectangle(width=1, height=1, stroke_opacity=0.0).scale(0.75)
        self.add(self.icon)

    def add_message(self, message: Message):
        self.messages.append(message)

    def count_regular_opinions(self):
        opinions = [
            msg.message for msg in self.messages if not isinstance(msg, LeaderMessage)
        ]
        return opinions.count("Y"), opinions.count("N")

    def sort_messages(self):
        # Reorganize the messages by the opinion they carry
        anims = []
        y_cnt, n_cnt = 0, 0
        message_spacing = 3 * MESSAGE_RADIUS  # 2 * radius + spacing
        for msg in self.messages:
            if isinstance(msg, LeaderMessage):
                # Leader messages are not sorted, they are just shifted up
                # to make space for the inequality symbol.
                anims.append(msg.animate.shift(UP * MESSAGE_BUFFER_VERTICAL_OFFSET))
                continue
            if msg.message == "Y":
                row = y_cnt // MESSAGE_BUFFER_COLUMNS
                col = y_cnt % MESSAGE_BUFFER_COLUMNS
                pos = (
                    self.get_center()
                    + LEFT * MESSAGE_BUFFER_HORIZONTAL_OFFSET
                    + UP * MESSAGE_BUFFER_VERTICAL_OFFSET
                    + row * message_spacing * DOWN
                    + col * message_spacing * RIGHT
                )
                y_cnt += 1
            elif msg.message == "N":
                row = n_cnt // MESSAGE_BUFFER_COLUMNS
                col = n_cnt % MESSAGE_BUFFER_COLUMNS
                pos = (
                    self.get_center()
                    + RIGHT * MESSAGE_BUFFER_HORIZONTAL_OFFSET
                    + UP * MESSAGE_BUFFER_VERTICAL_OFFSET
                    + row * message_spacing * DOWN
                    + col * message_spacing * LEFT
                )
                n_cnt += 1
            else:
                raise Exception("Invalid message")
            anims.append(msg.animate.move_to(pos))
        return anims


class CodeWithStepping(Code):
    CODE = """for leader_id in [1, 2, 3]:
  send my opinion to everybody
  if I am the leader:  # Leader-based algorithm
    my opinion ← majority opinion
    broadcast my opinion
  count YES and NO messages  # Distributed algorithm
  if #YES >= 10 or #NO >= 10:
    my opinion ← local opinion
  else:
    my opinion ← leader opinion
"""

    # if YES >> NO or NO >> YES:
    def __init__(self, code_text=CODE, **kwargs):
        super().__init__(
            code=code_text,
            language="python",
            # Would love to set this to False, but then highlighting lines breaks.
            insert_line_no=True,
            style="solarized-dark",
            **kwargs,
        )
        # Manim colors the line numbers black no matter the theme, so fix that
        for i in self.line_numbers:
            i.set_color(BASE00)

        self.indicator = None
        self.rectangle = None

    def indicator_position(self, line_number: int):
        return self.line_numbers[line_number].get_right() + 0.25 * LEFT

    def rectangle_around_line(self, line_number: int):
        line = self.code[line_number]
        offset = 0 if line_number == 0 else 0.03
        return Rectangle(
            width=line.width + 0.2,
            height=line.height - offset + 0.02,
            color=RED,
        ).move_to(line.get_center() + offset * DOWN)

    def highlight_line(self, line_number: int, scene: Scene):
        if self.indicator is not None:
            new_rectangle = self.rectangle_around_line(line_number)
            scene.play(
                self.indicator.animate.move_to(self.indicator_position(line_number)),
                self.rectangle.animate.become(new_rectangle),
            )
        else:
            self.indicator = Arrow(
                start=self.indicator_position(line_number),
                end=self.indicator_position(line_number) + 0.1 * RIGHT,
                color=RED,
                max_tip_length_to_length_ratio=1,
            )
            self.indicator.move_to(self.indicator_position(line_number))
            self.rectangle = self.rectangle_around_line(line_number)
            scene.add(self.indicator, self.rectangle)


class General(Group):
    def __init__(
        self,
        icon_color: ManimColor,
        fill_icon: bool,
        with_clipart: bool = False,
        number: Optional[int] = None,
    ):
        super().__init__()
        self.icon = Circle(
            radius=GENERAL_RADIUS,
            color=icon_color,
            fill_color=icon_color,
            # Don't show the circle if we're using the clipart.
            fill_opacity=1 if fill_icon and not with_clipart else 0,
            stroke_width=0 if with_clipart else 4,
        )
        self.add(self.icon)

        if with_clipart:
            self.clipart = ImageMobject("img/icon_general_2.png").scale(0.25)
            if number != None:
                if number == -1:
                    number = 1
                    self.clipart = ImageMobject("img/icon_traitor_2.png").scale(0.25)
                txt = (
                    Tex(
                        rf"\#{number}",
                        color=utils.chat_window.SENDER_COLORS_ORDER[number - 1],
                    )
                    .scale(0.5)
                    .align_to(self.clipart, DL)
                    .shift(0.2 * LEFT)
                )
                self.clipart = Group(self.clipart, txt)

            self.add(self.clipart)

        self.crown = None

    def get_center(self):
        return self.icon.get_center()

    def is_leader(self) -> bool:
        return self.crown is not None

    def make_leader(
        self, generals: Optional[list["General"]] = None, use_black_crown: bool = False
    ) -> Animation:
        """Pass the crown to this general.

        If `generals` is given, moves the crown visually from the current leader
        in `generals` to this general.
        """
        if self.is_leader():
            return Wait(0.0)  # Nothing to do.

        current_leader = None

        if generals:
            for g in generals:
                if g.is_leader():
                    current_leader = g
                    break

        CROWN_BUFFER = MED_LARGE_BUFF if use_black_crown else 0.4

        if current_leader is not None:
            old_crown = current_leader.crown
            self.crown = old_crown
            current_leader.crown = None
            return old_crown.animate.next_to(
                self.get_center(), direction=UP, buff=CROWN_BUFFER
            )
        else:
            # No other generals given. Simply become the leader.
            CrownConstructor = BlackCrown if use_black_crown else Crown
            self.crown = CrownConstructor(self.icon).next_to(
                self.get_center(), direction=UP, buff=CROWN_BUFFER
            )
            return FadeIn(self.crown)

    def remove_leader(self) -> Animation:
        assert self.is_leader()

        crown = self.crown
        self.crown = None
        return FadeOut(crown)

    def add_receive_buffer(self, buffer: MessageBuffer):
        self.receive_buffer = buffer
        self.add(buffer)

    def add_thinking_buffer(self, buffer: MessageBuffer):
        self.thinking_buffer = buffer
        self.add(buffer)

    def move_receive_buffer_to_thinking_buffer(self) -> List[Animation]:
        # Traitors don't move their receive buffer to the thinking buffer,
        # they just discard the messages.
        if self.is_traitor:
            anims = [FadeOut(msg) for msg in self.receive_buffer.messages]
            self.receive_buffer.messages = []
            return anims

        receive_to_thinking = (
            self.thinking_buffer.get_center() - self.receive_buffer.get_center()
        )
        anims = [
            msg.animate.shift(receive_to_thinking)
            for msg in self.receive_buffer.messages
        ]
        self.thinking_buffer.messages += self.receive_buffer.messages
        self.receive_buffer.messages = []
        return anims

    def update_opinion_to_majority(self, scene: Scene, short_version: bool = False):
        thinking_buffer = self.thinking_buffer

        y_cnt, n_cnt = thinking_buffer.count_regular_opinions()
        win = "Y" if y_cnt >= n_cnt else "N"

        if not short_version:
            scene.play(*thinking_buffer.sort_messages())
            msgs = thinking_buffer.messages

            inequality_symbol = Tex("$\ge$" if win == "Y" else "$<$", color=BLACK)
            inequality_symbol.move_to(thinking_buffer.get_center())
            scene.play(FadeIn(inequality_symbol))

            new_opinion = Message(win).scale(4)  # Make the new opinion 4x bigger
            new_opinion.move_to(inequality_symbol)

            scene.play(
                *[msg.animate.move_to(new_opinion) for msg in msgs],
                inequality_symbol.animate.become(new_opinion.icon),
            )
            self.thinking_buffer.messages = []
            scene.remove(inequality_symbol, *msgs)
        else:
            new_opinion = Message(win).scale(4)
            new_opinion.move_to(thinking_buffer.get_center())
            scene.play(
                FadeIn(new_opinion), *[FadeOut(msg) for msg in thinking_buffer.messages]
            )
        return new_opinion

    def update_opinion_to_supermajority_or_leader(
        self, scene: Scene, example=False
    ) -> Message:
        """Returns a Message with the new opinion."""
        thinking_buffer = self.thinking_buffer
        scene.play(*thinking_buffer.sort_messages())

        if example == True:
            unit = thinking_buffer.messages[0].get_width()
            scene.play(thinking_buffer.messages[-1].animate.shift(UP * 2 * unit))
            txt_scale = 0.2
            # circumscribe the messages with thin line
            scene.play(Circumscribe(Group(*thinking_buffer.messages[:-1]), color=RED))
            scene.wait()
            sign = (
                Tex(r"$\ge$", color=BLACK)
                .scale(0.8)
                .move_to(thinking_buffer.get_center())
                .shift(UP * unit)
            )
            signg = Tex(r"$\gg$", color=BLACK).scale(0.8).move_to(sign)
            signl = Tex(r"$\ll$", color=BLACK).scale(0.8).move_to(sign)
            signs = Tex(r"$\approx$", color=BLACK).scale(0.8).move_to(sign)
            scene.play(FadeIn(sign))
            scene.wait()
            fake_circles = [circle.copy() for circle in thinking_buffer.messages]
            local_opinion_tex = Tex("Local opinion: ", color=TEXT_COLOR).scale(
                txt_scale
            )
            local_opinion_circle = Circle(
                radius=1, color=GREEN, fill_color=GREEN, fill_opacity=1
            ).scale_to_fit_width(thinking_buffer.messages[-1].get_width())
            local_opinion = Group(local_opinion_tex, local_opinion_circle)
            leader_opinion_tex = Tex("Leader opinion: ", color=TEXT_COLOR).scale(
                txt_scale
            )
            leader_opinion_circle = fake_circles[3].copy()
            leader_opinion = Group(leader_opinion_tex, leader_opinion_circle)
            opinions = (
                Group(*local_opinion, *leader_opinion)
                .arrange_in_grid(rows=2, buff=0.05, cell_alignment=LEFT)
                .next_to(Group(*thinking_buffer.messages), DOWN, buff=0.1)
                .shift(1.5 * unit * UP + 1 * unit * RIGHT)
            )

            scene.play(Write(local_opinion_tex))
            scene.play(
                *[
                    circle.animate.move_to(local_opinion_circle)
                    for circle in fake_circles
                    if circle.get_center()[0] < sign.get_center()[0]
                ]
            )
            scene.wait()

            arrow1 = (
                ImageMobject("img/arrow.png")
                .scale_to_fit_height(unit)
                .next_to(thinking_buffer.messages[0], direction=LEFT, buff=0)
            )
            arrow2 = arrow1.copy().next_to(
                thinking_buffer.messages[2], direction=LEFT, buff=0
            )
            scene.play(FadeIn(arrow1), FadeIn(arrow2))
            scene.wait()
            scene.play(FadeOut(arrow1), FadeOut(arrow2))
            scene.wait()

            scene.play(thinking_buffer.messages[-1].animate.scale(1.5), run_time=0.5)
            scene.play(
                thinking_buffer.messages[-1].animate.scale(1 / 1.5), run_time=0.5
            )
            scene.wait()
            scene.play(Write(leader_opinion_tex))
            pos = leader_opinion_circle.get_center()
            leader_opinion_circle.move_to(fake_circles[-1])
            scene.play(leader_opinion_circle.animate.move_to(pos))
            scene.wait()

            scene.play(local_opinion_circle.animate.scale(1.5), run_time=0.5)
            scene.play(local_opinion_circle.animate.scale(1 / 1.5), run_time=0.5)
            scene.wait()
            scene.play(leader_opinion_circle.animate.scale(1.5), run_time=0.5)
            scene.play(leader_opinion_circle.animate.scale(1 / 1.5), run_time=0.5)
            scene.wait()

            code_text = """if ??????:
    my opinion ← local opinion
else:
    my opinion ← leader opinion"""
            code_text2 = """if YES >> NO or NO >> YES:
    my opinion ← local opinion
else:
    my opinion ← leader opinion"""
            code_text3 = """if YES >= 10 or NO >= 10:
    my opinion ← local opinion
else:
    my opinion ← leader opinion"""
            code = (
                CodeWithStepping(code_text=code_text)
                .scale(0.3)
                .next_to(thinking_buffer, RIGHT, buff=0.5)
            )

            scene.play(
                scene.camera.auto_zoom(
                    Group(*self.thinking_buffer.messages, code), margin=0.7
                ),
                FadeIn(code),
                FadeOut(opinions),
                FadeOut(*fake_circles),
            )
            scene.wait()

            new_circles = [
                circle.icon.copy().move_to(circle)
                for circle in thinking_buffer.messages[:-1]
            ]
            scene.add(*new_circles)
            scene.remove(*thinking_buffer.messages[:-1])

            # first some red circles go to the left and become green
            r = new_circles[1].get_center() - new_circles[0].get_center()
            d = new_circles[2].get_center() - new_circles[0].get_center()
            new_pos = {}
            new_pos[6] = new_circles[0].get_center() + r + 3 * d
            new_pos[8] = new_circles[0].get_center() + 0 * r + 4 * d
            new_pos[9] = new_circles[0].get_center() + r + 4 * d
            for i in range(len(new_circles)):
                new_circles[i].save_state()

            anims = []
            for i in new_pos.keys():
                anims.append(
                    AnimationGroup(
                        new_circles[i]
                        .animate.set_fill(GREEN)
                        .set_color(GREEN)
                        .move_to(new_pos[i])
                    )
                )
            scene.play(
                *anims,
                sign.animate.become(signg),
            )
            scene.wait()

            new_pos = {}
            new_pos[11] = new_circles[5].get_center() + 0 * r + 2 * d
            new_pos[7] = new_circles[5].get_center() + 0 * r + 3 * d
            new_pos[10] = new_circles[5].get_center() + 1 * r + 3 * d
            anims = []
            for i in new_pos.keys():
                anims.append(
                    AnimationGroup(
                        new_circles[i]
                        .animate.set_fill(RED)
                        .set_color(RED)
                        .move_to(new_pos[i])
                    )
                )
            scene.play(
                *[
                    c.animate.restore()
                    for c in [new_circles[6], new_circles[8], new_circles[9]]
                ],
                *anims,
                sign.animate.become(signl),
                new_circles[0]
                .animate.set_fill(RED)
                .move_to(new_circles[5].get_center() + 0 * r + 4 * d),
                new_circles[2]
                .animate.set_fill(RED)
                .move_to(new_circles[5].get_center() + r + 4 * d),
                new_circles[4].animate.move_to(
                    new_circles[0].get_center() + 0 * r + 0 * d
                ),
            )
            scene.wait()

            new_circles[0].save_state()
            new_circles[2].save_state()
            scene.play(
                new_circles[0]
                .animate.set_fill(GREEN)
                .move_to(new_circles[4].get_center() + 0 * r + 1 * d),
                new_circles[2]
                .animate.set_fill(GREEN)
                .move_to(new_circles[4].get_center() + r + 1 * d),
            )
            scene.wait()
            scene.play(
                new_circles[0].animate.restore(),
                new_circles[2].animate.restore(),
            )
            scene.wait()

            scene.play(
                new_circles[0]
                .animate.set_fill(GREEN)
                .move_to(new_circles[4].get_center() + 0 * r + 1 * d),
                new_circles[2]
                .animate.set_fill(GREEN)
                .move_to(new_circles[4].get_center() + r + 1 * d),
                new_circles[10]
                .animate.set_fill(GREEN)
                .set_color(GREEN)
                .move_to(new_circles[4].get_center() + 0 * r + 2 * d),
                new_circles[7]
                .animate.set_fill(GREEN)
                .set_color(GREEN)
                .move_to(new_circles[4].get_center() + r + 2 * d),
                sign.animate.become(signs),
            )
            scene.wait()

            scene.play(thinking_buffer.messages[-1].animate.scale(1.5), run_time=0.5)
            scene.play(
                thinking_buffer.messages[-1].animate.scale(1 / 1.5), run_time=0.5
            )
            scene.wait()

            code2 = (
                CodeWithStepping(code_text=code_text3)
                .scale_to_fit_width(code.get_width())
                .move_to(code)
            )
            scene.play(code.animate.become(code2))
            return

        msgs = thinking_buffer.messages

        leader_msg = list(filter(lambda msg: isinstance(msg, LeaderMessage), msgs))
        assert len(leader_msg) == 1
        leader_msg = leader_msg[0]

        y_msgs = filter(
            lambda msg: not isinstance(msg, LeaderMessage) and msg.message == "Y", msgs
        )
        n_msgs = filter(
            lambda msg: not isinstance(msg, LeaderMessage) and msg.message == "N", msgs
        )

        y_cnt, n_cnt = thinking_buffer.count_regular_opinions()
        if n_cnt <= 2:
            win = "Y"
            tex = "$\gg$"  # Supermajority
        elif y_cnt <= 2:
            win = "N"
            tex = "$\ll$"  # Supermajority
        else:
            win = leader_msg.message
            tex = "$\\approx$"

        inequality_symbol = Tex(tex, color=BLACK).scale(0.8)
        inequality_symbol.move_to(thinking_buffer.get_center())
        scene.play(FadeIn(inequality_symbol))

        new_opinion = Message(win).scale(4)  # Make the new opinion 4x bigger
        new_opinion.move_to(inequality_symbol)

        if n_cnt <= 2:
            anims = (
                [msg.animate.move_to(new_opinion) for msg in y_msgs]
                + [FadeOut(msg) for msg in n_msgs]
                + [FadeOut(leader_msg)]
            )
        elif y_cnt <= 2:
            anims = (
                [msg.animate.move_to(new_opinion) for msg in n_msgs]
                + [FadeOut(msg) for msg in y_msgs]
                + [FadeOut(leader_msg)]
            )
        else:
            anims = (
                [leader_msg.animate.move_to(new_opinion)]
                + [FadeOut(msg) for msg in y_msgs]
                + [FadeOut(msg) for msg in n_msgs]
            )

        scene.play(
            *anims,
            inequality_symbol.animate.become(new_opinion.icon),
        )
        self.thinking_buffer.messages = []
        scene.remove(inequality_symbol, *msgs)
        return new_opinion


class Player(General):
    def __init__(
        self,
        opinion: str = "",
        with_clipart: bool = False,
        number: Optional[int] = None,
    ):
        # The icon color gets overwritten by self.change_opinion() below
        super().__init__(
            icon_color=GRAY, fill_icon=False, with_clipart=with_clipart, number=number
        )
        self.opinion = opinion
        self.is_traitor = False
        self.opinion_text = Tex(opinion)
        self.change_opinion(opinion)
        self.add(self.opinion_text)

    def get_color(self):
        return {
            "Y": GREEN,
            "N": RED,
            "-": GRAY,
        }.get(self.opinion, MAGENTA)

    def change_opinion(self, opinion: str, with_highlight: bool = False):
        self.opinion = opinion
        color = self.get_color()

        new_opinion_text = Tex(opinion, color=color)
        if opinion == "-":
            new_opinion_text.scale(1.0 / 100)
        new_opinion_text.move_to(self.icon)
        self.opinion_text.become(new_opinion_text)
        self.icon.set_stroke(color=color, opacity=1)
        if with_highlight:
            self.icon.set_fill(color=color, opacity=0.2)
        else:
            # Perhaps not necessary
            self.icon.set_fill(color=color, opacity=0.0)


class Traitor(General):
    def __init__(self, with_clipart: bool = False, number: Optional[int] = None):
        super().__init__(
            icon_color=MAGENTA, fill_icon=True, with_clipart=with_clipart, number=number
        )
        self.is_traitor = True

    def change_opinion(self, opinion: str, with_highlight: bool = False):
        pass


class CyclicOpinionTraitor(Traitor):
    def __init__(self, opinions: str = ""):
        super().__init__()
        self.opinions = opinions
        self.opinion_idx = 0

    @property
    def opinion(self):
        """
        Traitors opinion is cyclic and changes every time it is accessed.
        """
        ret = self.opinions[self.opinion_idx]
        self.opinion_idx = (self.opinion_idx + 1) % len(self.opinions)
        return ret


class GameState(Group):
    def __init__(self, generals: List[General], shft=None):
        super().__init__()
        self.generals = generals
        # Distribute generals in a circle
        for i in range(len(self.generals)):
            # Create the ith general
            g = self.generals[i]
            g.shift(self.circle_position(i) * GENERAL_CIRCLE_SIZE)
            self.add(g)
            # Create the ith general's message buffer
            receive_buffer = MessageBuffer()
            receive_buffer.shift(
                self.circle_position(i) * GENERAL_RECEIVE_BUFFER_RADIUS
            )
            g.add_receive_buffer(receive_buffer)
            # Create the ith general's thinking buffer
            thinking_buffer = MessageBuffer()
            thinking_buffer.shift(
                self.circle_position(i) * GENERAL_THINKING_BUFFER_RADIUS
            )
            if shft is not None and i in shft:
                thinking_buffer.shift(shft[i])
            g.add_thinking_buffer(thinking_buffer)

    # TODO pls check
    def change_general(
        self, scene: Scene, i: int, new_general: General, with_animation: bool = True
    ):
        """
        Replace the ith general with a new general.
        """
        new_general.shift(self.circle_position(i) * GENERAL_CIRCLE_SIZE)

        if with_animation:
            scene.play(FadeOut(self.generals[i]), FadeIn(new_general))
            scene.wait()
        else:
            scene.remove(self.generals[i])
            scene.add(new_general)

        self.remove(self.generals[i])
        self.generals[i] = new_general
        self.add(new_general)

        receive_buffer = MessageBuffer()
        receive_buffer.shift(self.circle_position(i) * GENERAL_RECEIVE_BUFFER_RADIUS)
        new_general.add_receive_buffer(receive_buffer)

        thinking_buffer = MessageBuffer()
        thinking_buffer.shift(self.circle_position(i) * GENERAL_THINKING_BUFFER_RADIUS)
        new_general.add_thinking_buffer(thinking_buffer)

    def circle_position(self, i: int):
        """
        Return the position of the ith general in the circle.
        """
        # Shift the index by 1 so that the generals are numbered like clocks
        ii = (i + 1) % len(self.generals)
        x = np.sin(ii * 2 * np.pi / len(self.generals))
        y = np.cos(ii * 2 * np.pi / len(self.generals))
        return x * RIGHT + y * UP

    def send_messages_low_tech(
        self,
        scene: Scene,
        messages: List[MessageToSend],
        lag_ratio=0.1,
        # Sending messages pairwise between all 12 generals is too much.
        max_messages: int = 25,
    ):
        """
        Sends messages from the sender to the receiver.
        Only cliparts are shown, no additional info.
        """

        rng = np.random.default_rng(0)
        rng.shuffle(messages)
        messages = messages[:max_messages]

        anims = []
        for message in messages:
            sender = self.generals[message.sender_id]
            receiver = self.generals[message.receiver_id]
            msg = message.message.clipart.copy()

            msg.shift(RIGHT * 100)

            anims.append(
                SendMessage(msg, start=sender.get_center(), end=receiver.get_center())
            )

        for i in range(len(anims)):
            scene.add_sound(random_click_file(), time_offset=lag_ratio * i)

        # Note that `Succession` doesn't work here.
        scene.play(LaggedStart(*anims, lag_ratio=lag_ratio))

    def send_messages(
        self,
        messages_to_send: List[MessageToSend],
        circular_receive=False,
        circular_send=False,
    ) -> Tuple[List[Message], List[Animation], List[Mobject]]:
        """
        Send messages from the sender to the receiver.
        If circular_receive is True, the messages are received in the receive buffer
        in the same layout as the generals are positioned in the circle.
        """
        msg_objects = []
        anims = []
        to_remove = []

        for message_to_send in messages_to_send:
            sender = self.generals[message_to_send.sender_id]
            receiver: General = self.generals[message_to_send.receiver_id]
            message = message_to_send.message

            if sender.is_traitor:
                # Make the message border black if the sender is a traitor
                # to indicate that the message is not trustworthy.
                message.icon.stroke_color = BLACK
                pass

            if circular_send:
                # Before sending, messages are aligned around the sender's icon,
                # corresponding to which receiver they are sent to.
                message.move_to(
                    sender.icon.get_center()
                    + self.circle_position(message_to_send.receiver_id) * GENERAL_RADIUS
                )
            else:
                # Messages are sent from the sender's position to the receiver's buffer
                # TODO hlasilo chybu
                # msg.move_to(sender.receive_buffer)
                message.move_to(sender.icon.get_center())

            # Make the message icon appear from the sender's icon
            message_icon_copy = message.icon.copy()

            message.icon = sender.icon.copy()

            # Animate the message moving from the sender to the receiver.
            if circular_receive:
                # Arange the messages in the buffer in the same circle as the generals from
                # which they were sent.
                receive_location = (
                    receiver.receive_buffer.get_center()
                    + self.circle_position(message_to_send.sender_id)
                    * RECEIVE_BUFFER_CIRCULAR_RADIUS
                )
            else:
                receive_location = receiver.receive_buffer.get_center()

            message_icon_copy.move_to(receive_location)
            anims.append(message.icon.animate.become(message_icon_copy))

            if isinstance(message, LeaderMessage):
                # TODO(vv): handle
                pass
                # print("leader message")
                # message_crown_copy = message.crown.copy().move_to(
                #     receive_location
                # )
                # anims.append(FadeIn(message_crown_copy))

            msg_objects.append(message)

            message.move_to(receive_location)
            receiver.receive_buffer.add_message(message)

            to_remove.append(message.icon)

        # NOTE(vv): It's ugly to have to return a separate to_remove list
        # but I couldn't figure out how to avoid it because of Manim's weird
        # behavior with animations scheduled ahead of time and .become().
        # Specifically, when you run move_receive_buffer_to_thinking_buffer(),
        # copies of the message dots would say behind.
        return msg_objects, anims, to_remove

    def broadcast_opinion(
        self,
        scene: Scene,
        general_ids: List[int],
        send_to_self=False,
        circular_receive=False,
        circular_send=False,
        msg_class=Message,
    ) -> List[Message]:
        messages = []
        for general_id in general_ids:
            for i in range(len(self.generals)):
                if i != general_id or send_to_self:
                    messages.append(
                        MessageToSend(
                            general_id, i, msg_class(self.generals[general_id].opinion)
                        )
                    )
        msg_objects, anims, to_remove = self.send_messages(
            messages,
            circular_receive=circular_receive,
            circular_send=circular_send,
        )
        scene.play(*anims)
        scene.remove(*to_remove)

        return msg_objects

    def send_opinions_to(self, general_id: int, send_to_self: bool = False):
        messages = []
        for i in range(len(self.generals)):
            if send_to_self or i != general_id:
                messages.append(
                    MessageToSend(i, general_id, Message(self.generals[i].opinion))
                )
        msg_objects, anims, to_remove = self.send_messages(
            messages, circular_receive=True
        )
        return msg_objects, anims, to_remove

    def send_opinions_from(self, general_id: int, send_to_self: bool = False):
        messages = []
        for i in range(len(self.generals)):
            if send_to_self or i != general_id:
                messages.append(
                    MessageToSend(
                        general_id, i, Message(self.generals[general_id].opinion)
                    )
                )
        msg_objects, anims, to_remove = self.send_messages(
            messages, circular_receive=True
        )
        return msg_objects, anims, to_remove

    def update_general_opinions(
        self,
        scene: Scene,
        general_ids: List[int],
        opinions: List[Message],
        with_highlight: bool = False,
    ):
        anims = []
        new_icons = []
        for general_id, opinion in zip(general_ids, opinions):
            new_icon = self.generals[general_id].icon.copy()
            if not self.generals[general_id].is_traitor:
                new_icon.color = opinion.color
            new_icons.append(new_icon)

            anims.append(
                self.generals[general_id].animate.change_opinion(
                    opinion.message, with_highlight=with_highlight
                )
            )
            anims.append(opinion.icon.animate.become(new_icon))

            # The opinion was also sent via `broadcast_opinion` and stored in the receive
            # buffer, so make sure we remove it
            self.generals[general_id].receive_buffer.messages = []

        scene.play(*anims)
        scene.remove(*opinions, *new_icons)

    def leader_algorithm(
        self,
        scene: Scene,
        leader_id: int,
        send_to_self: bool = True,
        remove_leader_when_done: bool = True,
        add_background_at_the_end: bool = True,
    ):
        scene.play(self.set_leader(leader_id))

        scene.wait(0.5)

        _, anims, to_remove = self.send_opinions_to(leader_id, send_to_self)
        scene.add_sound(random_whoosh_file(), time_offset=WHOOSH_OFFSET)
        scene.play(*anims)

        scene.wait(0.5)

        scene.remove(*to_remove)
        scene.play(*self.generals[leader_id].move_receive_buffer_to_thinking_buffer())
        if not self.generals[leader_id].is_traitor:
            new_opinion = self.generals[leader_id].update_opinion_to_majority(scene)
            self.update_general_opinions(scene, [leader_id], [new_opinion])

        # Whether it's a trator or not, the leader broadcasts the decision
        scene.add_sound(random_whoosh_file(), time_offset=WHOOSH_OFFSET)
        msgs = self.broadcast_opinion(scene, [leader_id], msg_class=LeaderMessage)

        self.update_general_opinions(
            scene,
            [i for i in range(len(self.generals)) if i != leader_id],
            msgs,
        )

        if remove_leader_when_done:
            scene.play(self.set_leader(None))

        if add_background_at_the_end:
            self.set_output(scene)

    def majority_algorithm(self, scene: Scene, send_to_self: bool = True, second=False):
        anims = []
        to_remove = []

        for i in range(len(self.generals)):
            _, cur_anims, cur_to_remove = self.send_opinions_from(i, send_to_self)
            anims.append(AnimationGroup(*cur_anims))
            to_remove += cur_to_remove

        if second == False:
            for i in range(12):
                scene.add_sound(
                    random_whoosh_file(), time_offset=WHOOSH_OFFSET + 0.3 * i
                )
            scene.play(LaggedStart(*anims, lag_ratio=0.3))
        else:
            n_slow = 5
            for i in range(n_slow):
                scene.add_sound(random_whoosh_file(), time_offset=WHOOSH_OFFSET)
                scene.play(anims[i])
            for i in range(12 - n_slow):
                scene.add_sound(
                    random_whoosh_file(), time_offset=WHOOSH_OFFSET + 0.3 * i
                )
            scene.play(LaggedStart(*anims[n_slow:], lag_ratio=0.3))
        scene.remove(*to_remove)
        self.move_all_receive_buffers_to_thinking_buffers(scene)

        n_long_played = 0
        for i in range(len(self.generals)):
            if self.generals[i].is_traitor:
                continue

            new_opinion = self.generals[i].update_opinion_to_majority(
                scene, short_version=n_long_played >= 3
            )
            n_long_played += 1
            self.update_general_opinions(scene, [i], [new_opinion], with_highlight=True)

    def move_all_receive_buffers_to_thinking_buffers(self, scene: Scene):
        anims = []
        for general in self.generals:
            anims.extend(general.move_receive_buffer_to_thinking_buffer())
        scene.play(*anims)

    def full_algorithm(
        self,
        scene: Scene,
        leader_ids: List[int],
        code: Optional[CodeWithStepping],
        send_to_self: bool = True,
        early_stop: bool = False,
    ):
        def highlight_line(line_number: int):
            if code is not None:
                code.highlight_line(line_number, scene)

        for leader_id in leader_ids:
            highlight_line(0)
            scene.play(self.generals[leader_id].make_leader(self.generals))

            to_remove = []
            highlight_line(1)

            anims = []
            to_remove = []

            for i in range(len(self.generals)):
                _, cur_anims, cur_to_remove = self.send_opinions_from(i, send_to_self)
                anims.append(AnimationGroup(*cur_anims))
                to_remove += cur_to_remove

            for i in range(12):
                scene.add_sound(
                    random_whoosh_file(), time_offset=WHOOSH_OFFSET + 0.3 * i
                )
            scene.play(LaggedStart(*anims, lag_ratio=0.3))
            scene.remove(*to_remove)
            self.move_all_receive_buffers_to_thinking_buffers(scene)

            if not self.generals[leader_id].is_traitor:
                highlight_line(3)
                new_opinion = self.generals[leader_id].update_opinion_to_majority(scene)
                self.update_general_opinions(scene, [leader_id], [new_opinion])

            # Whether it's a trator or not, the leader broadcasts its updated opinion
            highlight_line(4)
            scene.add_sound(random_whoosh_file(), time_offset=WHOOSH_OFFSET)
            self.broadcast_opinion(
                scene, [leader_id], circular_send=True, msg_class=LeaderMessage
            )

            self.move_all_receive_buffers_to_thinking_buffers(scene)

            if early_stop:
                return

            highlight_line(5)
            for i in range(len(self.generals)):
                g = self.generals[i]
                if not g.is_traitor and not g.is_leader():
                    new_opinion = g.update_opinion_to_supermajority_or_leader(scene)
                    self.update_general_opinions(scene, [i], [new_opinion])

        self.set_output(scene)

    def set_opinions(self, scene: Scene, opinions: List[str]):
        lag_ratio = 0.05
        for i in range(len(self.generals)):
            scene.add_sound(random_click_file(), time_offset=lag_ratio * i)

        scene.play(
            LaggedStart(
                *[
                    general.animate.change_opinion(opinion)
                    for general, opinion in zip(self.generals, opinions)
                ],
                lag_ratio=lag_ratio,
            )
        )

    def set_output(self, scene: Scene):
        scene.play(
            AnimationGroup(
                *[
                    # Set both fill color and stroke color to match border color
                    general.icon.animate.set_fill(
                        color=general.icon.get_stroke_color(), opacity=0.2
                    )
                    for general in self.generals
                    if not general.is_traitor
                ]
            )
        )

    def set_input(self, scene: Scene):
        scene.play(
            AnimationGroup(
                *[
                    # Set both fill color and stroke color to match border color
                    general.icon.animate.set_fill(
                        color=general.icon.get_stroke_color(), opacity=0.0
                    )
                    for general in self.generals
                    if not general.is_traitor
                ]
            )
        )

    def highlight_generals_with_opinion(self, scene: Scene, opinion: str):
        scene.play(
            *[
                Indicate(
                    g.opinion_text, color=g.opinion_text.get_color(), scale_factor=1.5
                )
                for g in self.generals
                if not isinstance(g, Traitor) and g.opinion == opinion
            ],
        )

    def set_leader(self, leader_id: Optional[int]) -> Animation:
        if leader_id is not None:
            return self.generals[leader_id].make_leader(self.generals)
        else:
            for g in self.generals:
                if g.is_leader():
                    return g.remove_leader()
