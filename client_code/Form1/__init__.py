"""
from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
from anvil.js import get_dom_node  # ✅ supported way to style DOM
import uuid


class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)
  
    # ----------------------------
    # Game state (UI mirrors backend)
    # ----------------------------
    self.board = [[[0.0, 0.0] for _ in range(7)] for _ in range(6)]
    self.player = 0
    self.game_over = False
    self.game_id = str(uuid.uuid4())
    self.loading = False
  
    # ----------------------------
    # Overlay buttons
    # ----------------------------
    self.overlay_panel.role = "c4_overlay"
    self.col_buttons = []
    self._build_overlay_buttons()
  
    # ----------------------------
    # Status + Loading + Restart UI (under board)
    # ----------------------------
    self.loading_lbl = Label(
      text="Loading…",
      role="c4_loading",
      visible=False
    )
  
    self.status_lbl = Label(
      text="",
      role="c4_status"
    )
  
    self.restart_btn = Button(
      text="Play again",
      role="c4_restart_btn",
      enabled=False
    )
    self.restart_btn.set_event_handler("click", self.restart_game)
  
    # Prefer the panel in the HTML slot under the board
    if hasattr(self, "underboard_panel"):
      target = self.underboard_panel
    elif hasattr(self, "content_panel"):
      target = self.content_panel
    else:
      target = self
  
    # Clear once to avoid duplicates on reload
    if hasattr(target, "clear"):
      target.clear()
  
    target.add_component(self.loading_lbl)
    target.add_component(self.status_lbl)
    target.add_component(self.restart_btn)
  
    # ----------------------------
    # Initial render + status
    # ----------------------------
    self.render_board()
    self._update_status_ui()


  # ----------------------------
  # UI helpers
  # ----------------------------
  def _make_drop_handler(self, col):
    def handler(**e):
      self.drop_piece(col)
    return handler

  def _build_overlay_buttons(self):
    self.overlay_panel.clear()
    self.col_buttons = []

    for col in range(7):
      btn = Button(text="", role="c4_col_btn")
      btn.set_event_handler("click", self._make_drop_handler(col))
      self.overlay_panel.add_component(btn)
      self.col_buttons.append(btn)

  def _landing_row_for_col(self, col: int):
    # Returns the row index (0=top..5=bottom) where a new piece would land.
    # Returns None if the column is full.
    for r in range(5, -1, -1):
      if self.board[r][col][0] == 0.0 and self.board[r][col][1] == 0.0:
        return r
    return None

  def _update_ghost_positions(self):
    # Sets a CSS variable --ghost-y on each column button so the CSS pseudo-element
    # can appear at the correct landing row.
    cell = 42
    gap = 8
    pad = 12

    for col, btn in enumerate(self.col_buttons):
      r = self._landing_row_for_col(col)
      dom = get_dom_node(btn)

      if r is None:
        dom.classList.add("c4-full")
        dom.style.removeProperty("--ghost-y")
      else:
        dom.classList.remove("c4-full")
        GHOST_RAISE = 12
        y = pad + r * (cell + gap) - GHOST_RAISE
        dom.style.setProperty("--ghost-y", f"{y}px")

  def _sync_turn_classes(self):
    shell = self.dom_nodes.get("board_shell")
    if shell is None:
      return
    shell.classList.remove("player-red", "player-yellow")
    shell.classList.add("player-red" if self.player == 0 else "player-yellow")

  def _sync_loading_class(self):
    shell = self.dom_nodes.get("board_shell")
    if shell is None:
      return
  
    if self.loading:
      shell.classList.add("loading")
      self.status_lbl.text = "Loading…"
    else:
      shell.classList.remove("loading")

  def _sync_game_over_class(self):
    shell = self.dom_nodes.get("board_shell")
    if shell is None:
      return
    if self.game_over:
      shell.classList.add("game-over")
    else:
      shell.classList.remove("game-over")

  def _update_status_ui(self, winner=None, is_draw=False):
    # Updates the label text and enables/disables the restart button.
    if self.game_over:
      if is_draw:
        self.status_lbl.text = "Game over: Draw"
      elif winner == 0:
        self.status_lbl.text = "Game over: Red wins!"
      elif winner == 1:
        self.status_lbl.text = "Game over: Yellow wins!"
      else:
        self.status_lbl.text = "Game over"
      self.restart_btn.enabled = True
    else:
      self.status_lbl.text = "Turn: Red" if self.player == 0 else "Turn: Yellow"
      self.restart_btn.enabled = False

  # ----------------------------
  # Rendering
  # ----------------------------
  def render_board(self):
    self._sync_turn_classes()
    self._sync_loading_class()
    self._sync_game_over_class()

    def disc_class(cell):
      a, b = cell
      if a > 0.5: return "c4-disc c4-red"
      if b > 0.5: return "c4-disc c4-yellow"
      return "c4-disc"

    turn_class = "player-red" if self.player == 0 else "player-yellow"

    parts = [f'<div class="c4-stage {turn_class}">']
    parts.append('<div class="c4-board">')
    for r in range(6):
      for c in range(7):
        parts.append(f'<div class="{disc_class(self.board[r][c])}"></div>')
    parts.append('</div></div>')

    self.dom_nodes["board_root"].innerHTML = "".join(parts)
    self._update_ghost_positions()

  # ----------------------------
  # Gameplay
  # ----------------------------
  def drop_piece(self, col: int):
    # Ignore clicks after game ends or while waiting
    if self.game_over or getattr(self, "loading", False):
      return
  
    # ----------------------------
    # Optimistic local placement
    # ----------------------------
    prev_board = [[cell[:] for cell in row] for row in self.board]
  
    r = self._landing_row_for_col(col)
    if r is None:
      return
  
    if self.player == 0:
      self.board[r][col] = [1.0, 0.0]
    else:
      self.board[r][col] = [0.0, 1.0]
  
    # Show piece immediately
    self.render_board()
  
    # ----------------------------
    # Enter loading state AFTER render
    # ----------------------------
    self.loading = True
    self._sync_loading_class()
  
    try:
      resp = anvil.server.call(
        "forward_move_to_lightsail",
        self.game_id,
        col,
        self.player
      )
    except Exception as e:
      # Revert optimistic move on error
      self.board = prev_board
      self.render_board()
      Notification(f"Backend error: {e}").show()
      return
    finally:
      self.loading = False
      self._sync_loading_class()
  
    if not resp.get("ok"):
      # Revert optimistic move if rejected
      self.board = prev_board
      self.render_board()
      Notification(resp.get("error", "Move rejected")).show()
      return
  
    # ----------------------------
    # Apply authoritative backend state
    # ----------------------------
    self.board = resp["board"]
    self.player = resp.get("next_player", self.player)
    self.game_over = resp.get("game_over", False)
  
    self.render_board()
  
    if self.game_over:
      self._update_status_ui(
        winner=resp.get("winner"),
        is_draw=resp.get("is_draw", False)
      )
    else:
      self._update_status_ui()



  def restart_game(self, **e):
    # Start a fresh game by using a new game_id (backend in-memory store keyed by game_id)
    self.game_id = str(uuid.uuid4())
    self.board = [[[0.0, 0.0] for _ in range(7)] for _ in range(6)]
    self.player = 0
    self.game_over = False
    self.render_board()
    self._update_status_ui()
#"""

