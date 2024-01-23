# manim -pql --fps 10 -r 290,180 anims.py Polylogo
from pathlib import Path

from manim import *

from utils.chat_window import ChatMessage, ChatWindow
from utils.generals import (
    CodeWithStepping,
    Crown,
    CyclicOpinionTraitor,
    GameState,
    Message,
    MessageToSend,
    Player,
    Traitor,
)
from utils.util_cliparts import *
from utils.util_general import *

# Vasek's constants for the scenes
SAMPLE_OPINIONS = ["Y", "N", "Y", "N", "Y", "N", "N", "Y", "N", "Y", "N", "Y"]
GAME_SHIFT = 2 * LEFT
TRAITOR_IDS = [3, 5]

SAMPLE_OPINIONS2 = ["Y", "N", "Y", "N", "Y", "N", "N", "Y", "Y", "Y", "N", "Y"]
TRAITOR_IDS2 = [2, 4]

SAMPLE_OPINIONS_MANY_Y = ["Y", "N", "Y", "Y", "Y", "N", "N", "Y", "Y", "Y", "Y", "Y"]

SAMPLE_OPINIONS3 = ["N", "N", "Y", "N", "Y", "N", "N", "Y", "N", "N", "N", "Y"]
TRAITOR_IDS3 = [1, 3]

SAMPLE_OPINIONS4 = ["N", "N", "Y", "N", "Y", "N", "N", "Y", "N", "N", "Y", "Y"]
TRAITOR_IDS4 = [0, 2]


SAMPLE_OPINIONS5 = ["N", "N", "Y", "N", "Y", "N", "N", "Y", "N", "N", "Y", "Y"]
TRAITOR_IDS5 = [0, 2]

# explanation texts

explanation_texts = [
    r"\raggedright \textbf{Input}: YES/NO for every honest general",
    r"\raggedright \textbf{Output}: YES/NO for every honest general",
    r"\raggedright \textbf{Task}: all honest generals output \\ the same answer",
    r"\raggedright \textbf{Condition}: if all generals agreed \\ at the beginning, nobody changes opinion",
]
Path("./media/Tex").mkdir(parents=True, exist_ok=True)
explanations = (
    VGroup(
        *[
            Tex(text, color=TEXT_COLOR).scale(0.75)
            for i, text in enumerate(explanation_texts)
        ]
    )
    .arrange_in_grid(rows=len(explanation_texts), cell_alignment=LEFT)
    .to_edge(RIGHT, buff=0.5)
)
Group(*explanations[2:]).shift(0.5 * DOWN)


#######################################################


class LeaderNoTraitors(Scene):
    def construct(self):
        opinions = ["Y", "N", "Y", "N", "Y", "N", "N", "Y", "N", "Y", "N", "Y"]
        game = GameState([Player() for i in range(len(opinions))])
        game.shift(2 * LEFT)

        # add the generals from the game one by one
        for i in range(len(game.generals)):
            self.play(
                FadeIn(game.generals[i]),
            )
            self.wait(0.5)

        self.wait(0.5)
        return

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
        opinions = [None, "Y", None, "N", "Y", "Y", "Y", "N", "Y", "Y", "Y", "Y"]
        game = GameState(
            [
                CyclicOpinionTraitor("YNNY"),
                Player(),
                CyclicOpinionTraitor("NNYY"),
                Player(),
                Player(),
                Player(),
                Player(),
                Player(),
                Player(),
                Player(),
                Player(),
                Player(),
            ]
        )
        game.shift(3.0 * LEFT)
        self.add(game)

        self.wait(0.5)
        for i in range(len(game.generals)):
            if opinions[i] is not None:
                self.play(
                    game.generals[i].animate.change_opinion(opinions[i]), run_time=0.2
                )

        code = CodeWithStepping(
            code="""for leader_id in [1, 2, 3]:
    send my opinion to everybody (including myself)
    if I am the leader:  # Algorithm 1
        update opinion to majority of received messages
        broadcast my opinion
    compute number of YES and NO messages # Algorithm 2
    if YES >> NO or NO >> YES:
        update opinion to the majority of received messages
    else:
        update opinion to the opinion of the leader
""",
            language="python",
            font_size=12,
        )
        code.shift(3.5 * RIGHT)
        self.add(code)

        for i in range(10):
            code.highlight_line(i, self)

        game.full_algorithm(self, leader_ids=[0, 1, 2], send_to_self=True, code=code)

        self.wait(1)


######
# vasek
######


class Intro(Scene):
    def construct(self):
        default()

        # It turns out that a pretty similar game is one of the most fundamental problems of computer science.

        # přejde se z videa karet do obrázků generálů

        # It’s known as the Byzantine Generals problem and in this video,

        # zazoomuje se doprostřed generálů, objeví se text

        # we’ll see how to solve it and why it is so important for databases storing your data and for blockchain protocols like Bitcoin.

        # nalevo se zobrazí síť kde se posílají zprávy

        # pak napravo se zobrazí kryptoobrázek kde si posílají bitcoiny

        # [kryptoměny, nějaký obrázky distribuovaný databáze nebo internetu]

        # [polylogo]


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


