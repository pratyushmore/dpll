import sys, cProfile
    
num_vars = 0
num_clauses = 0
num_processed = 0
all_literals = {}
all_clauses = {}
current_state = []
literals_resolved = {}
unit_clauses  = []
single_sign_literals = []

def copy_literal(i, literal, original_literal, my_all_literals, key_orig_clauses):
    literal.value = original_literal.value
    clauses = original_literal.get_clauses()
    for clause in clauses.keys():
        if not key_orig_clauses[clause]:
            new_clause = Clause([])
            literals_for_clause = clause.literals.keys()
            literals_temp = {}
            for i in literals_for_clause:
                literals_temp[i] = my_all_literals[i]
            new_clause.literals = literals_temp
            key_orig_clauses[clause] = new_clause
        literal.add_clause(key_orig_clauses[clause])

def copy_own(all_literals):
    my_all_literals = {}
    clauses = {}
    for k, v in all_literals.items():
        my_all_literals[k] = Literal(k)
        literal_clauses = v.get_clauses()
        for c in literal_clauses:
            clauses[c] = False
    for k, v in my_all_literals.items():
        copy_literal(k, v, all_literals[k], my_all_literals, clauses)
    return my_all_literals

def get_single_sign_literals():
    single_sign_l = []
    for literal in all_literals.keys():
        if all_literals[-literal].num_clauses() == 0:
            single_sign_l.append(literal)
    return single_sign_l

def add_to_clauses(parts, num):
    clause = Clause(parts[:-1])    
    for i in parts[:-1]:
        all_literals[int(i)].add_clause(clause)
    all_clauses[num] = clause
    if clause.num_literals() == 1:
        unit_clauses.append(clause)
        

""" change (i,c) means literal i was removed from clause c """

""" How do I revert the changes? And do I have to checck if a literal and its negation are both unit clauses when I run bcp? Once I set a literal to a particular value, how do I actually revert it? How do I readd the clauses? I should get the new single sign value and unit clauses once I set the new value right?"""

"""
When I set value of a variable, hwo do I remoe the variables from corresponding clauses and then readd them back later? Otherwise recursion wont work right? Otherwise Ill have to use something immutable. Like copy which would have its own cost?

"""

def bcp(unit_clauses, single_sign_literals, all_literals, literals_resolved):
    for i in unit_clauses:
        literal_for_clause = -i.literals.keys()[0]
        opposite_sign_clauses = all_literals[literal_for_clause].get_clauses()
        for c in opposite_sign_clauses.keys():
            if c.num_literals() == 1:
                return False, all_literals 
            c.literals.pop(literal_for_clause, None)
            opposite_sign_clauses.pop(c, None)
            if c.num_literals() == 1:
                unit_clauses.append(c)
        if literal_for_clause < 0:
            current_state[-literal_for_clause - 1] = True
            literals_resolved[- literal_for_clause] = True
        else:
            current_state[literal_for_clause - 1] = False
            #if literal_for_clause == 11:
            #    print current_state
            literals_resolved[literal_for_clause] = True
    for i in single_sign_literals:
        clauses = all_literals[i].get_clauses()
        for c in clauses:
            literals_to_change = c.literals.values()
            for l in literals_to_change:
                if l.num != i: 
                    l.clauses.pop(c, None)
        all_literals[i].clauses = {}
        if i < 0:    
            current_state[-i - 1] = False    
            #if i == -11:
            #    print "YES", i
            #    print current_state
            literals_resolved[-i] = True
        else:
            current_state[i -1] = True
            literals_resolved[i] = True
    return True, all_literals

class Literal():
    def __init__(self, num):
        self.num = num
        self.value = None
        self.clauses = {}

    def add_clause(self, clause):
        self.clauses[clause] = True
    
    def num_clauses(self):
        return len(self.clauses)    

    def get_clauses(self):
        return self.clauses

    def get_val(self):
        return self.value

    def set_val(self, val):
        self.value = val
        unit_clauses = []
        single_sign_literals = []
        if val:
            for clause in self.clauses.keys():
                literals_temp = clause.literals.values()
                clause.literals = {}
                for literal in literals_temp:
                    literal.clauses.pop(clause, None)
                    if literal.num_clauses() == 0 and literal is not self:
                        single_sign_literals.append(-literal.num)
        else:
            for clause in self.clauses.keys():
                clause.literals.pop(self.num, None)
                if clause.num_literals() == 1:
                    unit_clauses.append(clause)
            single_sign_literals.append(-self.num)
        return unit_clauses, single_sign_literals

        

