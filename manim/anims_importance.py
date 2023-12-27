import collections
from manim import *
import numpy as np

from utils import util_general


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