class Setup1(Scene):
    def construct(self):
        # You can imagine the Byzantine generals' problem as a game played in rounds. In our example, there will be 12 players.

        game = GameState(
            [Player(with_clipart=True) for i in range(len(SAMPLE_OPINIONS))]
        )
        game.shift(GAME_SHIFT)

        # add the generals from the game one by one,
        self.play(
            Succession(
                *[FadeIn(game.generals[i].clipart) for i in range(len(game.generals))],
                lag_ratio=0.3,
            )
        )
        self.wait(0.5)

        # Each player plays one general in a camp outside a city.

        # image of the city
        city = ImageMobject("img/city.png").scale(0.5).shift(game.get_center())
        self.play(FadeIn(city))
        self.wait()

        # The generals are trying to conquer the city, but to be successful, they all have to attack at the same time.

        # all generals at once move a bit towards the city, then back
        self.play(
            AnimationGroup(
                *[
                    game.generals[i].clipart.animate.shift(
                        -0.5 * game.circle_position(i)
                    )
                    for i in range(len(game.generals))
                ],
            )
        )
        self.play(
            AnimationGroup(
                *[
                    game.generals[i].clipart.animate.shift(
                        0.5 * game.circle_position(i)
                    )
                    for i in range(len(game.generals))
                ],
            )
        )
        self.wait()

        # Should they try to attack tomorrow? Every general has some opinion on that

        # we reveal the opinions of generals one by one, each opinion is a letter Y or N in a bubble which is a SVG image
        cliparts = Group(*[game.generals[i].clipart for i in range(len(game.generals))])
        for c in cliparts:
            c.save_state()
        bubbles = [
            SVGMobject("img/bubble_say.svg")
            .scale(0.5)
            .next_to(game.generals[i].clipart, RIGHT)
            .shift(0.3 * UP)
            for i in range(len(game.generals))
        ]
        letters = [
            Tex(SAMPLE_OPINIONS[i], color=TEXT_COLOR).scale(0.5).move_to(bubbles[i])
            for i in range(len(game.generals))
        ]
        self.play(
            Succession(
                *[
                    AnimationGroup(
                        FadeIn(b),
                        FadeIn(l),
                    )
                    for b, l in zip(bubbles, letters)
                ],
                lag_ratio=0.3,
            )
        )
        self.wait()

        # Now they will have to communicate and reach a consensus together.

        # generals exchange a few messages
        messages = []
        for i in range(len(game.generals)):
            for j in range(len(game.generals)):
                if i != j:
                    messages.append(
                        MessageToSend(i, j, Message(SAMPLE_OPINIONS[i], clipart=True))
                    )

        game.send_messages_low_tech(
            self,
            messages,
        )
        self.wait()

        # [animace jak se Y/N změní na samá Y a pak zpět]

        # There are two issues that are standing in their way:

        # First, the generals don’t have the option to get together as a group or use some kind of group chat application.
        # all generals shift together to the right where they make a block 4x3

        # positions = [game.generals[i].get_center() for i in range(len(game.generals))]
        # # animate generals so that they are in a table 4x3

        # self.play(
        #     AnimationGroup(
        #         cliparts.animate.arrange_in_grid(rows=3, cols=4, buff=0).next_to(city, RIGHT, buff=1),
        #         *[FadeOut(bubble) for bubble in bubbles],
        #         *[FadeOut(l) for l in letters],
        #     )
        # )
        # self.wait()
        # # we cross the block with a big red cross
        # cross = Text("×", color=RED, font_size=150).move_to(cliparts.get_center())
        # self.play(
        #     FadeIn(cross)
        # )
        # self.wait()
        # self.play(
        #     FadeOut(cross),
        #     *[c.animate.restore() for c in cliparts],
        # )
        # self.wait()

        message_pairs = [
            ("General #2", "Let's make a vote"),
            ("General #4", "I vote YES. "),
            ("General #7", "I vote NO."),
        ]

        chat = ChatWindow().next_to(game, RIGHT, buff=MED_SMALL_BUFF)

        for pair in message_pairs:
            self.play(chat.add_message(ChatMessage(sender=pair[0], message=pair[1])))
            self.wait()

        # remove the chat window
        self.play(FadeOut(chat))
        self.wait()
        return

        # Each general has to stay in his camp and in each round, he can only send a direct message to each other general.

        id = 3
        # general with index id gets a bit bigger and shifts a bit outside of the circle
        self.play(
            AnimationGroup(
                game.generals[id]
                .clipart.animate.scale(1.5)
                .shift(2 * game.circle_position(id)),
            )
        )
        self.wait()

        # the general then sends a message to all other generals
        # [generál pošle obálku pár dalším]

        messages_from = []
        messages_to = []
        for i in range(len(game.generals)):
            if i != id:
                messages_from.append(MessageToSend(id, i, Message("hi", clipart=True)))
                messages_to.append(MessageToSend(i, id, Message("hi", clipart=True)))

        for messages in [messages_from, messages_to]:
            game.send_messages_low_tech(
                self,
                messages,
            )
            self.wait()

        # the icon of the special general scales back and joins the circle again

        self.play(
            AnimationGroup(
                game.generals[id]
                .clipart.animate.scale(1 / 1.5)
                .shift(-2 * game.circle_position(id)),
            )
        )
        self.wait()
        # The second reason why this is going to be hard is that two of the generals are secretly plotting together against the rest - I will call these two traitors. Whatever strategy you come up with for the honest generals to play, the traitors know this strategy and will try to break it.
        # [traitoři jsou generálové kterým narostou rohy, nebo se změní clipart na čertíka]

        # traitor generals are replaced with a traitor image

        self.play(
            AnimationGroup(
                *[
                    game.generals[id]
                    .clipart.animate.scale(1.5)
                    .shift(2 * game.circle_position(id))
                    for id in TRAITOR_IDS
                ],
            )
        )
        self.wait()
        traitor_pics = [
            ImageMobject("img/traitor.png")
            .scale_to_fit_width(game.generals[id].clipart.get_width())
            .move_to(game.generals[id].clipart)
            for id in TRAITOR_IDS
        ]
        self.play(
            AnimationGroup(
                *[
                    game.generals[id].clipart.animate.become(pic)
                    for id, pic in zip(TRAITOR_IDS, traitor_pics)
                ],
                *[FadeOut(bubbles[i]) for i in TRAITOR_IDS],
                *[FadeOut(letters[i]) for i in TRAITOR_IDS],
            )
        )
        self.wait()
        self.play(
            AnimationGroup(
                *[
                    game.generals[id]
                    .clipart.animate.scale(1 / 1.5)
                    .shift(-2 * game.circle_position(id))
                    for id in TRAITOR_IDS
                ],
            )
        )
        self.wait()

        # So these will be the obstacles:
        # First: only direct messages.

        # we generate a few random pairs of generals and send messages between them

        num_pairs = 10
        pairs = []
        for i in range(num_pairs):
            pairs.append(
                (
                    random.randint(0, len(game.generals) - 1),
                    random.randint(0, len(game.generals) - 1),
                )
            )
            if pairs[-1][0] == pairs[-1][1]:
                pairs.pop()

        messages = []
        for pair in pairs:
            messages.append(
                MessageToSend(pair[0], pair[1], Message("hi", clipart=True))
            )

        # TODO add a parameter lag ratio?
        game.send_messages_low_tech(
            self,
            messages,
        )

        #  Second: two secret traitors.

        # the traitor icons scale up and then scale back down

        self.play(
            AnimationGroup(
                *[game.generals[i].clipart.animate.scale(1.5) for i in TRAITOR_IDS],
            )
        )
        self.wait()
        self.play(
            AnimationGroup(
                *[game.generals[i].clipart.animate.scale(1 / 1.5) for i in TRAITOR_IDS],
            )
        )
        self.wait()

        # fadeout
        self.play(
            FadeOut(city),
            *[
                FadeOut(bubbles[i])
                for i in range(len(game.generals))
                if i not in TRAITOR_IDS
            ],
            *[
                FadeOut(letters[i])
                for i in range(len(game.generals))
                if i not in TRAITOR_IDS
            ],
            # *[game.generals[i].animate.change_opinion("") for i in range(len(game.generals))],
        )
        self.wait()

        self.play(
            *[FadeOut(game.generals[i].clipart) for i in range(len(game.generals))],
            *[FadeIn(game.generals[i].icon) for i in range(len(game.generals))],
        )
        self.wait()


