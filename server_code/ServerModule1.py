import anvil.server

@anvil.server.callable
def forward_move_to_lightsail(game_id, col, player):
  # Calls the uplink worker function running on Lightsail
  return anvil.server.call("receive_move", game_id, col, player)

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#