from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
from anvil.js import get_dom_node
import uuid


class Form1(Form1Template):
  def __init__(self, **properties):
    self.init_components(**properties)

    # ----------------------------
    # Game state
    # ----------------------------
    self.board = [[[0.0, 0.0] for _ in range(7)] for _ in range(6)]
    self.player = 0
    self.game_over = False
    self.game_id = str(uuid.uuid4())
    self.loading = False

    # ----------------------------
    # Dropdown menu ABOVE board
    # ----------------------------
    self.selected_mode = "Player"
    self.model_dd = DropDown(
      items=["Player", "CNN", "Transformer"],
      selected_value="Player"
    )
    self.model_dd.role = "c4_model_dd"
    self.model_dd.set_event_handler("change", self.model_dd_change)

    if hasattr(self, "topbar_panel"):
      if hasattr(self.topbar_panel, "clear"):
        self.topbar_panel.clear()
      self.topbar_panel.add_component(self.model_dd)
    else:
      self.add_component(self.model_dd)

    # ----------------------------
    # Overlay buttons
    # ----------------------------
    self.overlay_panel.role = "c4_overlay"
    self.col_buttons = []
    self._build_overlay_buttons()

    # ----------------------------
    # Status + Loading + Restart UI (under board)
    # ----------------------------
    self.loading_lbl = Label(text="Loading…", role="c4_loading", visible=False)
    self.status_lbl = Label(text="", role="c4_status")

    # ✅ New behavior:
    # - Button is always enabled
    # - Shows "New Game" during play
    # - Switches to "Play again" after game ends
    self.restart_btn = Button(
      text="New Game",
      role="c4_restart_btn",
      enabled=True
    )
    self.restart_btn.set_event_handler("click", self.restart_game)

    if hasattr(self, "underboard_panel"):
      target = self.underboard_panel
    elif hasattr(self, "content_panel"):
      target = self.content_panel
    else:
      target = self

    if hasattr(target, "clear"):
      target.clear()

    target.add_component(self.loading_lbl)
    target.add_component(self.status_lbl)
    target.add_component(self.restart_btn)

    # Initial render
    self.render_board()
    self._update_status_ui()

  # ----------------------------
  # Dropdown handler
  # ----------------------------
  def model_dd_change(self, **e):
    # update mode
    self.selected_mode = self.model_dd.selected_value
  
    # ✅ start a fresh game whenever the mode changes
    self.restart_game()

  # ----------------------------
  # UI helpers
  # ----------------------------
  def _make_drop_handler(self, col):
    def handler(**e):
      self.drop_piece(col)
    return handler

  def _build_overlay_buttons(self):
    self.overlay_panel.clear()
    self.col_buttons = []
    for col in range(7):
      btn = Button(text="", role="c4_col_btn")
      btn.set_event_handler("click", self._make_drop_handler(col))
      self.overlay_panel.add_component(btn)
      self.col_buttons.append(btn)

  def _landing_row_for_col(self, col):
    for r in range(5, -1, -1):
      if self.board[r][col] == [0.0, 0.0]:
        return r
    return None

  def _update_ghost_positions(self):
    cell, gap, pad = 42, 8, 12
    for col, btn in enumerate(self.col_buttons):
      r = self._landing_row_for_col(col)
      dom = get_dom_node(btn)
      if r is None:
        dom.classList.add("c4-full")
        dom.style.removeProperty("--ghost-y")
      else:
        dom.classList.remove("c4-full")
        y = pad + r * (cell + gap) - 12
        dom.style.setProperty("--ghost-y", f"{y}px")

  def _sync_turn_classes(self):
    shell = self.dom_nodes.get("board_shell")
    if shell:
      shell.classList.toggle("player-red", self.player == 0)
      shell.classList.toggle("player-yellow", self.player == 1)

  def _sync_loading_class(self):
    shell = self.dom_nodes.get("board_shell")
    if shell:
      shell.classList.toggle("loading", self.loading)
      if self.loading:
        self.status_lbl.text = "Loading…"

  def _sync_game_over_class(self):
    shell = self.dom_nodes.get("board_shell")
    if shell:
      shell.classList.toggle("game-over", self.game_over)

  def _update_status_ui(self, winner=None, is_draw=False):
    # ✅ Button always works
    self.restart_btn.enabled = True

    if self.game_over:
      # After game ends, change button label
      self.restart_btn.text = "Play again"

      if is_draw:
        self.status_lbl.text = "Game over: Draw"
      elif winner == 0:
        self.status_lbl.text = "Game over: Red wins!"
      elif winner == 1:
        self.status_lbl.text = "Game over: Yellow wins!"
      else:
        self.status_lbl.text = "Game over"
      return

    # Game in progress: button says New Game
    self.restart_btn.text = "New Game"

    # If currently loading, show loading message and stop
    if self.loading:
      self.status_lbl.text = "Loading…"
      return

    # Turn text logic (your requested behavior)
    if self.player == 0:
      self.status_lbl.text = "Turn: Red"
    else:
      if self.selected_mode == "Player":
        self.status_lbl.text = "Turn: Yellow"
      else:
        self.status_lbl.text = f"Turn: {self.selected_mode}"

  # ----------------------------
  # Rendering
  # ----------------------------
  def render_board(self):
    self._sync_turn_classes()
    self._sync_loading_class()
    self._sync_game_over_class()

    def disc_class(cell):
      if cell[0] > 0.5: return "c4-disc c4-red"
      if cell[1] > 0.5: return "c4-disc c4-yellow"
      return "c4-disc"

    parts = ['<div class="c4-stage">', '<div class="c4-board">']
    for r in range(6):
      for c in range(7):
        parts.append(f'<div class="{disc_class(self.board[r][c])}"></div>')
    parts.append('</div></div>')

    self.dom_nodes["board_root"].innerHTML = "".join(parts)
    self._update_ghost_positions()

  # ----------------------------
  # Gameplay
  # ----------------------------
  def drop_piece(self, col):
    if self.game_over or self.loading:
      return

    prev_board = [[cell[:] for cell in row] for row in self.board]
    r = self._landing_row_for_col(col)
    if r is None:
      return

    self.board[r][col] = [1.0, 0.0] if self.player == 0 else [0.0, 1.0]
    self.render_board()

    self.loading = True
    self._sync_loading_class()
    self._update_status_ui()  # ✅ ensures button text + loading message stay consistent

    try:
      resp = anvil.server.call("forward_move_to_lightsail", self.game_id, col, self.player)
    except Exception as e:
      self.board = prev_board
      self.render_board()
      Notification(str(e)).show()
      return
    finally:
      self.loading = False
      self._sync_loading_class()

    if not resp.get("ok"):
      self.board = prev_board
      self.render_board()
      self._update_status_ui()
      return

    self.board = resp["board"]
    self.player = resp.get("next_player", self.player)
    self.game_over = resp.get("game_over", False)

    self.render_board()
    self._update_status_ui(resp.get("winner"), resp.get("is_draw", False))

  def restart_game(self, **e):
    self.game_id = str(uuid.uuid4())
    self.board = [[[0.0, 0.0] for _ in range(7)] for _ in range(6)]
    self.player = 0
    self.game_over = False
    self.loading = False
    self.render_board()
    self._update_status_ui()
