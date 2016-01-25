# ataxx.py

import random as R

class Game:
	def __init__(self, game=None):
		if not game:
			self.b = Board()
			self.history = [] # list of copies of Board after each move, to support undo
		else:
			self.b = Board(game.b)
			self.history = []
			for board in game.history:
				self.history.append(Board(board))
		
	# attempts to make move
	# doesn't catch illegal move exceptions --- job of ui
	def move(self, old, new):
		oldBoard = Board(self.b)
		self.b.move(old, new)
		self.history.append(oldBoard)
		
	def undo(self):
		if len(self.history) == 0:
			raise Exception('Cannot undo any further')
		self.b = self.history.pop()

class Board:
	def __init__(self, board=None):
		self.SIZE = 7 # length of board
		self.squares = []
		# make grid. 0 for empty
		for i in range(self.SIZE):
			self.squares.append([])
			for j in range(self.SIZE):
				self.squares[i].append(0)
		if not board:
			# first blobs added. 1 for player 1, 2 for player 2
			self.squares[0][0] = 1
			self.squares[-1][-1] = 1
			self.squares[0][-1] = 2
			self.squares[-1][0] = 2
			self.turn = 1 # the player to move next
			self.legalMoves = []
			self.computeLegalMoves()
			self.score1 = 2
			self.score2 = 2
		else:
			# copy board
			for i in range(self.SIZE):
				for j in range(self.SIZE):
					self.squares[i][j] = board.squares[i][j]
			self.turn = board.turn
			self.legalMoves = board.legalMoves
			self.score1 = board.score1
			self.score2 = board.score2
	
	# private
	def get(self, pos):
		self.assertInBounds(pos)
		return self.squares[pos[0]][pos[1]]
	
	# private
	def assertInBounds(self, pos):
		if pos[0] < 0 or pos[0] >= self.SIZE or pos[1] < 0 or pos[1] >= self.SIZE:
			raise Exception('Index out of bounds')
	
	# private
	def set(self, pos, player):
		self.assertInBounds(pos)
		self.squares[pos[0]][pos[1]] = player
	
	def score(self):
		return (self.score1, self.score2)
	
	def computeScore(self):
		s1 = 0
		s2 = 0
		for i in range(self.SIZE):
			for j in range(self.SIZE):
				if self.squares[i][j] == 1:
					s1 += 1
				elif self.squares[i][j] == 2:
					s2 += 1
		self.score1 = s1
		self.score2 = s2
	
	# check if a proposed move is legal
	# old: (row, column) of place to move from
	# new: (row, column) of place to move to
	def isLegal(self, old, new):
		try:
			# assert that old position contains blob of current player
			if not self.get(old) == self.turn:
				return False
			# assert that new position is empty
			if self.get(new):
				return False
		except: # assert that old and new are in bounds
			return False
		# assert that y distance is no greater than 2
		if abs(old[0]-new[0]) > 2:
			return False
		# assert that x distance is no greater than 2
		if abs(old[1]-new[1]) > 2:
			return False
		return True
	
	def computeLegalMoves(self):
		self.legalMoves = []
		for i in range(self.SIZE):
			for j in range(self.SIZE):
				if self.squares[i][j] == self.turn:
					old = (i,j)
					for k in range(i-2, i+3):
						for l in range(j-2, j+3):
							new = (k,l)
							if self.isLegal(old, new):
								self.legalMoves.append((old, new))
								
	def getLegalMoves(self):
		return self.legalMoves
	
	def isJump(self, old, new):
		if abs(old[0]-new[0]) > 1 or abs(old[1]-new[1]) > 1:
			return True
		return False
	
	def otherPlayer(self):
		return 1+int(not self.turn-1) # only works with players defined as integers 1 and 2
		
	def switchPlayer(self):
		self.turn = self.otherPlayer()
	
	# make a move on the board
	# old: (row, column) of place to move from
	# new: (row, column) of place to move to
	def move(self, old, new):
		if not self.isLegal(old, new):
			raise Exception('Illegal move')
		if self.isJump(old, new):
			self.set(old, 0)
		self.set(new, self.turn)
		# absorb blobs adjacent to new
		for i in range(new[0]-1, new[0]+2):
			for j in range(new[1]-1, new[1]+2):
				try:
					if self.get((i,j)):
						self.set((i,j), self.turn)
				except: # skip over indices out of bounds
					continue
		self.switchPlayer()
		self.computeScore()
		self.computeLegalMoves()
					
	def __str__(self):
		s = '    ' + ' '.join(str(i) for i in range(self.SIZE)) + '\n'
		s += '    ' + ' '.join('|' for i in range(self.SIZE)) + '\n'
		for m in range(self.SIZE):
			s += str(m) + ' - ' + ' '.join(str(i) for i in self.squares[m])
			if m < self.SIZE-1:
				s += '\n'
		return s
		
