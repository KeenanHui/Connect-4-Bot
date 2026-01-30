"""
from ._anvil_designer import Form1Template
from anvil import *

class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Example tensor (replace with your real one)
    board = [[[0.0, 0.0] for _ in range(7)] for _ in range(6)]
    board[5][6] = [0.0, 1.0]  # yellow

    self.set_board(board)

  def set_board(self, tensor):
    def disc_class(cell):
      a, b = cell[0], cell[1]
      if a > 0.5 and b < 0.5:
        return "c4-disc c4-red"
      if b > 0.5 and a < 0.5:
        return "c4-disc c4-yellow"
      return "c4-disc"

    parts = ['<div class="c4-board">']
    for r in range(6):
      for c in range(7):
        parts.append(f'<div class="{disc_class(tensor[r][c])}"></div>')
    parts.append('</div>')

    self.dom_nodes["board_root"].innerHTML = "".join(parts)
"""

"""
from ._anvil_designer import Form1Template
from anvil import *

class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)

    self.board = [[[0.0, 0.0] for _ in range(7)] for _ in range(6)]
    self.player = 0  # 0=red, 1=yellow
    self.render_board()

  def render_board(self):
    def disc_class(cell):
      a, b = cell
      if a > 0.5: return "c4-disc c4-red"
      if b > 0.5: return "c4-disc c4-yellow"
      return "c4-disc"

    parts = ['<div class="c4-board">']
    for r in range(6):
      for c in range(7):
        parts.append(f'<div class="{disc_class(self.board[r][c])}"></div>')
    parts.append('</div>')
    self.dom_nodes["board_root"].innerHTML = "".join(parts)

  def drop_piece(self, col: int):
    for r in range(5, -1, -1):
      if self.board[r][col][0] == 0.0 and self.board[r][col][1] == 0.0:
        self.board[r][col] = [1.0, 0.0] if self.player == 0 else [0.0, 1.0]
        self.player = 1 - self.player
        self.render_board()
        return
    Notification("Column is full").show()

  @handle("ov0_btn", "click")
  def ov0_btn_click(self, **e): self.drop_piece(0)

  @handle("ov1_btn", "click")
  def ov1_btn_click(self, **e): self.drop_piece(1)

  @handle("ov2_btn", "click")
  def ov2_btn_click(self, **e): self.drop_piece(2)

  @handle("ov3_btn", "click")
  def ov3_btn_click(self, **e): self.drop_piece(3)

  @handle("ov4_btn", "click")
  def ov4_btn_click(self, **e): self.drop_piece(4)

  @handle("ov5_btn", "click")
  def ov5_btn_click(self, **e): self.drop_piece(5)

  @handle("ov6_btn", "click")
  def ov6_btn_click(self, **e): self.drop_piece(6)
"""

"""
from ._anvil_designer import Form1Template
from anvil import *

class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Game state: 6x7x2 tensor
    self.board = [[[0.0, 0.0] for _ in range(7)] for _ in range(6)]
    self.player = 0  # 0 = red, 1 = yellow

    self.render_board()

  # ---------- Rendering ----------
  def render_board(self):
    def disc_class(cell):
      a, b = cell
      if a > 0.5:
        return "c4-disc c4-red"
      if b > 0.5:
        return "c4-disc c4-yellow"
      return "c4-disc"

    parts = ['<div class="c4-board">']
    for r in range(6):
      for c in range(7):
        parts.append(f'<div class="{disc_class(self.board[r][c])}"></div>')
    parts.append('</div>')

    # board_root must exist in Form1 Edit HTML:
    # <div anvil-name="board_root"></div>
    self.dom_nodes["board_root"].innerHTML = "".join(parts)

  # ---------- Game logic ----------
  def drop_piece(self, col: int):
    # Find lowest empty slot in this column
    for r in range(5, -1, -1):
      if self.board[r][col][0] == 0.0 and self.board[r][col][1] == 0.0:
        # Place piece for current player
        self.board[r][col] = [1.0, 0.0] if self.player == 0 else [0.0, 1.0]
        self.player = 1 - self.player
        self.render_board()
        return

    Notification("Column is full").show()

  # ---------- Overlay button handlers ----------
  @handle("ov0_btn", "click")
  def ov0_btn_click(self, **e): self.drop_piece(0)

  @handle("ov1_btn", "click")
  def ov1_btn_click(self, **e): self.drop_piece(1)

  @handle("ov2_btn", "click")
  def ov2_btn_click(self, **e): self.drop_piece(2)

  @handle("ov3_btn", "click")
  def ov3_btn_click(self, **e): self.drop_piece(3)

  @handle("ov4_btn", "click")
  def ov4_btn_click(self, **e): self.drop_piece(4)

  @handle("ov5_btn", "click")
  def ov5_btn_click(self, **e): self.drop_piece(5)

  @handle("ov6_btn", "click")
  def ov6_btn_click(self, **e): self.drop_piece(6)
"""

