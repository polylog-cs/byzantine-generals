import collections
from typing import Optional

import numpy as np
from manim import *

from utils import util_general
from utils.chat_window import ChatMessage, ChatWindow
from utils.generals import Player

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


class BlockchainPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, with_icon=True, **kwargs)
        self.chat_window: Optional[ChatWindow] = None

    def set_chat_window(self, chat_window: ChatWindow):
        if self.chat_window is not None:
            self.remove(self.chat_window)

        self.chat_window = chat_window
        self.add(chat_window)


class BlockchainGroupChat(Scene):
    def construct(self):
        coef = 2.3
        player_locations = [
            (x * coef - 3, y * coef - 0.5)
            for x, y in [(-1, 1), (1, 1), (1, -1), (-1, -1)]
        ]

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

        animations = []
        players: list[BlockchainPlayer] = []

        for x, y in player_locations:
            player = BlockchainPlayer().shift(x * RIGHT + y * UP)
            players.append(player)
            chat_window = chat.copy()
            chat_window_scale = 0.3
            animations.append(
                chat_window.animate.shift((x + 1.5) * RIGHT + y * UP).scale(
                    chat_window_scale
                )
            )
            chat_window.messages_scale *= chat_window_scale
            player.chat_window = chat_window

        self.remove(chat)
        self.play(FadeIn(*players), *animations)
        self.wait(1)

        def make_message_from_general(general_id: int, message: str):
            assert general_id in [0, 1, 2, 3]
            general_data = [
                {
                    "tail_up": True,
                    "next_to_direction": DOWN + RIGHT,
                    "shift": LEFT * 0.8 + UP * 0.4,
                },
                {
                    "tail_up": True,
                    "next_to_direction": DOWN + RIGHT,
                    "shift": LEFT * 0.8 + UP * 0.4,
                },
                {
                    "tail_up": False,
                    "next_to_direction": UP + RIGHT,
                    "shift": LEFT * 0.8,
                },
                {
                    "tail_up": False,
                    "next_to_direction": UP + RIGHT,
                    "shift": LEFT * 0.8,
                },
            ][general_id]

            message = ChatMessage(
                f"General #{general_id+1}",
                message,
                tail_up=general_id in [0, 1],
            )
            message.next_to(
                players[general_id], direction=general_data["next_to_direction"]
            ).shift(general_data["shift"])

            return message

        messages_per_round = [
            [
                make_message_from_general(1, "Livvy rizzed up baby Gronk"),
                make_message_from_general(2, "He might be the new rizz king"),
            ],
            # Different #messages in each round to show that it doesn't always have
            # to be a fixed number (do we want this?)
            [
                make_message_from_general(1, "Foo"),
                make_message_from_general(3, "Bar"),
                make_message_from_general(0, "Baz"),
            ],
            [
                make_message_from_general(1, "Quux"),
            ],
        ]

        for leader_id, messages_to_add in zip(range(3), messages_per_round):
            self.play(players[leader_id].make_leader(generals=players))

            for message in messages_to_add:
                self.play(FadeIn(message))

            self.play(
                players[leader_id].chat_window.copy_messages(
                    messages_to_add,
                    background_color=util_general.BASE01,
                    keep_original=False,
                )
            )
            self.wait(1)

            # Copy the new messages from the leader to the other players
            self.play(
                LaggedStart(
                    *[
                        players[i].chat_window.copy_messages(
                            messages_to_add, keep_original=True
                        )
                        for i in range(4)
                        if i != leader_id
                    ],
                    lag_ratio=0.5,
                )
            )

            # Set the background colors of the newly-added messages back to the standard one
            color_change_animations = []
            for player_id in range(len(players)):
                for i in range(len(messages_to_add)):
                    # I tried wrapping this into a method of ChatMessage but that lead to the
                    # message's text disappearing behind the bubble... why??
                    message = players[player_id].chat_window.all_messages[-i - 1]
                    color_change_animations.append(
                        message.bubble.animate.set_fill_color(util_general.BASE02)
                    )
                    color_change_animations.append(
                        message.tail.animate.set_fill_color(util_general.BASE02)
                    )

            self.play(*color_change_animations)
            self.wait(1)
