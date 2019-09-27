import copy
import numpy as np


class RegretSolver:
	def __init__(self, dim):
		self.round = 0
		self.sumRewVector = np.zeros(dim)
		self.sumStgyVector = np.zeros(dim)
		self.gained = 0
		self.sumWeight = 0.0
		self.dim = dim
		self.curstgy = np.ones(dim) / self.dim
		
	def take(self):
		ret = np.zeros(self.dim)
		for d in range(self.dim):
			if self.sumRewVector[d] > self.gained:
				ret[d] = self.sumRewVector[d] - self.gained
		s = sum(ret)
		if s < 1e-8:
			return np.ones(self.dim) / self.dim
		return ret / s

	def receive(self, rew, stgy=0, weight=1.0):
		if type(stgy) == list:
			stgy = np.array(stgy)
		elif type(stgy) == int:
			stgy = self.take()
		curgain = np.inner(rew, stgy)
		self.gained += curgain
		self.round += 1
		self.sumRewVector += rew
		self.sumStgyVector += self.curstgy * weight 
		self.curstgy = stgy.copy()
		self.sumWeight += weight

	def avg(self):
		if self.sumWeight < 1e-8:
			return np.ones(self.dim) / self.dim
		return self.sumStgyVector / self.sumWeight

	def regret(self):
		m = -np.inf 
		for i in range(self.dim):
			m = max(m, self.sumRewVector[i])
		return m - self.gained

def exploitability(game, stgy_prof):
	def best(owner, iset, probs):
		hists = game.Iset2Hists[owner][iset]
		if game.isTerminal[hists[0]]:
			ret = np.zeros(2)
			for i, h in enumerate(hists):
				tmp = np.array(game.reward[h]) * probs[i]
				ret += tmp

			return ret
		player = game.playerOfIset[owner][iset]
		if player != owner:
			obsnacts = game.nactsOnIset[owner][iset]
			if obsnacts == 1:
				realnacts = game.nactsOnHist[hists[0]]
				nxtprobs = np.zeros(0)
				for i in range(realnacts):
					tmp = np.zeros(len(hists))
					for j, p in enumerate(probs):
						h = hists[j]
						_stgy = None
						if player == 2:
							_stgy = game.chanceprob[h]
						else:
							piset = game.Hist2Iset[player][h]
							_stgy = stgy_prof[player][piset]
						tmp[j] = probs[j] * _stgy[i]
					nxtprobs = np.concatenate((nxtprobs, tmp))
				return best(owner, game.isetSucc[owner][iset][0], nxtprobs)
			else:
				ret = np.zeros(2)
				for i in range(obsnacts):
					nxtprobs = np.zeros(0)
					tmp = np.zeros(len(hists))
					for j, p in enumerate(probs):
						h = hists[j]
						_stgy = None
						if player == 2:
							_stgy = game.chanceprob[h]
						else:
							piset = game.Hist2Iset[player][h]
							_stgy = stgy_prof[player][piset]
						tmp[j] = probs[j] * _stgy[i]
					nxtprobs = np.concatenate((nxtprobs, tmp))
					ret += best(owner, game.isetSucc[owner][iset][i], nxtprobs)
				return ret
		else:
			nacts = game.nactsOnIset[owner][iset]
			ret = -np.inf * np.ones(2)
			for i in range(nacts):
				tmp = best(owner, game.isetSucc[owner][iset][i], probs.copy())
				if tmp[owner] > ret[owner]:
					ret = tmp
			return ret



	b0 = best(0, 0, np.ones(1))
	b1 = best(1, 0, np.ones(1))
	return b0[0] + b1[1]


def generateOutcome(game, stgy_prof):
	outcome = np.zeros(game.numHists).tolist()
	rew = np.zeros(game.numHists)
	def solve(hist):
		if game.isTerminal[hist]:
			rew[hist] = game.reward[hist][0]
			outcome[hist] = []
			return rew[hist]
		outcome[hist] = []
		player = game.playerOfHist[hist]
		stgy = None
		if player < 2:
			iset = game.Hist2Iset[player][hist]
			stgy = stgy_prof[player][iset]
		else:
			stgy = game.chanceprob[hist]
		for a in range(game.nactsOnHist[hist]):
			srew = solve(game.histSucc[hist][a])
			outcome[hist].append(srew)
			rew[hist] += stgy[a] * srew

		return rew[hist]

	solve(0)
	return outcome, rew

	

class RegretSolverPlus:
	def __init__(self, dim):
		self.round = 0
		self.sumRewVector = np.zeros(dim)
		self.sumStgyVector = np.zeros(dim)
		self.sumQ = np.zeros(dim)
		self.gained = 0
		self.sumWeight = 0.0
		self.dim = dim
		self.curstgy = np.ones(dim) / self.dim
		
	def take(self):
		s = sum(self.sumQ)
		if s < 1e-8:
			return np.ones(self.dim) / self.dim
		return self.sumQ / s

	def receive(self, rew, stgy=0, weight=1.0):
		if type(stgy) == list:
			stgy = np.array(stgy)
		elif type(stgy) == int:
			stgy = self.take()
		curgain = np.inner(rew, stgy)
		for i in range(self.dim):
			self.sumQ[i] += rew[i] - curgain
			self.sumQ[i] = max(self.sumQ[i], 0)
		self.gained += curgain
		self.round += 1
		self.sumRewVector += rew
		self.sumStgyVector += self.curstgy * self.round# weight 
		self.curstgy = stgy.copy()
		self.sumWeight += self.round

	def avg(self):
		if self.sumWeight < 1e-8:
			return np.ones(self.dim) / self.dim
		return self.sumStgyVector / self.sumWeight

	def regret(self):
		m = -np.inf 
		for i in range(self.dim):
			m = max(m, self.sumRewVector[i])
		return m - self.gained
