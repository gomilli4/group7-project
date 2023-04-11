def on_board(i, j, grid):
    """
    Code from CMSE 201, used for checking if neighboring cells are on the board
    """
    if i <= grid.shape[0] - 1 and i >= 0 and j <= grid.shape[1] - 1 and j >= 0:
        return True
    else:
        return False


def get_neighbor_values(i, j, board):
    """
    Code from CMSE 201, used to check the values of the neighboring cells.
    As per the grass growing rules, if a neighbor cell has an amount
    of grass > 0, the cell starts growing grass itself
    """
    neighborhood = [(i - 1, j), (i, j - 1), (i + 1, j), (i, j + 1)]

    neighbor_values = []
    for neighbor in neighborhood:
        if on_board(neighbor[0], neighbor[1], board):
            neighbor_values.append(board[neighbor[0], neighbor[1]])

    return neighbor_values