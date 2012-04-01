import itertools

def negate(literal):
    return literal*(-1)
    
class CNF_formula:

    def __init__(self,encoding_nvars):
        self.clauses = []
        self.nvars = encoding_nvars

    def print_dimacs(self,fname):
        """Write the cnf formula with dimacs format
        in the fname file.
        """
        if fname == None:
            import sys
            f  = sys.stdout
        else:
            f = open(fname,'w')

        def print_dimacs_clause(clause):
            f.write(" ".join(map(str,clause))+" 0\n")

        f.write("c\nc CNF Sudoku Translation\nc\np cnf "+str(self.nvars)+" "
                +str(len(self.clauses))+"\n")
        map(print_dimacs_clause,self.clauses)

        if fname != None: f.close()

    def implies(self,a,b):
        self.clauses.append([a*(-1),b])

    def biimplies(self,a,b):
        self.implies(a,b)
        self.implies(b,a)

    def at_least_one(self,B):
        self.clauses.append(B)

    def at_most_one(self,B):
        for combination in itertools.combinations(range(len(B)),2):
            self.clauses.append([(-1)*B[combination[0]],(-1)*B[combination[1]]])

    def addclause(self,cl):
        self.clauses.append(cl)

    def exacly_one(self,B):
        """ Exacly one restriction. Choose between normal encoding
        or regular encoding depending with its length
        """
        if len(B) == 1: self.clauses.append([B[0]])
        elif len(B) > 7: #Regular encoding O(n )
            self.regular_encoding_exacly_one(B)
        else:# Normal encoding O(n**2)
            self.at_least_one(B)
            self.at_most_one(B)


    def regular_encoding_exacly_one(self,B):
        n = len(B)
        R = range(self.nvars,self.nvars + n)
        R[0]=None
        self.nvars += (n - 1)
        #Rn -> Rn-1
        for i in range(2,n):self.implies(R[i],R[i-1])
        #B1 <-> no(R2)
        self.biimplies(B[0],negate(R[1]))
        #Bn <-> Rn
        self.biimplies(B[-1],R[-1])
        #Bi <-> Ri and no(Ri+1)
        for i in range(1,n - 1):
            self.clauses.extend([[negate(B[i]),R[i]],
                        [negate(B[i]), negate(R[i+1])],
                        [negate(R[i]),R[i+1],B[i]]])

