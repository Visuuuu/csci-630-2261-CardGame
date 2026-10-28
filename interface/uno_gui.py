import tkinter as tk
from tkinter import ttk, messagebox
from interface.demo_config import (
    AGENT_TYPES,
    DEFAULT_LINEUP,
    create_demo_controller,
)
from interface.game_view import (
    get_game_view,
    color_hex,
)
from uno_game.card import Color
from interface.async_turn import AsyncTurnRunner


class UNOGUI:
    """Graphical interface for a four-agent UNO match."""
    BACKGROUND = "#123E34"
    PANEL = "#205747"
    TEXT = "#FFFFFF"

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("CSCI 630 - UNO AI Competition")
        self.root.geometry("1050x760")
        self.root.minsize(850, 650)
        self.game_number = 0
        self.agent_choices = list(DEFAULT_LINEUP)
        self.include_draw_four = False
        self.controller = create_demo_controller(
            agent_types=self.agent_choices,
            game_seed=42,
            mc_simulations=25,
            mc_depth=3,
        )
        self.turn_runner = AsyncTurnRunner(self.controller)
        self.poll_after_id = None
        self.auto_playing = False
        self.after_id = None
        self.game_number = 0
        self.reveal_hands = tk.BooleanVar(
            value=False
        )
        self.speed_ms = tk.IntVar(value=800)
        self.root.configure(bg=self.BACKGROUND)
        self._build_interface()
        self._refresh_display()
        self.root.protocol(
            "WM_DELETE_WINDOW",
            self._close_window,
        )

    def _build_interface(self):
        """Create the main window components."""
        header = tk.Frame(
            self.root,
            bg=self.BACKGROUND,
        )
        header.pack(fill="x", pady=12)
        tk.Label(
            header,
            text="UNO AI STRATEGY COMPETITION",
            font=("Arial", 22, "bold"),
            fg=self.TEXT,
            bg=self.BACKGROUND,
        ).pack()
        self.status_label = tk.Label(
            header,
            text="",
            font=("Arial", 12),
            fg="#E8F2EC",
            bg=self.BACKGROUND,
        )
        self.status_label.pack(pady=5)
        self.last_action_label = tk.Label(
            header,
            text="Game ready. Click Next Turn or Auto Play.",
            font=("Arial", 11, "bold"),
            fg="#FFD166",
            bg=self.BACKGROUND,
            wraplength=850,
        )
        self.last_action_label.pack(pady=4)
        # Main playing table
        self.table = tk.Frame(
            self.root,
            bg=self.BACKGROUND,
        )
        self.table.pack(
            fill="both",
            expand=True,
            padx=25,
        )
        self.table.grid_columnconfigure(
            0, weight=1
        )
        self.table.grid_columnconfigure(
            1, weight=2
        )
        self.table.grid_columnconfigure(
            2, weight=1
        )
        self.table.grid_rowconfigure(
            0, weight=1
        )
        self.table.grid_rowconfigure(
            1, weight=2
        )
        self.table.grid_rowconfigure(
            2, weight=1
        )
        self.player_frames = []
        # Position players around the table.
        positions = {
            0: (2, 1),  # Bottom
            1: (1, 0),  # Left
            2: (0, 1),  # Top
            3: (1, 2),  # Right
        }
        for player_id in range(4):
            row, column = positions[player_id]
            frame = tk.Frame(
                self.table,
                bg=self.PANEL,
                padx=10,
                pady=10,
                highlightthickness=2,
                highlightbackground=self.PANEL,
            )
            frame.grid(
                row=row,
                column=column,
                padx=10,
                pady=10,
                sticky="nsew",
            )
            self.player_frames.append(frame)
        # Center discard pile.
        center = tk.Frame(
            self.table,
            bg=self.BACKGROUND,
        )
        center.grid(row=1, column=1)
        tk.Label(
            center,
            text="DISCARD PILE",
            font=("Arial", 12, "bold"),
            fg=self.TEXT,
            bg=self.BACKGROUND,
        ).pack(pady=5)
        self.card_display = tk.Label(
            center,
            text="",
            width=13,
            height=5,
            font=("Arial", 20, "bold"),
            fg="#FFFFFF",
            bg="#C73540",
            relief="ridge",
            bd=5,
            wraplength=145,
            highlightthickness=3,
            highlightbackground="#FFFFFF",
        )
        self.card_display.pack(pady=10)
        self.color_label = tk.Label(
            center,
            text="",
            font=("Arial", 12, "bold"),
            fg=self.TEXT,
            bg=self.BACKGROUND,
        )
        self.color_label.pack()
        self.deck_label = tk.Label(
            center,
            text="",
            font=("Arial", 10),
            fg="#E8F2EC",
            bg=self.BACKGROUND,
        )
        self.deck_label.pack(pady=5)
        # Controls
        controls = tk.Frame(
            self.root,
            bg=self.BACKGROUND,
        )
        controls.pack(fill="x", pady=8)
        self.next_button = ttk.Button(
            controls,
            text="Next Turn",
            command=self.next_turn,
        )
        self.next_button.pack(
            side="left", padx=8
        )
        self.auto_button = ttk.Button(
            controls,
            text="Auto Play",
            command=self.start_auto_play,
        )
        self.auto_button.pack(
            side="left", padx=8
        )
        self.pause_button = ttk.Button(
            controls,
            text="Pause",
            command=self.pause_auto_play,
        )
        self.pause_button.pack(
            side="left", padx=8
        )
        ttk.Button(
            controls,
            text="New Game",
            command=self.new_game,
        ).pack(side="left", padx=8)
        ttk.Checkbutton(
            controls,
            text="Reveal All Hands (Demo)",
            variable=self.reveal_hands,
            command=self._refresh_display,
        ).pack(side="left", padx=8)
        ttk.Label(
            controls,
            text="Delay (ms):",
        ).pack(side="left")
        ttk.Combobox(
            controls,
            textvariable=self.speed_ms,
            values=(300, 800, 1500, 2500),
            width=6,
            state="readonly",
        ).pack(side="left", padx=5)
        # Live AI performance statistics
        stats_frame = tk.Frame(
            self.root,
            bg=self.PANEL,
            padx=12,
            pady=8,
        )
        stats_frame.pack(
            fill="x",
            padx=25,
            pady=6,
        )
        tk.Label(
            stats_frame,
            text="LIVE AI PERFORMANCE",
            font=("Arial", 11, "bold"),
            fg=self.TEXT,
            bg=self.PANEL,
        ).pack(anchor="w", pady=(0, 6))
        self.stats_label = tk.Label(
            stats_frame,
            text="",
            font=("Consolas", 10),
            fg=self.TEXT,
            bg=self.PANEL,
            justify="left",
            anchor="w",
        )
        self.stats_label.pack(
            fill="x",
            anchor="w",
        )
        # Action history
        history_frame = tk.Frame(
            self.root,
            bg=self.BACKGROUND,
        )
        history_frame.pack(
            fill="both",
            padx=25,
            pady=(5, 15),
        )
        tk.Label(
            history_frame,
            text="AI ACTION HISTORY",
            fg=self.TEXT,
            bg=self.BACKGROUND,
            font=("Arial", 11, "bold"),
        ).pack(anchor="w")
        self.history_text = tk.Text(
            history_frame,
            height=8,
            state="disabled",
            font=("Consolas", 10),
            bg="#F3F6F4",
            fg="#202820",
        )
        self.history_text.pack(
            fill="both",
            expand=True,
        )

    def _update_player_frame(
        self,
        frame,
        player_data,
    ):
        """Update one player's visual panel."""
        for widget in frame.winfo_children():
            widget.destroy()
        current = player_data["is_current"]
        frame.configure(
            highlightbackground=(
                "#FFD166" if current else self.PANEL
            )
        )
        name = player_data["name"]
        if current:
            name += "  ◀ TURN"
        tk.Label(
            frame,
            text=name,
            font=("Arial", 12, "bold"),
            fg=self.TEXT,
            bg=self.PANEL,
        ).pack()
        tk.Label(
            frame,
            text=f"{player_data['card_count']} cards",
            font=("Arial", 10),
            fg="#E8F2EC",
            bg=self.PANEL,
        ).pack(pady=3)
        if player_data["has_uno"]:
            tk.Label(
                frame,
                text="UNO!",
                font=("Arial", 11, "bold"),
                fg="#FFD166",
                bg=self.PANEL,
            ).pack()
        cards_frame = tk.Frame(
            frame,
            bg=self.PANEL,
        )
        cards_frame.pack(pady=5)
        # Limit visible cards to keep layout readable.
        visible_cards = player_data["cards"][:8]
        for index, card_name in enumerate(
            visible_cards
        ):
            if self.reveal_hands.get():
                card_color = self._card_background(
                    card_name
                )
                foreground = (
                    "#1B1B1B"
                    if card_color == "#E6AD32"
                    else "#FFFFFF"
                )
            else:
                card_color = "#263C7A"
                foreground = "#FFFFFF"
            tk.Label(
                cards_frame,
                text=(
                    card_name
                    if self.reveal_hands.get()
                    else "UNO\n★"
                ),
                font=("Arial", 8, "bold"),
                bg=card_color,
                fg=foreground,
                width=12,
                height=2,
                relief="raised",
                wraplength=85,
            ).grid(
                row=index // 4,
                column=index % 4,
                padx=2,
                pady=2,
            )
        extra = player_data["card_count"] - 8
        if extra > 0:
            tk.Label(
                frame,
                text=f"+{extra} more cards",
                fg=self.TEXT,
                bg=self.PANEL,
            ).pack()

    @staticmethod
    def _card_background(card_name: str) -> str:
        """Choose a background based on card text."""
        for color in (
            Color.RED,
            Color.YELLOW,
            Color.GREEN,
            Color.BLUE,
        ):
            if card_name.startswith(color.value):
                return color_hex(color)
        return color_hex(Color.WILD)

    def _refresh_display(self):
        """Refresh every visible component."""
        game = self.controller.game
        view = get_game_view(
            game,
            reveal_hands=self.reveal_hands.get(),
        )
        for index, player_data in enumerate(
            view["players"]
        ):
            self._update_player_frame(
                self.player_frames[index],
                player_data,
            )
        self.card_display.configure(
            text=view["top_card"],
            bg=view["top_card_color"],
            highlightbackground=view["active_color_hex"],
        )
        self.color_label.configure(
            text=f"Active Color: {view['active_color']}",
            fg=view["active_color_hex"],
        )
        self.deck_label.configure(
            text=f"Draw pile: {view['deck_count']} cards"
        )
        if view["game_over"]:
            status = f"WINNER: {view['winner']}"
        else:
            status = (
                f"Turn {view['turn_count']}  |  "
                f"Next: {view['current_player']}  |  "
                f"{view['direction']}"
            )
        self.status_label.configure(text=status)
        busy = self.turn_runner.is_busy
        self.next_button.configure(
            state=(
                "disabled"
                if game.game_over or busy or self.auto_playing
                else "normal"
            )
        )
        self.auto_button.configure(
            state=(
                "disabled"
                if game.game_over or self.auto_playing
                else "normal"
            )
        )
        self.pause_button.configure(
            state="normal" if self.auto_playing
            else "disabled"
        )
        self._refresh_statistics()

    def _append_history(self, message: str):
        """Display an AI move in the action log."""
        self.history_text.configure(state="normal")
        self.history_text.insert(
            "end", message + "\n"
        )
        self.history_text.see("end")
        self.history_text.configure(
            state="disabled"
        )

    def next_turn(self):
        """Start one background AI decision."""
        if (
            self.controller.game.game_over
            or self.turn_runner.is_busy
        ):
            return
        try:
            self.turn_runner.request_turn()
        except Exception as error:
            self.pause_auto_play()
            messagebox.showerror(
                "UNO AI Error",
                str(error),
            )
            return
        self.last_action_label.configure(
            text=(
                f"{self.controller.game.current_player.name}"
                " is thinking..."
            )
        )
        self._refresh_display()
        self.poll_after_id = self.root.after(
            30,
            self._poll_turn,
        )

    def _poll_turn(self):
        """Check for a finished AI decision."""
        self.poll_after_id = None
        try:
            record = self.turn_runner.poll()
        except Exception as error:
            self.pause_auto_play()
            self.last_action_label.configure(
                text="An AI decision failed."
            )
            messagebox.showerror(
                "UNO Turn Error",
                str(error),
            )
            self._refresh_display()
            return
        if record is None:
            if self.turn_runner.is_busy:
                self.poll_after_id = self.root.after(
                    30,
                    self._poll_turn,
                )
            return
        self._append_history(
            f"Turn {record.turn_number:03d}: "
            f"{record.message} "
            f"({record.decision_time_ms:.3f} ms)"
        )
        self.last_action_label.configure(
            text=record.message
        )
        self._refresh_display()
        if self.controller.game.game_over:
            self.pause_auto_play()
            messagebox.showinfo(
                "Game Finished",
                f"Winner: {self.controller.game.winner.name}",
            )
            return
        # Continue automatic playback only if
        # the user has not pressed Pause.
        if self.auto_playing:
            self.after_id = self.root.after(
                self.speed_ms.get(),
                self._auto_step,
            )

    def _auto_step(self):
        """Start the next automatic AI turn."""
        self.after_id = None
        if (
            not self.auto_playing
            or self.controller.game.game_over
            or self.turn_runner.is_busy
        ):
            return
        self.next_turn()

    def start_auto_play(self):
        """Start or resume automatic playback."""
        if (
            self.auto_playing
            or self.controller.game.game_over
        ):
            return
        self.auto_playing = True
        self._refresh_display()
        # If an AI decision is already running,
        # its completion will schedule the next turn.
        if not self.turn_runner.is_busy:
            self.after_id = self.root.after(
                self.speed_ms.get(),
                self._auto_step,
            )

    def pause_auto_play(self):
        """Stop automatic play."""
        self.auto_playing = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self._refresh_display()

    def _refresh_statistics(self):
        """Update each AI player's live performance data."""
        game = self.controller.game
        history = self.controller.turn_history

        # Reveal hand points only in demo mode
        # or after the game is finished.
        show_points = (
            self.reveal_hands.get()
            or game.game_over
        )
        header = (
            f"{'Player':<22}"
            f"{'Cards':>7}"
            f"{'Decisions':>11}"
            f"{'Avg ms':>12}"
            f"{'Points':>9}"
        )
        lines = [
            header,
            "-" * 65,
        ]
        for player in game.players:
            durations = [
                record.decision_time_ms
                for record in history
                if record.player_id == player.player_id
            ]
            average_ms = (
                sum(durations) / len(durations)
                if durations
                else 0.0
            )
            points = (
                str(player.hand_points())
                if show_points
                else "Hidden"
            )
            lines.append(
                f"{player.name[:22]:<22}"
                f"{player.hand_size():>7}"
                f"{len(durations):>11}"
                f"{average_ms:>12.4f}"
                f"{points:>9}"
            )
        self.stats_label.configure(
            text="\n".join(lines)
        )

    def new_game(self):
        """Open a dialog to configure the next match."""
        if self.turn_runner.is_busy:
            messagebox.showinfo(
                "AI Decision in Progress",
                "Finish the current AI decision before starting a new game.",
            )
            return
        self.pause_auto_play()
        dialog = tk.Toplevel(self.root)
        dialog.title("Configure New UNO Game")
        dialog.geometry("440x390")
        dialog.resizable(False, False)
        dialog.configure(bg=self.BACKGROUND)
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(
            dialog,
            text="SELECT AI STRATEGIES",
            font=("Arial", 17, "bold"),
            fg=self.TEXT,
            bg=self.BACKGROUND,
        ).pack(pady=18)
        selections = []
        for player_id in range(4):
            row = tk.Frame(
                dialog,
                bg=self.BACKGROUND,
            )
            row.pack(fill="x", padx=35, pady=8)
            tk.Label(
                row,
                text=f"Player {player_id}",
                font=("Arial", 11),
                fg=self.TEXT,
                bg=self.BACKGROUND,
                width=12,
                anchor="w",
            ).pack(side="left")
            selected = tk.StringVar(
                value=self.agent_choices[player_id]
            )
            ttk.Combobox(
                row,
                textvariable=selected,
                values=AGENT_TYPES,
                state="readonly",
                width=19,
            ).pack(side="right")
            selections.append(selected)
        # Wild Draw Four game option
        draw_four_var = tk.BooleanVar(
            value=self.include_draw_four
        )
        ttk.Checkbutton(
            dialog,
            text="Enable Wild Draw Four (108-card deck)",
            variable=draw_four_var,
        ).pack(pady=8)
        buttons = tk.Frame(
            dialog,
            bg=self.BACKGROUND,
        )
        buttons.pack(pady=20)
        ttk.Button(
            buttons,
            text="Start New Game",
            command=lambda: self._start_configured_game(
                [item.get() for item in selections],
                dialog,
                draw_four_var.get(),
            ),
        ).pack(side="left", padx=8)
        ttk.Button(
            buttons,
            text="Cancel",
            command=dialog.destroy,
        ).pack(side="left", padx=8)

    def _start_configured_game(
        self,
        agent_types: list[str],
        dialog: tk.Toplevel,
        include_draw_four: bool,
    ):
        """Create a new match with selected AI agents and rules."""
        next_seed = 42 + self.game_number + 1
        try:
            new_controller = create_demo_controller(
                agent_types=agent_types,
                game_seed=next_seed,
                mc_simulations=25,
                mc_depth=3,
                include_draw_four=include_draw_four,
            )
        except (ValueError, TypeError) as error:
            messagebox.showerror(
                "Invalid Game Configuration",
                str(error),
                parent=dialog,
            )
            return
        # Stop automatic playback before changing games.
        self.pause_auto_play()
        # Close the previous asynchronous turn runner.
        self.turn_runner.close()
        # Install the new game and runner.
        self.controller = new_controller
        self.turn_runner = AsyncTurnRunner(self.controller)
        # Save the settings for the next dialog.
        self.agent_choices = list(agent_types)
        self.include_draw_four = include_draw_four
        self.game_number += 1
        # Clear previous game history.
        self.history_text.configure(state="normal")
        self.history_text.delete("1.0", "end")
        self.history_text.configure(state="disabled")
        # Reset the latest-action message.
        self.last_action_label.configure(
            text=(
                "New game started. "
                "Choose Next Turn or Auto Play."
            )
        )
        # Close the configuration dialog.
        dialog.destroy()
        # Update all game information on screen.
        self._refresh_display()

    def _close_window(self):
        self.pause_auto_play()
        if self.poll_after_id is not None:
            self.root.after_cancel(self.poll_after_id)
            self.poll_after_id = None
        self.turn_runner.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    UNOGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
