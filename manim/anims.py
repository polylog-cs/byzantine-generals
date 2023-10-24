# manim -pql --fps 15 -r 290,180 anims.py Polylogo
from random import randrange
from re import I
from unittest import skip
from manim import config as global_config
from icecream import ic
from utils.util_general import *
from collections import namedtuple

from typing import List


class General(Group):
    def __init__(self):
        super().__init__()
        self.is_leader = False

    def make_leader(self, scene: Scene):
        assert not self.is_leader
        self.is_leader = True
        self.crown = SVGMobject("img/crown.svg").scale(0.25)
        self.crown.move_to(self)
        self.crown.shift(0.75 * UP)
        scene.play(FadeIn(self.crown))

    def remove_leader(self, scene: Scene):
        assert self.is_leader
        self.is_leader = False
        scene.play(FadeOut(self.crown))


class Player(General):
    def __init__(self, opinion: str):
        super().__init__()
        self.opinion = opinion
        self.is_traitor = False
        self.icon = Rectangle(width=1, height=1, color=GREEN)
        self.opinion_text = Tex(opinion, color=GREEN)
        self.add(self.icon)
        self.add(self.opinion_text)

    def change_opinion(self, opinion: str):
        self.opinion = opinion
        new_opinion_text = Tex(opinion, color=GREEN)
        new_opinion_text.move_to(self.opinion_text)
        self.opinion_text.become(new_opinion_text)


class Traitor(General):
    def __init__(self):
        super().__init__()
        self.is_traitor = True
        self.icon = Rectangle(width=1, height=1, color=RED)
        self.add(self.icon)


MsgType = namedtuple("MsgType", ["sender_id", "receiver_id", "message"])


class Message(Group):
    def __init__(self, message: str):
        super().__init__()
        self.message = message
        self.box = Rectangle(width=1, height=1, color=ORANGE).scale(0.5)
        self.message_text = Tex(message, color=ORANGE)
        self.add(self.box, self.message_text)


class GameState(Group):
    def __init__(self, generals: List[General], circle_size=3):
        super().__init__()
        self.generals = generals
        # Distribute generals in a circle
        for i in range(len(self.generals)):
            g = self.generals[i]
            x = np.cos(i * 2 * np.pi / len(self.generals))
            y = np.sin(i * 2 * np.pi / len(self.generals))
            g.shift(x * RIGHT * circle_size + y * UP * circle_size)
            self.add(g)

    def send_messages(self, scene: Scene, messages: List[MsgType]):
        msg_objects = []
        for message in messages:
            msg = Message(message.message)
            msg.move_to(self.generals[message.sender_id])
            msg_objects.append(msg)
        scene.add(*msg_objects)
        scene.play(
            *[
                msg_objects[i].animate.move_to(self.generals[messages[i].receiver_id])
                for i in range(len(msg_objects))
            ]
        )
        scene.remove(*msg_objects)


class GameScene(Scene):
    def construct(self):
        game = GameState(
            [
                Player("Y"),
                Player("N"),
                Traitor(),
                Player("N"),
                Player("Y"),
                Traitor(),
                Player("N"),
                Player("Y"),
                Player("N"),
                Player("Y"),
                Player("N"),
                Player("Y"),
            ]
        )
        game.shift(2 * LEFT)
        self.add(game)

        self.wait(0.5)
        self.play(game.generals[3].animate.change_opinion("Y"))
        self.wait(0.5)

        game.send_messages(
            self, [MsgType(3, 4, "Y"), MsgType(3, 5, "Y"), MsgType(3, 6, "Y")]
        )

        self.wait(1)

        game.generals[2].make_leader(self)

        self.wait(1)

        game.generals[2].remove_leader(self)

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
