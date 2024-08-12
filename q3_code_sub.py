from __future__ import division
from pyomo.environ import *

num_nodes = 40

edges = [(0, 1, 200), (0, 6, 200), (1, 2, 75), (1, 7, 200), (2, 3, 80), (2, 8, 100), (3, 4, 200), (3, 9, 100), (4, 5, 100), (4, 19, 200),
 (5, 20, 400), (6, 7, 100), (6, 10, 100), (7, 12, 100), (8, 9, 100), (8, 13, 200), (9, 18, 200), (10, 11, 50), (10, 14, 50), (11, 12, 50),
 (11, 15, 50), (12, 13, 75), (13, 17, 130), (14, 15, 50), (14, 25, 200), (15, 16, 75), (16, 17, 75), (16, 21, 75), (17, 18, 150), (17, 22, 75), (18, 19, 50),
 (19, 20, 100), (20, 28, 250), (21, 22, 75), (21, 23, 75), (22, 24, 75), (23, 24, 75), (24, 27, 75), (25, 26, 500), (25, 37, 100), (26, 27, 100), (26, 29, 100),
 (27, 28, 300), (28, 33, 150), (29, 30, 75), (29, 31, 20), (30, 32, 20), (31, 32, 75), (31, 34, 70), (32, 33, 250), (32, 35, 70), (33, 36, 100), (34, 35, 100),
 (34, 38, 70), (35, 36, 250), (36, 39, 50), (37, 38, 400), (38, 39, 300)]

model = ConcreteModel()

model.x = Var(range(num_nodes), range(num_nodes), within=Binary)
model.u = Var(range(num_nodes), within=NonNegativeReals)

def obj_rule(model):
    sum = 0
    for edge in edges:
        sum = sum + edge[2] * (model.x[int(edge[0]),int(edge[1])])
    return sum

def visit_rule(model,i):
    sum = 0
    for j in range(num_nodes):
        sum = sum + model.x[i,j]
    return sum == 1

def leave_rule(model,j):
    sum = 0
    for i in range(num_nodes):
        sum = sum + model.x[i,j]
    return sum == 1

# def mtz_constraints_rule(model, i):
#     if i != 0:
#         return sum(model.x[i, j] for j in range(num_nodes) if j != i) == 1 - model.u[i]
#     else:
#         return Constraint.Skip

def mtz_constraints_rule(model, i, j):
    if i != 0:
        return model.u[i] + model.x[i,j] <= model.u[j] + (num_nodes - 1) * (1 - model.x[i,j])
    else:
        return Constraint.Skip

model.obj = Objective(rule=obj_rule, sense=maximize)
model.con1 = Constraint(range(num_nodes), rule=visit_rule)
model.con2 = Constraint(range(num_nodes), rule=leave_rule)

model.con3 = Constraint(range(num_nodes), range(num_nodes), rule=mtz_constraints_rule)

opt = SolverFactory("ipopt", executable='/opt/homebrew/bin/ipopt', validate=False)
result = opt.solve(model)

if result.solver.status == SolverStatus.ok and result.solver.termination_condition == TerminationCondition.optimal:
    print("Optimized Objective Value : ", (model.obj())*1.6, " meters")
else:
    print("Optimization was not successful.")