class Setup2(Scene):
    def construct(self):
        # add to the scene the objects that were there at the end of Setup1:

        game = GameState(
            [
                (
                    Player(with_clipart=True)
                    if i not in TRAITOR_IDS
                    else Traitor(with_clipart=True)
                )
                for i in range(len(SAMPLE_OPINIONS))
            ]
        )
        game.shift(GAME_SHIFT)
        self.add(game)
        self.play(
            *[FadeOut(game.generals[i].clipart) for i in range(len(game.generals))],
        )
        for i in range(len(game.generals)):
            game.generals[i].remove(game.generals[i].clipart)

        self.wait()
        self.play(game.animate.shift(1.5 * LEFT))
        self.wait()
        # fade out generals' icons

        # Now let me formalize the problem that the honest generals need to solve. Every honest general starts with an opinion of either YES or NO.

        # every general gets his opinion in succession, also, the first explanation text appears
        self.play(
            AnimationGroup(
                Succession(
                    *[
                        game.generals[i].animate.change_opinion(SAMPLE_OPINIONS[i])
                        for i in range(len(game.generals))
                        if i not in TRAITOR_IDS
                    ],
                    lag_ratio=0.3,
                ),
                FadeIn(explanations[0]),
            )
        )
        self.wait(0.5)

        # The generals then go through several rounds of sending each other messages following some strategy, or protocol.

        # five rounds, in each round every general sends an opinion to every other general:
        # at the top of the scene, there is also counter "Round: x" where x is the round number that increments every round
        # TODO just send envelopes

        counter_tex = Tex("Round: 0", color=TEXT_COLOR).next_to(
            game, UP, buff=-MED_LARGE_BUFF
        )  # .align_to(game, LEFT)
        self.play(FadeIn(counter_tex))
        self.wait()

        for it in range(2):
            messages = []
            for i in range(len(game.generals)):
                for j in range(len(game.generals)):
                    if i != j:
                        messages.append(
                            MessageToSend(
                                i, j, Message(SAMPLE_OPINIONS[i], clipart=True)
                            )
                        )

            # TODO do both together
            self.play(
                counter_tex.animate.become(
                    Tex(f"Round: {it + 1}", color=TEXT_COLOR)
                    .move_to(counter_tex)
                    .align_to(counter_tex, LEFT)
                )
            )

            game.send_messages_low_tech(
                self,
                messages,
            )

            self.wait(0.5)

        # When the protocol finishes, each general outputs his answer which is either YES or NO and which may be different from his initial opinion.
        self.play(
            FadeIn(explanations[1]),
        )
        self.wait()

        # each honest general changes his opinion to "Y"
        # TODO every general will still have the input to the left and now also output to the right
        self.play(
            *[
                game.generals[i].animate.change_opinion("Y")
                for i in range(len(game.generals))
                if i not in TRAITOR_IDS
            ],
        )
        self.wait()

        # [každý generál má u sebe input i output, traitor asi žádný input/output nemá, ať je jasný co znamená “honest generals”]

        # Every honest general should output the same answer, meaning that the honest generals agreed whether to attack tomorrow.
        # the letters Y are scaled up and then back down
        self.play(
            AnimationGroup(
                *[
                    game.generals[i].opinion_text.animate.scale(1.5)
                    for i in range(len(game.generals))
                    if i not in TRAITOR_IDS
                ],
                FadeIn(explanations[2]),
            )
        )
        self.wait()
        # next scale down:
        self.play(
            AnimationGroup(
                *[
                    game.generals[i].opinion_text.animate.scale(1 / 1.5)
                    for i in range(len(game.generals))
                    if i not in TRAITOR_IDS
                ],
            )
        )
        self.wait()
        # Our task is to design a protocol under which the generals always manage to reach this consensus.
        # requirement 3 fades in

        # But we need to add one more condition to make the problem non-trivial. Right now, we can use the berserk protocol: don’t look at your input at all, don’t communicate with other generals, and just output YES. Surely, with this strategy, all honest generals output the same answer.

        # change opinions back to the starting opinions:
        self.play(
            *[
                game.generals[i].animate.change_opinion(SAMPLE_OPINIONS[i])
                for i in range(len(game.generals))
                if i not in TRAITOR_IDS
            ],
        )
        self.wait()

        # fadeout all input letters
        self.play(
            *[
                game.generals[i].animate.change_opinion("-")
                for i in range(len(game.generals))
                if i not in TRAITOR_IDS
            ],
        )
        self.wait()

        # crosses = [Text("×", color=RED, font_size=80).move_to(game.generals[i].opinion_text) for i in range(len(game.generals)) if i not in TRAITOR_IDS]
        # self.play(
        #     *[FadeIn(crosses[i]) for i in range(len(crosses))],
        # )
        # self.wait()

        # then, an envelope appears in the middle and then gets crossed
        envelope = (
            ImageMobject("img/envelope.png").scale(0.3).move_to(game.get_center())
        )
        cross_envelope = Text("×", color=RED, font_size=80).scale(2).move_to(envelope)
        self.play(FadeIn(envelope))
        self.wait()
        self.play(FadeIn(cross_envelope))
        self.wait()

        # every general now outputs the same answer
        self.play(
            *[
                game.generals[i].animate.change_opinion("Y")
                for i in range(len(game.generals))
                if i not in TRAITOR_IDS
            ],
        )
        # fade out the envelope and the crosses
        self.play(
            FadeOut(envelope),
            FadeOut(cross_envelope),
        )
        self.wait()

        # To fix this, we’ll explicitly request that if all honest generals start with YES, they all need to output YES at the end. And conversely, if all start with NO, they all need to output NO. In other words, if all generals already agreed at the beginning of the protocol, nobody is going to change their opinion.

        # the letters Y are scaled up and then back down
        for it in range(2):
            self.play(
                AnimationGroup(
                    *[
                        game.generals[i].opinion_text.animate.scale(1.5)
                        for i in range(len(game.generals))
                        if i not in TRAITOR_IDS
                    ],
                )
            )
            self.wait()
            self.play(
                AnimationGroup(
                    *[
                        game.generals[i].opinion_text.animate.scale(1 / 1.5)
                        for i in range(len(game.generals))
                        if i not in TRAITOR_IDS
                    ],
                )
            )
            self.wait()

            if it == 0:
                # change opinions to all NO:
                self.play(
                    *[
                        game.generals[i].animate.change_opinion("N")
                        for i in range(len(game.generals))
                        if i not in TRAITOR_IDS
                    ],
                )

        # add the third explanation text
        self.play(
            FadeIn(explanations[3]),
        )
        self.wait()

        # revert back the opinions of generals
        self.play(
            *[
                game.generals[i].animate.change_opinion(SAMPLE_OPINIONS[i])
                for i in range(len(game.generals))
                if i not in TRAITOR_IDS
            ],
        )
        self.wait()

        # So, our goal is to come up with a protocol with these two properties
        # we create a red rectangle around the third explanation text, then change it into a rectangle around the fourth explanation text, then fade out the rectangle
        rec = SurroundingRectangle(explanations[2], color=RED)
        self.play(Create(rec))
        self.wait()
        self.play(Transform(rec, SurroundingRectangle(explanations[3], color=RED)))
        self.wait()
        self.play(FadeOut(rec))
        self.wait()

        # that works regardless of the starting opinions of generals,
        # generate two random opinions for each general, then change the opinions of generals to these random opinions
        for it in range(2):
            random_opinions = [
                random.choice(["Y", "N"]) for i in range(len(game.generals))
            ]
            self.play(
                *[
                    game.generals[i].animate.change_opinion(random_opinions[i])
                    for i in range(len(game.generals))
                    if i not in TRAITOR_IDS
                ],
            )
            self.wait()

        # whichever two generals are traitors, and whatever the traitors are trying to do.
        # generate two new random traitors that are different from current ones. Then swap the traitors with the new ones
        new_traitors = [[2, 7], [4, 6]]

        for it in range(2):
            anims = []
            for i in range(2):
                anims.append(
                    game.generals[TRAITOR_IDS[i]].animate.shift(
                        game.generals[new_traitors[it][i]].icon.get_center()
                        - game.generals[TRAITOR_IDS[i]].icon.get_center()
                    )
                )
                anims.append(
                    game.generals[new_traitors[it][i]].animate.shift(
                        game.generals[TRAITOR_IDS[i]].icon.get_center()
                        - game.generals[new_traitors[it][i]].icon.get_center()
                    )
                )

            self.play(*anims)
            self.wait()

        # This is a good place to stop the video and try to solve this problem yourself, or at least you can try to figure out how you’d solve it if there were no traitors.

        # There are several approaches you can have. In fact, we will solve the problem twice in this video. First, we will solve it similarly to how large databases are solving the problem in practice. Then, we will solve it again using the tricks from cryptocurrency protocols.

        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait()

        # two red rectangles appear
        rec1 = Rectangle(height=7, width=6, color=RED)
        rec2 = rec1.copy()
        _recs = Group(rec1, rec2).arrange(RIGHT)
        self.play(Create(rec1), Wait(), Create(rec2), Wait())


