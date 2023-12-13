# manim -pql --fps 10 -r 290,180 anims.py Polylogo
from random import randrange
from re import I
from unittest import skip
from manim import config as global_config
from manim import *
from icecream import ic
from utils.util_general import *
from collections import namedtuple
from typing import Any, List

from utils.util_cliparts import *

MsgType = namedtuple("MsgType", ["sender_id", "receiver_id", "message"])

GENERAL_RADIUS = 0.5

GENERAL_CIRCLE_SIZE = 2.2
GENERAL_THINKING_BUFFER_RADIUS = 3.5
GENERAL_RECEIVE_BUFFER_RADIUS = 1.3

CROWN_SVG = "img/crown.svg"
CROWN_OFFSET = 1.1  # How much is the crown shifted up from the icon

MESSAGE_RADIUS = 0.05

MESSAGE_BUFFER_COLUMNS = 2
MESSAGE_BUFFER_HORIZONTAL_OFFSET = 0.45
MESSAGE_BUFFER_VERTICAL_OFFSET = 0.3

# Messages are received in a circle with this radius
RECEIVE_BUFFER_CIRCULAR_RADIUS = 0.23

# Vasek's constants for the scenes
SAMPLE_OPINIONS = ["Y", "N", "Y", "N", "Y", "N", "N", "Y", "N", "Y", "N", "Y"]
GAME_SHIFT = 2 * LEFT
TRAITOR_IDS = [3, 5]

SAMPLE_OPINIONS2 = ["Y", "N", "Y", "N", "Y", "N", "N", "Y", "Y", "Y", "N", "Y"]
TRAITOR_IDS2 = [2, 4]

SAMPLE_OPINIONS_MANY_Y = ["Y", "N", "Y", "Y", "Y", "N", "N", "Y", "Y", "Y", "Y", "Y"]

SAMPLE_OPINIONS3 = ["N", "N", "Y", "N", "Y", "N", "N", "Y", "N", "N", "N", "Y"]
TRAITOR_IDS3 = [1,3]

SAMPLE_OPINIONS4 = ["N", "N", "Y", "N", "Y", "N", "N", "Y", "N", "N", "Y", "Y"]
TRAITOR_IDS4 = [0, 2]

# explanation texts
explanation_texts = [
    r"\raggedright Input: YES/NO for every honest general",
    r"\raggedright Output: YES/NO for every honest general",
    r"\raggedright Task: all honest generals output \\ the same answer",
    r"\raggedright Condition: if all generals agreed \\ at the beginning, nobody changes opinion"
]
explanations = VGroup(
    *[Tex(text, color = TEXT_COLOR).scale(0.75) for i, text in enumerate(explanation_texts)]
).arrange_in_grid(rows = len(explanation_texts), cell_alignment=LEFT).to_edge(RIGHT, buff = 0.5)
Group(*explanations[2:]).shift(0.5 * DOWN)



class Message(Group):
    def __init__(self, message: str, clipart = False):
        super().__init__()
        self.message = message
        self.color = RED if message == "N" else GREEN
        self.icon = Circle(
            radius=MESSAGE_RADIUS,
            color=self.color,
            stroke_width=2,
            fill_color=self.color,
            fill_opacity=1,
        )
        self.add(self.icon)
        if clipart == True:
            self.clipart = ImageMobject("img/envelope.png").scale(0.2)
            self.add(self.clipart)

class Crown(SVGMobject):
    def __init__(self, parent: Mobject):
        super().__init__(CROWN_SVG)
        self.scale(parent.width / self.width)
        self.move_to(parent)
        self.shift(UP * (parent.height / 2 + self.height / 2) * CROWN_OFFSET)


class LeaderMessage(Message):
    def __init__(self, message: str):
        super().__init__(message)
        self.crown = Crown(self)
        self.add(self.crown)


class MessageBuffer(Group):
    def __init__(self):
        super().__init__()
        self.messages = []
        self.icon = Rectangle(width=1, height=1, stroke_opacity=0.0).scale(0.75)
        self.add(self.icon)

    def add_msg(self, msg: Message):
        self.messages.append(msg)

    def count_regular_opinions(self):
        opinions = [
            msg.message for msg in self.messages if not isinstance(msg, LeaderMessage)
        ]
        return opinions.count("Y"), opinions.count("N")

    def sort_messages(self):
        # Reorganize the messages by the opinion they carry
        anims = []
        y_cnt, n_cnt = 0, 0
        message_spacing = 3 * MESSAGE_RADIUS  # 2 * radius + spacing
        for msg in self.messages:
            if isinstance(msg, LeaderMessage):
                # Leader messages are not sorted, they are just shifted up
                # to make space for the inequality symbol.
                anims.append(msg.animate.shift(UP * MESSAGE_BUFFER_VERTICAL_OFFSET))
                continue
            if msg.message == "Y":
                row = y_cnt // MESSAGE_BUFFER_COLUMNS
                col = y_cnt % MESSAGE_BUFFER_COLUMNS
                pos = (
                    self.get_center()
                    + LEFT * MESSAGE_BUFFER_HORIZONTAL_OFFSET
                    + UP * MESSAGE_BUFFER_VERTICAL_OFFSET
                    + row * message_spacing * DOWN
                    + col * message_spacing * RIGHT
                )
                y_cnt += 1
            elif msg.message == "N":
                row = n_cnt // MESSAGE_BUFFER_COLUMNS
                col = n_cnt % MESSAGE_BUFFER_COLUMNS
                pos = (
                    self.get_center()
                    + RIGHT * MESSAGE_BUFFER_HORIZONTAL_OFFSET
                    + UP * MESSAGE_BUFFER_VERTICAL_OFFSET
                    + row * message_spacing * DOWN
                    + col * message_spacing * LEFT
                )
                n_cnt += 1
            else:
                raise Exception("Invalid message")
            anims.append(msg.animate.move_to(pos))
        return anims


