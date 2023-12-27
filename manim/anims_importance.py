import collections
from manim import *
import numpy as np
from utils.generals import General, Player
from utils.chat_window import ChatMessage, ChatWindow
from utils import util_general


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
        self.chat_window = None

    def set_chat_window(self, chat_window: ChatWindow):
        if self.chat_window is not None:
            self.remove(self.chat_window)

        self.chat_window = chat_window
        self.add(chat_window)


class BlockchainGroupChat(Scene):
    def construct(self):
        coef = 2.6
        player_locations = [
            (x * coef - 3, y * coef) for x, y in [(-1, 1), (1, 1), (1, -1), (-1, -1)]
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
        players[0].make_leader(self)

        messages_to_add = [
            ChatMessage("General #1", "Livvy rizzed up baby Gronk", tail_up=True)
            .next_to(players[1], direction=DOWN + RIGHT)
            .shift(LEFT),
            ChatMessage("General #2", "He might be the new rizz king")
            .next_to(players[2], direction=UP + RIGHT)
            .shift(LEFT),
        ]

        for message in messages_to_add:
            self.play(FadeIn(message))

            last_message = players[0].chat_window.add_message(
                message.sender,
                message.message,
                action="nothing",
                background_color=util_general.BASE01,
            )

            self.play(message.animate.become(last_message))

            # Since we created `last_message` but didn't actually add it to the group,
            # add it manually here. This is needed so that the next message is put
            # under this one etc.
            players[0].chat_window.displayed_messages.add(message)

        self.wait(1)
