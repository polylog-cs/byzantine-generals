import collections
import itertools
from typing import Optional

import numpy as np
from manim import *

from utils import util_general
from utils.blockchain import BlockchainPlayer, BlockchainState
from utils.chat_window import ChatMessage, ChatWindow
from utils.generals import *
from utils.generals import Player, Traitor
from utils.util_general import *

util_general.disable_rich_logging()


class ComputerVertex(Group):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add(ImageMobject("img/server.png").scale(0.17))


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
        edge_config={"stroke_color": BASE1},
    )

    return graph


# TODO(vv): unify with the SendMessage class?
class SendNetworkMessage(Animation):
    def __init__(self, mobject: Mobject, start, end, **kwargs) -> None:
        # Pass number as the mobject of the animation
        super().__init__(mobject, **kwargs)
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

    fire_is = []
    toggle_every_n = round(1 / fraction_fire) if fraction_fire > 0 else int(1e9)
    for i in range(n):
        toggle_fire = i > 0 and i % toggle_every_n == 0

        if toggle_fire:
            create_fire = (
                rng.random() < 0.4
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
                fire_is.append(i)
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

            animation = SendNetworkMessage(
                dot, graph[v1].get_center(), graph[v2].get_center()
            )
            animations.append(animation)

    lag_ratio = 0.1

    def flush(group: List[Animation]):
        # Sounds of messages being sent
        for i in range(len(group)):
            scene.add_sound(get_sound_effect("click"), time_offset=i * lag_ratio)

        if isinstance(animation, GrowFromCenter):  # A computer is catching fire
            scene.add_sound(
                get_sound_effect("explosion"),
                time_offset=len(group) * lag_ratio,
                gain=-6,
            )

        scene.play(LaggedStart(*group, lag_ratio=lag_ratio))

    # TODO(vv): Just putting everything into a single LaggedStart causes weird behavior.
    #   The fires don't appear and disappear in the right order. I don't know why.
    group = []
    for animation in animations:
        group.append(animation)
        if not isinstance(animation, SendNetworkMessage):
            flush(group)
            group = []

    if group:
        flush(group)


class NetworkMessages(Scene):
    def construct(self):
        util_general.default()

        graph = get_example_graph()
        self.add(graph)
        play_message_animations(self, graph, n=100, fraction_fire=0.0)

        self.wait(1)

        calculation_tex = Tex(
            r"{{$1$ failure per 10 years \;\;}}{{$\times$\;\; $10^6$ computers \;\;}}{{= \;\;$1$ failure per $5$ minutes}}",
            color=TEXT_COLOR,
        ).scale(0.9)
        calculation_rec = SurroundingRectangle(
            calculation_tex,
            color=BACKGROUND_COLOR,
            fill_color=BACKGROUND_COLOR,
            fill_opacity=1.0,
            buff=0.5,
        )
        calculation_group = VGroup(calculation_rec, calculation_tex).to_edge(UP)

        self.play(FadeIn(calculation_rec))
        self.wait()
        self.play(Write(calculation_tex[0]))
        self.wait()
        self.play(Write(calculation_tex[1]))
        self.wait()
        self.play(Write(calculation_tex[2]))
        self.wait()


class JeffDean(Scene):
    def construct(self):
        quote_text = r"""\raggedright
        In each cluster's first year, it's typical that 1,000 individual machine failures will occur;
        thousands of hard drive failures will occur; one power distribution unit will fail, bringing down
        500 to 1,000 machines for about 6 hours; 20 racks will fail, each time causing 40 to 80 machines
        to vanish from the network; 5 racks will "go wonky," with half their network packets missing in action;
        and the cluster will have to be rewired once, affecting 5 percent of the machines at any given moment
        over a 2-day span. And there's about a 50 percent chance that the cluster will overheat, taking down
        most of the servers in less than 5 minutes and taking 1 to 2 days to recover.
        """

        quote = Tex(quote_text, color=text_color).scale(0.8).to_edge(UP)
        jeff = (
            Tex("Jeff Dean, Alphabet's (Google) chief scientist", color=text_color)
            .scale(0.8)
            .next_to(quote, direction=DOWN, buff=0.5)
            .align_to(quote, RIGHT)
            .shift(1 * DOWN)
        )
        cit = (
            Tex(
                "news.com, 2008 (the reference is old since this info is usually not public)",
                color=text_color,
            )
            .scale(0.4)
            .next_to(jeff, direction=DOWN, buff=0.25)
            .align_to(jeff, LEFT)
        )
        jeff_pic = (
            ImageMobject("img/jeff.jpg")
            .scale_to_fit_height(2)
            .next_to(jeff, direction=LEFT, buff=0.5)
            .align_to(jeff, UP)
            .shift(1 * UP)
        )
        self.add(quote, jeff, jeff_pic, cit)


class NetworkMessagesWithFires(Scene):
    def construct(self):
        util_general.default()

        graph = get_example_graph()
        self.add(graph)
        play_message_animations(self, graph, n=100, fraction_fire=0.1)

        self.wait(1)


class GoogleDoc(Scene):
    def construct(self):
        util_general.default()

        graph = get_example_graph()
        self.add(graph)

        # for vertex in graph.vertices:
        #     index_label = Text(str(vertex), color=PINK).scale(2)
        #     index_label.move_to(graph.vertices[vertex].get_center())
        #     graph.add(index_label)

        servers = [2, 8, 1, 10, 5]
        shifts = {
            2: 1 * LEFT,
            8: 1 * LEFT,
            1: 1 * RIGHT + 0.5 * UP,
            10: 1 * RIGHT + 0.5 * UP,
            5: 1 * RIGHT,
        }
        datas1 = []
        datas2 = []
        for i in servers:
            sc = 0.7
            data1 = Tex("Edit A", color=BLUE).scale(sc)
            data2 = Tex("Edit B", color=RED).scale(sc)
            if i in [2, 8]:
                VGroup(data1, data2).arrange_in_grid(
                    cols=1, cell_alignment=LEFT, buff=0.1
                ).move_to(graph.vertices[i].get_center() + shifts[i])
            else:
                VGroup(data2, data1).arrange_in_grid(
                    cols=1, cell_alignment=LEFT, buff=0.1
                ).move_to(graph.vertices[i].get_center() + shifts[i])
            datas1.append(data1)
            datas2.append(data2)

        self.play(
            LaggedStart(
                *[
                    FadeIn(SurroundingRectangle(graph.vertices[i], color=RED))
                    for i in shifts.keys()
                ],
                lag_ratio=0.5,
            )
        )
        self.wait()

        figure1 = (
            ImageMobject("img/person_icon.png")
            .scale_to_fit_height(1.5)
            .to_corner(DL, buff=1)
        )
        figure2 = (
            ImageMobject("img/person_icon.png")
            .scale_to_fit_height(1.5)
            .to_corner(DR, buff=1)
        )
        col = graph.edges[list(graph.edges.keys())[0]].get_color()

        edge1 = Line(figure1.get_center(), graph.vertices[11].get_center(), color=col)
        edge2 = Line(figure2.get_center(), graph.vertices[19].get_center(), color=col)

        self.play(
            LaggedStart(
                FadeIn(Group(edge1, figure1)),
                FadeIn(Group(edge2, figure2)),
                lag_ratio=0.5,
            )
        )
        self.wait()

        r = 0.1
        messages1 = [
            Circle(radius=r, color=BLUE, fill_opacity=1).move_to(figure1)
            for _ in range(5)
        ]
        messages2 = [
            Circle(radius=r, color=RED, fill_opacity=1).move_to(figure2)
            for _ in range(5)
        ]

        paths1 = [
            [11, 2],
            [11, 8],
            [11, 15, 17, 1],
            [11, 0, 3, 10],
            [11, 15, 17, 16, 5],
        ]
        paths2 = [
            [19, 17, 7, 2],
            [19, 16, 3, 8],
            [19, 16, 1],
            [19, 16, 5, 10],
            [19, 16, 5],
        ]

        uz1 = set()
        uz2 = set()
        for t in range(10):
            anims = []
            for messages, paths, uz, datas in zip(
                [messages1, messages2], [paths1, paths2], [uz1, uz2], [datas1, datas2]
            ):
                for i in range(5):
                    if t < len(paths[i]):
                        anims.append(
                            AnimationGroup(
                                messages[i].animate.move_to(
                                    graph.vertices[paths[i][t]]
                                ),
                                rate_func=linear,
                            )
                        )
                    elif len(paths[i]) == t:
                        anims.append(FadeOut(messages[i]))
                        if i not in uz:
                            anims.append(FadeIn(datas[i]))
                            uz.add(i)
            if anims == []:
                break
            self.play(*anims)
            if t < 5:
                self.add_sound(get_sound_effect("click"), time_offset=-0.2)
            # self.wait(0.5)

        self.play(
            *[Indicate(d, color=BLUE) for d in datas1[:2]],
        )
        self.wait()
        self.play(
            *[Indicate(d, color=RED) for d in datas2[2:]],
        )
        self.wait()

        play_message_animations(self, graph, n=50, fraction_fire=0.0)

        fire = (
            ImageMobject("img/fire_apple_emoji.png")
            .scale(0.8)
            .move_to(graph.vertices[10])
        )
        self.add_sound(get_sound_effect("explosion"), time_offset=EXPLOSION_OFFSET)
        self.play(FadeIn(fire))

        self.wait()


class BlockchainGroupChat(Scene):
    def construct(self):
        util_general.default()

        message_pairs = [
            # Use a list comprehension because otherwise we mix 1-based and 0-based indices
            (f"General #{i+1}", message)
            for i, message in [
                (1, "anybody up for invading tmr?"),
                (3, "sounds good"),
                (0, "idk im kinda tired"),
            ]
        ]

        chat = ChatWindow()

        for pair in message_pairs:
            chat.add_message(ChatMessage(sender=pair[0], message=pair[1]), action="add")

        self.add(chat)
        self.wait(1)

        state = BlockchainState(chat)

        self.remove(chat)
        self.play(FadeIn(*state.players), *state.creation_animations)
        self.wait(1)

        messages_per_round = [
            [
                state.make_message_from_general(1, "guys cmon"),
                state.make_message_from_general(2, "good morning"),
            ],
            # Different #messages in each round to show that it doesn't always have
            # to be a fixed number (do we want this?)
            [
                state.make_message_from_general(1, "cmon let's do it"),
                state.make_message_from_general(2, "I'm thinking about thos beans"),
                state.make_message_from_general(0, "i'm busy :("),
            ],
            [
                state.make_message_from_general(1, "eh ok let's skip"),
            ],
        ]

        for leader_id, messages_to_add in zip(range(3), messages_per_round):
            state.make_leader(leader_id, self, use_black_crown=False)

            for message in messages_to_add:
                self.play(FadeIn(message))

            self.add_sound(get_sound_effect("whoosh"), time_offset=WHOOSH_OFFSET)
            self.play(
                state.players[leader_id].chat_window.copy_messages(
                    messages_to_add,
                    background_color=util_general.BASE01,
                    keep_original=False,
                )
            )
            self.wait(1)

            if leader_id == 0:
                block1 = Group(*state.players[0].chat_window.messages_group[0:3])
                block2 = Group(*state.players[0].chat_window.all_messages[3:5])
                delta = 0.2
                self.play(
                    block1.animate.shift(UP * 0 * delta),
                    block2.animate.shift(DOWN * 2 * delta),
                )
                self.wait()

                cr = 0.1
                rec1 = SurroundingRectangle(
                    block1, color=util_general.RED, corner_radius=cr
                )
                rec2 = SurroundingRectangle(
                    block2, color=util_general.RED, corner_radius=cr
                )
                rec2 = (
                    RoundedRectangle(
                        width=rec1.get_width(),
                        height=rec2.get_height(),
                        color=util_general.RED,
                        corner_radius=cr,
                    )
                    .move_to(rec2)
                    .align_to(rec1, LEFT)
                )

                lines = [
                    Line(
                        rec1.get_top(), rec1.get_top() + 1 * UP, color=util_general.RED
                    ),
                    Line(rec1.get_bottom(), rec2.get_top(), color=util_general.RED),
                    Line(
                        rec2.get_bottom(),
                        rec2.get_bottom() + 0.5 * DOWN,
                        color=util_general.RED,
                    ),
                ]
                blockchain_tex = (
                    Tex("Blockchain", color=util_general.text_color)
                    .scale(1.5)
                    .next_to(rec2, direction=DOWN, buff=0.6)
                )

                self.play(
                    Create(rec1),
                    Create(rec2),
                    *[Create(l) for l in lines],
                )
                self.wait()
                self.play(
                    Write(blockchain_tex),
                )
                self.wait()

                self.play(
                    FadeOut(rec1),
                    FadeOut(rec2),
                    *[FadeOut(l) for l in lines],
                    block2.animate.shift(-DOWN * 2 * delta),
                    FadeOut(blockchain_tex),
                )
            for i in range(3):
                self.add_sound(
                    get_sound_effect("whoosh"), time_offset=i * 0.5 + WHOOSH_OFFSET
                )
            state.send_block_to_other_players(messages_to_add, self)


class ElectronicSignature(Scene):
    def construct(self):
        util_general.default()

        player1 = Player(with_clipart=True, number=1).shift(LEFT * 4 + UP * 2)
        player2 = Traitor(with_clipart=True, number=2).shift(LEFT * 4 + DOWN * 2)
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
        signature_tex = Tex(
            r"Electronic signature", color=util_general.text_color
        ).scale(1.5)
        self.play(Write(signature_tex))

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
            FadeOut(signature_tex),
            Write(Text("Can't pretend to be somebody else", color=util_general.RED)),
        )

        self.wait()