class General(Group):
    def __init__(self):
        super().__init__()
        self.is_leader = False

    def make_leader(self, scene: Scene):
        assert not self.is_leader
        self.is_leader = True
        self.crown = Crown(self.icon)
        scene.play(FadeIn(self.crown))

    def remove_leader(self, scene: Scene):
        assert self.is_leader
        self.is_leader = False
        scene.play(FadeOut(self.crown))

    def add_receive_buffer(self, buffer: MessageBuffer):
        self.receive_buffer = buffer
        self.add(buffer)

    def add_thinking_buffer(self, buffer: MessageBuffer):
        self.thinking_buffer = buffer
        self.add(buffer)

    def move_receive_buffer_to_thinking_buffer(self):
        # Traitors don't move their receive buffer to the thinking buffer,
        # they just discard the messages.
        if self.is_traitor:
            anims = [FadeOut(msg) for msg in self.receive_buffer.messages]
            self.receive_buffer.messages = []
            return anims

        receive_to_thinking = (
            self.thinking_buffer.get_center() - self.receive_buffer.get_center()
        )
        anims = [
            msg.animate.shift(receive_to_thinking)
            for msg in self.receive_buffer.messages
        ]
        self.thinking_buffer.messages += self.receive_buffer.messages
        self.receive_buffer.messages = []
        return anims

    def update_opinion_to_majority(self, scene: Scene):
        thinking_buffer = self.thinking_buffer
        scene.play(*thinking_buffer.sort_messages())
        msgs = thinking_buffer.messages

        y_cnt, n_cnt = thinking_buffer.count_regular_opinions()
        win = "Y" if y_cnt >= n_cnt else "N"

        inequality_symbol = Tex("$\ge$" if win == "Y" else "$<$", color=BLACK)
        inequality_symbol.move_to(thinking_buffer.get_center())
        scene.play(FadeIn(inequality_symbol))

        new_opinion = Message(win).scale(4)  # Make the new opinion 4x bigger
        new_opinion.move_to(inequality_symbol)

        scene.play(
            *[msg.animate.move_to(new_opinion) for msg in msgs],
            inequality_symbol.animate.become(new_opinion.icon),
        )
        self.thinking_buffer.messages = []
        scene.remove(inequality_symbol, *msgs)
        return new_opinion

    def update_opinion_to_supermajority_or_leader(self, scene: Scene):
        thinking_buffer = self.thinking_buffer
        scene.play(*thinking_buffer.sort_messages())
        msgs = thinking_buffer.messages

        leader_msg = list(filter(lambda msg: isinstance(msg, LeaderMessage), msgs))
        assert len(leader_msg) == 1
        leader_msg = leader_msg[0]

        y_msgs = filter(
            lambda msg: not isinstance(msg, LeaderMessage) and msg.message == "Y", msgs
        )
        n_msgs = filter(
            lambda msg: not isinstance(msg, LeaderMessage) and msg.message == "N", msgs
        )

        y_cnt, n_cnt = thinking_buffer.count_regular_opinions()
        if n_cnt <= 2:
            win = "Y"
            tex = "$\gg$"  # Supermajority
        elif y_cnt <= 2:
            win = "N"
            tex = "$\ll$"  # Supermajority
        else:
            win = leader_msg.message
            tex = "$\\approx$"

        inequality_symbol = Tex(tex, color=BLACK).scale(0.8)
        inequality_symbol.move_to(thinking_buffer.get_center())
        scene.play(FadeIn(inequality_symbol))

        new_opinion = Message(win).scale(4)  # Make the new opinion 4x bigger
        new_opinion.move_to(inequality_symbol)

        if n_cnt <= 2:
            anims = (
                [msg.animate.move_to(new_opinion) for msg in y_msgs]
                + [FadeOut(msg) for msg in n_msgs]
                + [FadeOut(leader_msg)]
            )
        elif y_cnt <= 2:
            anims = (
                [msg.animate.move_to(new_opinion) for msg in n_msgs]
                + [FadeOut(msg) for msg in y_msgs]
                + [FadeOut(leader_msg)]
            )
        else:
            anims = (
                [leader_msg.animate.move_to(new_opinion)]
                + [FadeOut(msg) for msg in y_msgs]
                + [FadeOut(msg) for msg in n_msgs]
            )

        scene.play(
            *anims,
            inequality_symbol.animate.become(new_opinion.icon),
        )
        self.thinking_buffer.messages = []
        scene.remove(inequality_symbol, *msgs)
        return new_opinion


class Player(General):
    def __init__(self, opinion: str = "", no_icon = True):
        super().__init__()
        self.opinion = opinion
        self.is_traitor = False
        self.icon = Circle(radius=GENERAL_RADIUS)
        self.opinion_text = Tex(opinion)
        self.change_opinion(opinion)
        self.add(self.opinion_text)
        self.add(self.icon)

        if not no_icon:
            self.clipart = ImageMobject("img/general.png").scale(0.5)
            self.add(self.clipart)

    def get_color(self):
        return GREEN if self.opinion == "Y" else RED if self.opinion == "N" else GRAY if self.opinion == "-" else PINK#"#333" # TODO weird thing here

    def change_opinion(self, opinion: str):
        self.opinion = opinion
        color = self.get_color()


        new_opinion_text = Tex(opinion, color=color)
        new_opinion_text.move_to(self.icon)
        self.opinion_text.become(new_opinion_text)
        self.icon.set_stroke(color=color, opacity=1)
        

class Traitor(General):
    def __init__(self, no_icon = True):
        super().__init__()
        self.is_traitor = True

        # TODO I am getting a weird error saying that some transition functions don't know this color
        #color = "#333"
        color = PINK
        self.icon = Circle(
            radius=GENERAL_RADIUS, color=color, fill_color=color, fill_opacity=1
        )
        self.add(self.icon)

        if not no_icon:
            self.clipart = ImageMobject("img/general.png").scale(0.5)
            self.add(self.clipart)

    
    def change_opinion(self, opinion: str):
        pass


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


