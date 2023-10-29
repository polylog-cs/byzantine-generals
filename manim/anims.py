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
        self.crown.shift(0.75 * UP)
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
        self.icon = Rectangle(width=1, height=1)
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
        self.icon = Rectangle(
            width=1, height=1, color=color, fill_color=color, fill_opacity=1
        )
        self.add(self.icon)


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
            radius=0.2, color=self.color, fill_color=self.color, fill_opacity=1
        )
        self.add(self.icon)


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
        return self.send_messages(scene, messages)


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
        self.wait(0.5)

        msgs = game.send_messages(
            self, [MsgType(3, 5, "Y"), MsgType(7, 11, "N"), MsgType(9, 2, "N")]
        )
        self.remove(*msgs)

        self.wait(0.5)

        msgs = game.broadcast_opinion(self, [0, 3])
        self.remove(*msgs)

        self.wait(1)

        game.generals[2].make_leader(self)

        self.wait(1)

        msgs = game.send_opinions_to(self, 2)
        self.remove(*msgs)

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
