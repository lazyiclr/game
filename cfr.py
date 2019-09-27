import numpy as np
from LeducHoldem import Game
import copy
import queue
import utils
from utils import RegretSolver, exploitability, generateOutcome, RegretSolverPlus
import time



class CFR:
	def __init__(self, game, Type="regretmatching"):
		self.game = game
		self.Type = Type
		Solver = None
		if Type == "regretmatching":
			Solver=RegretSolver
		else:
			Solver=RegretSolverPlus


		self.isetflag = [-1 * np.ones(game.numIsets[0]), -1 * np.ones(game.numIsets[1])]


		self.solvers = []
		self.solvers.append(list(map(lambda x:  Solver(game.nactsOnIset[0][x]), range(game.numIsets[0]))))
		self.solvers.append(list(map(lambda x:  Solver(game.nactsOnIset[1][x]), range(game.numIsets[1]))))
		self.stgy = [[], []]
		for i, iset in enumerate(range(game.numIsets[0])):
			nact = game.nactsOnIset[0][iset]
			if game.playerOfIset[0][iset] == 0:
				self.stgy[0].append(np.ones(nact) / nact)
			else:
				self.stgy[0].append(np.ones(0))

		for i, iset in enumerate(range(game.numIsets[1])):
			nact = game.nactsOnIset[1][iset]
			if game.playerOfIset[1][iset] == 1:
				self.stgy[1].append(np.ones(nact) / nact)
			else:
				self.stgy[1].append(np.ones(0))

		self.outcome,self.reward = generateOutcome(game, self.stgy)
		self.nodestouched = 0
		self.round = -1


		self.sumstgy = [[], []]
		for i, iset in enumerate(range(game.numIsets[0])):
			nact = game.nactsOnIset[0][iset]
			if game.playerOfIset[0][iset] == 0:
				self.sumstgy[0].append(np.ones(nact) / nact)
			else:
				self.sumstgy[0].append(np.ones(0))
		for i, iset in enumerate(range(game.numIsets[1])):
			nact = game.nactsOnIset[1][iset]
			if game.playerOfIset[1][iset] == 1:
				self.sumstgy[1].append(np.ones(nact) / nact)
			else:
				self.sumstgy[1].append(np.ones(0))


	def updateAll(self):
		game = self.game
		self.round += 1
		self.update(0, 0, [np.ones(1), np.ones(1)], [0])
		self.update(1, 0, [np.ones(1), np.ones(1)], [0])


		def updStgy(owner, iset):
			if self.isetflag[owner][iset] != self.round:
				return
			player = game.playerOfIset[owner][iset]
			if player == owner:
				self.stgy[owner][iset] = self.solvers[owner][iset].curstgy.copy()
			for nxtiset in game.isetSucc[owner][iset]:
				updStgy(owner, nxtiset)
		updStgy(0, 0)
		updStgy(1, 0)
		

		def updSumstgy(owner, iset, prob = 1.0):
			player = game.playerOfIset[owner][iset]
			if player == owner:

				if self.Type == "regretmatching":
					self.sumstgy[owner][iset] += prob * self.stgy[player][iset]
				else:
					self.sumstgy[owner][iset] += prob * (self.round + 1) * self.stgy[player][iset]
				for aid, nxtiset in enumerate(game.isetSucc[owner][iset]):
					if prob * self.stgy[player][iset][aid] > 1e-8:
						updSumstgy(owner, nxtiset, prob * self.stgy[player][iset][aid])
			else:
				for aid, nxtiset in enumerate(game.isetSucc[owner][iset]):
					updSumstgy(owner, nxtiset, prob)
		updSumstgy(0, 0)
		updSumstgy(1, 0)

	def update(self, owner, iset, probs, histories):
		self.isetflag[owner][iset] = self.round
		if len(histories) == 0:
			return np.zeros(0)
		
		self.nodestouched += len(histories)
		game = self.game
		player = game.playerOfIset[owner][iset] 

		if game.isTerminal[game.Iset2Hists[owner][iset][0]]:
			ret = np.zeros(len(histories))
			for hid, h in enumerate(histories):
				ret[hid] = game.reward[h][owner]
			return  ret

		if player == owner:
			nacts = game.nactsOnIset[owner][iset]
			ret = np.zeros(len(histories))
			cfv = np.zeros(game.nactsOnIset[owner][iset])
			for a in range(nacts):
				nxthistories = []
				nxtprobs = [probs[0].copy(), probs[1].copy()]
				nxtprobs[owner] *= self.stgy[owner][iset][a]
				for h in histories:
					nxthistories.append(game.histSucc[h][a])
				tmpr = self.update(owner, game.isetSucc[owner][iset][a], nxtprobs, nxthistories)
				for nhid, nh in enumerate(nxthistories):
					cfv[a] += probs[1 - owner][nhid] * tmpr[nhid]
					ret[nhid] += tmpr[nhid] * self.stgy[player][iset][a]
			#for hid, h in enumerate(histories):
			#	cfv += np.array(self.outcome[h]) * probs[1 - owner][hid]
			#if owner == 1:
			#	cfv *= -1.0
			self.solvers[owner][iset].receive(cfv, weight=probs[owner][0])
			return ret

		else:
			obsnact = game.nactsOnIset[owner][iset]
			nacts = np.array(list(map(lambda _u: game.nactsOnHist[_u], histories)))
			truenact = int(nacts.max())

			if truenact == obsnact:
				ret = np.zeros(len(histories))
				for i in range(truenact):
					nxtiset = game.isetSucc[owner][iset][i]
					nxtprobs = [[],[]]
					nxthistories = []
					_ps = []
					_ids = []
					for j, h in enumerate(histories):
						player = game.playerOfHist[h]
						stgy = None
						if player == 2:
							stgy = game.chanceprob[h]
						else:
							piset = game.Hist2Iset[player][h]
							stgy = self.stgy[player][piset]
						if probs[1 - owner][j] * stgy[i] < 1e-5:#player == 2 and 
							pass
						else:
							nxtprobs[1 - owner].append(probs[1 - owner][j] * stgy[i])
							nxthistories.append(game.histSucc[h][i])
							nxtprobs[owner].append(probs[owner][j])
							_ps.append(stgy[i])
							_ids.append(j)
					nxtprobs[0] = np.array(nxtprobs[0])
					nxtprobs[1] = np.array(nxtprobs[1])
					tmpr = self.update(owner, nxtiset, nxtprobs, nxthistories)
					if len(_ids) > 0:
						for _id, _r in enumerate(tmpr):
							ret[_ids[_id]] += _ps[_id] * _r
				return ret

			else:
				ret = np.zeros(len(histories))
				nxtprobs = [[], []]
				nxthistories = []
				_ps = []
				_ids = []
				for aid in range(truenact):
					for hid, h in enumerate(histories):


						player = game.playerOfHist[h]
						stgy = None
						if player == 2:
							stgy = game.chanceprob[h]
						else:
							piset = game.Hist2Iset[player][h]
							stgy = self.stgy[player][piset]
						if probs[1 - owner][hid] * stgy[aid] < 1e-5:#player == 2 and 
							pass
						else:
							nxtprobs[1 - owner].append(probs[1 - owner][hid] * stgy[aid])
							nxthistories.append(game.histSucc[h][aid])
							nxtprobs[owner].append(probs[owner][hid])
							_ps.append(stgy[aid])
							_ids.append(hid)
				nxtiset = game.isetSucc[owner][iset][0]
				nxtprobs[0] = np.array(nxtprobs[0])
				nxtprobs[1] = np.array(nxtprobs[1])
				tmpr = self.update(owner, game.isetSucc[owner][iset][0], nxtprobs, nxthistories)
				for _i, _r in enumerate(tmpr):
					ret[_ids[_i]] += _r * _ps[_i]
				return ret


	def getExploitability(self):
		stgy_prof = []
		def avg(_x):
			s = np.sum(_x)
			l = _x.shape[0]
			if s < 1e-5:
				return np.ones(l) / l
			return _x / s
		stgy_prof.append(list(map( lambda _x: avg(_x), self.sumstgy[0] )))
		stgy_prof.append(list(map( lambda _x: avg(_x), self.sumstgy[1] )))

		return exploitability(self.game, stgy_prof)

