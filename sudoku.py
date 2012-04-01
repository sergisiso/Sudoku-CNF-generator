import cnf

class sudoku:

    def __init__(self, fname):
        f = open(fname)
        self.order, self.m = map(int, f.readline().split()[1:3])
        self.n = self.order / self.m
        self.sudoku = [f.readline().split() for i in range(self.order)]

    def variable(self,row,col,num):
        """Return the variable which represents a (row,col,num)."""
        return row * self.order**2 + col * self.order + num + 1 # +1 to avoid 0

    def sameCell(self, row, col, num ):
        return [self.variable(row,col,i) for i in range(self.order) if i != num]

    def sameRow(self, row, col, num ):
        return [self.variable(row,i,num) for i in range(self.order) if i != col]

    def sameCol(self, row, col, num ):
        return [self.variable(i,col,num) for i in range(self.order) if i != row]

    def sameBlock(self, row, col, num ):
        init_row = (row/self.m)*self.m
        init_col = (col/self.n)*self.n
        return [self.variable(init_row + i,init_col+j,num) for i in range(self.m)
                for j in range(self.n) if (i != row%self.m or j != col%self.n) ]

    def extended_translate_to_CNF(self):
        """ Translate to CNF all restrictions with all variales"""

        cnff = cnf.CNF_formula(self.order**3)
        
        for i in range(self.order):
            for j in range(self.order):
                A = [  self.variable(i,j,k) for k in range(self.order)]
                cnff.exacly_one(A)# Cell restrictions
                B = [  self.variable(i,k,j) for k in range(self.order)]
                cnff.exacly_one(B)# Row restrictions
                C = [  self.variable(k,i,j) for k in range(self.order)]
                cnff.exacly_one(C)# Col restrictions
                if self.sudoku[i][j] != "-1": #Fixed variables restrictions
                    cnff.addclause([self.variable(i,j,int(self.sudoku[i][j]))])

        #Region restrictions
        for region in range(self.order):
            i,j =  (region/self.m)*self.m,(region%self.m)*self.n
            for num in range(self.order):
                D = [ self.variable(i+i_inc,j+j_inc,num)  for i_inc in range(self.n)
                      for j_inc in range(self.m) ]
                cnff.exacly_one(D)
        
        return cnff,[i for i in range((self.order**3)+1)]

    def optimized_translate_to_CNF(self):
        """Translate to CNF with only the unknow variables"""

        useful_vars = [i for i in range((self.order**3)+1)]
        prefixed=[]

        for row in range(self.order):
            for col in range(self.order):
                if self.sudoku[row][col] != "-1": #Fixed variables restrictions
                    num = int (self.sudoku[row][col])
                        
                    prefixed.extend(self.sameCell(row,col,num))
                    prefixed.extend(self.sameRow(row,col,num))
                    prefixed.extend(self.sameCol(row,col,num))
                    prefixed.extend(self.sameBlock(row,col,num))

        prefixed = list(set(prefixed)) # Delete duplicates and sort the list

        for var in prefixed:
            useful_vars[var]=-1
            
        counter = 0
        for i in range(len(useful_vars)):
            if useful_vars[i] >= 0:
                useful_vars[i] = counter
                counter += 1

        cnff = cnf.CNF_formula(counter-1)
 
        def invalid(item):
            return    item != -1

        for i in range(self.order):
            for j in range(self.order):
                #Cell Restrictions: i=rows, j=cols
                if self.sudoku[i][j] == "-1":
                    A = filter(invalid,[ useful_vars[self.variable(i,j,k)] for k in range(self.order)])
                    cnff.exacly_one(A)
                else:
                    cnff.addclause([useful_vars[self.variable(i,j,int(self.sudoku[i][j]))]])
                #Row Restrictions:
                B = filter(invalid,[useful_vars[self.variable(i,k,j)] for k in range(self.order)])
                if B != []: cnff.exacly_one(B)
                #Col Restrictions:
                C = filter(invalid,[useful_vars[self.variable(k,i,j)] for k in range(self.order)])
                if C != []: cnff.exacly_one(C)

        #Region restrictions
            
        for region in range(self.order):
            i,j =  (region/self.m)*self.m,(region%self.m)*self.n
            for num in range(self.order):
                D = filter(invalid,[ useful_vars[self.variable(i+i_inc,j+j_inc,num)]
                                     for i_inc in range(self.n) for j_inc in range(self.m)])
                if D != []:cnff.exacly_one(D)
                  
        return cnff,useful_vars

