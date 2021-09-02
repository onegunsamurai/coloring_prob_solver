# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 23:44:15 2020

@author: soshr
"""

from ortools.sat.python import cp_model
from ortools.sat.pywrapsat import SolutionCallback
from ortools.sat import pywrapsat
import time

class CpSolverSolutionCallback(pywrapsat.SolutionCallback):
    """Solution callback.

  This class implements a callback that will be called at each new solution
  found during search.

  The method OnSolutionCallback() will be called by the solver, and must be
  implemented. The current solution can be queried using the BooleanValue()
  and Value() methods.

  It inherits the following methods from its base class:

  * `ObjectiveValue(self)`
  * `BestObjectiveBound(self)`
  * `NumBooleans(self)`
  * `NumConflicts(self)`
  * `NumBranches(self)`
  * `WallTime(self)`
  * `UserTime(self)`

  These methods returns the same information as their counterpart in the
  `CpSolver` class.
  """

    def __init__(self):
        pywrapsat.SolutionCallback.__init__(self)

    def OnSolutionCallback(self):
        """Proxy for the same method in snake case."""
        self.on_solution_callback()

    def BooleanValue(self, lit):
        """Returns the boolean value of a boolean literal.

    Args:
        lit: A boolean variable or its negation.

    Returns:
        The Boolean value of the literal in the solution.

    Raises:
        RuntimeError: if `lit` is not a boolean variable or its negation.
    """
        if not self.HasResponse():
            raise RuntimeError('Solve() has not be called.')
        if isinstance(lit, numbers.Integral):
            return bool(lit)
        elif isinstance(lit, IntVar) or isinstance(lit, _NotBooleanVariable):
            index = lit.Index()
            return self.SolutionBooleanValue(index)
        else:
            raise TypeError('Cannot interpret %s as a boolean expression.' %
                            lit)

    def Value(self, expression):
        """Evaluates an linear expression in the current solution.

    Args:
        expression: a linear expression of the model.

    Returns:
        An integer value equal to the evaluation of the linear expression
        against the current solution.

    Raises:
        RuntimeError: if 'expression' is not a LinearExpr.
    """
        if not self.HasResponse():
            raise RuntimeError('Solve() has not be called.')
        if isinstance(expression, numbers.Integral):
            return expression
        if not isinstance(expression, LinearExpr):
            raise TypeError('Cannot interpret %s as a linear expression.' %
                            expression)

        value = 0
        to_process = [(expression, 1)]
        while to_process:
            expr, coef = to_process.pop()
            if isinstance(expr, _ProductCst):
                to_process.append(
                    (expr.Expression(), coef * expr.Coefficient()))
            elif isinstance(expr, _SumArray):
                for e in expr.Expressions():
                    to_process.append((e, coef))
                    value += expr.Constant() * coef
            elif isinstance(expr, _ScalProd):
                for e, c in zip(expr.Expressions(), expr.Coefficients()):
                    to_process.append((e, coef * c))
                value += expr.Constant() * coef
            elif isinstance(expr, IntVar):
                value += coef * self.SolutionIntegerValue(expr.Index())
            elif isinstance(expr, _NotBooleanVariable):
                value += coef * (1 -
                                 self.SolutionIntegerValue(expr.Not().Index()))
        return value

class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions (variable values, time)."""

    def __init__(self, variables):
        CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.__solution_count = 0
        self.__start_time = time.time()

    def on_solution_callback(self):
        """Called on each new solution."""
        current_time = time.time()
        print('Solution %i, time = %0.2f s' %
              (self.__solution_count, current_time - self.__start_time))
        for v in self.__variables:
            print('  %s = %i' % (v, self.Value(v)), end=' ')
        print()
        self.__solution_count += 1

    def solution_count(self):
        """Returns the number of solutions found."""
        return self.__solution_count


file_location = r"C:\Users\soshr\Desktop\Проекты\Optimization\Coloring\coloring\data\gc_500_1"

with open(file_location, 'r') as input_data_file:
    input_data = input_data_file.read()
# Modify this code to run your optimization algorithm

    # parse the input
    lines = input_data.split('\n')

    first_line = lines[0].split()
    node_count = int(first_line[0])
    edge_count = int(first_line[1])

    edges = []

    for i in range(1, edge_count + 1):
        line = lines[i]
        parts = line.split()
        edges.append((int(parts[0]), int(parts[1])))

    # build a trivial solution
    # every node has its own color

    k = 1
    while True:
        model = cp_model.CpModel()
        nodes = []
        for i in range(0, node_count):
            i = model.NewIntVar(0,k, "node %i" % i)
            nodes.append(i)
        for i, conn in enumerate(edges):
            model.Add(nodes[conn[0]] != nodes[conn[1]])

        solver = cp_model.CpSolver()
        solution_printer = VarArraySolutionPrinter(nodes)
        status = solver.Solve(model)
        solution = []
        if status == cp_model.FEASIBLE:
            print('Solution is FEASIBLE \n\n\n')
            print("Colors Used: %i" % k )
            for i in nodes:
                i = solver.Value(i)
                solution.append(i)
            break
        if status == cp_model.OPTIMAL:
            print('Solution is OPTIMAL \n\n\n')
            print("Colors Used: %i \n\n\n" % k )
            for i in nodes:
                i = solver.Value(i)
                solution.append(i)
            break
        if status == cp_model.INFEASIBLE:
            k = k + 1

    print(solution)