class Solution1(Scene):
    def construct(self):
        # create a game with no traitors
        game = GameState([Player(opinion="-") for i in range(len(SAMPLE_OPINIONS2))])
        self.play(
            *[FadeIn(game.generals[i]) for i in range(len(game.generals))],
        )
        self.wait()
        # generals get their starting opinion
        game.set_opinions(self, SAMPLE_OPINIONS2)
        self.wait()

        # Solution 1
        game.leader_algorithm(self, 1)
        self.wait()

        rng = np.random.default_rng(1)

        # This protocol surely works if there are no traitors, but if we are unlucky and choose a traitor as the leader, he gets a complete control over the output of honest generals, a spectacular failure!

        for i in TRAITOR_IDS3:
            game.change_general(
                self,
                i,
                CyclicOpinionTraitor(
                    "".join(rng.choice(["Y", "N"]) for _ in range(12))
                ),
            )

        game.leader_algorithm(self, 1)
        self.wait()

        # [ukáže se jak traitor dostane korunku a pak pošle někomu YES a někomu NO]

        # But let’s look on the bright side! If we could somehow ensure that the leader is honest, this protocol would work really well.

        # change opinions back
        for i in TRAITOR_IDS3:
            game.change_general(
                self, i, CyclicOpinionTraitor("Y"), with_animation=False
            )
        game.set_opinions(self, SAMPLE_OPINIONS3)

        self.wait()

        # Notice that the output of the protocol is not necessarily the majority opinion of honest generals, because the traitors also get to vote,

        game.leader_algorithm(self, 2)
        self.wait()

        # but fortunately, we only want to ensure this weaker condition, which is satisfied.
        # shift the game to the left, then reveal explanations

        self.play(
            game.animate.to_edge(LEFT, buff=-1),
            FadeIn(explanations),
        )
        self.wait()
        self.play(FadeIn(SurroundingRectangle(explanations[3], color=RED)))
        self.wait(5)


