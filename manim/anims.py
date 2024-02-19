# manim -pql --fps 10 -r 290,180 anims.py Polylogo
from pathlib import Path

from manim import *

from utils import util_general
from utils.chat_window import ChatMessage, ChatWindow
from utils.generals import *
from utils.util_cliparts import *
from utils.util_general import *

util_general.disable_rich_logging()

# Vasek's constants for the scenes
SAMPLE_OPINIONS = ["Y", "N", "Y", "N", "Y", "N", "N", "Y", "N", "Y", "N", "Y"]
TRAITOR_IDS = [2, 9]

SAMPLE_OPINIONS2 = ["Y", "N", "Y", "N", "Y", "N", "N", "Y", "Y", "Y", "N", "Y"]
TRAITOR_IDS2 = [2, 4]
SAMPLE_OPINIONS20 = ["Y", "N", "N", "N", "Y", "N", "N", "Y", "Y", "Y", "N", "Y"]
TRAITOR_IDS20 = [8, 10]

SAMPLE_OPINIONS_MANY_Y = ["Y", "N", "Y", "Y", "Y", "N", "N", "Y", "Y", "Y", "Y", "Y"]

SAMPLE_OPINIONS3 = ["N", "N", "Y", "N", "Y", "N", "N", "Y", "N", "N", "N", "Y"]
TRAITOR_IDS3 = [0, 3]

SAMPLE_OPINIONS4 = ["N", "Y", "Y", "N", "Y", "N", "N", "Y", "N", "N", "Y", "Y"]
TRAITOR_IDS4 = [0, 2]


SAMPLE_OPINIONS5 = ["N", "N", "Y", "N", "Y", "N", "N", "Y", "N", "N", "Y", "Y"]
TRAITOR_IDS5 = [0, 2]

# explanation texts

explanation_texts = [
    r"\raggedright \textbf{Input}: YES/NO for every honest general",
    r"\raggedright \textbf{Output}: YES/NO for every honest general",
    r"\raggedright \textbf{Task}: all honest generals output \\ the same answer",
    (
        r"\raggedright \textbf{Condition}: if all generals already started \\"
        r" with the same opinion, they must stick to it"
    ),
]
Path("./media/Tex").mkdir(parents=True, exist_ok=True)
explanations = (
    VGroup(
        *[
            Tex(text, color=TEXT_COLOR).scale(0.75)
            for i, text in enumerate(explanation_texts)
        ]
    )
    .arrange_in_grid(rows=len(explanation_texts), cell_alignment=LEFT, buff=0.4)
    .to_edge(RIGHT, buff=0.5)
    .shift(1 * UP)
)
Group(*explanations[2:]).shift(0.5 * DOWN)


#######################################################

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


shft12 = 2 * LEFT


