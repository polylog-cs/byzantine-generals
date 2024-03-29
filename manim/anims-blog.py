# manim -pql --fps 10 -r 290,180 anims.py Polylogo
from pathlib import Path

from manim import *

from utils import util_general
from utils.chat_window import ChatMessage, ChatWindow
from utils.generals import *
from utils.util_cliparts import *
from utils.util_general import *

util_general.disable_rich_logging()


class Reduction(Scene):
    def construct(self):
        # we show 12 generals in a circle
        game = GameState([Player(with_clipart=True) for i in range(12)])
        # make the icons smaller
        for i in range(12):
            game.generals[i].clipart.scale(0.7)
        self.add(*[game.generals[i].clipart for i in range(12)])
        self.wait(2)

        shifts = [2 * RIGHT, 1 * DOWN, 1 * LEFT]
        groups = [
            Group(*[g.clipart for g in game.generals[4 * i : 4 * (i + 1)]])
            for i in range(3)
        ]

        self.play(*[groups[i].animate.shift(shifts[i]) for i in range(3)])
        self.wait(2)

        nexts = [RIGHT, LEFT, LEFT]
        mega_generals = [Player(with_clipart=True) for i in range(3)]
        for i in range(3):
            mega_generals[i].clipart.scale(1.5).next_to(groups[i], nexts[i])

        for i in range(3):
            self.play(
                Create(SurroundingRectangle(groups[i], color=RED)),
                FadeIn(mega_generals[i].clipart),
            )
            self.wait(1)


class Unwrapping(Scene):
    def construct(self):
        # Create the graph
        side_length = 3
        height = (np.sqrt(3) / 2) * side_length

        # Define new positions for an equilateral triangle layout
        equilateral_layout = {
            0: np.array([-side_length / 2, -height / 3, 0]),  # Bottom left
            1: np.array([side_length / 2, -height / 3, 0]),  # Bottom right
            2: np.array([0, 2 * height / 3, 0]),  # Top
            3: np.array([-side_length / 2, -height / 3, 0]),  # Bottom left (same as 0)
            4: np.array([side_length / 2, -height / 3, 0]),  # Bottom right (same as 1)
            5: np.array([0, 2 * height / 3, 0]),  # Top (same as 2)
        }

        graph = Graph(
            vertices=range(6),
            edges=[(i, (i + 1) % 6) for i in range(6)],
            layout="circular",
            layout_scale=3,
            vertex_config={
                "stroke_color": GRAY,
                "stroke_width": 0.1,
                "fill_color": GRAY,
                "radius": 0.1,  # Adjust the radius here to decrease the size of the vertices
            },
            edge_config={"stroke_color": GRAY},
        ).change_layout(equilateral_layout)

        # Add the graph to the scene
        self.add(graph)

        # For each vertex, create an image mobject and add an updater
        for vertex in graph.vertices:
            pla = Player(with_clipart=True, number=1 + (5 - (vertex % 3)) % 3)
            im = pla.clipart
            im.move_to(graph[vertex].get_center())
            im.add_updater(lambda mobj, v=vertex: mobj.move_to(graph[v].get_center()))
            self.add(im)
        self.play(graph.animate.shift(0.01 * LEFT), run_time=0.01)
        self.wait(2)

        self.play(graph.animate.change_layout("circular"), run_time=5)
        self.wait(2)


class Mess(Scene):
    def construct(self):
        game = GameState(
            [Player(with_clipart=True, number=1 + (i + 2) % 3) for i in range(6)]
        )
        lines = [
            Line(
                game.generals[i].icon.get_center(),
                game.generals[(i + 1) % 6].icon.get_center(),
                color=GRAY,
            )
            for i in range(6)
        ]

        self.add(game, *lines)

        for it in range(2):
            messages = []
            for i in range(6):
                messages.append(
                    MessageToSend(i, (i + 1) % 6, Message("Y", clipart=True))
                )
                messages.append(
                    MessageToSend(i, (i + 5) % 6, Message("Y", clipart=True))
                )

            game.send_messages_low_tech(self, messages, lag_ratio=0)
            self.wait(2)

        rec = SurroundingRectangle(
            Group(*[g.icon for g in game.generals[0:4]]),
            fill_opacity=1,
            fill_color=MAGENTA,
            color=MAGENTA,
        ).scale(1.1)

        trait = Traitor(with_clipart=True, number=-3).scale(1.5).next_to(game, RIGHT)
        self.play(Create(rec), FadeIn(trait))
        self.wait(2)

        for it in range(2):
            messages = []
            for i in [4, 5]:
                messages.append(
                    MessageToSend(i, (i + 1) % 6, Message("Y", clipart=True))
                )
                messages.append(
                    MessageToSend(i, (i + 5) % 6, Message("Y", clipart=True))
                )
            messages.append(MessageToSend(0, 5, Message("Y", clipart=True)))
            messages.append(MessageToSend(3, 4, Message("Y", clipart=True)))

            game.send_messages_low_tech(self, messages, lag_ratio=0)
            self.wait(2)


class Last(Scene):
    def construct(self):
        game = GameState([Player(with_clipart=True) for i in range(6)])
        lines = [
            Line(
                game.generals[i].icon.get_center(),
                game.generals[(i + 1) % 6].icon.get_center(),
                color=GRAY,
            )
            for i in range(6)
        ]

        self.add(game, *lines)
        inp = ["Y", "N", "N", "N", "Y", "Y"]
        inputs = [
            Tex(inp[i], color=BLUE)
            .scale(1)
            .align_to(game.generals[i].icon, UR)
            .shift(0.3 * UR)
            for i in range(6)
        ]
        # inputs2 = [Tex(inp[i] + r"\rightarrow " + inp[i], color = GRAY).scale(0.7).align_to(game.generals[i].icon, UR) for i in range(6)]
        self.play(*[FadeIn(inputs[i]) for i in range(6)])
        self.wait(2)

        rec = SurroundingRectangle(
            Group(game.generals[4].icon, game.generals[5].icon), color=RED
        ).scale(1.7)
        self.play(Create(rec))
        self.wait()
        self.play(
            inputs[4].animate.become(
                Tex(r"Y $\rightarrow$ Y", color=BLUE).scale(1).align_to(inputs[4], DL)
            ),
            inputs[5].animate.become(
                Tex(r"Y $\rightarrow$ Y", color=BLUE).scale(1).align_to(inputs[5], DL)
            ),
        )
        self.wait(2)

        # rec gets rotated by 50 degrees
        self.play(
            rec.animate.rotate(-4.0 / 6.0 * TAU).move_to(
                Group(game.generals[2].icon, game.generals[3].icon)
            )
        )
        self.wait()
        self.play(
            inputs[2].animate.become(
                Tex(r"N $\rightarrow$ N", color=BLUE).scale(1).align_to(inputs[2], DL)
            ),
            inputs[3].animate.become(
                Tex(r"N $\rightarrow$ N", color=BLUE).scale(1).align_to(inputs[3], DL)
            ),
        )
        self.wait(2)

        self.play(
            rec.animate.rotate(-1 / 6.0 * TAU).move_to(
                Group(game.generals[4].icon, game.generals[3].icon)
            )
        )
        self.wait()
        self.play(
            Write(Tex("?????", color=RED).scale(1.5).next_to(game, LEFT).shift(1 * UP))
        )
        self.wait(2)