class Clause():
    def __init__(self, nums):
        self.literals = {}
        for num in nums:
            i = int(num)
            self.literals[i] = all_literals[i]
    
    def num_literals(self):
        return len(self.literals)

    def eval(self):
        if len(self.literals) == 0:
            return True
        for literal in self.literals.values():
            val = literal.get_val()
            if val == None:
                return True        
            else:
                if val:
                    return True
        return False          

def check_satisfiability(num, unit_clauses, all_literals, single_sign_literals, literals_resolved):
    print num
    #if num >= 11:
    #    print current_state
    #print "single", single_sign_literals
    if num > num_vars:
        return True
    #literal = all_literals[num]
    #neg_literal = all_literals[-num]
    #literal_clauses = literal.get_clauses().keys()
    #literal_clauses.extend(neg_literal.get_clauses().keys())
    #for clause in literal_clauses:
    #    print num, clause.literals.keys()
    #print literals_resolved
    #print current_state
    my_literals_resolved = literals_resolved.copy()
    possible, all_literals = bcp(unit_clauses, single_sign_literals, all_literals, my_literals_resolved)
    if not possible:
        return False
    #print "resolved: ", my_literals_resolved
    my_literals = copy_own(all_literals)
    if my_literals_resolved.get(num):
    #    print "IN"
        return check_satisfiability(num + 1, unit_clauses, my_literals, single_sign_literals, my_literals_resolved)
    literal = my_literals[num]
    neg_literal = my_literals[-num]
    unit_clauses, single_sign_literals = literal.set_val(True)
    unit_clauses2, single_sign_literals2 = neg_literal.set_val(False)
    unit_clauses.extend(unit_clauses2)
    single_sign_literals.extend(single_sign_literals2)
    #print "UNIT", num, unit_clauses
    #print "SINGLE", num, single_sign_literals
    #print "STILL HERE", num
    current_state[num - 1] = True
    possible = True
    literal_clauses = literal.get_clauses().keys()
    literal_clauses.extend(neg_literal.get_clauses().keys())
    for clause in literal_clauses:
    #    print num, clause.literals.keys()
        if not clause.eval():
    #        print "NOT". clause.literals.keys()
            possible = False
            break
    if possible:
        if check_satisfiability(num+1, unit_clauses, my_literals, single_sign_literals, my_literals_resolved):
            return True
    my_literals = copy_own(all_literals)
    literal = my_literals[num]
    neg_literal = my_literals[-num]
    unit_clauses, single_sign_literals = literal.set_val(False)
    unit_clauses2, single_sign_literals2 = neg_literal.set_val(True)
    unit_clauses.extend(unit_clauses2)
    single_sign_literals.extend(single_sign_literals2)
    #print "UNIT", num, unit_clauses
    #print "SINGLE", num, single_sign_literals
    current_state[num - 1] = False
    literal_clauses = literal.get_clauses().keys()
    literal_clauses.extend(neg_literal.get_clauses().keys())
    for clause in literal_clauses:
        if not clause.eval():
            possible = False
            break
    if possible:
        if check_satisfiability(num+1, unit_clauses, my_literals, single_sign_literals, my_literals_resolved):
            return True
    return False



if len(sys.argv) < 2:
    print "You must enter a filename."
    sys.exit(1)

if len(sys.argv) > 2:
    print "You entered more than one filename. Considering first argument only."

filename = sys.argv[1]

try:
    with open(filename) as f:
        content = f.readlines()
except IOError:
    print "No file of the given name exists."
    sys.exit(1)


for line in content:
    if line[0] == 'c':
        continue
    parts = line.split()
    if parts[0] == "p":
        num_vars = int(parts[2])
        num_clauses = int(parts[3])
        current_state = [None]*num_vars    
        for i in xrange(1, num_vars + 1):
            all_literals[i] = Literal(i)
            all_literals[-i] = Literal(-i)
    else:
        num_processed += 1
        add_to_clauses(parts, num_processed)

if num_processed != num_clauses:
    print "Warning: Could not process the number of clauses mentioned."

single_sign_literals = get_single_sign_literals()


def get_result():
    if check_satisfiability(1, unit_clauses, all_literals, single_sign_literals, literals_resolved):
        print "Satisfiable."
        #print current_state
        for i in xrange(0, num_vars):
            if current_state[i]:
                print i + 1
            else:
                print "-",i + 1 
    else:
        print "Unsatisfiable."

cProfile.run('get_result()')