class Setup1(Scene):
    def construct(self):
        # You can imagine the Byzantine generals' problem as a game played in rounds. In our example, there will be 12 players.

        game = GameState(
            [Player(with_clipart=True) for i in range(len(SAMPLE_OPINIONS))]
        )

        # add the generals from the game one by one,
        self.play(
            LaggedStart(
                *[FadeIn(game.generals[i].clipart) for i in range(len(game.generals))],
                lag_ratio=0.1,
            )
        )
        self.wait(0.5)

        # add numbers 1 to 12 to the generals
        numbers = [
            Tex(str(i + 1), color=TEXT_COLOR)
            .scale(1.5)
            .move_to(
                game.get_center()
                + (game.generals[i].get_center() - game.get_center()) * 1.5
            )
            for i in range(len(game.generals))
        ]
        self.play(LaggedStart(*[FadeIn(n) for n in numbers], lag_ratio=0.1))
        self.wait()

        # fadeout the numbers, again in a lagged way

        self.play(LaggedStart(*[FadeOut(n) for n in numbers], lag_ratio=0.1))
        self.wait()

        # Each player plays one general in a camp outside a city.

        # image of the city
        city = (
            ImageMobject("img/city_3.png")
            .scale(0.8)
            .shift(game.get_center() + UP * 0.1)
        )
        self.play(FadeIn(city))
        self.wait()

        # The generals are trying to conquer the city, but to be successful, they all have to attack at the same time.
        # Also show the "wait" aka "no" option by moving the generals away from the city

        for attack in [True, False]:
            movement = -0.5 if attack else 0.5

            # all generals at once move a bit towards the city, then back
            self.play(
                *[
                    game.generals[i].clipart.animate.shift(
                        movement * game.circle_position(i)
                    )
                    for i in range(len(game.generals))
                ],
            )
            if not attack:
                self.wait(1)

            self.play(
                *[
                    game.generals[i].clipart.animate.shift(
                        -movement * game.circle_position(i)
                    )
                    for i in range(len(game.generals))
                ],
            )
            self.wait()

        # Should they try to attack tomorrow? Every general has some opinion on that

        # we reveal the opinions of generals one by one, each opinion is a letter Y or N in a bubble which is a SVG image
        cliparts = Group(*[game.generals[i].clipart for i in range(len(game.generals))])
        for c in cliparts:
            c.save_state()

        no_bubbles, yes_bubbles, orig_bubbles = [], [], []
        bubbles = []
        shifts = [
            0 * RIGHT,
            0.3 * DOWN,
            0.3 * DOWN,
            0.3 * UP + 0.2 * RIGHT,
            0.2 * RIGHT + 0.2 * UP,
            0 * RIGHT,
            0 * RIGHT,
            0.2 * LEFT + 0.2 * UP,
            0.2 * LEFT + 0.3 * UP,
            0.1 * LEFT + 0.2 * DOWN,
            0.1 * LEFT + 0.1 * DOWN,
            0 * LEFT,
        ]
        for i, opinion in enumerate(SAMPLE_OPINIONS):
            delta = game.generals[i].clipart.get_center() - game.get_center()
            delta = normalize(delta)

            # not very elegant, but it works
            is_right = i in range(6)
            is_up = i in [0, 1, 2, 9, 10, 11]

            def make_message(opinion: str, scale: float):
                return (
                    ChatMessage(
                        sender="",
                        message=opinion,
                        tail_right=not is_right,
                        tail_up=not is_up,
                    )
                    # SVGMobject("img/bubble_say.svg")
                    .scale(scale)
                    .move_to(game.generals[i].clipart.get_center())
                    .shift(
                        0.9 * (UP if is_up else DOWN)
                        + 0.9 * (RIGHT if is_right else LEFT)
                        + shifts[i]
                    )
                )

            bubbles.append(make_message(opinion, scale=0.9))
            no_bubbles.append(make_message(" N", scale=1.1))
            yes_bubbles.append(make_message(" Y", scale=1.1))
            orig_bubbles.append(make_message(opinion, scale=0.9))

        for i in range(len(game.generals)):
            self.add_sound(
                get_sound_effect("click"), time_offset=0.3 * i + CLICK_OFFSET
            )

        self.play(
            LaggedStart(
                *[FadeIn(b) for b in bubbles],
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

        # Turn everybody's opinion into "Y" and show they decided to attack.
        anims = []
        for i in range(len(game.generals)):
            delta = 0.5 * game.circle_position(i)
            anims.append(
                AnimationGroup(
                    bubbles[i].animate.become(yes_bubbles[i]),
                )
            )
        self.play(LaggedStart(*anims))
        self.wait()

        anims = []
        for i in range(len(game.generals)):
            delta = -0.5 * game.circle_position(i)
            anims.append(
                AnimationGroup(
                    bubbles[i].animate.shift(delta),
                    game.generals[i].clipart.animate.shift(delta),
                )
            )
        self.play(AnimationGroup(*anims))
        self.wait()

        anims = []
        for i in range(len(game.generals)):
            anims.append(
                AnimationGroup(
                    bubbles[i].animate.become(orig_bubbles[i]),
                    game.generals[i].clipart.animate.shift(
                        0.5 * game.circle_position(i)
                    ),
                )
            )
        self.play(AnimationGroup(*anims))
        self.wait()

        # Turn everybody's opinion into "N" and show they decided not to attack.
        anims = []
        for i in range(len(game.generals)):
            delta = 0.5 * game.circle_position(i)
            anims.append(
                AnimationGroup(
                    bubbles[i].animate.become(no_bubbles[i]),
                )
            )
        self.play(LaggedStart(*anims))
        self.wait()

        anims = []
        for i in range(len(game.generals)):
            delta = 0.5 * game.circle_position(i)
            anims.append(
                AnimationGroup(
                    bubbles[i].animate.shift(delta),
                    game.generals[i].clipart.animate.shift(delta),
                )
            )
        self.play(AnimationGroup(*anims))
        self.wait()

        anims = []
        for i in range(len(game.generals)):
            anims.append(
                AnimationGroup(
                    bubbles[i].animate.become(orig_bubbles[i]),
                    game.generals[i].clipart.animate.shift(
                        -0.5 * game.circle_position(i)
                    ),
                )
            )
        self.play(AnimationGroup(*anims))
        self.wait()

        # There are two issues that are standing in their way:

        # First, the generals don’t have the option to get together as a group or use some kind of group chat application.
        # all generals shift together to the right where they make a block 4x3

        # Each general has to stay in his camp and in each round, he can only send a direct message to each other general.

        self.play(Group(game, *bubbles, city).animate.shift(shft12))
        self.wait()

        issues_tex = VGroup(
            *[
                Tex(str, color=TEXT_COLOR)
                for str in [
                    "1. Only direct messages",
                    "2. Two traitors",
                ]
            ]
        )
        # align left
        issues_tex.arrange_in_grid(cols=1, cell_alignment=LEFT).to_corner(UR)

        self.play(FadeIn(issues_tex[0]))
        rng = np.random.default_rng(1)
        for it in range(8):
            while True:
                i, j = rng.choice(range(len(game.generals)), size=2, replace=False)
                # the animation looks bad if the generals are too close to each other
                if 2 < abs(max(i, j) - min(i, j)) < 10:
                    break

            game.send_messages_low_tech(
                self,
                [MessageToSend(i, j, Message(SAMPLE_OPINIONS[i], clipart=True))],
            )

        # The second reason why this is going to be hard is that two of the generals are secretly plotting together against the rest - I will call these two traitors. Whatever strategy you come up with for the honest generals to play, the traitors know this strategy and will try to break it.
        # [traitoři jsou generálové kterým narostou rohy, nebo se změní clipart na čertíka]

        # traitor generals are replaced with a traitor image
        self.play(FadeIn(issues_tex[1]))
        self.play(
            *[
                game.generals[id]
                .clipart.animate.scale(1.5)
                .shift(2 * game.circle_position(id))
                for id in TRAITOR_IDS
            ],
            *[FadeOut(bubbles[i]) for i in TRAITOR_IDS],
        )
        self.wait()
        traitor_pics = [
            ImageMobject("img/icon_traitor_2.png")
            .scale_to_fit_width(game.generals[id].clipart.get_width())
            .move_to(game.generals[id].clipart)
            for id in TRAITOR_IDS
        ]
        self.play(
            *[
                game.generals[id].clipart.animate.become(pic)
                for id, pic in zip(TRAITOR_IDS, traitor_pics)
            ],
        )
        self.wait()
        self.play(
            *[
                game.generals[id]
                .clipart.animate.scale(1 / 1.5)
                .shift(-2 * game.circle_position(id))
                for id in TRAITOR_IDS
            ],
        )
        self.wait()

        # create surrounding rectangle around issues
        rec = SurroundingRectangle(issues_tex[0], color=RED)
        self.play(Create(rec))
        self.wait()
        rec2 = SurroundingRectangle(issues_tex[1], color=RED)
        self.play(rec.animate.become(rec2))
        self.wait()


class Setup2(Scene):
    def construct(self):
        # add to the scene the objects that were there at the end of Setup1:

        game = GameState(
            [
                (
                    Player(with_clipart=False, opinion="-")
                    if i not in TRAITOR_IDS
                    else Traitor(with_clipart=False)
                )
                for i in range(len(SAMPLE_OPINIONS))
            ]
        ).shift(4 * LEFT)
        self.add(game)
        self.wait()
        # self.play(game.animate.shift(shft12))
        # self.wait()
        # fade out generals' icons

        # Now let me formalize the problem that the honest generals need to solve. Every honest general starts with an opinion of either YES or NO.

        # every general gets his opinion in succession, also, the first explanation text appears
        self.play(
            AnimationGroup(
                LaggedStart(
                    *[
                        game.generals[i].animate.change_opinion(SAMPLE_OPINIONS[i])
                        for i in range(len(game.generals))
                        if i not in TRAITOR_IDS
                    ],
                    lag_ratio=0.1,
                ),
                FadeIn(explanations[0]),
            )
        )
        self.wait(0.5)

        # The generals then go through several rounds of sending each other messages following some strategy, or protocol.

        # five rounds, in each round every general sends an opinion to every other general:
        # at the top of the scene, there is also counter "Round: x" where x is the round number that increments every round
        # TODO just send envelopes

        counter_tex = (
            Tex("Round: 1", color=TEXT_COLOR)
            .next_to(game, UP, buff=-MED_LARGE_BUFF)
            .move_to(game.get_center())
        )  # .align_to(game, LEFT)
        self.play(FadeIn(counter_tex))
        self.wait(0.5)

        for it in range(3):
            messages = []
            for i in range(len(game.generals)):
                for j in range(len(game.generals)):
                    if i != j:
                        # select random half
                        if random.choice([True, False]):
                            messages.append(
                                MessageToSend(
                                    i, j, Message(SAMPLE_OPINIONS[i], clipart=True)
                                )
                            )

            game.send_messages_low_tech(
                self,
                messages,
            )

            if it < 2:
                self.play(
                    counter_tex.animate.become(
                        Tex(f"Round: {it + 2}", color=TEXT_COLOR)
                        .move_to(counter_tex)
                        .align_to(counter_tex, LEFT)
                    )
                )

            self.wait(0.5)

        # When the protocol finishes, each general outputs his answer which is either YES or NO and which may be different from his initial opinion.
        self.play(
            FadeIn(explanations[1]),
        )
        self.wait()

        # each honest general changes his opinion to "Y"
        self.play(
            *[
                game.generals[i].animate.change_opinion("N")
                for i in range(len(game.generals))
                if i not in TRAITOR_IDS
            ],
            FadeOut(counter_tex),
        )
        game.set_output(self)
        self.wait()
        game.set_input(self)
        self.play(
            *[
                game.generals[i].animate.change_opinion(SAMPLE_OPINIONS[i])
                for i in range(len(game.generals))
                if i not in TRAITOR_IDS
            ],
        )
        self.wait()

        self.play(FadeIn(explanations[2]))
        self.wait()

        # [každý generál má u sebe input i output, traitor asi žádný input/output nemá, ať je jasný co znamená “honest generals”]

        # Every honest general should output the same answer, meaning that the honest generals agreed whether to attack tomorrow.
        # the letters Y are scaled up and then back down
        # self.play(
        #     AnimationGroup(
        #         *[
        #             game.generals[i].opinion_text.animate.scale(1.5)
        #             for i in range(len(game.generals))
        #             if i not in TRAITOR_IDS
        #         ],
        #         FadeIn(explanations[2]),
        #     )
        # )
        # self.wait()
        # # next scale down:
        # self.play(
        #     AnimationGroup(
        #         *[
        #             game.generals[i].opinion_text.animate.scale(1 / 1.5)
        #             for i in range(len(game.generals))
        #             if i not in TRAITOR_IDS
        #         ],
        #     )
        # )
        # self.wait()
        # Our task is to design a protocol under which the generals always manage to reach this consensus.
        # requirement 3 fades in

        # But we need to add one more condition to make the problem non-trivial. Right now, we can use the berserk protocol: don’t look at your input at all, don’t communicate with other generals, and just output YES. Surely, with this strategy, all honest generals output the same answer.

        # # change opinions back to the starting opinions:
        # self.play(
        #     *[
        #         game.generals[i].animate.change_opinion(SAMPLE_OPINIONS[i])
        #         for i in range(len(game.generals))
        #         if i not in TRAITOR_IDS
        #     ],
        # )
        # self.wait()

        # # fadeout all input letters
        # self.play(
        #     *[
        #         game.generals[i].animate.change_opinion("-")
        #         for i in range(len(game.generals))
        #         if i not in TRAITOR_IDS
        #     ],
        # )
        # self.wait()
        code_text_berserk = r"""\# Solution to the Byzantine Generals Problem
def solution():
    print("YES")"""
        code_berserk = (
            CodeWithStepping(code_text=code_text_berserk)
            .scale(0.85)
            .to_corner(DR, buff=0)
            .shift(1.5 * UP)
        )
        # berserk_img = (
        #     Group(
        #         ImageMobject("img/berserk.png").scale_to_fit_height(1.6),
        #         # ImageMobject("img/chad.jpg").scale_to_fit_height(2),
        #     )
        #     .arrange(RIGHT)
        #     .to_corner(DR)
        # )
        self.play(Create(code_berserk))
        self.wait()

        self.play(
            *[
                AnimationGroup(
                    game.generals[i].animate.change_opinion("Y"),
                    game.generals[i]
                    .icon.animate.set_fill(color=GREEN, opacity=0.2)
                    .set_stroke(color=GREEN),
                )
                for i in range(len(game.generals))
                if i not in TRAITOR_IDS
            ],
        )
        game.set_output(self)
        self.wait()

        self.play(FadeOut(code_berserk))
        self.wait()

        # # then, an envelope appears in the middle and then gets crossed
        # envelope = (
        #     ImageMobject("img/envelope_2.png").scale(0.3).move_to(game.get_center())
        # )
        # cross_envelope = Text("×", color=RED, font_size=80).scale(2).move_to(envelope)
        # self.play(FadeIn(envelope))
        # self.wait()
        # self.play(FadeIn(cross_envelope))
        # self.wait()

        # # every general now outputs the same answer
        # self.play(
        #     LaggedStart(
        #         *[
        #             game.generals[i].animate.change_opinion("Y")
        #             for i in range(len(game.generals))
        #             if i not in TRAITOR_IDS
        #         ]
        #     )
        # )
        # # fade out the envelope and the crosses
        # self.play(
        #     FadeOut(envelope),
        #     FadeOut(cross_envelope),
        # )
        # self.wait()

        # To fix this, we’ll explicitly request that if all honest generals start with YES, they all need to output YES at the end. And conversely, if all start with NO, they all need to output NO. In other words, if all generals already agreed at the beginning of the protocol, nobody is going to change their opinion.

        # the letters Y are scaled up and then back down
        # for it in range(2):
        #     self.play(
        #         AnimationGroup(
        #             *[
        #                 game.generals[i].opinion_text.animate.scale(1.5)
        #                 for i in range(len(game.generals))
        #                 if i not in TRAITOR_IDS
        #             ],
        #         )
        #     )
        #     self.wait()
        #     self.play(
        #         AnimationGroup(
        #             *[
        #                 game.generals[i].opinion_text.animate.scale(1 / 1.5)
        #                 for i in range(len(game.generals))
        #                 if i not in TRAITOR_IDS
        #             ],
        #         )
        #     )
        #     self.wait()

        #     if it == 0:
        #         # change opinions to all NO:
        #         self.play(
        #             *[
        #                 game.generals[i].animate.change_opinion("N")
        #                 for i in range(len(game.generals))
        #                 if i not in TRAITOR_IDS
        #             ],
        #         )

        game.set_input(self)
        self.play(
            *[
                game.generals[i].animate.change_opinion("N")
                for i in range(len(game.generals))
                if i not in TRAITOR_IDS
            ],
        )
        game.set_output(self)
        self.wait()

        # add the third explanation text
        self.play(FadeIn(explanations[3]))
        self.wait()

        # revert back the opinions of generals
        game.set_input(self)
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
        # rec = SurroundingRectangle(explanations[2], color=RED)
        # self.play(Create(rec))
        # self.wait()
        # self.play(Transform(rec, SurroundingRectangle(explanations[3], color=RED)))
        # self.wait()
        # self.play(FadeOut(rec))
        # self.wait()

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


title_scale = 0.9


class Solution1(Scene):
    def construct(self):
        title = (
            Tex("1. Leader-based algorithm", color=TEXT_COLOR)
            .scale(title_scale)
            .to_corner(UL)
        )
        # create a game with no traitors
        game = GameState(
            [Player(opinion="-") for i in range(len(SAMPLE_OPINIONS2))],
            shft={0: 1 * RIGHT + 0.5 * DOWN},
        )
        self.play(
            *[FadeIn(game.generals[i]) for i in range(len(game.generals))],
            FadeIn(title),
        )
        self.wait()
        # generals get their starting opinion

        game.set_opinions(self, SAMPLE_OPINIONS2)
        self.wait()

        # Solution 1
        game.leader_algorithm(self, 0)
        self.wait()

        # change opinions back
        game.set_input(self)
        game.set_opinions(self, SAMPLE_OPINIONS2)
        self.wait()

        rng = np.random.default_rng(3)

        # This protocol surely works if there are no traitors, but if we are unlucky and choose a traitor as the leader, he gets a complete control over the output of honest generals, a spectacular failure!

        for i in TRAITOR_IDS3:
            game.change_general(self, i, CyclicOpinionTraitor("YYYYYYYNNNNN"))

        game.leader_algorithm(self, 0)
        self.wait()

        # [ukáže se jak traitor dostane korunku a pak pošle někomu YES a někomu NO]

        # But let’s look on the bright side! If we could somehow ensure that the leader is honest, this protocol would work really well.

        # change opinions back
        # for i in TRAITOR_IDS3:
        #     game.change_general(
        #         self, i, CyclicOpinionTraitor("Y"), with_animation=False
        #     )
        # game.set_opinions(self, SAMPLE_OPINIONS3)

        # self.wait()

        # Notice that the output of the protocol is not necessarily the majority opinion of honest generals, because the traitors also get to vote,

        # game.leader_algorithm(self, 2)
        # self.wait()

        # but fortunately, we only want to ensure this weaker condition, which is satisfied.
        # shift the game to the left, then reveal explanations

        # self.play(
        #     game.animate.to_edge(LEFT, buff=-1),
        #     FadeIn(explanations),
        # )
        # self.wait()
        # self.play(FadeIn(SurroundingRectangle(explanations[3], color=RED)))
        # self.wait(5)


class Solution2(Scene):
    def construct(self):
        # So, how can we approach the problem? Well, let’s first see how we could solve it if there were no traitors at all and understand how those approaches fail.
        title = (
            Tex("2. Local algorithm", color=TEXT_COLOR).scale(title_scale).to_corner(UL)
        )
        # create a game with no traitors
        game = GameState([Player("-") for i in range(len(SAMPLE_OPINIONS2))])
        self.play(
            *[FadeIn(game.generals[i]) for i in range(len(game.generals))],
            FadeIn(title),
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

        game.local_algorithm(self)
        self.wait()
        # game.set_input(self)
        # self.wait()

        # [“7 YES messages” circubscribe 7 YES tokenů u každého generála]

        rng = np.random.default_rng(0)

        game_with_traitors = GameState(
            [
                (
                    CyclicOpinionTraitor("YYYYYYNNNNNN")
                    if i in TRAITOR_IDS20
                    else Player(opinion=SAMPLE_OPINIONS20[i])
                )
                for i in range(len(SAMPLE_OPINIONS2))
            ]
        )

        anims = []
        for i in range(len(game.generals)):
            # if i not in TRAITOR_IDS2:
            #     anims.append(
            #         game.generals[i].animate.change_opinion(SAMPLE_OPINIONS2[i])
            #     )
            # else:
            anims.append(
                AnimationGroup(
                    FadeOut(game.generals[i]),
                    FadeIn(game_with_traitors.generals[i]),
                )
            )
        for i in range(12):
            self.add_sound(
                get_sound_effect("click"), time_offset=0.05 * i + CLICK_OFFSET
            )

        self.play(LaggedStart(*anims, lag_ratio=0.05))
        for i in range(len(game.generals)):
            if i not in TRAITOR_IDS20:
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

        game.local_algorithm(self, second=True)
        self.wait()

        # [ukáže se jak traitoři pošlou nejdřív YES tokeny některým, pak NO tokeny zbylým (sobě traitoři nepošlou nic)]
        # This leads to some generals outputting YES, and some generals outputting NO. So, this simple protocol fails.

        # highlight generals with output Y, then N
        for opinion in ["Y", "N"]:
            game.highlight_generals_with_opinion(self, opinion=opinion)
            self.wait()

        # [obtáhnou se ti co outputnou YES, je vidět že jejich YES kopička je větší než NO kopička, pak to samé s NO]
        # But let’s look on the bright side – the protocol only fails if the initial opinion of the honest generals was roughly split. If at least 7 honest generals start with the YES opinion, then this protocol works well.

        game.set_input(self)
        game.set_opinions(self, SAMPLE_OPINIONS_MANY_Y)

        self.wait()

        # we show numbers 1,2, ... next to generals with Y
        numbers = []
        num = 0
        anims = []
        for i in range(len(game.generals)):
            if i not in TRAITOR_IDS20 and SAMPLE_OPINIONS_MANY_Y[i] == "Y":
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

        # game.local_algorithm(self)
        # self.wait()


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
        rec = SurroundingRectangle(
            Group(game.generals[0].icon, game.generals[2].icon), color=RED
        )
        self.play(Create(rec))
        self.wait()
        self.play(FadeOut(rec))
        self.wait()

        # [u prvního generála se objeví korunka, možná vedle ní něco jako “Phase 1”, pak se posune k druhému generálovi, pak k třetímu “at least once the leader…” -> první a třetí generál jsou řekněme traitoři, highlightujeme toho druhého který je honest]

        # Here is how that would work in detail. Each time, every general sends his current opinion to the leader and then gets a new opinion back. This new opinion is the general’s starting opinion for the next phase. We repeat this three times with three different leaders and the final opinion is the output of every general.

        for i in range(3):
            game.leader_algorithm(
                self,
                i,
                remove_leader_when_done=(i == 2),
                add_background_at_the_end=(i == 2),
            )
            self.wait()
        game.set_input(self)
        # fade out the crown

        arrow = (
            ImageMobject("img/arrow.png")
            .scale(0.2)
            .rotate(PI)
            .next_to(game.generals[1].icon, RIGHT, buff=0.3)
        )
        self.play(FadeIn(arrow))
        self.wait()
        self.play(arrow.animate.next_to(game.generals[2].icon, RIGHT, buff=0.5))
        self.wait()
        self.play(FadeOut(arrow))
        self.wait()

        # [
        # provede se algoritmus – třikrát se zopakuje předchozí leader algoritmus. Řekněme že všichni tři generálové jsou honest?
        # ]

        # This protocol still does not work. For example, even if the first two leaders are honest and generals reach consensus, the last leader may be a traitor. He can then break the synchrony again by sending the generals some random junk.

        # [animace obojího]

        # generals change opinions to Y
        game.set_opinions(self, ["Y"] * len(game.generals))

        locks = [
            ImageMobject("img/lock.png")
            .scale_to_fit_width(game.generals[i].icon.width / 1.5)
            .next_to(game.generals[i].icon, RIGHT, buff=-0.5)
            .shift(0.3 * DOWN)
            for i in range(len(game.generals))
            if i not in TRAITOR_IDS4
        ]
        self.add_sound("audio/lock.wav")

        # For some reason, LaggedStart + FadeIn only fades in the first lock
        # and the others appear instantly. Let's just fade them all in at once.
        self.play(*[FadeIn(lock) for lock in locks])

        self.play(game.generals[2].make_leader(game.generals))
        self.wait()

        self.play(
            *[FadeOut(lock) for lock in locks],
            game.set_leader(None),
        )
        self.wait()


# class FullSolutionWithoutCode(Scene):
#     def construct(self):
#         rng = np.random.default_rng(0)
#         game = GameState(
#             [
#                 (
#                     CyclicOpinionTraitor(
#                         "".join(rng.choice(["Y", "N"]) for _ in range(12))
#                     )
#                     if i in TRAITOR_IDS4
#                     else Player(opinion="-")
#                 )
#                 for i in range(len(SAMPLE_OPINIONS4))
#             ]
#         )
#         self.add(game)
#         game.set_opinions(self, SAMPLE_OPINIONS4)

#         # Here’s how we can do that concretely. In each of the three phases, we run both algorithms.
#         # So: first, every general sends his opinion to everybody. This allows everybody to compute what we’ll call the majority opinion. Then, the leader of that phase sends his majority opinion back to everybody as the leader’s opinion.

#         game.full_algorithm(self, leader_ids=[1], send_to_self=True, code=None)


class FullSolutionDecisionRule(MovingCameraScene):
    def construct(self):
        rng = np.random.default_rng(0)
        game = GameState(
            [
                (
                    CyclicOpinionTraitor("NNNYYYNNYYNY")
                    if i in TRAITOR_IDS4
                    else Player(opinion="-")
                )
                for i in range(len(SAMPLE_OPINIONS4))
            ]
        )
        self.add(game)
        game.set_opinions(self, SAMPLE_OPINIONS4)

        # Here’s how we can do that concretely. In each of the three phases, we run both algorithms.
        # So: first, every general sends his opinion to everybody. This allows everybody to compute what we’ll call the majority opinion. Then, the leader of that phase sends his majority opinion back to everybody as the leader’s opinion.

        game.full_algorithm(
            self, leader_ids=[1], send_to_self=True, code=None, early_stop=True
        )
        self.wait()

        self.play(
            self.camera.auto_zoom(
                game.generals[3].thinking_buffer.messages, margin=0.7
            ),
            FadeOut(game),
        )
        self.wait()
        game.generals[3].play_decision_rule_example(self)
        # self.add(message)
        self.wait()


class FullSolutionWithCode(Scene):
    def construct(self):
        rng = np.random.default_rng(0)

        players = [Player(opinion="Y") for i in range(12)]
        # The traitors should be yes-leaning so that we have mostly YES opinions
        # coming into the second round. Then in the second round, some players should
        # use the majority opinion and some should use the leader's opinion (though
        # in both cases they'll choose YES).
        # Finally, in the third round there should be a varying number of NO opinions
        # sent by the traitors to illustrate that they can behave arbitrarily.
        players[0] = CyclicOpinionTraitor("NNNYNYYNYYNYYNYYYYNYYNYYYYNNNYYYNNYYYYYYYY")
        players[2] = CyclicOpinionTraitor(
            "YYNYYNYNYYNNYYYNNYYYNYYNNYYNYYNYNYNNNNNNNNYNNYYYY"
        )
        #
        game = GameState(players)

        code = CodeWithStepping(font_size=24)

        self.play(Create(code, run_time=10))
        self.wait()

        self.play(code.animate.scale(0.8).to_corner(UL, buff=0))

        game.shift(3.3 * RIGHT)
        self.play(FadeIn(game))
        game.set_opinions(self, SAMPLE_OPINIONS4)
        self.wait()

        game.full_algorithm(
            self, leader_ids=[0, 1, 2], send_to_self=True, code=code, stops=True
        )


class ImportanceSectionTitle(Scene):
    def construct(self):
        title = Tex(r"Importance", color=text_color)
        title.scale(4)
        self.play(Write(title))
        self.wait()
        self.play(Unwrite(title))
        self.wait()


class FirstSolutionTitle(Scene):
    def construct(self):
        title = Tex(r"First Solution", color=text_color)
        title.scale(4)
        self.play(Write(title))
        self.wait()
        self.play(Unwrite(title))
        self.wait()


class SecondSolutionTitle(Scene):
    def construct(self):
        title = Tex(r"Blockchain-based Solution", color=text_color)
        title.scale(4)
        self.play(Write(title))
        self.wait()
        self.play(Unwrite(title))
        self.wait()


class WrapupTitle(Scene):
    def construct(self):
        title = Tex(r"Wrap-up", color=text_color)
        title.scale(4)
        self.play(Write(title))
        self.wait()
        self.play(Unwrite(title))
        self.wait()


class Thumbnail(Scene):
    def construct(self):
        self.add(
            Text("Byzantine Generals", color=TEXT_COLOR).scale(2.3).shift(UP * 2.5)
        )
        player1 = (
            Player(with_clipart=True).set_color(GREEN).shift(LEFT * 5 + DOWN).scale(2)
        )
        self.add(player1)
        self.add(
            ChatMessage(sender="", message="YES")
            .scale(2)
            .next_to(player1, RIGHT)
            .shift(UP)
        )

        player2 = (
            Player(with_clipart=True).set_color(RED).shift(RIGHT * 5 + DOWN).scale(2)
        )
        self.add(player2)
        self.add(
            ChatMessage(sender="", message="NO", tail_right=True)
            .scale(2)
            .next_to(player2, LEFT)
            .shift(UP)
        )


class Final(Scene):
    def construct(self):
        thanks_text = "Big thanks to everyone who gave us feedback on an early version of this video!"
        patrons_thanks_text = "Our amazing Patrons:"
        patrons_text = [
            "George Chahir",
            "Adam Dřínek",
            "Anh Dung Le",
            "Hugo Madge León",
            "George Mihaila",
            "Amit Nambiar",
            "George Ronides",
            "sjbtrn",
            "Tomáš Sláma",
            "Pepa Tkadlec",
        ]
        support_tex = "Thank you for your support!"

        thanks_tex = Tex(thanks_text, color=TEXT_COLOR).scale(0.8).to_edge(UP)
        patrons_thanks_tex = (
            Tex(patrons_thanks_text, color=TEXT_COLOR)
            .scale(0.8)
            .next_to(thanks_tex, DOWN, buff=1)
        )
        patrons_tex = (
            VGroup(*[Tex(t, color=TEXT_COLOR).scale(0.8) for t in patrons_text])
            .arrange_in_grid(cell_alignment=LEFT)
            .next_to(patrons_thanks_tex, DOWN, buff=0.5)
        )
        support_tex = (
            Tex(support_tex, color=TEXT_COLOR)
            .scale(1.2)
            .next_to(patrons_tex, DOWN, buff=1)
        )
        self.add(patrons_thanks_tex, patrons_tex, support_tex)
        self.wait(5)