class TraitorGroupChat(Scene):
    def construct(self):
        util_general.default()

        message_pairs = [
            # Use a list comprehension because otherwise we mix 1-based and 0-based indices
            (f"General #{i+1}", message)
            for i, message in [
                (1, "anybody up for invading tmr?"),
                (3, "sounds good"),
                (0, "idk im kinda tired"),
            ]
        ]

        chat = ChatWindow()

        for pair in message_pairs:
            chat.add_message(ChatMessage(sender=pair[0], message=pair[1]), action="add")

        self.add(chat)
        self.wait(1)

        state = BlockchainState(chat, with_traitor=True)

        self.remove(chat)
        self.play(FadeIn(*state.players), *state.creation_animations)
        self.wait(1)

        messages_per_round = [
            [
                state.make_message_from_general(
                    0, "totally real message", alleged_general_id=1
                ),
                state.make_message_from_general(2, "good morning"),
            ],
        ]

        # vv: This for loop is unnecessary here, but keeping it now in case
        # we want more rounds later
        for leader_id, messages_to_add in enumerate(messages_per_round):
            state.make_leader(leader_id, self, use_black_crown=False)

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


class OtherLeaderAttacks(Scene):
    def construct(self):
        leader = BlockchainPlayer().scale(1.5)
        leader.shift(LEFT * 6)

        # It's difficult to scale the crown if we don't do this hack with first passing
        # the crown to a fake leader
        fake_leader = BlockchainPlayer().scale(1.5).shift(LEFT * 10)
        self.play(fake_leader.make_leader(use_black_crown=False))
        fake_leader.crown.scale(1.5)

        self.play(FadeIn(leader))
        self.play(
            leader.make_leader(generals=[leader, fake_leader], use_black_crown=False)
        )

        chat = ChatWindow().shift(LEFT * 2)
        chat.add_message(ChatMessage(sender="General #1", message="Foo"), action="add")
        chat.add_message(ChatMessage(sender="General #2", message="Bar"), action="add")
        chat.add_message(ChatMessage(sender="General #3", message="Baz"), action="add")
        self.play(FadeIn(chat))
        self.wait()

        if False:  # Doesn't match the voiceover
            # Shuffle messages
            message_positions = [message.get_center() for message in chat.all_messages]
            self.play(
                chat.all_messages[0].animate.move_to(message_positions[1]),
                chat.all_messages[1].animate.move_to(message_positions[2]),
                chat.all_messages[2].animate.move_to(message_positions[0]),
            )
            self.wait()
            # Shuffle messages back
            self.play(
                chat.all_messages[0].animate.move_to(message_positions[0]),
                chat.all_messages[1].animate.move_to(message_positions[1]),
                chat.all_messages[2].animate.move_to(message_positions[2]),
            )
            self.wait()

        copies = [[m.copy() for m in chat.all_messages] for _ in range(2)]

        # Attack 1: Send different messages to different generals
        # TODO(vv): maybe we should make this send all messages, but with different texts?
        self.add_sound(get_sound_effect("whoosh"), time_offset=WHOOSH_OFFSET)
        self.play(
            *[c.animate.shift(RIGHT * 4) for c in [copies[0][0], copies[0][1]]],
            Create(
                Text("For general #2", color=util_general.BASE00)
                .next_to(copies[0][0], direction=UP)
                .shift(RIGHT * 4)
                .scale(0.6)
            ),
        )
        self.wait()
        self.add_sound(get_sound_effect("whoosh"), time_offset=WHOOSH_OFFSET)
        self.play(
            *[c.animate.shift(RIGHT * 8) for c in [copies[1][1], copies[1][2]]],
            Create(
                Text("For general #3", color=util_general.BASE00)
                .next_to(copies[1][0], direction=UP)
                .shift(RIGHT * 8)
                .scale(0.6)
            ),
        )
        self.wait()

        # Pretend you didn't receive a message.
        copies[1][0].shift(RIGHT * 8)
        self.play(FadeIn(copies[1][0]), FadeOut(copies[1][2]))
        self.wait()