class CodeWithStepping(Code):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.indicator = None
        self.rectangle = None

    def indicator_position(self, line_number: int):
        return self.line_numbers[line_number].get_right() + 0.25 * LEFT

    def rectangle_around_line(self, line_number: int):
        line = self.code[line_number]
        offset = 0 if line_number == 0 else 0.03
        return Rectangle(
            width=line.width + 0.2,
            height=line.height - offset + 0.02,
            color=RED,
        ).move_to(line.get_center() + offset * DOWN)

    def highlight_line(self, line_number: int, scene: Scene):
        if self.indicator is not None:
            new_rectangle = self.rectangle_around_line(line_number)
            scene.play(
                self.indicator.animate.move_to(self.indicator_position(line_number)),
                self.rectangle.animate.become(new_rectangle),
            )
        else:
            self.indicator = Arrow(
                start=self.indicator_position(line_number),
                end=self.indicator_position(line_number) + 0.1 * RIGHT,
                color=RED,
                max_tip_length_to_length_ratio=1,
            )
            self.indicator.move_to(self.indicator_position(line_number))
            self.rectangle = self.rectangle_around_line(line_number)
            scene.add(self.indicator, self.rectangle)


class GameState(Group):
    def __init__(self, generals: List[General]):
        super().__init__()
        self.generals = generals
        # Distribute generals in a circle
        for i in range(len(self.generals)):
            # Create the ith general
            g = self.generals[i]
            g.shift(self.circle_position(i) * GENERAL_CIRCLE_SIZE)
            self.add(g)
            # Create the ith general's message buffer
            receive_buffer = MessageBuffer()
            receive_buffer.shift(
                self.circle_position(i) * GENERAL_RECEIVE_BUFFER_RADIUS
            )
            g.add_receive_buffer(receive_buffer)
            # Create the ith general's thinking buffer
            thinking_buffer = MessageBuffer()
            thinking_buffer.shift(
                self.circle_position(i) * GENERAL_THINKING_BUFFER_RADIUS
            )
            g.add_thinking_buffer(thinking_buffer)

    #TODO pls check
    def change_general(self, scene: Scene, i: int, new_general: General):
        """
        Replace the ith general with a new general.
        """
        new_general.shift(self.circle_position(i) * GENERAL_CIRCLE_SIZE)
        
        scene.play(
            FadeOut(self.generals[i]),
            FadeIn(new_general)
        )
        scene.wait()
        
        self.remove(self.generals[i])
        self.generals[i] = new_general
        self.add(new_general)

        receive_buffer = MessageBuffer()
        receive_buffer.shift(
            self.circle_position(i) * GENERAL_RECEIVE_BUFFER_RADIUS
        )
        new_general.add_receive_buffer(receive_buffer)
        
        thinking_buffer = MessageBuffer()
        thinking_buffer.shift(
            self.circle_position(i) * GENERAL_THINKING_BUFFER_RADIUS
        )
        new_general.add_thinking_buffer(thinking_buffer)

    def circle_position(self, i: int):
        """
        Return the position of the ith general in the circle.
        """
        # Shift the index by 1 so that the generals are numbered like clocks
        ii = (i + 1) % len(self.generals)
        x = np.sin(ii * 2 * np.pi / len(self.generals))
        y = np.cos(ii * 2 * np.pi / len(self.generals))
        return x * RIGHT + y * UP


    def send_messages_low_tech(
        self,
        scene: Scene,
        messages: List[MsgType],
        #lag_ratio = 0,
    ):
        """
        Sends messages from the sender to the receiver.
        Only cliparts are shown, no additional info. 
        Returns an AnimationGroup
        """
        
        for message in messages:
            sender = self.generals[message.sender_id]
            receiver = self.generals[message.receiver_id]
            msg = message.message.clipart

            msg.move_to(sender)

            scene.play(
                GrowFromCenter(msg)
            )
            scene.wait(0.5)
            scene.play(
                msg.animate.move_to(receiver)
            )
            scene.wait(0.5)
            scene.play(
                msg.animate.scale(0)
            )
            scene.wait(0.5)

        


    def send_messages(
        self,
        scene: Scene,
        messages: List[MsgType],
        circular_receive=False,
        circular_send=False,
    ):
        """
        Send messages from the sender to the receiver.
        If circular_receive is True, the messages are received in the receive buffer
        in the same layout as the generals are positioned in the circle.
        """
        msg_objects = []
        anims_msg_creation = []
        anims = []
        to_remove = []
        for message in messages:
            sender = self.generals[message.sender_id]
            receiver = self.generals[message.receiver_id]
            msg = message.message
            if sender.is_traitor:
                # Make the message border black if the sender is a traitor
                # to indicate that the message is not trustworthy.
                msg.icon.stroke_color = BLACK

            if circular_send:
                # Before sending, messages are aligned around the sender's icon,
                # corresponding to which receiver they are sent to.
                msg.move_to(
                    sender.icon.get_center()
                    + self.circle_position(message.receiver_id) * GENERAL_RADIUS
                )
            else:
                # Messages are sent from the sender's position to the receiver's buffer
                #TODO hlasilo chybu
                #msg.move_to(sender.receive_buffer)
                msg.move_to(sender.icon.get_center())

            # Make the message icon appear from the sender's icon
            sender_icon_copy = sender.icon.copy()
            sender_icon_copy.fill_color = sender_icon_copy.stroke_color
            sender_msg_copy = msg.icon.copy()
            to_remove.append(sender_icon_copy)
            to_remove.append(sender_msg_copy)
            anims_msg_creation.append(sender_icon_copy.animate.become(sender_msg_copy))

            msg_objects.append(msg)
            # Animate the message moving from the sender to the receiver.
            if circular_receive:
                # Arange the messages in the buffer in the same circle as the generals from
                # which they were sent.
                receive_location = (
                    receiver.receive_buffer.get_center()
                    + self.circle_position(message.sender_id)
                    * RECEIVE_BUFFER_CIRCULAR_RADIUS
                )
            else:
                receive_location = receiver.receive_buffer.get_center()
            anims.append(msg.animate.move_to(receive_location))
            receiver.receive_buffer.add_msg(msg)
        scene.play(*anims_msg_creation)
        scene.remove(*to_remove)
        scene.add(*msg_objects)
        scene.play(*anims)
        return msg_objects

    def broadcast_opinion(
        self,
        scene: Scene,
        general_ids: int,
        send_to_self=False,
        circular_receive=False,
        circular_send=False,
        msg_class=Message,
    ):
        messages = []
        for general_id in general_ids:
            for i in range(len(self.generals)):
                if i != general_id or send_to_self:
                    messages.append(
                        MsgType(
                            general_id, i, msg_class(self.generals[general_id].opinion)
                        )
                    )
        return self.send_messages(
            scene,
            messages,
            circular_receive=circular_receive,
            circular_send=circular_send,
        )

    def send_opinions_to(
        self, scene: Scene, general_id: int, send_to_self: bool = False
    ):
        messages = []
        for i in range(len(self.generals)):
            if send_to_self or i != general_id:
                messages.append(
                    MsgType(i, general_id, Message(self.generals[i].opinion))
                )
        return self.send_messages(scene, messages, circular_receive=True)

    def update_general_opinions(
        self, scene: Scene, general_ids: List[int], opinions: List[Message]
    ):
        anims = []
        new_icons = []
        for general_id, opinion in zip(general_ids, opinions):
            new_icon = self.generals[general_id].icon.copy()
            if not self.generals[general_id].is_traitor:
                new_icon.color = opinion.color
            new_icons.append(new_icon)

            anims.append(
                self.generals[general_id].animate.change_opinion(opinion.message)
            )
            anims.append(opinion.icon.animate.become(new_icon))
        scene.play(*anims)
        scene.remove(*opinions, *new_icons)

    def leader_algorithm(self, scene: Scene, leader_id: int, send_to_self: bool = True):
        self.generals[leader_id].make_leader(scene)

        scene.wait(0.5)

        msgs = self.send_opinions_to(scene, leader_id, send_to_self)

        scene.wait(0.5)

        scene.play(*self.generals[leader_id].move_receive_buffer_to_thinking_buffer())
        if not self.generals[leader_id].is_traitor:
            new_opinion = self.generals[leader_id].update_opinion_to_majority(scene)
            self.update_general_opinions(scene, [leader_id], [new_opinion])

        # Whether it's a trator or not, the leader broadcasts the decision
        msgs = self.broadcast_opinion(scene, [leader_id], msg_class=LeaderMessage)

        self.update_general_opinions(
            scene,
            [i for i in range(len(self.generals)) if i != leader_id],
            msgs,
        )

        self.generals[leader_id].remove_leader(scene)

    def majority_algorithm(self, scene: Scene, send_to_self: bool = True):
        for i in range(len(self.generals)):
            self.send_opinions_to(scene, i, send_to_self)
            scene.play(*self.generals[i].move_receive_buffer_to_thinking_buffer())
        for i in range(len(self.generals)):
            if self.generals[i].is_traitor:
                continue
            new_opinion = self.generals[i].update_opinion_to_majority(scene)
            self.update_general_opinions(scene, [i], [new_opinion])

    def move_all_receive_buffers_to_thinking_buffers(self, scene: Scene):
        anims = []
        for general in self.generals:
            anims.extend(general.move_receive_buffer_to_thinking_buffer())
        scene.play(*anims)

    def full_algorithm(
        self,
        scene: Scene,
        leader_ids: List[int],
        code: CodeWithStepping,
        send_to_self: bool = True,
    ):
        for leader_id in leader_ids:
            code.highlight_line(0, scene)
            self.generals[leader_id].make_leader(scene)
            code.highlight_line(1, scene)
            for i in range(len(self.generals)):
                self.broadcast_opinion(
                    scene,
                    [i],
                    send_to_self=send_to_self,
                    circular_receive=True,
                    circular_send=True,
                )

            self.move_all_receive_buffers_to_thinking_buffers(scene)

            if not self.generals[leader_id].is_traitor:
                code.highlight_line(3, scene)
                new_opinion = self.generals[leader_id].update_opinion_to_majority(scene)
                self.update_general_opinions(scene, [leader_id], [new_opinion])

            # Whether it's a trator or not, the leader broadcasts its updated opinion
            code.highlight_line(4, scene)
            self.broadcast_opinion(
                scene, [leader_id], circular_send=True, msg_class=LeaderMessage
            )

            self.move_all_receive_buffers_to_thinking_buffers(scene)

            code.highlight_line(5, scene)
            for i in range(len(self.generals)):
                g = self.generals[i]
                if not g.is_traitor and not g.is_leader:
                    new_opinion = g.update_opinion_to_supermajority_or_leader(scene)
                    self.update_general_opinions(scene, [i], [new_opinion])

            self.generals[leader_id].remove_leader(scene)


