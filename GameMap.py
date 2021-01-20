from enum import IntEnum
import pygame
from pygame.locals import *
import numpy as np
GAME_VERSION = 'V1.0'

REC_SIZE = 50
CHESS_RADIUS = REC_SIZE//2 - 2
CHESS_LEN = 15
MAP_WIDTH = CHESS_LEN * REC_SIZE
MAP_HEIGHT = CHESS_LEN * REC_SIZE

INFO_WIDTH = 200
BUTTON_WIDTH = 140
BUTTON_HEIGHT = 50

SCREEN_WIDTH = MAP_WIDTH + INFO_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT

class MAP_ENTRY_TYPE(IntEnum):
	MAP_EMPTY = 0,
	MAP_PLAYER_ONE = 1,
	MAP_PLAYER_TWO = 2,
	MAP_NONE = 3, # out of map range
	
class Map():
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.map = [[0 for x in range(self.width)] for y in range(self.height)]
		self.steps = []
	
	def reset(self):
		for y in range(self.height):
			for x in range(self.width):
				self.map[y][x] = 0
		self.steps = []
	
	def setHalfGame(self):
		self.reset()
		self.click(7,7,MAP_ENTRY_TYPE.MAP_PLAYER_ONE)
		self.click(7,8,MAP_ENTRY_TYPE.MAP_PLAYER_ONE)
		self.click(8,7,MAP_ENTRY_TYPE.MAP_PLAYER_ONE)
		self.click(10,7,MAP_ENTRY_TYPE.MAP_PLAYER_ONE)

		self.click(6,7,MAP_ENTRY_TYPE.MAP_PLAYER_TWO)
		self.click(6,6,MAP_ENTRY_TYPE.MAP_PLAYER_TWO)
		self.click(9,7,MAP_ENTRY_TYPE.MAP_PLAYER_TWO)
		self.click(9,8,MAP_ENTRY_TYPE.MAP_PLAYER_TWO)



	def reverseTurn(self, turn):
		if turn == MAP_ENTRY_TYPE.MAP_PLAYER_ONE:
			return MAP_ENTRY_TYPE.MAP_PLAYER_TWO
		else:
			return MAP_ENTRY_TYPE.MAP_PLAYER_ONE

	def getMapUnitRect(self, x, y):
		map_x = x * REC_SIZE
		map_y = y * REC_SIZE
		
		return (map_x, map_y, REC_SIZE, REC_SIZE)
	
	def MapPosToIndex(self, map_x, map_y):
		x = map_x // REC_SIZE
		y = map_y // REC_SIZE		
		return (x, y)
	
	def isInMap(self, map_x, map_y):
		if (map_x <= 0 or map_x >= MAP_WIDTH or 
			map_y <= 0 or map_y >= MAP_HEIGHT):
			return False
		return True
	
	def isEmpty(self, x, y):
		return (self.map[y][x] == 0)
	
	def click(self, x, y, type):
		self.map[y][x] = type.value
		self.steps.append((x,y))

	def drawChess(self, screen):
		player_two = (255, 251, 240)
		player_one = (88, 87, 86)
		player_color = [player_one, player_two]
		
		font = pygame.font.SysFont(None, REC_SIZE*2//3)
		for i in range(len(self.steps)):
			x, y = self.steps[i]
			map_x, map_y, width, height = self.getMapUnitRect(x, y)
			pos, radius = (map_x + width//2, map_y + height//2), CHESS_RADIUS
			turn = self.map[y][x]
			if turn == 1:
				op_turn = 2
			else:
				op_turn = 1
			pygame.draw.circle(screen, player_color[turn-1], pos, radius)
			
			msg_image = font.render(str(i+1), True, player_color[op_turn-1], player_color[turn-1])
			msg_image_rect = msg_image.get_rect()
			msg_image_rect.center = pos
			screen.blit(msg_image, msg_image_rect)
			
		
		if len(self.steps) > 0:
			last_pos = self.steps[-1]
			map_x, map_y, width, height = self.getMapUnitRect(last_pos[0], last_pos[1])
			purple_color = (255, 0, 255)
			point_list = [(map_x, map_y), (map_x + width, map_y), 
					(map_x + width, map_y + height), (map_x, map_y + height)]
			pygame.draw.lines(screen, purple_color, True, point_list, 1)
			
	def drawBackground(self, screen):
		color = (0, 0, 0)
		for y in range(self.height):
			# draw a horizontal line
			start_pos, end_pos= (REC_SIZE//2, REC_SIZE//2 + REC_SIZE * y), (MAP_WIDTH - REC_SIZE//2, REC_SIZE//2 + REC_SIZE * y)
			if y == (self.height)//2:
				width = 2
			else:
				width = 1
			pygame.draw.line(screen, color, start_pos, end_pos, width)
		
		for x in range(self.width):
			# draw a horizontal line
			start_pos, end_pos= (REC_SIZE//2 + REC_SIZE * x, REC_SIZE//2), (REC_SIZE//2 + REC_SIZE * x, MAP_HEIGHT - REC_SIZE//2)
			if x == (self.width)//2:
				width = 2
			else:
				width = 1
			pygame.draw.line(screen, color, start_pos, end_pos, width)
				
		
		rec_size = 8
		pos = [(3,3), (11,3), (3, 11), (11,11), (7,7)]
		for (x, y) in pos:
			pygame.draw.rect(screen, color, (REC_SIZE//2 + x * REC_SIZE - rec_size//2, REC_SIZE//2 + y * REC_SIZE - rec_size//2, rec_size, rec_size))

class AlphaMap():
	def __init__(self, **kwargs):
		self.width = int(kwargs.get('width', 8))
		self.height = int(kwargs.get('height', 8))
		self.states = {}
		# need how many pieces in a row to win
		self.n_in_row = int(kwargs.get('n_in_row', 5))
		self.players = [1, 2]  # player1 and player2

	def init_board(self, start_player=0):
		if self.width < self.n_in_row or self.height < self.n_in_row:
			raise Exception('board width and height can not be '
							'less than {}'.format(self.n_in_row))
		self.current_player = self.players[start_player]  # start player
		# keep available moves in a list
		self.availables = list(range(self.width * self.height))
		self.states = {}
		self.last_move = -1

	def do_move(self, *location):
		if len(location) == 2:
			x,y = location
			move = x * self.height + y
		else:
			move = location[0]
		
		self.states[move] = self.current_player
		self.availables.remove(move)
		self.current_player = (
			self.players[0] if self.current_player == self.players[1]
			else self.players[1]
		)
		self.last_move = move

	def move_to_location(self, move):
		"""
		3*3 board's moves like:
		6 7 8
		3 4 5
		0 1 2
		and move 5's location is (1,2)
		"""
		h = move // self.width
		w = move % self.width
		return [h, w]

	def location_to_move(self, location):
		if len(location) != 2:
			return -1
		h = location[0]
		w = location[1]
		move = h * self.width + w
		if move not in range(self.width * self.height):
			return -1
		return move

	def current_state(self):
		"""return the board state from the perspective of the current player.
		state shape: 4*width*height
		"""

		square_state = np.zeros((4, self.width, self.height))
		if self.states:
			moves, players = np.array(list(zip(*self.states.items())))
			move_curr = moves[players == self.current_player]
			move_oppo = moves[players != self.current_player]
			square_state[0][move_curr // self.width,
							move_curr % self.height] = 1.0
			square_state[1][move_oppo // self.width,
							move_oppo % self.height] = 1.0
			# indicate the last move location
			square_state[2][self.last_move // self.width,
							self.last_move % self.height] = 1.0
		if len(self.states) % 2 == 0:
			square_state[3][:, :] = 1.0  # indicate the colour to play
		return square_state[:, ::-1, :]

	def has_a_winner(self):
		width = self.width
		height = self.height
		states = self.states
		n = self.n_in_row

		moved = list(set(range(width * height)) - set(self.availables))
		if len(moved) < self.n_in_row *2-1:
			return False, -1

		for m in moved:
			h = m // width
			w = m % width
			player = states[m]

			if (w in range(width - n + 1) and
					len(set(states.get(i, -1) for i in range(m, m + n))) == 1):
				return True, player

			if (h in range(height - n + 1) and
					len(set(states.get(i, -1) for i in range(m, m + n * width, width))) == 1):
				return True, player

			if (w in range(width - n + 1) and h in range(height - n + 1) and
					len(set(states.get(i, -1) for i in range(m, m + n * (width + 1), width + 1))) == 1):
				return True, player

			if (w in range(n - 1, width) and h in range(height - n + 1) and
					len(set(states.get(i, -1) for i in range(m, m + n * (width - 1), width - 1))) == 1):
				return True, player

		return False, -1

	def game_end(self):
		"""Check whether the game is ended or not"""
		win, winner = self.has_a_winner()
		if win:
			return True, winner
		elif not len(self.availables):
			return True, -1
		return False, -1

	def get_current_player(self):
		return self.current_player