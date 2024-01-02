import collections
from typing import Optional

import numpy as np
from manim import *

from utils import util_general
from utils.blockchain import BlockchainState
from utils.chat_window import ChatMessage, ChatWindow
from utils.generals import Player, Traitor

util_general.disable_rich_logging()


class ComputerVertex(Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add(SVGMobject("img/server.svg").scale(0.4))


def get_example_graph():
    rng = np.random.default_rng(16)  # also try: 2
    n = 20
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < 0.25:
                edges.append((i, j))

    vertices = set(v for edge in edges for v in edge)

    graph = Graph(
        vertices,
        edges,
        layout="kamada_kawai",
        vertex_type=ComputerVertex,
        layout_scale=4.5,
    )

    return graph


class SendMessage(Animation):
    def __init__(self, dot: Dot, start, end, **kwargs) -> None:
        # Pass number as the mobject of the animation
        super().__init__(dot, **kwargs)
        # Set start and end
        self.start = start
        self.end = end

    def interpolate_mobject(self, alpha: float) -> None:
        # Set value of DecimalNumber according to alpha
        # value = self.start + (alpha * (self.end - self.start))
        # self.mobject.set_value(value)
        alpha = rate_functions.ease_in_out_sine(alpha)
        opacity = rate_functions.there_and_back(alpha)
        self.mobject.move_to(self.start + alpha * (self.end - self.start))
        self.mobject.set_opacity(opacity)


def play_message_animations(scene: Scene, graph: Graph, n: int, fraction_fire: float):
    rng = np.random.default_rng(16)

    fires = {k: None for k in graph.vertices.keys()}
    # Remove fires in the order they were created to avoid fires "flashing" only for a few frames
    fire_queue = collections.deque()

    animations = []

    toggle_every_n = round(1 / fraction_fire) if fraction_fire > 0 else int(1e9)
    for i in range(n):
        toggle_fire = i > 0 and i % toggle_every_n == 0

        if toggle_fire:
            create_fire = (
                rng.random() < 0.5
                or i < n // 3  # Always create fires at the beginning
                or all(f is None for f in fires.values())  # No fires, can't remove
            )

            if create_fire:
                v = rng.choice(
                    [k for k, fire in fires.items() if fire is None], size=1
                )[0]
                center = graph.vertices[v].get_center()
                fires[v] = (
                    ImageMobject("img/fire_apple_emoji.png").scale(0.8).move_to(center)
                )
                fire_queue.append(v)
                animations.append(GrowFromCenter(fires[v]))
            else:
                v = fire_queue.popleft()
                animations.append(ShrinkToCenter(fires[v]))
                fires[v] = None

        else:
            if sum(f is None for f in fires.values()) < 2:
                raise ValueError("Not enough computers are ok")

            while True:
                v1, v2 = rng.choice(list(graph.edges.keys()), size=1)[0]

                # Only send messages between computers that are ok
                if fires[v1] is None and fires[v2] is None:
                    break

            if rng.random() < 0.5:
                v1, v2 = v2, v1

            dot = Dot(color=util_general.BLUE, fill_opacity=0).move_to(
                graph[v1].get_center()
            )
            scene.add(dot)

            animation = SendMessage(dot, graph[v1].get_center(), graph[v2].get_center())
            animations.append(animation)

    lag_ratio = 0.1

    # TODO(vv): Just putting everything into a single LaggedStart causes weird behavior.
    #   The fires don't appear and disappear in the right order. I don't know why.
    group = []
    for animation in animations:
        group.append(animation)
        if not isinstance(animation, SendMessage):
            # Flush the group
            scene.play(LaggedStart(*group, lag_ratio=lag_ratio))
            group = []

    if group:
        scene.play(LaggedStart(*group, lag_ratio=lag_ratio))


class NetworkMessages(Scene):
    def construct(self):
        util_general.default()

        graph = get_example_graph()
        self.add(graph)
        play_message_animations(self, graph, n=100, fraction_fire=0.0)

        self.wait(1)


class NetworkMessagesWithFires(Scene):
    def construct(self):
        util_general.default()

        graph = get_example_graph()
        self.add(graph)
        play_message_animations(self, graph, n=100, fraction_fire=0.1)

        self.wait(1)


class BlockchainGroupChat(Scene):
    def construct(self):
        util_general.default()

        message_pairs = [
            ("General #2", "OK guys let’s vote, I vote YES"),
            ("General #4", "sounds good, I vote YES"),
            ("General #7", "I vote NO"),
        ]

        chat = ChatWindow()

        for pair in message_pairs:
            chat.add_message(pair[0], pair[1], action="add")
            # self.play()
            # self.wait()
        self.add(chat)
        self.wait(1)

        state = BlockchainState(chat)

        self.remove(chat)
        self.play(FadeIn(*state.players), *state.creation_animations)
        self.wait(1)

        messages_per_round = [
            [
                state.make_message_from_general(1, "Livvy rizzed up baby Gronk"),
                state.make_message_from_general(2, "He might be the new rizz king"),
            ],
            # Different #messages in each round to show that it doesn't always have
            # to be a fixed number (do we want this?)
            [
                state.make_message_from_general(1, "Foo"),
                state.make_message_from_general(3, "Bar"),
                state.make_message_from_general(0, "Baz"),
            ],
            [
                state.make_message_from_general(1, "Quux"),
            ],
        ]

        for leader_id, messages_to_add in zip(range(3), messages_per_round):
            state.make_leader(leader_id, self)

            for message in messages_to_add:
                self.play(FadeIn(message))

            self.play(
                state.players[leader_id].chat_window.copy_messages(
                    messages_to_add,
                    background_color=util_general.BASE01,
                    keep_original=False,
                )
            )
            self.wait(1)

            state.send_block_to_other_players(messages_to_add, self)


class ElectronicSignature(Scene):
    def construct(self):
        util_general.default()

        player1 = Player(with_icon=True).shift(LEFT * 4 + UP * 2)
        player2 = Traitor(with_icon=True).shift(LEFT * 4 + DOWN * 2)
        self.add(player1, player2)

        message = (
            ChatMessage(
                sender="General #1",
                message="felt cute, might delete later",
                with_verification=True,
            )
            .scale(1.3)
            .next_to(player1, direction=RIGHT)
        )
        # Copy the header but keep the original position so that we can later
        # .become() it
        header_group_unmoved = message.pop_header_group()
        header_group = header_group_unmoved.copy()

        header_group.next_to(player1, direction=DOWN)
        header_group.submobjects[0].set_fill(util_general.BASE00)

        self.play(FadeIn(message))
        self.play(FadeIn(header_group))
        self.play(header_group.animate.become(header_group_unmoved))

        self.wait()

        # Traitors can't fake signatures

        message2 = (
            ChatMessage(
                sender="General #1",
                message="I hate spinach",  # TODO: better text?
                with_verification=True,
            )
            .scale(1.3)
            .next_to(player2, direction=RIGHT)
        )
        header_group_unmoved = message2.header_group.copy()
        header_group = message2.header_group
        message2.text_group.remove(message2.header_group)

        header_group.next_to(player2, direction=DOWN)
        header_group.submobjects[0].set_fill(util_general.BASE00)

        self.play(FadeIn(message2))
        self.play(FadeIn(header_group))
        self.play(header_group.animate.become(header_group_unmoved))

        self.wait()
        self.play(Create(Cross(header_group, color=util_general.RED)))
        self.play(
            Write(Text("Can't pretend to be somebody else", color=util_general.RED))
        )

        self.wait()


class TraitorGroupChat(Scene):
    def construct(self):
        util_general.default()

        message_pairs = [
            ("General #2", "OK guys let’s vote, I vote YES"),
            ("General #4", "sounds good, I vote YES"),
            ("General #7", "I vote NO"),
        ]

        chat = ChatWindow()

        for pair in message_pairs:
            chat.add_message(pair[0], pair[1], action="add")

        self.add(chat)
        self.wait(1)

        state = BlockchainState(chat)

        self.remove(chat)
        self.play(FadeIn(*state.players), *state.creation_animations)
        self.wait(1)

        messages_per_round = [
            [
                state.make_message_from_general(
                    0, "Totally real message", alleged_general_id=1
                ),
                state.make_message_from_general(2, "He might be the new rizz king"),
            ],
        ]

        # vv: This for loop is unnecessary here, but keeping it now in case
        # we want more rounds later
        for leader_id, messages_to_add in enumerate(messages_per_round):
            state.make_leader(leader_id, self)

            for message in messages_to_add:
                self.play(FadeIn(message))

            fake_message_header = messages_to_add[0].header_group
            rectangle = SurroundingRectangle(
                fake_message_header, color=util_general.RED
            )
            self.play(Create(rectangle))
            self.wait()
            self.play(Uncreate(rectangle))

            verifications = [message.add_verification() for message in messages_to_add]

            self.play(*[FadeIn(verification) for verification in verifications])
            self.wait()

            failed_text = Text("Failed verification", color=util_general.RED)
            failed_text.next_to(messages_to_add[0], direction=DOWN).shift(LEFT)

            self.play(
                Create(failed_text),
                verifications[0].animate.set_color(util_general.RED),
                Create(
                    Arrow(
                        failed_text.get_center(),
                        verifications[0].get_center(),
                        color=util_general.RED,
                    )
                ),
            )
            self.wait()