"""
from ._anvil_designer import Form1Template
from anvil import *

class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)

    # 6x7x2 tensor: red=[1,0], yellow=[0,1], empty=[0,0]
    self.board = [[[0.0, 0.0] for _ in range(7)] for _ in range(6)]
    self.player = 0  # 0=red, 1=yellow

    self.render_board()

  # ---------- Rendering ----------
  def render_board(self):
    def disc_class(cell):
      a, b = cell
      if a > 0.5:
        return "c4-disc c4-red"
      if b > 0.5:
        return "c4-disc c4-yellow"
      return "c4-disc"

    parts = ['<div class="c4-board">']
    for r in range(6):
      for c in range(7):
        parts.append(f'<div class="{disc_class(self.board[r][c])}"></div>')
    parts.append('</div>')

    self.dom_nodes["board_root"].innerHTML = "".join(parts)

  # ---------- Game logic ----------
  def drop_piece(self, col: int):
    # Find lowest empty row in the column
    for r in range(5, -1, -1):
      if self.board[r][col][0] == 0.0 and self.board[r][col][1] == 0.0:
        self.board[r][col] = [1.0, 0.0] if self.player == 0 else [0.0, 1.0]
        self.player = 1 - self.player
        self.render_board()
        return

    Notification("Column is full").show()

  # ---------- Overlay button handlers ----------
  @handle("ov0_btn", "click")
  def ov0_btn_click(self, **e): self.drop_piece(0)

  @handle("ov1_btn", "click")
  def ov1_btn_click(self, **e): self.drop_piece(1)

  @handle("ov2_btn", "click")
  def ov2_btn_click(self, **e): self.drop_piece(2)

  @handle("ov3_btn", "click")
  def ov3_btn_click(self, **e): self.drop_piece(3)

  @handle("ov4_btn", "click")
  def ov4_btn_click(self, **e): self.drop_piece(4)

  @handle("ov5_btn", "click")
  def ov5_btn_click(self, **e): self.drop_piece(5)

  @handle("ov6_btn", "click")
  def ov6_btn_click(self, **e): self.drop_piece(6)
"""

from ._anvil_designer import Form1Template
from anvil import *

class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Safety: ensure buttons are children of overlay_panel
    for b in [
      self.ov0_btn, self.ov1_btn, self.ov2_btn,
      self.ov3_btn, self.ov4_btn, self.ov5_btn, self.ov6_btn
    ]:
      if b.parent is not self.overlay_panel:
        b.remove_from_parent()
        self.overlay_panel.add_component(b)

    self.board = [[[0.0, 0.0] for _ in range(7)] for _ in range(6)]
    self.player = 0
    self.render_board()

  def render_board(self):
    def disc_class(cell):
      a, b = cell
      if a > 0.5: return "c4-disc c4-red"
      if b > 0.5: return "c4-disc c4-yellow"
      return "c4-disc"

    parts = ['<div class="c4-board">']
    for r in range(6):
      for c in range(7):
        parts.append(f'<div class="{disc_class(self.board[r][c])}"></div>')
    parts.append('</div>')

    self.dom_nodes["board_root"].innerHTML = "".join(parts)

  def drop_piece(self, col: int):
    for r in range(5, -1, -1):
      if self.board[r][col][0] == 0.0 and self.board[r][col][1] == 0.0:
        self.board[r][col] = [1.0, 0.0] if self.player == 0 else [0.0, 1.0]
        self.player = 1 - self.player
        self.render_board()
        return
    Notification("Column is full").show()

  @handle("ov0_btn", "click")
  def ov0_btn_click(self, **e): self.drop_piece(0)
  @handle("ov1_btn", "click")
  def ov1_btn_click(self, **e): self.drop_piece(1)
  @handle("ov2_btn", "click")
  def ov2_btn_click(self, **e): self.drop_piece(2)
  @handle("ov3_btn", "click")
  def ov3_btn_click(self, **e): self.drop_piece(3)
  @handle("ov4_btn", "click")
  def ov4_btn_click(self, **e): self.drop_piece(4)
  @handle("ov5_btn", "click")
  def ov5_btn_click(self, **e): self.drop_piece(5)
  @handle("ov6_btn", "click")
  def ov6_btn_click(self, **e): self.drop_piece(6)
