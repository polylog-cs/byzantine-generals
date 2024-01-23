from typing import Optional

from manim import *

from . import util_general
from .chat_window import ChatMessage, ChatWindow
from .generals import Player


class BlockchainPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, with_clipart=True, **kwargs)
        self.chat_window: Optional[ChatWindow] = None

    def set_chat_window(self, chat_window: ChatWindow):
        if self.chat_window is not None:
            self.remove(self.chat_window)

        self.chat_window = chat_window
        self.add(chat_window)


class BlockchainState(Group):
    def __init__(self, base_chat: ChatWindow, x_offset=-3, y_offset=-0.5):
        coef = 2.3
        player_locations = [
            (x * coef + x_offset, y * coef + y_offset)
            for x, y in [(-1, 1), (1, 1), (1, -1), (-1, -1)]
        ]

        self.players: list[BlockchainPlayer] = []
        animations = []

        for x, y in player_locations:
            player = BlockchainPlayer().shift(x * RIGHT + y * UP)
            self.players.append(player)
            chat_window = base_chat.copy()
            chat_window_scale = 0.3
            animations.append(
                chat_window.animate.shift((x + 1.5) * RIGHT + y * UP).scale(
                    chat_window_scale
                )
            )
            chat_window.messages_scale *= chat_window_scale
            player.chat_window = chat_window

        self.creation_animations = animations
        self.leader_id = None

    def make_message_from_general(
        self, general_id: int, message: str, alleged_general_id: Optional[int] = None
    ) -> ChatMessage:
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

        # The general whose name will be shown next to the message
        alleged_general_id = alleged_general_id or general_id

        chat_message = ChatMessage(
            f"General #{alleged_general_id+1}",
            message,
            tail_up=general_id in [0, 1],
        )
        chat_message.next_to(
            self.players[general_id], direction=general_data["next_to_direction"]
        ).shift(general_data["shift"])

        return chat_message

    def make_leader(self, leader_id: int, scene: Scene):
        self.leader_id = leader_id
        scene.play(self.players[leader_id].make_leader(generals=self.players))

    def send_block_to_other_players(
        self, messages_to_add: list[ChatMessage], scene: Scene
    ):
        # Copy the new messages from the leader to the other players
        scene.play(
            LaggedStart(
                *[
                    self.players[i].chat_window.copy_messages(
                        messages_to_add, keep_original=True
                    )
                    for i in range(4)
                    if i != self.leader_id
                ],
                lag_ratio=0.5,
            )
        )

        # Set the background colors of the newly-added messages back to the standard one
        color_change_animations = []
        for player_id in range(len(self.players)):
            for i in range(len(messages_to_add)):
                # I tried wrapping this into a method of ChatMessage but that lead to the
                # message's text disappearing behind the bubble... why??
                message = self.players[player_id].chat_window.all_messages[-i - 1]
                color_change_animations.append(
                    message.bubble.animate.set_fill_color(util_general.BASE02)
                )

        scene.play(*color_change_animations)
        scene.wait(1)
