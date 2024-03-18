def print_board(board):
    for row in board:
        print(" | ".join(row))
        print("-" * 9)

def check_winner(board):
    # Check rijen en kolommen
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != " ":
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != " ":
            return board[0][i]

    # Check diagonalen
    if board[0][0] == board[1][1] == board[2][2] != " ":
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != " ":
        return board[0][2]

    return None

def is_board_full(board):
    for row in board:
        if " " in row:
            return False
    return True

def main():
    board = [[" " for _ in range(3)] for _ in range(3)]
    current_player = "X"

    print("Welkom bij Tic-Tac-Toe!")
    print_board(board)

    while True:
        print(f"Speler {current_player}, het is jouw beurt.")

        # Vraag om rij en kolom van de speler
        while True:
            row = int(input("Kies een rij (1-3): ")) - 1
            col = int(input("Kies een kolom (1-3): ")) - 1
            if 0 <= row < 3 and 0 <= col < 3 and board[row][col] == " ":
                break
            print("Ongeldige invoer. Probeer opnieuw.")

        # Zet de speler op het bord
        board[row][col] = current_player
        print_board(board)

        # Controleer of er een winnaar is of het bord vol is
        winner = check_winner(board)
        if winner:
            print(f"Speler {winner} wint!")
            break
        if is_board_full(board):
            print("Het is een gelijkspel!")
            break

        # Wissel van speler
        current_player = "O" if current_player == "X" else "X"

if __name__ == "__main__":
    main()

