# manim -pql --fps 15 -r 290,180 anims.py Polylogo
from random import randrange
from re import I
from unittest import skip
from manim import config as global_config
from icecream import ic
from utils.util_general import *
from collections import namedtuple

from typing import Any, List

MsgType = namedtuple("MsgType", ["sender_id", "receiver_id", "message"])


class Message(Group):
    def __init__(self, message: str):
        super().__init__()
        self.message = message
        self.color = RED if message == "N" else GREEN
        self.icon = Circle(
            radius=0.05,
            color=self.color,
            stroke_width=2,
            fill_color=self.color,
            fill_opacity=1,
        )
        self.add(self.icon)


class MessageBuffer(Group):
    """
    Each general has a message buffer, which is a list of messages.
    """

    def __init__(self):
        super().__init__()
        self.messages = []
        self.icon = Rectangle(width=1, height=1, stroke_opacity=0.0).scale(0.75)
        self.add(self.icon)

    def add_msg(self, msg: Message):
        self.messages.append(msg)

    def sort_messages(self):
        # Reorganize the messages by the opinion they carry
        anims = []
        y_cnt, n_cnt = 0, 0
        for msg in self.messages:
            if msg.message == "Y":
                row = y_cnt // 2
                col = y_cnt % 2
                pos = (
                    self.get_center()
                    + 0.45 * LEFT
                    + 0.3 * UP
                    + row * 0.15 * DOWN
                    + col * 0.15 * RIGHT
                )
                y_cnt += 1
            elif msg.message == "N":
                row = n_cnt // 2
                col = n_cnt % 2
                pos = (
                    self.get_center()
                    + 0.45 * RIGHT
                    + 0.3 * UP
                    + row * 0.15 * DOWN
                    + col * 0.15 * LEFT
                )
                n_cnt += 1
            else:
                raise Exception("Invalid message")
            anims.append(msg.animate.move_to(pos))
        return anims


class General(Group):
    def __init__(self):
        super().__init__()
        self.is_leader = False

    def make_leader(self, scene: Scene):
        assert not self.is_leader
        self.is_leader = True
        self.crown = SVGMobject("img/crown.svg").scale(0.25)
        self.crown.move_to(self)
        self.crown.shift(0.8 * UP)
        scene.play(FadeIn(self.crown))

    def remove_leader(self, scene: Scene):
        assert self.is_leader
        self.is_leader = False
        scene.play(FadeOut(self.crown))

    def add_receive_buffer(self, buffer: MessageBuffer):
        self.receive_buffer = buffer
        self.add(buffer)

    def add_thinking_buffer(self, buffer: MessageBuffer):
        self.thinking_buffer = buffer
        self.add(buffer)

    def move_receive_buffer_to_thinking_buffer(self):
        # Traitors don't move their receive buffer to the thinking buffer,
        # they just discard the messages.
        if self.is_traitor:
            return [FadeOut(msg) for msg in self.receive_buffer.messages]

        receive_to_thinking = (
            self.thinking_buffer.get_center() - self.receive_buffer.get_center()
        )
        self.thinking_buffer.messages += self.receive_buffer.messages
        self.receive_buffer.messages = []
        return [
            msg.animate.shift(receive_to_thinking)
            for msg in self.thinking_buffer.messages
        ]

    def update_opinion_to_majority(self, scene: Scene):
        thinking_buffer = self.thinking_buffer
        scene.play(*thinking_buffer.sort_messages())
        msgs = thinking_buffer.messages

        opinions = [msg.message for msg in msgs]
        win = "Y" if opinions.count("Y") > opinions.count("N") else "N"

        inequality_symbol = Tex("$>$" if win == "Y" else "$\le$", color=BLACK)
        inequality_symbol.move_to(thinking_buffer.get_center())
        scene.play(FadeIn(inequality_symbol))

        new_opinion = Message(win).scale(4)
        new_opinion.move_to(inequality_symbol)

        scene.play(
            *[msg.animate.move_to(new_opinion) for msg in msgs],
            inequality_symbol.animate.become(new_opinion.icon),
        )
        self.thinking_buffer.messages = []
        scene.remove(inequality_symbol, *msgs)
        return new_opinion


