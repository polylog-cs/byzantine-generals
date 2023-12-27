from typing import Any, List
from collections import namedtuple
from manim import *

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

MsgType = namedtuple("MsgType", ["sender_id", "receiver_id", "message"])


class Message(Group):
    def __init__(self, message: str, clipart=False):
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
    def __init__(self, opinion: str = "", with_icon=False):
        super().__init__()
        self.opinion = opinion
        self.is_traitor = False
        self.icon = Circle(radius=GENERAL_RADIUS)
        self.opinion_text = Tex(opinion)
        self.change_opinion(opinion)
        self.add(self.opinion_text)
        self.add(self.icon)

        if with_icon:
            self.clipart = ImageMobject("img/general.png").scale(0.5)
            self.add(self.clipart)

    def get_color(self):
        return (
            GREEN
            if self.opinion == "Y"
            else RED
            if self.opinion == "N"
            else GRAY
            if self.opinion == "-"
            else PINK
        )  # "#333" # TODO weird thing here

    def change_opinion(self, opinion: str):
        self.opinion = opinion
        color = self.get_color()

        new_opinion_text = Tex(opinion, color=color)
        new_opinion_text.move_to(self.icon)
        self.opinion_text.become(new_opinion_text)
        self.icon.set_stroke(color=color, opacity=1)


class Traitor(General):
    def __init__(self, with_icon=False):
        super().__init__()
        self.is_traitor = True

        # TODO I am getting a weird error saying that some transition functions don't know this color
        # color = "#333"
        color = PINK
        self.icon = Circle(
            radius=GENERAL_RADIUS, color=color, fill_color=color, fill_opacity=1
        )
        self.add(self.icon)

        if with_icon:
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

    # TODO pls check
    def change_general(self, scene: Scene, i: int, new_general: General):
        """
        Replace the ith general with a new general.
        """
        new_general.shift(self.circle_position(i) * GENERAL_CIRCLE_SIZE)

        scene.play(FadeOut(self.generals[i]), FadeIn(new_general))
        scene.wait()

        self.remove(self.generals[i])
        self.generals[i] = new_general
        self.add(new_general)

        receive_buffer = MessageBuffer()
        receive_buffer.shift(self.circle_position(i) * GENERAL_RECEIVE_BUFFER_RADIUS)
        new_general.add_receive_buffer(receive_buffer)

        thinking_buffer = MessageBuffer()
        thinking_buffer.shift(self.circle_position(i) * GENERAL_THINKING_BUFFER_RADIUS)
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
        lag_ratio=0,
    ):
        """
        Sends messages from the sender to the receiver.
        Only cliparts are shown, no additional info.
        """

        # anims = []
        for message in messages:
            sender = self.generals[message.sender_id]
            receiver = self.generals[message.receiver_id]
            msg = message.message.clipart

            msg.move_to(sender)

            # anims.append(
            #     Succession(
            #         GrowFromCenter(msg),
            #          msg.animate.move_to(receiver),
            #          msg.animate.scale(0)
            #     )
            # )

            scene.play(GrowFromCenter(msg))
            scene.wait(0.5)
            scene.play(msg.animate.move_to(receiver))
            scene.wait(0.5)
            scene.play(msg.animate.scale(0))
            scene.wait(0.5)

        # scene.play(
        #     Succession(
        #         *anims,
        #         lag_ratio = lag_ratio
        #     )
        # )

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
                # TODO hlasilo chybu
                # msg.move_to(sender.receive_buffer)
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