class Solution2(Scene):
    def construct(self):
        # So, how can we approach the problem? Well, let’s first see how we could solve it if there were no traitors at all and understand how those approaches fail.

        # create a game with no traitors
        game = GameState([Player("-") for i in range(len(SAMPLE_OPINIONS2))])
        self.play(
            *[FadeIn(game.generals[i]) for i in range(len(game.generals))],
        )
        self.wait()
        # generals get their starting opinion
        game.set_opinions(self, SAMPLE_OPINIONS2)
        self.wait()

        # Without traitors, there are two pretty simple protocols. Let’s look at them. In the first protocol, everybody simply sends their opinion to everybody else, including themselves.

        # [animace máme kroužek 12 lidí, animace toho jak si pošlou všichni mezi sebou token s YES/NO – tohle je brutálně hodně animací, dá se to udělat jinak? Kdo ví, možná to bude vypadat hezky? ]

        # Then, each general outputs the majority opinion among the messages he received.

        # [představuju si, že tokeny u každého generála skončí na kopičkách]

        # If there’s a tie, let’s say he outputs YES. In this example, everybody got 7 YES messages and 5 NO messages, so everybody agrees on YES.

        game.majority_algorithm(self)
        self.wait()

        # [“7 YES messages” circubscribe 7 YES tokenů u každého generála]

        rng = np.random.default_rng(0)

        game_with_traitors = GameState(
            [
                (
                    CyclicOpinionTraitor(
                        "".join(rng.choice(["Y", "N"]) for _ in range(12))
                    )
                    if i in TRAITOR_IDS2
                    else Player(opinion=SAMPLE_OPINIONS2[i])
                )
                for i in range(len(SAMPLE_OPINIONS2))
            ]
        )

        anims = []
        for i in range(len(game.generals)):
            if i not in TRAITOR_IDS2:
                anims.append(
                    game.generals[i].animate.change_opinion(SAMPLE_OPINIONS2[i])
                )
            else:
                anims.append(
                    AnimationGroup(
                        FadeOut(game.generals[i]),
                        FadeIn(game_with_traitors.generals[i]),
                    )
                )

        self.play(LaggedStart(*anims))
        for i in range(len(game.generals)):
            if i not in TRAITOR_IDS2:
                self.remove(game.generals[i])
                self.add(game_with_traitors.generals[i])
        self.wait()
        self.remove(game)

        game = game_with_traitors

        # Well, imagine that the honest generals start with 5 YES opinions and 5 NO opinions. Honest generals follow the protocol and send their opinion to everybody else.

        # highlight 5 Y, then 5 N opinions
        for opinion in ["Y", "N"]:
            game.highlight_generals_with_opinion(self, opinion=opinion)
            self.wait()

        # Now the traitors can send 2 YES messages to some generals and 2 NO messages to some other generals.

        game.majority_algorithm(self)
        self.wait()

        # [ukáže se jak traitoři pošlou nejdřív YES tokeny některým, pak NO tokeny zbylým (sobě traitoři nepošlou nic)]
        # This leads to some generals outputting YES, and some generals outputting NO. So, this simple protocol fails.

        # highlight generals with output Y, then N
        for opinion in ["Y", "N"]:
            game.highlight_generals_with_opinion(self, opinion=opinion)
            self.wait()

        # [obtáhnou se ti co outputnou YES, je vidět že jejich YES kopička je větší než NO kopička, pak to samé s NO]
        # But let’s look on the bright side – the protocol only fails if the initial opinion of the honest generals was roughly split. If at least 7 honest generals start with the YES opinion, then this protocol works well.

        game.set_opinions(self, SAMPLE_OPINIONS_MANY_Y)

        self.wait()

        # we show numbers 1,2, ... next to generals with Y
        numbers = []
        num = 0
        anims = []
        for i in range(len(game.generals)):
            if i not in TRAITOR_IDS2 and SAMPLE_OPINIONS_MANY_Y[i] == "Y":
                txt = (
                    Text(str(num + 1), color=TEXT_COLOR)
                    .scale(0.8)
                    .move_to(
                        game.generals[i].opinion_text.get_center() * 1.4,
                        # direction=game.generals[i].get_center() - game.get_center(),
                        # buff=MED_LARGE_BUFF,
                    )
                )
                numbers.append(txt)
                anims.append(FadeIn(txt))
                num += 1

        self.play(LaggedStart(*anims))
        self.wait(2)

        # vv: I don't think we need to play the algorittm again.
        # fadeout numbers
        # self.play(*[FadeOut(n) for n in numbers])
        # self.wait()

        # In that case, whatever the traitors do, every honest general ends up with at least 7 YES opinions, which is enough to make him output YES. Similarly, the protocol works if at least 7 honest generals start with the NO opinion.
        # [traitoři něco udělají, je pak vidět jak honest generálové skončili s 7 YES/5 NO,  8 YES/4 NO,  9 YES/3 NO, a všichni odpověděli YES]

        # game.majority_algorithm(self)
        # self.wait()


