# MASTER BRANCH!!!
import tkinter as tk
from tkinter import messagebox
import random

# Hallo KAAN
# hallo test


class TicTacToe:
    def __init__(self, master):
        self.master = master
        self.master.title("Tic Tac Toe")
        self.current_player = "X"
        self.board = [" "] * 9

        self.buttons = []
        for i in range(3):
            for j in range(3):
                btn = tk.Button(
                    self.master,
                    text=" ",
                    font=("Helvetica", 20),
                    width=6,
                    height=3,
                    command=lambda row=i, col=j: self.make_move(row, col),
                )
                btn.grid(row=i, column=j)
                self.buttons.append(btn)

    def make_move(self, row, col):
        index = 3 * row + col
        if self.board[index] == " ":
            self.board[index] = self.current_player
            self.buttons[index].config(text=self.current_player, state="disabled")
            if self.check_winner():
                messagebox.showinfo("Tic Tac Toe", f"{self.current_player} wint!")
                self.reset_game()
            elif " " not in self.board:
                messagebox.showinfo("Tic Tac Toe", "Gelijkspel!")
                self.reset_game()
            else:
                self.current_player = "O" if self.current_player == "X" else "X"
                if self.current_player == "O":
                    self.computer_move()

    def computer_move(self):
        empty_cells = [i for i, val in enumerate(self.board) if val == " "]
        index = random.choice(empty_cells)
        self.board[index] = "O"
        self.buttons[index].config(text="O", state="disabled")
        if self.check_winner():
            messagebox.showinfo("Tic Tac Toe", f"{self.current_player} wint!")
            self.reset_game()
        elif " " not in self.board:
            messagebox.showinfo("Tic Tac Toe", "Gelijkspel!")
            self.reset_game()
        else:
            self.current_player = "X"

    def check_winner(self):
        win_conditions = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]

        for condition in win_conditions:
            if (
                self.board[condition[0]]
                == self.board[condition[1]]
                == self.board[condition[2]]
                != " "
            ):
                return True
        return False

    def reset_game(self):
        self.current_player = "X"
        self.board = [" "] * 9
        for btn in self.buttons:
            btn.config(text=" ", state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    game = TicTacToe(root)
    root.mainloop()
