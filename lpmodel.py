from pulp import LpProblem, LpMinimize, LpVariable, LpInteger, lpSum, LpStatus
import constants as ct
import numpy as np


class Lpmodel:

    def __init__(self, costs, sigmas, thetas, alphas, bethas):
        self.prob = LpProblem("AsignacionPacientes", LpMinimize)
        self.A = LpVariable.dicts(
            "A", (ct.citiesIndex, ct.citiesIndex, ct.daysIndex), 0, None, LpInteger)
        self.D = LpVariable.dicts(
            "D", (ct.citiesIndex,  ct.daysIndex), 0, None, LpInteger)
        self.H = LpVariable.dicts(
            "H", (ct.citiesIndex,  ct.daysIndex), 0, None, LpInteger)
        self.costs = costs
        self.sigmas = sigmas
        self.thetas = thetas
        self.alphas = alphas
        self.bethas = bethas
        self.outMatrix = np.zeros((ct.citiesLength, ct.citiesLength))

    def execute(self):
        self.processOne()
        self.processTwo()
        self.processThree()
        self.processFour()
        self.processFive()
        self.solve()
        return self.outMatrix

    def processOne(self):
        '''
        The objective function is added to prob.
        The sum of the transportation costs and the building fixed costs
        '''
        self.prob += lpSum([[self.H[i][t]*(ct.days-t)*100 for i in ct.citiesIndex] for t in ct.daysIndex])+lpSum(
            [[[self.A[i][j][t]*self.costs[i][j] for i in ct.citiesIndex] for j in ct.citiesIndex] for t in ct.daysIndex])

    def processTwo(self):
        '''
        Constrain balance del 1er periodo de UCIs disponibles.
        d[i,1] + sum {i in LOCALS} a[i,i,0] = Sigma[i]
        '''
        for j in ct.citiesIndex:
            self.prob += self.D[j][0] + lpSum([self.A[i][j][0]
                                               for i in ct.citiesIndex]) == self.sigmas[j]

    def processThree(self):
        '''
        Constrain balance del 1er periodo de pacientes no asignados
        Subject to Backorder_DiaUno {j in LOCALS}:
        h[i,0] +  sum {j in LOCALS} a[i,j,0] = Theta[i]
        '''
        for i in ct.citiesIndex:
            self.prob += self.H[i][0] + lpSum([self.A[i][j][0]
                                               for j in ct.citiesIndex]) == self.thetas[i]

    def processFour(self):
        '''
        # Restricción de balance, depende del númerod e dias del horizonte de planeación.
        Case IF
        La PRIMERA RESTRICCIÓN CONTABILIZA T < epsilon
        Constraint balance de UCIs antes de epsilon
        subject to Balance_InvAntesEpsilon {j1 in LOCALS, t in DIAS: 2<=t<=epsilon}:
        d[j,t] - d[j,t-1]  + sum {i in LOCALS} d[i,j,t] = alpha[j,t];
        Case ELSE
        Se ejecutan estas dos restricciones si el número de dias es mayor a epsilon
        Constraint balance de UCIs despues de epsilon
            Subject to Balance_InvUltDias {j1 in LOCALS, t in DIAS: t>epsilon}:
            d[j,t] = d[j,t-1] + alpha[j,t] + sum {i in LOCALS} alpha[i,j,t-epsilon] - sum{i in LOCALS} alpha[i,j,t] ;
        '''
        if ct.days <= ct.epsilon:
            for j in ct.citiesIndex:
                for t in range(1, ct.daysIndex):
                    self.prob += self.D[j][t] - self.D[j][t-1] + lpSum(
                        [self.A[i][j][t] for i in ct.citiesIndex]) == self.alphas[j][t]
        else:
            for j in ct.citiesIndex:
                for t in range(1, ct.epsilon):
                    self.prob += self.D[j][t] - self.D[j][t-1] + lpSum(
                        [self.A[i][j][t] for i in ct.citiesIndex]) == self.alphas[j][t]

            for j in ct.citiesIndex:
                for t in range(ct.epsilon, ct.days):
                    self.prob += self.D[j][t] == self.D[j][t-1] + self.alphas[j][t] + lpSum(
                        [self.A[i][j][t-ct.epsilon] for i in ct.citiesIndex]) - lpSum([self.A[i][j][t] for i in ct.citiesIndex])

    def processFive(self):
        for i in ct.citiesIndex:
            for t in range(1, ct.days):
                self.prob += self.H[i][t] == self.H[i][t-1] + self.bethas[i][t] - \
                    lpSum([self.A[i][j][t] for j in ct.citiesIndex])

    def solve(self):
        '''
        The problem data is written to an .lp file
        The problem is solved using PuLP's choice of Solver
        '''
        self.prob.solve()
        for i in ct.citiesIndex:
            for j in ct.citiesIndex:
                self.outMatrix[i][j] = self.A[i][j][0].varValue