class SolutionCombine1(Scene):
    def construct(self):
        # So let’s now take a step back and see where we stand. We have two approaches to the problem. Both of them ultimately failed, but both of them also work well in some interesting situations.

        rng = np.random.default_rng(0)

        sc = 0.7
        shft = 3
        games = [
            GameState(
                [
                    (
                        CyclicOpinionTraitor(
                            "".join(rng.choice(["Y", "N"]) for _ in range(12))
                        )
                        if i in TRAITOR_IDS
                        else Player(opinion=SAMPLE_OPINIONS[i])
                    )
                    for i in range(len(SAMPLE_OPINIONS))
                ]
            )
            .scale(sc)
            .shift(shft * dir)
            for dir in [LEFT, RIGHT]
        ]
        titles = [
            Tex("Algorithm " + str(i + 1), color=TEXT_COLOR)
            .scale(0.7)
            .next_to(games[i], UP, buff=0.5)
            for i in range(2)
        ]
        comments = [
            Tex(str, color=TEXT_COLOR).scale(0.7).next_to(games[i], DOWN, buff=0.5)
            for i, str in enumerate(
                [
                    "works if the leader is honest",
                    "works if the initial opinions are skewed",
                ]
            )
        ]

        self.play(
            *[FadeIn(games[i]) for i in range(2)],
            *[FadeIn(titles[i]) for i in range(2)],
        )
        self.wait()

        # The first protocol works if the selected leader happens to be honest.

        self.play(FadeIn(comments[0]))
        self.wait()
        games[0].leader_algorithm(self, 0)
        self.wait()

        # The second protocol works if the initial opinions of honest generals are already skewed heavily in favor of one of the opinions.
        self.play(FadeIn(comments[1]))
        self.wait()
        games[1].majority_algorithm(self)
        self.wait()

        # Let’s try to combine the strengths of the two protocols into a new one that always works!
        self.play(
            *[FadeOut(m) for m in titles + comments],
            *[game.animate.scale(1 / sc).move_to(ORIGIN) for game in games],
        )
        self.wait(3)


