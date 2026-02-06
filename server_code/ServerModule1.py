import anvil.server

@anvil.server.callable
def forward_move_to_lightsail(game_id, col, player):
  # Calls the uplink worker function running on Lightsail
  return anvil.server.call("receive_move", game_id, col, player)