class BlockchainForConsensus(Scene):
    def construct(self):
        util_general.default()

        message_pairs = [
            ("General #2", "OK guys let’s vote, I vote YES"),
            ("General #4", "sounds good, I vote YES"),
            ("General #5", "I vote NO"),
            ("General #1", "Ok, so that's 9 votes for YES, let's attack."),
            ("General #3", "Ok, you got it"),
            ("General #4", "okok"),
        ]

        chat = ChatWindow().shift(LEFT * 4 + DOWN * 3)

        for sender, message_text in message_pairs:
            message = ChatMessage(
                sender,
                message_text,
                with_verification=True,
                sender_color=ChatWindow.SENDER_COLORS[sender],
            ).shift(DOWN * 3 + RIGHT * 2)
            self.play(FadeIn(message), run_time=0.5)
            self.play(chat.copy_messages([message], keep_original=False))
            chat.messages_group.add(message)


class BlockchainForCryptocurrencies(Scene):
    def construct(self):
        util_general.default()

        messages_data = [
            # from, to, money, allowed
            (2, 5, 10, True),
            (3, 7, 50, True),
            (2, 6, 80, True),
            (1, 8, 1000, False),
            (1, 8, 10, True),
        ]

        chat = ChatWindow().shift(LEFT * 4 + DOWN * 3)

        for general_from, general_to, money, allowed in messages_data:
            sender = f"General #{general_from}"
            message_str = f"Send {money} coins to General #{general_to}"

            message = ChatMessage(sender, message_str, with_verification=True).shift(
                DOWN * 3 + RIGHT * 2
            )
            self.play(FadeIn(message, shift=LEFT), run_time=0.5)

            if not allowed:
                not_allowed_text = Text("Insufficient funds!", color=util_general.RED)
                not_allowed_text.next_to(message, direction=UP).shift(RIGHT)
                self.add_sound("audio/polylog_failure.wav", time_offset=0.5)
                self.play(Create(not_allowed_text))
                self.wait()
                self.play(Uncreate(not_allowed_text), FadeOut(message))
            else:
                self.play(chat.copy_messages([message], keep_original=False))
                chat.messages_group.add(message)

            self.wait()