class SolutionCombine2(Scene):
    def construct(self):
        rng = np.random.default_rng(0)
        game = GameState(
            [
                (
                    CyclicOpinionTraitor(
                        "".join(rng.choice(["Y", "N"]) for _ in range(12))
                    )
                    if i in TRAITOR_IDS4
                    else Player(opinion=SAMPLE_OPINIONS4[i])
                )
                for i in range(len(SAMPLE_OPINIONS3))
            ]
        )
        self.add(game)

        # Let’s start by looking at the first protocol. How can we deal with the fact that the leader can be a traitor? Well, we know that there are at most 2 traitors, so we could try to run the protocol three times in a row, with three different leaders. We know that at least once the leader is going to be honest.

        self.wait()
        for i in range(0, 3):
            self.play(game.generals[i].make_leader(game.generals))

        self.wait()
        self.play(game.generals[2].remove_leader())
        self.wait()
        self.play(Circumscribe(game.generals[1].icon, color=RED))
        self.wait()

        # [u prvního generála se objeví korunka, možná vedle ní něco jako “Phase 1”, pak se posune k druhému generálovi, pak k třetímu “at least once the leader…” -> první a třetí generál jsou řekněme traitoři, highlightujeme toho druhého který je honest]

        # Here is how that would work in detail. Each time, every general sends his current opinion to the leader and then gets a new opinion back. This new opinion is the general’s starting opinion for the next phase. We repeat this three times with three different leaders and the final opinion is the output of every general.

        for i in range(3):
            game.leader_algorithm(self, i, remove_leader_when_done=False)
            self.wait()

        # [
        # provede se algoritmus – třikrát se zopakuje předchozí leader algoritmus. Řekněme že všichni tři generálové jsou honest?
        # ]

        # This protocol still does not work. For example, even if the first two leaders are honest and generals reach consensus, the last leader may be a traitor. He can then break the synchrony again by sending the generals some random junk.

        # [animace obojího]

        # generals change opinions to Y
        for i in range(len(game.generals)):
            if i not in TRAITOR_IDS4:
                self.play(game.generals[i].animate.change_opinion("Y"))

        locks = [
            ImageMobject("img/lock.png")
            .scale_to_fit_width(game.generals[i].icon.get_width() / 1.5)
            .next_to(game.generals[i].icon, RIGHT, buff=-0.3)
            .shift(0.3 * DOWN)
            for i in range(len(game.generals))
            if i not in TRAITOR_IDS4
        ]
        self.play(
            Succession(
                *[FadeIn(lock) for lock in locks],
                lag_ratio=0.3,
            )
        )
        self.play(game.generals[2].make_leader(game.generals))
        self.wait()

        self.play(
            *[FadeOut(lock) for lock in locks],
            game.set_leader(None),
        )
        self.wait()