class Player(General):
    def __init__(self, opinion: str = ""):
        super().__init__()
        self.opinion = opinion
        self.is_traitor = False
        self.icon = Circle(radius=0.5)
        self.opinion_text = Tex(opinion)
        self.change_opinion(opinion)
        self.add(self.opinion_text)
        self.add(self.icon)

    def get_color(self):
        return GREEN if self.opinion == "Y" else RED if self.opinion == "N" else "#333"

    def change_opinion(self, opinion: str):
        self.opinion = opinion
        color = self.get_color()

        new_opinion_text = Tex(opinion, color=color)
        new_opinion_text.move_to(self)
        self.opinion_text.become(new_opinion_text)
        self.icon.set_stroke(color=color, opacity=1)


class Traitor(General):
    def __init__(self):
        super().__init__()
        self.is_traitor = True
        color = "#333"
        self.icon = Circle(radius=0.5, color=color, fill_color=color, fill_opacity=1)
        self.add(self.icon)

    def change_opinion(self, opinion: str):
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
    def __init__(self, generals: List[General], circle_size=2.2):
        super().__init__()
        self.generals = generals
        receive_buffer_radius = circle_size - 1.1
        thinking_buffer_radius = circle_size + 1.15
        # Distribute generals in a circle
        for i in range(len(self.generals)):
            # Create the ith general
            g = self.generals[i]
            g.shift(self.circle_position(i) * circle_size)
            self.add(g)
            # Create the ith general's message buffer
            receive_buffer = MessageBuffer()
            receive_buffer.shift(self.circle_position(i) * receive_buffer_radius)
            g.add_receive_buffer(receive_buffer)
            # Create the ith general's thinking buffer
            thinking_buffer = MessageBuffer()
            thinking_buffer.shift(self.circle_position(i) * thinking_buffer_radius)
            g.add_thinking_buffer(thinking_buffer)

    def circle_position(self, i: int):
        """
        Return the position of the ith general in the circle.
        """
        x = np.cos(i * 2 * np.pi / len(self.generals))
        y = np.sin(i * 2 * np.pi / len(self.generals))
        return x * RIGHT + y * UP

    def send_messages(
        self, scene: Scene, messages: List[MsgType], circular_receive=False
    ):
        """
        Send messages from the sender to the receiver.
        If circular_receive is True, the messages are received in the receive buffer
        in the same layout as the generals are positioned in the circle.
        """
        msg_objects = []
        anims_msg_creation = []
        anims = []
        to_remove = []
        for message in messages:
            sender = self.generals[message.sender_id]
            receiver = self.generals[message.receiver_id]
            msg = Message(message.message)
            if sender.is_traitor:
                # Make the message border black if the sender is a traitor
                # to indicate that the message is not trustworthy.
                msg.icon.stroke_color = BLACK
            # Messages are sent from the sender's position to the receiver's buffer
            msg.move_to(sender.receive_buffer)

            # Make the message icon appear from the sender's icon
            sender_icon_copy = sender.icon.copy()
            sender_icon_copy.fill_color = sender_icon_copy.stroke_color
            sender_msg_copy = msg.icon.copy()
            to_remove.append(sender_icon_copy)
            to_remove.append(sender_msg_copy)
            anims_msg_creation.append(sender_icon_copy.animate.become(sender_msg_copy))

            msg_objects.append(msg)
            # Animate the message moving from the sender to the receiver.
            if circular_receive:
                # Arange the messages in the buffer in the same circle as the generals from
                # which they were sent.
                receive_location = (
                    receiver.receive_buffer.get_center()
                    + self.circle_position(message.sender_id) * 0.3
                )
            else:
                receive_location = receiver.receive_buffer.get_center()
            anims.append(msg.animate.move_to(receive_location))
            receiver.receive_buffer.add_msg(msg)
        scene.play(*anims_msg_creation)
        scene.remove(*to_remove)
        scene.add(*msg_objects)
        scene.play(*anims)
        return msg_objects

    def broadcast_opinion(
        self, scene: Scene, general_ids: int, send_to_self=False, circular_receive=False
    ):
        messages = []
        for general_id in general_ids:
            for i in range(len(self.generals)):
                if i != general_id or send_to_self:
                    messages.append(
                        MsgType(general_id, i, self.generals[general_id].opinion)
                    )
        return self.send_messages(scene, messages, circular_receive=circular_receive)

    def send_opinions_to(
        self, scene: Scene, general_id: int, send_to_self: bool = False
    ):
        messages = []
        for i in range(len(self.generals)):
            if send_to_self or i != general_id:
                messages.append(MsgType(i, general_id, self.generals[i].opinion))
        return self.send_messages(scene, messages, circular_receive=True)

    def update_general_opinions(
        self, scene: Scene, general_ids: List[int], opinions: List[Message]
    ):
        anims = []
        new_icons = []
        for general_id, opinion in zip(general_ids, opinions):
            new_icon = self.generals[general_id].icon.copy()
            if not self.generals[general_id].is_traitor:
                new_icon.color = opinion.color
            new_icons.append(new_icon)

            anims.append(
                self.generals[general_id].animate.change_opinion(opinion.message)
            )
            anims.append(opinion.icon.animate.become(new_icon))
        scene.play(*anims)
        scene.remove(*opinions, *new_icons)

    def leader_algorithm(self, scene: Scene, leader_id: int, send_to_self: bool = True):
        self.generals[leader_id].make_leader(scene)

        scene.wait(0.5)

        msgs = self.send_opinions_to(scene, leader_id, send_to_self)

        scene.wait(0.5)

        scene.play(*self.generals[leader_id].move_receive_buffer_to_thinking_buffer())
        if not self.generals[leader_id].is_traitor:
            new_opinion = self.generals[leader_id].update_opinion_to_majority(scene)
            self.update_general_opinions(scene, [leader_id], [new_opinion])

        # Whether it's a trator or not, the leader broadcasts the decision
        msgs = self.broadcast_opinion(scene, [leader_id])

        self.update_general_opinions(
            scene,
            [i for i in range(len(self.generals)) if i != leader_id],
            msgs,
        )

        self.generals[leader_id].remove_leader(scene)

    def majority_algorithm(self, scene: Scene, send_to_self: bool = True):
        for i in range(len(self.generals)):
            self.send_opinions_to(scene, i, send_to_self)
            scene.play(*self.generals[i].move_receive_buffer_to_thinking_buffer())
        for i in range(len(self.generals)):
            if self.generals[i].is_traitor:
                continue
            new_opinion = self.generals[i].update_opinion_to_majority(scene)
            self.update_general_opinions(scene, [i], [new_opinion])

    def move_all_receive_buffers_to_thinking_buffers(self, scene: Scene):
        anims = []
        for general in self.generals:
            anims.extend(general.move_receive_buffer_to_thinking_buffer())
        scene.play(*anims)

    def full_algorithm(
        self, scene: Scene, leader_ids: List[int], send_to_self: bool = True
    ):
        # v ← your initial opinion
        # For i in [1,2,3]:
        #   Send v to everybody
        #   Compute majority opinion, receive leader’s opinion
        #   if ??????
        #     v ←majority opinion
        #   else
        #     v ← leader’s opinion
        # output v

        for leader_id in leader_ids:
            self.generals[leader_id].make_leader(scene)
            for i in range(len(self.generals)):
                self.broadcast_opinion(
                    scene, [i], send_to_self=send_to_self, circular_receive=True
                )

            # self.broadcast_opinion(
            #    scene, range(len(self.generals)), circular_receive=True
            # )

            self.move_all_receive_buffers_to_thinking_buffers(scene)

            if not self.generals[leader_id].is_traitor:
                new_opinion = self.generals[leader_id].update_opinion_to_majority(scene)
                self.update_general_opinions(scene, [leader_id], [new_opinion])

            # Whether it's a trator or not, the leader broadcasts the decision
            self.broadcast_opinion(scene, [leader_id])

            for i in range(len(self.generals)):
                if not self.generals[i].is_traitor:
                    msgs = self.generals[i].thinking_buffer.sort_messages()
                    if not msgs:
                        print("No messages, general", i)
                    else:
                        scene.play(*msgs)

            self.generals[leader_id].remove_leader(scene)


