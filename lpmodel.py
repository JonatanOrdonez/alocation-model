from pulp import LpProblem, LpMinimize, LpVariable, LpInteger, lpSum
import constants as ct


class Lpmodel:
    def __init__(self, costs, sigmas, thetas, alphas):
        self.prob = LpProblem("AsignacionPacientes", LpMinimize)
        self.a = LpVariable.dicts(
            "A", (ct.citiesLengthIndex, ct.citiesLengthIndex, ct.daysIndex), 0, None, LpInteger)
        self.d = LpVariable.dicts(
            "D", (ct.citiesLengthIndex,  ct.daysIndex), 0, None, LpInteger)
        self.h = LpVariable.dicts(
            "H", (ct.citiesLengthIndex,  ct.daysIndex), 0, None, LpInteger)
        self.costs = costs
        self.sigmas = sigmas
        self.thetas = thetas
        self.alphas = alphas

    def execute(self):
        self.processOne()

    def processOne(self):
        '''
        The objective function is added to prob.
        The sum of the transportation costs and the building fixed costs
        '''
        hSum = [[self.h[i][t] * (ct.days - t) * 100 for i in ct.citiesLengthIndex]
                for t in ct.daysIndex]
        aSum = [[[self.a[i][j][t] * self.costs[i][j] for i in ct.citiesLengthIndex]
                 for j in ct.daysIndex] for t in ct.daysIndex]

        self.prob += lpSum(hSum) + lpSum(aSum)

    def processTwo(self):
        '''
        Constrain balance del 1er periodo de UCIs disponibles.
        d[i,1] + sum {i in LOCALS} a[i,i,0] = Sigma[i]
        '''
        for i in ct.citiesLengthIndex:
            aSum = [self.a[i][i][0] for i in ct.citiesLengthIndex]

            self.prob += self.d[i][0] + lpSum(aSum) == self.sigmas[i]

    def processThree(self):
        '''
        Constrain balance del 1er periodo de pacientes no asignados
        Subject to Backorder_DiaUno {j in LOCALS}:
        h[i,0] +  sum {j in LOCALS} a[i,j,0] = Theta[i] 
        '''
        for i in ct.citiesLengthIndex:
            aSum = [self.a[i][j][0] for j in ct.citiesLengthIndex]

            self.prob += self.h[i][0] + lpSum(aSum) == self.thetas[i]

    def processFour(self):
        '''
        #Restricción de balance, depende del númerod e dias del horizonte de planeación.
        Case IF
        Constraint balance de UCIs antes de epsilon
        subject to Balance_InvAntesEpsilon {j1 in LOCALS, t in DIAS: 2<=t<=epsilon}:
        D[j,t] - D[j,t-1]  + sum {i in LOCALS} A[i,j,t] = Alpha[j,t];
        Case ELSE
        Se ejecutan estas dos restricciones si el número de dias es mayor a epsilon
        La PRIMERA RESTRICCIÓN CONTABILIZA T < epsilon
        '''
        if ct.days <= ct.epsilon:
            for i in ct.citiesLengthIndex:
                for j in range(1, ct.daysIndex):
                    aSum = [self.a[i][j][t] for i in ct.citiesLengthIndex]
                    self.prob += self.d[j][t] - self.d[j][t - 1] + lpSum(aSum) == self.alphas[j][t]