class SolutionCombine3(Scene):
    def construct(self):
        rng = np.random.default_rng(0)
        game = GameState(
            [
                (
                    CyclicOpinionTraitor(
                        "".join(rng.choice(["Y", "N"]) for _ in range(12))
                    )
                    if i in TRAITOR_IDS4
                    else Player(opinion="Y")
                )
                for i in range(len(SAMPLE_OPINIONS4))
            ]
        )
        self.add(game)

        # We can do this with the help of our second protocol where everybody sends a token to everybody – in the case where all the generals agree on the same value, we will use this protocol to ensure that honest generals ignore the leader’s proposal and keep their initial opinion.

        # run majority algo
        game.majority_algorithm(self)
        self.wait()

        # [není mi jasné]

        # Here’s how we can do that concretely. In each of the three phases, we run both algorithms.
        # So: first, every general sends his opinion to everybody. This allows everybody to compute what we’ll call the majority opinion. Then, the leader of that phase sends his majority opinion back to everybody as the leader’s opinion.

        for i in range(len(game.generals)):
            if i not in TRAITOR_IDS4:
                self.play(game.generals[i].animate.change_opinion(SAMPLE_OPINIONS4[i]))
        code = CodeWithStepping(
            code="""for leader_id in [1, 2, 3]:
    send my opinion to everybody (including myself)
    if I am the leader:  # Algorithm 1
        update opinion to majority of received messages
        broadcast my opinion
    compute number of YES and NO messages # Algorithm 2
    if YES >> NO or NO >> YES:
        update opinion to the majority of received messages
    else:
        update opinion to the opinion of the leader
""",
            language="python",
            font_size=12,
        )

        game.full_algorithm(self, leader_ids=[1], send_to_self=True, code=code)

        # [provedou se obě animace co už známe]

        # So, every general has two proposals for his new opinion: the majority opinion and the leader’s opinion; which one of the two should he choose as the new opinion?

        # [tohle bude brutal na animace, není mi jasné]

        # Before we answer that question, let me write a short pseudocode of our algorithm as it’s no longer that simple. So, each general starts with an opinion. Then, there are three phases. In each phase, the general sends his current opinion to everybody. The leader computes the majority opinion he got and sends it back to everybody.
        # Each general also locally computes the majority opinion.
        # Then, he chooses either the majority opinion or the leader’s opinion as his new opinion and the question is which one to choose.

        # [

        # v ← your initial opinion
        # For i in [1,2,3]:
        # Send v to everybody
        # If you a leader: compute majority and send that to everybody (algorithm 1)
        #     Else: receive leader’s opinion
        # Compute number of YES and NO received messages (algorithm 2),
        #     compute majority opinion
        # if YES >> NO or YES << NO
        # v ←majority opinion
        # otherwise
        # v ← leader’s opinion
        # output v

        # ]

        # The right choice is that whenever a general gets at least 10 YES tokens from other generals, he chooses the majority opinion, and the same for at least 10 NO tokens. This is because whenever all honest generals already agree on the same value, we know that each general receives at least 10 YES or 10 NO tokens. So, this is the case when we want to disregard the leader and just go with the majority.

        # And this is our final algorithm!


# vv: this was named SolutionCombine3, shadowing an earlier class
class SolutionCombine4(Scene):
    def construct(self):
        game = GameState(
            [
                (
                    CyclicOpinionTraitor(
                        "".join(random.choice(["Y", "N"]) for _ in range(12))
                    )
                    if i in TRAITOR_IDS5
                    else Player(opinion=SAMPLE_OPINIONS[i])
                )
                for i in range(len(SAMPLE_OPINIONS5))
            ]
        )
        self.add(game)

        code = CodeWithStepping(
            code="""for leader_id in [1, 2, 3]:
    send my opinion to everybody (including myself)
    if I am the leader:  # Algorithm 1
        update opinion to majority of received messages
        broadcast my opinion
    compute number of YES and NO messages # Algorithm 2
    if YES >> NO or NO >> YES:
        update opinion to the majority of received messages
    else:
        update opinion to the opinion of the leader
""",
            language="python",
            font_size=12,
        )

        game.full_algorithm(self, leader_ids=[0, 1, 2], send_to_self=True, code=code)
        # postprocessing : stopnout na správných místech
