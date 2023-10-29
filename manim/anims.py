# manim -pql --fps 15 -r 290,180 anims.py Polylogo
from random import randrange
from re import I
from unittest import skip
from manim import config as global_config
from icecream import ic
from utils.util_general import *
from collections import namedtuple

from typing import Any, List


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


class Player(General):
    def __init__(self, opinion: str = ""):
        super().__init__()
        self.opinion = opinion
        self.is_traitor = False
        self.icon = Circle(radius=0.5)
        self.icon.set_stroke(color=self.get_color(), opacity=1)
        self.opinion_text = Tex(opinion, color=self.get_color())
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
        self.message_objects = []
        self.icon = Rectangle(width=1, height=1, stroke_opacity=0.0).scale(0.75)
        self.add(self.icon)


class GameState(Group):
    def __init__(self, generals: List[General], circle_size=3):
        super().__init__()
        self.generals = generals
        self.receive_buffers = []
        self.thinking_buffers = []
        receive_buffer_radius = circle_size - 1.1
        thinking_buffer_radius = circle_size + 1.3
        # Distribute generals in a circle
        for i in range(len(self.generals)):
            # Create the ith general
            g = self.generals[i]
            g.shift(self.circle_position(i) * circle_size)
            self.add(g)
            # Create the ith general's message buffer
            receive_buffer = MessageBuffer()
            receive_buffer.shift(self.circle_position(i) * receive_buffer_radius)
            self.receive_buffers.append(receive_buffer)
            self.add(receive_buffer)
            # Create the ith general's thinking buffer
            thinking_buffer = MessageBuffer()
            thinking_buffer.shift(self.circle_position(i) * thinking_buffer_radius)
            self.thinking_buffers.append(thinking_buffer)
            self.add(thinking_buffer)

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
        anims = []
        for message in messages:
            sender = self.generals[message.sender_id]
            msg = Message(message.message)
            if sender.is_traitor:
                # Make the message border black if the sender is a traitor
                # to indicate that the message is not trustworthy.
                msg.icon.stroke_color = BLACK
            # Messages are sent from the sender's position to the receiver's buffer
            msg.move_to(self.receive_buffers[message.sender_id])
            msg_objects.append(msg)
            # Animate the message moving from the sender to the receiver.
            if circular_receive:
                # Arange the messages in the buffer in the same circle as the generals from
                # which they were sent.
                receive_location = (
                    self.receive_buffers[message.receiver_id].get_center()
                    + self.circle_position(message.sender_id) * 0.3
                )
            else:
                receive_location = self.receive_buffers[
                    message.receiver_id
                ].get_center()
            anims.append(msg.animate.move_to(receive_location))
        scene.add(*msg_objects)
        scene.play(*anims)
        return msg_objects

    def broadcast_opinion(self, scene: Scene, general_ids: int):
        messages = []
        for general_id in general_ids:
            for i in range(len(self.generals)):
                if i != general_id:
                    messages.append(
                        MsgType(general_id, i, self.generals[general_id].opinion)
                    )
        return self.send_messages(scene, messages)

    def send_opinions_to(self, scene: Scene, general_id: int):
        messages = []
        for i in range(len(self.generals)):
            if i != general_id:
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

    def leader_algorithm(self, scene: Scene, leader_id: int):
        self.generals[leader_id].make_leader(scene)

        scene.wait(1)

        msgs = self.send_opinions_to(scene, leader_id)

        scene.wait(1)
        receive_buffer = self.receive_buffers[leader_id]
        thinking_buffer = self.thinking_buffers[leader_id]

        # Move all the messages to the thinking buffer
        receive_to_thinking = thinking_buffer.get_center() - receive_buffer.get_center()
        scene.play(*[msg.animate.shift(receive_to_thinking) for msg in msgs])

        scene.wait(1)

        # Reorganize the messages by the opinion they carry
        anims = []
        y_cnt, n_cnt = 0, 0
        for msg in msgs:
            if msg.message == "Y":
                row = y_cnt % 4
                col = y_cnt // 4
                pos = (
                    thinking_buffer.get_center()
                    + 0.45 * LEFT
                    + 0.3 * UP
                    + row * 0.15 * DOWN
                    + col * 0.15 * RIGHT
                )
                y_cnt += 1
            elif msg.message == "N":
                row = n_cnt % 4
                col = n_cnt // 4
                pos = (
                    thinking_buffer.get_center()
                    + 0.45 * RIGHT
                    + 0.3 * UP
                    + row * 0.15 * DOWN
                    + col * 0.15 * LEFT
                )
                n_cnt += 1
            else:
                raise Exception("Invalid message")
            anims.append(msg.animate.move_to(pos))
        scene.play(*anims)

        win = "Y" if y_cnt > n_cnt else "N"

        inequality_symbol = Tex("$>$" if win == "Y" else "$\le$", color=BLACK)
        inequality_symbol.move_to(thinking_buffer.get_center())
        scene.play(FadeIn(inequality_symbol))

        new_opinion = Message(win).scale(4)
        new_opinion.move_to(inequality_symbol)

        scene.play(
            *[msg.animate.move_to(new_opinion) for msg in msgs],
            inequality_symbol.animate.become(new_opinion.icon),
        )
        scene.remove(inequality_symbol, *msgs)

        self.update_general_opinions(scene, [leader_id], [new_opinion])

        msgs = self.broadcast_opinion(scene, [leader_id])

        self.update_general_opinions(
            scene,
            [i for i in range(len(self.generals)) if i != leader_id],
            msgs,
        )

        self.generals[leader_id].remove_leader(scene)


class GameScene(Scene):
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
        self.play(game.generals[3].animate.change_opinion("N"))

        game.leader_algorithm(self, 1)

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