class ChatWindow(VGroup):
    def __init__(self, h = 4, w = 6, **kwargs):
        super().__init__(**kwargs)
        self.displayed_messages = VGroup()
        self.add(self.displayed_messages)
        self.window = Rectangle(height=h, width=w, color = text_color)
        self.add(self.window)
        
    def create_window(self):
        # Create a basic window frame for the chat
        animation = Create(self.window)
        return animation
    
    def add_message(self, sender, message):
        # Format the message as "sender: message"
        full_message = f"{sender}: {message}"

        # Position for the new message
        if self.displayed_messages:
            position = self.displayed_messages[-1].get_left() + DOWN * 0.4
        else:
            position = self.window.get_corner(UP + LEFT) + RIGHT * 0.2 + DOWN * 0.3

        # Create a text object for the message, positioned to the left
        message_obj = Text(full_message, font_size=24, color = text_color).move_to(position, aligned_edge=LEFT)
        self.displayed_messages.add(message_obj)
        
        # Animation: write each message letter by letter
        animation = Write(message_obj, run_time=len(full_message) * 0.1, rate_func=linear)

        # Return the animation
        return AnimationGroup(animation)



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


class Explore(Scene):
    def construct(self):
        pass




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
        

        game = GameState([Player(no_icon = False) for i in range(len(SAMPLE_OPINIONS))])
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
        self.play(
            FadeIn(city)
        )
        self.wait()
        
        # The generals are trying to conquer the city, but to be successful, they all have to attack at the same time. 
            
        # all generals at once move a bit towards the city, then back
        self.play(
            AnimationGroup(
                *[game.generals[i].clipart.animate.shift(-0.5 * game.circle_position(i)) for i in range(len(game.generals))],
            )
        )
        self.play(
            AnimationGroup(
                *[game.generals[i].clipart.animate.shift(0.5 * game.circle_position(i)) for i in range(len(game.generals))],
            )
        )
        self.wait()
        
        
        # Should they try to attack tomorrow? Every general has some opinion on that 

        # we reveal the opinions of generals one by one, each opinion is a letter Y or N in a bubble which is a SVG image
        cliparts= Group(*[game.generals[i].clipart for i in range(len(game.generals))])
        for c in cliparts:
            c.save_state()
        bubbles = [SVGMobject("img/bubble_say.svg").scale(0.5).next_to(game.generals[i].clipart, RIGHT).shift(0.3*UP) for i in range(len(game.generals))]
        letters = [Tex(SAMPLE_OPINIONS[i], color = TEXT_COLOR).scale(0.5).move_to(bubbles[i]) for i in range(len(game.generals))]
        self.play(
            Succession(
                *[AnimationGroup(
                    FadeIn(b),
                    FadeIn(l),
                ) for b, l in zip(bubbles, letters)],
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
                    if random.random() < 0.05:
                        messages.append(
                            MsgType(i, j, Message(SAMPLE_OPINIONS[i], clipart = True))
                        )
        random.shuffle(messages)

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

        message_pairs = [("General #2", "Let's make a vote"), ("General #4", "I vote YES. "), ("General #7", "I vote NO.")]

        chat = ChatWindow().next_to(game, RIGHT, buff=1)
        self.play(chat.create_window())
        self.wait()

        for pair in message_pairs:
            self.play(chat.add_message(pair[0], pair[1]))
            self.wait()

        # remove the chat window
        self.play(
            FadeOut(chat)
        )
        self.wait()


        # Each general has to stay in his camp and in each round, he can only send a direct message to each other general. 

        id = 3
        # general with index id gets a bit bigger and shifts a bit outside of the circle
        self.play(
            AnimationGroup(
                game.generals[id].clipart.animate.scale(1.5).shift(2 * game.circle_position(id)),
            )
        )
        self.wait()
        

        # the general then sends a message to all other generals
        # [generál pošle obálku pár dalším]

        messages_from = []
        messages_to = []
        for i in range(len(game.generals)):
            if i != id:
                messages_from.append(
                        MsgType(id, i, Message("hi", clipart=True))
                    )
                messages_to.append(
                    MsgType(i, id, Message("hi", clipart = True))
                )

        for messages in [messages_from, messages_to]:        
            game.send_messages_low_tech(
                self,
                messages,
            )
            self.wait()

        # the icon of the special general scales back and joins the circle again

        self.play(
            AnimationGroup(
                game.generals[id].clipart.animate.scale(1 / 1.5).shift(-2 * game.circle_position(id)),
            )
        )
        self.wait()
        # The second reason why this is going to be hard is that two of the generals are secretly plotting together against the rest - I will call these two traitors. Whatever strategy you come up with for the honest generals to play, the traitors know this strategy and will try to break it. 
        # [traitoři jsou generálové kterým narostou rohy, nebo se změní clipart na čertíka]

        # traitor generals are replaced with a traitor image

        self.play(
            AnimationGroup(
                *[game.generals[id].clipart.animate.scale(1.5).shift(2 * game.circle_position(id)) for id in TRAITOR_IDS],
            )
        )
        self.wait()
        traitor_pics = [ImageMobject("img/traitor.png").scale_to_fit_width(game.generals[id].clipart.get_width()).move_to(game.generals[id].clipart) for id in TRAITOR_IDS]
        self.play(
            AnimationGroup(
                *[game.generals[id].clipart.animate.become(pic) for id, pic in zip(TRAITOR_IDS, traitor_pics)],
                *[FadeOut(bubbles[i]) for i in TRAITOR_IDS]
            )
        )
        self.wait()
        self.play(
            AnimationGroup(
                *[game.generals[id].clipart.animate.scale(1 / 1.5).shift(-2 * game.circle_position(id)) for id in TRAITOR_IDS],
            )
        )
        self.wait()

        # So these will be the obstacles: 
        # First: only direct messages.
        
        # we generate a few random pairs of generals and send messages between them

        num_pairs = 10
        pairs = []
        for i in range(num_pairs):
            pairs.append((random.randint(0, len(game.generals) - 1), random.randint(0, len(game.generals) - 1)))
            if pairs[-1][0] == pairs[-1][1]:
                pairs.pop()
        
        messages = []
        for pair in pairs:
            messages.append(
                MsgType(pair[0], pair[1], Message("hi", clipart = True))
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
            *[FadeOut(bubbles[i]) for i in range(len(game.generals)) if i not in TRAITOR_IDS],
            #*[game.generals[i].animate.change_opinion("") for i in range(len(game.generals))],
        )
        self.wait()

class Setup2(Scene):
    def construct(self):

        # add to the scene the objects that were there at the end of Setup1:        

        game = GameState([(Player(no_icon = False) if i not in TRAITOR_IDS else Traitor(no_icon = False)) for i in range(len(SAMPLE_OPINIONS))])
        game.shift(GAME_SHIFT)
        self.add(game)
        self.play(
            *[FadeOut(game.generals[i].clipart) for i in range(len(game.generals))],
        )
        for i in range(len(game.generals)):
            game.generals[i].remove(game.generals[i].clipart)

        self.wait()
        self.play(
            game.animate.shift(1.5*LEFT)
        )
        self.wait()
        #fade out generals' icons



        # Now let me formalize the problem that the honest generals need to solve. Every honest general starts with an opinion of either YES or NO. 

        # every general gets his opinion in succession, also, the first explanation text appears
        self.play(
            AnimationGroup(
                Succession(
                    *[game.generals[i].animate.change_opinion(SAMPLE_OPINIONS[i]) for i in range(len(game.generals)) if i not in TRAITOR_IDS],
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

        counter_tex = Tex("Round: 0", color=TEXT_COLOR).next_to(game, UP, buff=0.5)#.align_to(game, LEFT)
        self.play(
            FadeIn(counter_tex)
        )
        self.wait()

        for it in range(5):
            messages = []
            for i in range(len(game.generals)):
                for j in range(len(game.generals)):
                    if i != j:
                        messages.append(
                            MsgType(i, j, Message(SAMPLE_OPINIONS[i], clipart = True))
                        )
            random.shuffle(messages)
            # TODO this is just for faster rendering
            messages = messages[:2]
            game.send_messages_low_tech(
                self,
                messages,
            )
            # TODO do both together
            self.play(
                counter_tex.animate.become(Tex(f"Round: {it + 1}", color=TEXT_COLOR).move_to(counter_tex).align_to(counter_tex, LEFT))
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
            *[game.generals[i].animate.change_opinion("Y") for i in range(len(game.generals)) if i not in TRAITOR_IDS],
        )
        self.wait()

        # [každý generál má u sebe input i output, traitor asi žádný input/output nemá, ať je jasný co znamená “honest generals”]

        # Every honest general should output the same answer, meaning that the honest generals agreed whether to attack tomorrow. 
        # the letters Y are scaled up and then back down
        self.play(
            AnimationGroup(
                *[game.generals[i].opinion_text.animate.scale(1.5) for i in range(len(game.generals)) if i not in TRAITOR_IDS],
                FadeIn(explanations[2]),
            )
        )
        self.wait()
        # next scale down:
        self.play(
            AnimationGroup(
                *[game.generals[i].opinion_text.animate.scale(1 / 1.5) for i in range(len(game.generals)) if i not in TRAITOR_IDS],
            )
        )
        self.wait()
        # Our task is to design a protocol under which the generals always manage to reach this consensus. 
        # requirement 3 fades in
        

        # But we need to add one more condition to make the problem non-trivial. Right now, we can use the berserk protocol: don’t look at your input at all, don’t communicate with other generals, and just output YES. Surely, with this strategy, all honest generals output the same answer. 

        # change opinions back to the starting opinions:
        self.play(
            *[game.generals[i].animate.change_opinion(SAMPLE_OPINIONS[i]) for i in range(len(game.generals)) if i not in TRAITOR_IDS],
        )
        self.wait()

        # fadeout all input letters
        self.play(
            *[game.generals[i].animate.change_opinion("-") for i in range(len(game.generals)) if i not in TRAITOR_IDS],
        )
        self.wait()

        # crosses = [Text("×", color=RED, font_size=80).move_to(game.generals[i].opinion_text) for i in range(len(game.generals)) if i not in TRAITOR_IDS]
        # self.play(
        #     *[FadeIn(crosses[i]) for i in range(len(crosses))],
        # )
        # self.wait()

        # then, an envelope appears in the middle and then gets crossed
        envelope = ImageMobject("img/envelope.png").scale(0.3).move_to(game.get_center())
        cross_envelope = Text("×", color=RED, font_size=80).scale(2).move_to(envelope)
        self.play(
            FadeIn(envelope)
        )
        self.wait()
        self.play(
            FadeIn(cross_envelope)
        )
        self.wait()

        # every general now outputs the same answer
        self.play(
            *[game.generals[i].animate.change_opinion("Y") for i in range(len(game.generals)) if i not in TRAITOR_IDS],
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
                    *[game.generals[i].opinion_text.animate.scale(1.5) for i in range(len(game.generals)) if i not in TRAITOR_IDS],
                )
            )
            self.wait()
            self.play(
                AnimationGroup(
                    *[game.generals[i].opinion_text.animate.scale(1/1.5) for i in range(len(game.generals)) if i not in TRAITOR_IDS],
                )
            )
            self.wait()

            if it == 0:
                # change opinions to all NO:
                self.play(
                    *[game.generals[i].animate.change_opinion("N") for i in range(len(game.generals)) if i not in TRAITOR_IDS],
                )        

        # add the third explanation text
        self.play(
            FadeIn(explanations[3]),
        )
        self.wait()
        
        # revert back the opinions of generals
        self.play(
            *[game.generals[i].animate.change_opinion(SAMPLE_OPINIONS[i]) for i in range(len(game.generals)) if i not in TRAITOR_IDS],
        )
        self.wait()


        # So, our goal is to come up with a protocol with these two properties   
        # we create a red rectangle around the third explanation text, then change it into a rectangle around the fourth explanation text, then fade out the rectangle
        rec = SurroundingRectangle(explanations[2], color=RED)
        self.play(
            Create(rec)
        )
        self.wait()
        self.play(
            Transform(rec, SurroundingRectangle(explanations[3], color=RED))
        )
        self.wait()
        self.play(
            FadeOut(rec)
        )
        self.wait()
        

        # that works regardless of the starting opinions of generals,
        # generate two random opinions for each general, then change the opinions of generals to these random opinions
        for it in range(2):
            random_opinions = [random.choice(["Y", "N"]) for i in range(len(game.generals))]
            self.play(
                *[game.generals[i].animate.change_opinion(random_opinions[i]) for i in range(len(game.generals)) if i not in TRAITOR_IDS],
            )
            self.wait()

        # whichever two generals are traitors, and whatever the traitors are trying to do. 
        # generate two new random traitors that are different from current ones. Then swap the traitors with the new ones
        new_traitors = [[2, 7], [4, 6]]

        for it in range(2):
            anims = []
            for i in range(2):
                anims.append(game.generals[TRAITOR_IDS[i]].animate.shift(game.generals[new_traitors[it][i]].icon.get_center() - game.generals[TRAITOR_IDS[i]].icon.get_center()))
                anims.append(game.generals[new_traitors[it][i]].animate.shift(game.generals[TRAITOR_IDS[i]].icon.get_center() - game.generals[new_traitors[it][i]].icon.get_center()))

            self.play(
                *anims
            )
            self.wait()

        # This is a good place to stop the video and try to solve this problem yourself, or at least you can try to figure out how you’d solve it if there were no traitors. 

        # There are several approaches you can have. In fact, we will solve the problem twice in this video. First, we will solve it similarly to how large databases are solving the problem in practice. Then, we will solve it again using the tricks from cryptocurrency protocols.  

        self.play(
            *[FadeOut(m) for m in self.mobjects]
        )
        self.wait()

        # two red rectangles appear
        rec1 = Rectangle(height=6, width=4, color=RED)
        rec2 = rec1.copy()
        recs = Group(rec1, rec2).arrange(RIGHT)
        self.play(
            Create(rec1),
            Wait(),
            Create(rec2),
            Wait()
        )


       
class Solution1(Scene):
    def construct(self):
        # create a game with no traitors
        game = GameState([Player(opinion="Y") for i in range(len(SAMPLE_OPINIONS2))])
        self.play(
            *[FadeIn(game.generals[i]) for i in range(len(game.generals))],
        )
        self.wait()
        #generals get their starting opinion
        for i in range(len(game.generals)):
            self.play(
                game.generals[i].animate.change_opinion(SAMPLE_OPINIONS2[i])
            )
        self.wait()
        # Solution 2
        # So this was the first approach. Here is a different approach. As part of our protocol, we could make one general the leader. Then, everybody sends their token to the leader, the leader decides on the answer, let’s say by choosing the majority opinion, and sends the answer back to the rest. 

        game.leader_algorithm(self, 1)
        self.wait()

        # This protocol surely works if there are no traitors, but if we are unlucky and choose a traitor as the leader, he gets a complete control over the output of honest generals, a spectacular failure! 

        for i in TRAITOR_IDS3:
            game.change_general(self, i, CyclicOpinionTraitor("YYYYYYNNNNNN"))

        game.leader_algorithm(self, 1)
        self.wait()

        # [ukáže se jak traitor dostane korunku a pak pošle někomu YES a někomu NO]

        # But let’s look on the bright side! If we could somehow ensure that the leader is honest, this protocol would work really well. 

        # change opinions back
        for i in range(len(game.generals)):
            if i not in TRAITOR_IDS3:
                self.play(
                    game.generals[i].animate.change_opinion(SAMPLE_OPINIONS3[i])
                )
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
        self.play(
            FadeIn(SurroundingRectangle(explanations[3], color=RED))
        )
        self.wait(5)

 
class Solution2(Scene):
    def construct(self):
        # So, how can we approach the problem? Well, let’s first see how we could solve it if there were no traitors at all and understand how those approaches fail. 
        
        # create a game with no traitors
        game = GameState([Player() for i in range(len(SAMPLE_OPINIONS2))])
        self.play(
            *[FadeIn(game.generals[i]) for i in range(len(game.generals))],
        )
        self.wait()
        #generals get their starting opinion
        for i in range(len(game.generals)):
            game.generals[i].change_opinion(SAMPLE_OPINIONS2[i])
        self.wait()

        # Without traitors, there are two pretty simple protocols. Let’s look at them. In the first protocol, everybody simply sends their opinion to everybody else, including themselves. 

        # [animace máme kroužek 12 lidí, animace toho jak si pošlou všichni mezi sebou token s YES/NO – tohle je brutálně hodně animací, dá se to udělat jinak? Kdo ví, možná to bude vypadat hezky? ]

        # Then, each general outputs the majority opinion among the messages he received. 

        # [představuju si, že tokeny u každého generála skončí na kopičkách]



        # If there’s a tie, let’s say he outputs YES. In this example, everybody got 7 YES messages and 5 NO messages, so everybody agrees on YES. 

        game.majority_algorithm(self)
        self.wait()

        # [“7 YES messages” circubscribe 7 YES tokenů u každého generála]

        game_with_traitors = GameState([(CyclicOpinionTraitor("YYYYYYNNNNNN") if i in TRAITOR_IDS2 else Player(opinion = SAMPLE_OPINIONS2[i])) for i in range(len(SAMPLE_OPINIONS2))])

        for i in range(len(game.generals)):
            if i not in TRAITOR_IDS2:
                self.play(
                    game.generals[i].animate.change_opinion(SAMPLE_OPINIONS2[i])
                )
                self.remove(game.generals[i])
                self.add(game_with_traitors.generals[i])
            else:
                self.play(
                    FadeOut(game.generals[i]),
                    FadeIn(game_with_traitors.generals[i]),
                )
        self.wait()        
        self.remove(game)
        game = game_with_traitors

        # Well, imagine that the honest generals start with 5 YES opinions and 5 NO opinions. Honest generals follow the protocol and send their opinion to everybody else. 

        # highlight 5 Y, then 5 N opinions
        for l in ["Y", "N"]:
            self.play(
                *[Indicate(game.generals[i].opinion_text, color = game.generals[i].opinion_text.get_color()) for i in range(len(game.generals)) if i not in TRAITOR_IDS2 and SAMPLE_OPINIONS2[i] == l],
            )
            self.wait()

        # Now the traitors can send 2 YES messages to some generals and 2 NO messages to some other generals. 
        

        game.majority_algorithm(self)
    
        # [ukáže se jak traitoři pošlou nejdřív YES tokeny některým, pak NO tokeny zbylým (sobě traitoři nepošlou nic)]
        # This leads to some generals outputting YES, and some generals outputting NO. So, this simple protocol fails. 

        # highlight generals with output Y, then N
        for l in ["Y", "N"]:
            self.play(
                *[Indicate(game.generals[i].opinion_text, color = game.generals[i].opinion_text.get_color()) for i in range(len(game.generals)) if i not in TRAITOR_IDS2 and SAMPLE_OPINIONS2[i] == l],
            )
            self.wait()

        # [obtáhnou se ti co outputnou YES, je vidět že jejich YES kopička je větší než NO kopička, pak to samé s NO]
        # But let’s look on the bright side – the protocol only fails if the initial opinion of the honest generals was roughly split. If at least 7 honest generals start with the YES opinion, then this protocol works well. 

        for i in range(len(game.generals)):
            if i not in TRAITOR_IDS2:
                self.play(
                    game.generals[i].animate.change_opinion(SAMPLE_OPINIONS_MANY_Y[i])
                )
        self.wait()

        # we show numbers 1,2, ... next to generals with Y
        numbers = []
        num = 0
        for it in range(len(game.generals)):
            if it not in TRAITOR_IDS2 and SAMPLE_OPINIONS_MANY_Y[it] == "Y":
                txt = Text(str(num + 1), color = TEXT_COLOR).scale(0.5).next_to(game.generals[it].opinion_text, RIGHT)
                numbers.append(txt)
                self.play(
                    FadeIn(txt)
                )
                num += 1
        self.wait()
        
        # fadeout numbers
        self.play(
            *[FadeOut(n) for n in numbers]
        )
        self.wait()

        # In that case, whatever the traitors do, every honest general ends up with at least 7 YES opinions, which is enough to make him output YES. Similarly, the protocol works if at least 7 honest generals start with the NO opinion. 
        # [traitoři něco udělají, je pak vidět jak honest generálové skončili s 7 YES/5 NO,  8 YES/4 NO,  9 YES/3 NO, a všichni odpověděli YES] 

        game.majority_algorithm(self)
        self.wait()


class SolutionCombine1(Scene):
    def construct(self):
        # So let’s now take a step back and see where we stand. We have two approaches to the problem. Both of them ultimately failed, but both of them also work well in some interesting situations. 
        
        sc = 0.7
        shft = 3
        games = [
            GameState([(CyclicOpinionTraitor("YYYYYYNNNNNN") if i in TRAITOR_IDS else Player(opinion=SAMPLE_OPINIONS[i])) for i in range(len(SAMPLE_OPINIONS))]).scale(sc).shift(shft*dir)
            for dir in [LEFT, RIGHT]
        ]
        titles = [
            Tex("Algorithm " + str(i + 1), color=TEXT_COLOR).scale(0.7).next_to(games[i], UP, buff=0.5)
            for i in range(2)
        ]
        comments = [Tex(str, color = TEXT_COLOR).scale(0.7).next_to(games[i], DOWN, buff = 0.5)
                    for i, str in enumerate(["works if the leader is honest", "works if the initial opinions are skewed"])]

        self.play(
            *[FadeIn(games[i]) for i in range(2)],
            *[FadeIn(titles[i]) for i in range(2)],
        )
        self.wait()
        
        # The first protocol works if the selected leader happens to be honest. 

        self.play(
            FadeIn(comments[0])
        )
        self.wait()
        games[0].leader_algorithm(self, 0)
        self.wait()  
        
        # The second protocol works if the initial opinions of honest generals are already skewed heavily in favor of one of the opinions. 
        self.play(
            FadeIn(comments[1])
        )
        self.wait()
        games[1].majority_algorithm(self)
        self.wait()  

        # Let’s try to combine the strengths of the two protocols into a new one that always works!
        self.play(
            *[FadeOut(m) for m in titles + comments],
            *[game.animate.scale(1/sc).move_to(ORIGIN) for game in games],
        )
        self.wait()

class SolutionCombine2(Scene):
    def construct(self):

        game = GameState([(CyclicOpinionTraitor(''.join(random.choice(['Y', 'N']) for _ in range(12))) if i in TRAITOR_IDS4 else Player(opinion=SAMPLE_OPINIONS4[i])) for i in range(len(SAMPLE_OPINIONS3))])
        self.add(game)

        # Let’s start by looking at the first protocol. How can we deal with the fact that the leader can be a traitor? Well, we know that there are at most 2 traitors, so we could try to run the protocol three times in a row, with three different leaders. We know that at least once the leader is going to be honest. 

        crowns = [Crown(parent = game.generals[i].icon) for i in range(3)]
        crown = crowns[0]

        self.play(
            FadeIn(crown)
        )
        self.wait()
        for i in [1, 2]:
            self.play(
                crown.animate.move_to(crowns[i])
            )
            self.wait()
        self.play(
            Circumscribe(game.generals[1].icon, color = RED)
        )
        self.wait()
        self.play(
            FadeOut(crown)
        )
        self.wait()
        # [u prvního generála se objeví korunka, možná vedle ní něco jako “Phase 1”, pak se posune k druhému generálovi, pak k třetímu “at least once the leader…” -> první a třetí generál jsou řekněme traitoři, highlightujeme toho druhého který je honest]

        # Here is how that would work in detail. Each time, every general sends his current opinion to the leader and then gets a new opinion back. This new opinion is the general’s starting opinion for the next phase. We repeat this three times with three different leaders and the final opinion is the output of every general. 

        for i in range(3):
            game.leader_algorithm(self, i)
            self.wait()

        # [
        # provede se algoritmus – třikrát se zopakuje předchozí leader algoritmus. Řekněme že všichni tři generálové jsou honest? 
        # ]

        # This protocol still does not work. For example, even if the first two leaders are honest and generals reach consensus, the last leader may be a traitor. He can then break the synchrony again by sending the generals some random junk. 

        # [animace obojího]

        # generals change opinions to Y
        for i in range(len(game.generals)):
            if i not in TRAITOR_IDS4:
                self.play(
                    game.generals[i].animate.change_opinion("Y")
                )
        print(game.generals[i].icon.get_width())
        locks = [ImageMobject("img/lock.png").scale_to_fit_width(game.generals[i].icon.get_width()/1.5).next_to(game.generals[i].icon, RIGHT, buff = -0.3).shift(0.3*DOWN) for i in range(len(game.generals))]
        self.play(
            Succession(
                *[FadeIn(lock) for lock in locks],
                lag_ratio=0.3,
            )
        )
        self.wait()
        self.play(
            *[FadeOut(lock) for lock in locks]
        )
        self.wait()
        

class SolutionCombine3(Scene):
    def construct(self):
        game = GameState([(CyclicOpinionTraitor(''.join(random.choice(['Y', 'N']) for _ in range(12))) if i in TRAITOR_IDS4 else Player(opinion="Y")) for i in range(len(SAMPLE_OPINIONS4))])
        self.add(game)

        #We can do this with the help of our second protocol where everybody sends a token to everybody – in the case where all the generals agree on the same value, we will use this protocol to ensure that honest generals ignore the leader’s proposal and keep their initial opinion. 

        # run majority algo
        game.majority_algorithm(self)
        self.wait()

        # [není mi jasné]

        # Here’s how we can do that concretely. In each of the three phases, we run both algorithms. 
        # So: first, every general sends his opinion to everybody. This allows everybody to compute what we’ll call the majority opinion. Then, the leader of that phase sends his majority opinion back to everybody as the leader’s opinion. 

        for i in range(len(game.generals)):
            if i not in TRAITOR_IDS4:
                self.play(
                    game.generals[i].animate.change_opinion(SAMPLE_OPINIONS4[i])
                )

        game.full_algorithm(self, leader_ids=[1], send_to_self=True)

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


