'''
Created on Apr 24, 2013

@author: khooks
'''
from google.apputils import app
import gflags
from constraint_solver import pywrapcp



def main(unuseg):
    
    solver = pywrapcp.Solver('CP is fun')
    
    digits = range(0, 10)
    
    c = solver.IntVar(digits, 'C')
    p = solver.IntVar(digits, 'P')
    i = solver.IntVar(digits, 'i')
    s = solver.IntVar(digits, 's')
    f = solver.IntVar(digits, 'F')
    u = solver.IntVar(digits, 'u')
    n = solver.IntVar(digits, 'n')
    t = solver.IntVar(digits, 't')
    r = solver.IntVar(digits, 'r')
    e = solver.IntVar(digits, 'e')
    
    letters = [c, p, i, s, f, u, n, t, r, e]
    print(letters)
    solver.Add( solver.AllDifferent(letters))
    solver.NewSearch(solver.Phase(letters,
                                solver.INT_VAR_DEFAULT,
                                solver.INT_VALUE_DEFAULT))
    solver.NextSolution()
    print(letters)
    solver.NextSolution()
    print(letters)
    
if __name__ == '__main__':
    app.run()