class BasicUI:

	def __init__(self):
		self.HELP_MSG = (
			'Available commands:\n'
			'	help   - displays this message\n'
			'	undo   - undo the last move\n'
			'	new    - start a new game\n'
			'	ai     - print list of AI algorithms available\n'
			'	quit   - close the program\n'
			'Syntax for making a move:\n'
			'	<row> <column> to <row> <column>\n'
			'	Example: 0 3 to 1 2\n'
			'Syntax for having an AI make a move:\n'
			'	ai <algorithm>\n'
			'	Example: ai greedy\n'
			'	Another example: ai greedy 2\n'
			'		- (extra parameter optional. denotes depth of search)\n'
			'		- (note: depth of 3 takes a couple minutes. depth of 4 WAY TOO LONG.)\n'
			'	Type \'ai\' by itself for a list of AI algorithms\n'
			'Additional pointers:\n'
			'	You can quickly bring up previous commands using the UP arrow.'
			)
		
		self.ai = AI()
		self.g = Game()
	
	def getScoreReport(self):
		(s1, s2) = self.g.b.score()
		return 'Score:\n\tPlayer 1: %02d\n\tPlayer 2: %02d' % (s1, s2) 
	
	def parseMoveCmd(self, cmd):
		data = cmd.split()
		old = (int(data[0]), int(data[1]))
		new = (int(data[-2]), int(data[-1]))
		return (old, new)
	
	def parseAiCmd(self, cmd):
		data = cmd.split()
		if len(data) < 2:
			raise Exception('No AI algorithm provided. Type \'help\' for available commands.')
		algo = data[1]
		args = data[2:]
		return (algo, args)
	
	def processMove(self, old, new):
		if not self.g.b.legalMoves:
			print 'Cannot process moves when game is over.'
			pass
		try:
			self.g.move(old, new)
		except Exception, e:
			print e.message
			pass
	
	def run(self):
		print ''
		print '##########################'
		print '# Ataxx                  #'
		print '##########################'
		print ''
		print self.HELP_MSG
		while True:
			print self.getScoreReport()
			print ''
			print self.g.b
			print ''
			if not self.g.b.legalMoves:
				print 'Game over'
				(s1, s2) = self.g.b.score()
				if s1 > s2:
					print 'Player 1 wins\n'
				elif s1 < s2:
					print 'Player 2 wins\n'
				else:
					print 'Draw\n'
				cmd = raw_input("Type 'new', 'undo', or 'quit': ")
				while cmd not in ['new', 'undo', 'quit', 'help', 'ai']:
					cmd = raw_input("I'm serious. Type 'new', 'undo', or 'quit': ")
			else:
				cmd = raw_input("Player %d's move: " % self.g.b.turn)
			print ''
			if cmd == 'help':
				print self.HELP_MSG
			elif cmd == 'undo':
				try:
					self.g.undo()
				except Exception, e:
					print e.message + '\n'
			elif cmd == 'new':
				self.g = Game()
			elif cmd == 'ai':
				print 'List of AI algorithms:'
				for algo in self.ai.ALGORITHMS:
					print '\t' + algo
				print ''
			elif cmd == 'quit':
				break
			elif cmd.startswith('ai '):
				try:
					(algo, args) = self.parseAiCmd(cmd)
					move = self.ai.suggestMove(self.g.b, algo, args)
					if not move:
						print 'AI algorithm returned None for some reason.\n'
						continue
					(old, new) = move
					self.processMove(old, new)
					print 'Moved %d %d to %d %d\n' % (old[0], old[1], new[0], new[1])
				except Exception, e:
					print e.message + '\n'
			else:
				try:
					(old, new) = self.parseMoveCmd(cmd)
					self.processMove(old, new)
				except:
					print "Bad command or syntax for move. Type 'help' for commands and syntax.\n"

# A collection of AI algorithms				
class AI:
	def __init__(self):
		self.WIN = 1000000
		self.ALGORITHMS = [
					'random',
					'greedy',
					]
					
	def suggestMove(self, board, algo, args=None):
		if algo not in self.ALGORITHMS:
			raise Exception('%s not in list of AI algorithms')
		if not board.legalMoves:
			return None # there is no move. the game is over.
		return getattr(self, algo)(board, args) # call the appropriate ai algorithm to get a suggested move
	
	##############################################
	# Note:                                      #
	# Every AI algorithm must be a function that #
	# takes in board and args and then returns   #
	# a suggested move (old, new).               #
	##############################################
	
	def random(self, board, args):
		return R.choice(board.legalMoves)
		
	def greedy(self, board, args):
		# parse args based on where the function was called from
		if not args:
			step = 1
			returnScore = False
		elif len(args) == 1:
			step = int(args[0])
			returnScore = False
		else:
			step, returnScore = args
		
		# set a limit on how deep of recursion we will tolerate
		if step > 3:
			raise Exception('greedy only supports up to 3 steps')
		
		# return very high, very low, or zero score if the board is a win, a loss, or a draw, respectively
		if not board.legalMoves:
			p1RelScore = board.score1 - board.score2
			if p1RelScore == 0:
				return 0
			elif (board.turn == 1 and p1RelScore > 0) or (board.turn == 2 and p1RelScore < 0):
				return self.WIN
			else:
				return -self.WIN
				
		# game isn't over. calculate which move gets the max relative score and what that score is
		maxRelScore = -self.WIN
		for (old, new) in board.legalMoves:
			b = Board(board)
			b.move(old, new)
			if step <= 1: # find 1-step relative score
				if board.turn == 1:
					relScore = b.score1 - b.score2
				else:
					relScore = b.score2 - b.score1
			else:
				# find k step score through recursion
				# must record opposite, since opponent's relScore is reported by the recursion
				relScore = -self.greedy(b, (step-1, True)) 
			if relScore > maxRelScore:
				maxRelScore = relScore
				maxOld = old
				maxNew = new
		if returnScore:
			return maxRelScore
		else:
			return (maxOld, maxNew)
	
if __name__ == '__main__':
	ui = BasicUI()
	ui.run()