class BlockchainRandomLeader(Scene):
    def construct(self):
        chat = ChatWindow()

        self.add(chat)
        self.wait(1)

        state = BlockchainState(chat, x_offset=0, y_offset=0)

        self.remove(chat)
        self.play(FadeIn(*state.players), *state.creation_animations)
        self.wait(1)

        rng = np.random.default_rng(120)

        for i in range(30):
            if i < 8:
                leader_id = i % 4
            else:
                leader_id = rng.choice(len(state.players))

            if leader_id != state.leader_id:
                self.add_sound(
                    get_sound_effect("lovely", variant=leader_id), time_offset=0
                )
                state.make_leader(leader_id, self, use_black_crown=False)

            if i == 5:
                player = BlockchainPlayer(number=5).shift(RIGHT)
                self.play(FadeIn(player))
                state.players.append(player)

            if i == 12:
                fades = [FadeOut(state.players[1]), FadeOut(state.players[2])]
                state.players.pop(2)
                state.players.pop(1)
                self.play(*fades)


class ComparisonTable(Scene):
    def construct(self):
        util_general.default()

        table = Table(
            [
                ["Ad-hoc approach", "Blockchain approach"],
                [
                    "Similar to\ndatabase synchronization",
                    "Similar to\ncryptocurrencies",
                ],
                ["No assumption on traitors", "Traitors cannot break RSA"],
                ["Works for <n/4 traitors", "Works for <n/2 traitors\n(best possible)"],
            ],
            element_to_mobject_config={"alignment": "center"},
        ).scale(0.8)

        self.play(Create(table.elements[:2]), Create(table.vertical_lines[0]))

        for row in range(1, table.row_dim):
            self.wait(0.5)
            # For row 3, reveal the right cell first to match the voiceover
            order = [0, 1] if row != 3 else [1, 0]

            self.play(Create(table.horizontal_lines[row - 1]))
            self.play(Create(table.elements[row * table.col_dim + order[0]]))
            self.wait(0.5)
            self.play(Create(table.elements[row * table.col_dim + order[1]]))

        self.wait()
