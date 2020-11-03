from pulp import *
import numpy as np
import constants as ct
import exceptions
from reader import readCSV
from utils import gompertzNewCases


class PatientsAllocationModel:
    def __init__(self):
        self.sigmas = readCSV(ct.sigmasPath)[0]
        self.thetas = readCSV(ct.thetasPath)[0]
        self.gompertzParams = readCSV(ct.gompertzPath)
        self.costs = readCSV(ct.costsPath)
        self.elapsedDays = ct.getElapsedDays()
        self.bethas = np.zeros((ct.citiesLength, ct.days))
        self.alphas = np.zeros((ct.citiesLength, ct.days))

    def readSigmas(self, sigmasArray):
        sigmasArray = np.array(sigmasArray).astype(np.float)
        if sigmasArray.shape != (ct.citiesLength,):
            raise exceptions.InvalidArrayShape

        self.sigmas = sigmasArray

    def readThetas(self, thetasArray):
        thetasArray = np.array(thetasArray).astype(np.float)
        if thetasArray.shape != (ct.citiesLength,):
            raise exceptions.InvalidArrayShape

        self.thetas = thetasArray

    def readGompertzParams(self, gompertzArray):
        gompertzArray = np.array(gompertzArray).astype(np.float)
        if gompertzArray.shape != (ct.gompertzParamsLength, ct.citiesLength):
            raise exceptions.InvalidArrayShape

        self.gompertzParams = gompertzArray

    def execute(self):
        self.__getPatientsForecasts()
        self.__getForecastsForFreeICU()

    def __getPatientsForecasts(self):
        for i in ct.citiesLengthIndex:
            for t in ct.daysIndex:
                a = self.gompertzParams[i][0]
                b = self.gompertzParams[i][1]
                r = self.gompertzParams[i][2]
                probHospital = self.gompertzParams[i][3]
                probICU = self.gompertzParams[i][5]
                day = self.elapsedDays + t

                newDiagnostics = gompertzNewCases(a, b, r, day)
                self.bethas[i][t] = int(
                    newDiagnostics * probHospital * probICU)

    def __getForecastsForFreeICU(self):
        for i in ct.citiesLengthIndex:
            for t in ct.daysIndex:
                if t < ct.epsilon:
                    a = self.gompertzParams[i][0]
                    b = self.gompertzParams[i][1]
                    r = self.gompertzParams[i][2]
                    probHospital = self.gompertzParams[i][3]
                    probICU = self.gompertzParams[i][5]
                    day = self.elapsedDays + t

                    previousDiagnostics = gompertzNewCases(a, b, r, day)
                    self.alphas[i][t] = int(previousDiagnostics *
                                            probHospital * probICU)
                else:
                    self.alphas[i][t] = 0


model = PatientsAllocationModel()
model.execute()

# # Creates the 'prob' variable to contain the problem data
# prob = LpProblem("AsignacionPacientes", LpMinimize)

# A = LpVariable.dicts("A", (nLocals, nLocals, nDias), 0, None, LpInteger)
# D = LpVariable.dicts("D", (nLocals, nDias), 0, None, LpInteger)
# H = LpVariable.dicts("H", (nLocals, nDias), 0, None, LpInteger)

# # The objective function is added to prob - The sum of the transportation costs and the building fixed costs
# prob += lpSum([[H[i][t]*(Dias-t)*100 for i in nLocals] for t in nDias])+lpSum(
#     [[[A[i][j][t]*Costo[i][j] for i in nLocals] for j in nLocals] for t in nDias])


# # Constraint balance del 1er periodo de UCIs disponibles
# # subject to Balance_InvDiaUno {j1 in LOCALS}:
# # D[j,1] + sum {j in LOCALS} A[i,j,0] = Sigma[j]

# for j in nLocals:
#     prob += D[j][0] + lpSum([A[i][j][0] for i in nLocals]) == Sigma[j]


# # Constraint balance del 1er periodo de pacientes no asignados
# # subject to Backorder_DiaUno {j in LOCALS}:
# # H[i,0] +  sum {j in LOCALS} A[i,j,0] = Theta[i]
# for i in nLocals:
#     prob += H[i][0] + lpSum([A[i][j][0] for j in nLocals]) == Theta[i]


# # Restricción de balance, depende del númerod e dias del horizonte de planeación
# if Dias <= epsilon:
#     # Constraint balance de UCIs antes de epsilon
#     # subject to Balance_InvAntesEpsilon {j1 in LOCALS, t in DIAS: 2<=t<=epsilon}:
#     # D[j,t] - D[j,t-1]  + sum {i in LOCALS} A[i,j,t] = Alpha[j,t];
#     for i in nLocals:
#         for i in range(1, nDias):
#             prob += D[j][t] - D[j][t-1] + \
#                 lpSum([A[i][j][t] for i in nLocals]) == Alpha[j][t]

# else:
#     # // Se ejecutan estas dos restricciones si el número de dias es mayor a epsilon
#     # La PRIMERA RESTRICCIÓN CONTABILIZA T< epsilon
#     for i in nLocals:
#         for t in range(1, epsilon):  # Arreglar
#             prob += D[j][t] - D[j][t-1] + \
#                 lpSum([A[i][j][t] for i in nLocals]) == Alpha[j][t]

#     # Constraint balance de UCIs despues de epsilon
#             # subject to Balance_InvUltDias {j1 in LOCALS, t in DIAS: t>epsilon}:
#             # 	D[j,t] = D[j,t-1] + Alpha[j,t] + sum {i in LOCALS} A[i,j,t-epsilon] - sum{i in LOCALS} A[i,j,t] ;

#     for i in nLocals:
#         for t in range(epsilon, Dias):
#             prob += D[j][t] == D[j][t-1] + Alpha[j][t] + lpSum(
#                 [A[i][j][t-epsilon] for i in nLocals]) - lpSum([A[i][j][t] for i in nLocals])


# # Constraint balance de pacientes no asignados para t>1
# # subject to Backorder_DiaNoUno {j in LOCALS, t in DIAS: t>=2}:
# # 	H[i,t] = H[i,t-1] + Beta[i,t] - sum {j in LOCALS} A[i,j,t];

# for i in nLocals:
#     for t in range(1, Dias):
#         prob += H[i][t] == H[i][t-1] + Beta[i][t] - \
#             lpSum([A[i][j][t] for j in nLocals])


# # The problem data is written to an .lp file
# prob.writeLP("Asignacion.lp")

# # The problem is solved using PuLP's choice of Solver
# prob.solve()

# # The status of the solution is printed to the screen
# print("Status:", LpStatus[prob.status])

# # Each of the variables is printed with it's resolved optimum value

# sA = np.zeros((Locals, Locals, Dias))

# for i in nLocals:
#     for j in nLocals:
#         for t in nDias:
#             sA[i, j, t] = A[i][j][t].varValue
#             if t == 0 and A[i][j][t].varValue > 0:
#                 #cplex.output().print("Asignaciones " + i + j + t + " de pacientes en UCIs");
#                 print("A_", Municipios[i], "					",
#                       Municipios[j], "", t, "		", A[i][j][t].varValue)


# # for v in prob.variables():
# #  if v.varValue > 0:
# #    print(v.name, "=", v.varValue)


# # The optimised objective function value is printed to the screen
# print("Total Costs = ", value(prob.objective))