class LeaderNoTraitors(Scene):
    def construct(self):
        opinions = ["Y", "N", "Y", "N", "Y", "N", "N", "Y", "N", "Y", "N", "Y"]
        game = GameState([Player() for i in range(len(opinions))])
        game.shift(2 * LEFT)
        self.add(game)

        self.wait(0.5)
        for i in range(len(game.generals)):
            if opinions[i] is not None:
                self.play(
                    game.generals[i].animate.change_opinion(opinions[i]), run_time=0.2
                )

        game.leader_algorithm(self, 1)

        self.wait(1)


class LeaderWithTraitors(Scene):
    def construct(self):
        opinions = ["Y", "N", None, "N", "Y", None, "N", "Y", "N", "Y", "N", "Y"]
        game = GameState(
            [
                Player(),
                Player(),
                CyclicOpinionTraitor("YNNY"),
                Player(),
                Player(),
                CyclicOpinionTraitor("NNYY"),
                Player(),
                Player(),
                Player(),
                Player(),
                Player(),
                Player(),
            ]
        )
        game.shift(2 * LEFT)
        self.add(game)

        self.wait(0.5)
        for i in range(len(game.generals)):
            if opinions[i] is not None:
                self.play(
                    game.generals[i].animate.change_opinion(opinions[i]), run_time=0.2
                )

        game.leader_algorithm(self, 1)

        self.wait(1)


class LeaderIsTraitor(Scene):
    def construct(self):
        opinions = ["Y", "N", None, "N", "Y", None, "N", "Y", "N", "Y", "N", "Y"]
        game = GameState(
            [
                Player(),
                Player(),
                CyclicOpinionTraitor("YNNY"),
                Player(),
                Player(),
                CyclicOpinionTraitor("NNYY"),
                Player(),
                Player(),
                Player(),
                Player(),
                Player(),
                Player(),
            ]
        )
        game.shift(2 * LEFT)
        self.add(game)

        self.wait(0.5)
        for i in range(len(game.generals)):
            if opinions[i] is not None:
                self.play(
                    game.generals[i].animate.change_opinion(opinions[i]), run_time=0.2
                )

        game.leader_algorithm(self, 2)

        self.wait(1)


class MajorityNoTraitors(Scene):
    def construct(self):
        opinions = ["Y", "N", "Y", "N", "Y", "N", "N", "Y", "N", "Y", "N", "Y"]
        game = GameState([Player() for i in range(len(opinions))])
        game.shift(2 * LEFT)
        self.add(game)

        self.wait(0.5)
        for i in range(len(game.generals)):
            if opinions[i] is not None:
                self.play(
                    game.generals[i].animate.change_opinion(opinions[i]), run_time=0.2
                )

        game.majority_algorithm(self)

        self.wait(1)


class MajorityWithTraitors(Scene):
    def construct(self):
        opinions = ["Y", "N", None, "N", "Y", None, "N", "Y", "N", "Y", "N", "Y"]
        game = GameState(
            [
                Player(),
                Player(),
                CyclicOpinionTraitor("YNNY"),
                Player(),
                Player(),
                CyclicOpinionTraitor("NNYY"),
                Player(),
                Player(),
                Player(),
                Player(),
                Player(),
                Player(),
            ]
        )
        game.shift(2 * LEFT)
        self.add(game)

        self.wait(0.5)
        for i in range(len(game.generals)):
            if opinions[i] is not None:
                self.play(
                    game.generals[i].animate.change_opinion(opinions[i]), run_time=0.2
                )

        game.majority_algorithm(self)

        self.wait(1)


class FullWithTraitors(Scene):
    def construct(self):
        opinions = ["Y", "N", None, "N", "Y", None, "N", "Y", "N", "Y", "N", "Y"]
        game = GameState(
            [
                Player(),
                Player(),
                CyclicOpinionTraitor("YNNY"),
                Player(),
                Player(),
                CyclicOpinionTraitor("NNYY"),
                Player(),
                Player(),
                Player(),
                Player(),
                Player(),
                Player(),
            ]
        )
        game.shift(2 * LEFT)
        self.add(game)

        self.wait(0.5)
        for i in range(len(game.generals)):
            if opinions[i] is not None:
                self.play(
                    game.generals[i].animate.change_opinion(opinions[i]), run_time=0.2
                )

        game.full_algorithm(self, leader_ids=[2, 4, 5], send_to_self=True)

        self.wait(1)


class Polylogo(Scene):
    def construct(self):
        default()
        authors = Tex(
            r"\textbf{Richard Hladík, Filip Hlásek, Václav Rozhoň, Václav Volhejn}",
            color=text_color,
            font_size=40,
        ).shift(3 * DOWN + 0 * LEFT)

        channel_name = Tex(r"polylog", color=text_color)
        channel_name.scale(4).shift(1 * UP)
        channel_name_without_o = Tex(r"p\hskip 5.28pt lylog", color=text_color)
        channel_name_without_o.scale(4).shift(1 * UP)

        logo_solarized = (
            SVGMobject("img/logo-solarized.svg")
            .scale(0.55)
            .move_to(2 * LEFT + 0.95 * UP + 0.49 * RIGHT)
        )
        self.play(
            Write(authors),
            Write(channel_name),
        )
        self.play(FadeIn(logo_solarized))
        self.add(channel_name_without_o)
        self.remove(channel_name)

        self.wait()

        self.play(*[FadeOut(o) for o in self.mobjects])
        self.wait()


class Explore(Scene):
    def construct(self):
        pass
