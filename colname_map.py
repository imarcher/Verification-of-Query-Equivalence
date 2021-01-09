from z3 import *

#查表用

t1 = Int('EMP_ID')
t2 = Int('EMP_NAME')
t3 = Int('DEPT_ID')
b1 = Bool('EMP_ID_isNULL')
b2 = Bool('EMP_NAME_isNULL')
b3 = Bool('DEPT_ID_isNULL')

colname_map = {'EMP_ID':[t1], 'EMP_NAME':[t2], 'DEPT_ID':[t3]}

val_isnull_map = {t1:b1,t2:b2,t3:b3}

#BEYOND SPJ QUERIES 所需的变量名字 ,从1开始
class TVarName:

    def __init__(self):
        self.B_id = 1
        self.COND_id = 1
        self.v_id = 1
        self.isnull_id = 1

    def addB(self):
        self.B_id = self.B_id + 1

    def addCOND(self):
        self.COND_id = self.COND_id + 1

    def add_vandisnull(self):
        self.v_id = self.v_id + 1
        self.isnull_id = self.isnull_id + 1

#BEYOND SPJ QUERIES 所需的关系约束，这里存的是sr
class RelationalConstraints:

    def __init__(self):
        #(b,q1,q2)
        self.first_left = []
        self.second_left = []
        #((t1,n1),q1)
        self.first_AGGREGATE = []
        self.second_AGGREGATE = []
        #用于切换
        self.isfirst = True

    def addleft(self,b,q1,q2):
        if self.isfirst == True:
            self.first_left.append((b, q1, q2))
        else:
            self.second_left.append((b, q1, q2))

    def addAGGREGATE(self,col,q):
        if self.isfirst == True:
            self.first_AGGREGATE.append((col, q))
        else:
            self.second_AGGREGATE.append((col, q))

    def change(self):
        self.isfirst = False

    #返回z3的表达式，add在普通的后面
    def get_rc_condition(self):
        #left out
        b_c = True
        for tuple1 in self.first_left:
            for tuple2 in self.second_left:
                r1 = relationshipUsingSMT(tuple1[1],tuple2[1])
                r2 = relationshipUsingSMT(tuple1[2],tuple2[2])
                #
                if r1 == 1 and r2 == 1:
                    b_c = And(b_c, tuple1[0] == tuple2[0])
                elif r1 == 1 and r2 == 2:
                    # B1 implies B2
                    b_c = And(b_c, Implies(tuple1[0], tuple2[0]))
                elif r1 == 1 and r2 == 3:
                    # B2 implies B1
                    b_c = And(b_c, Implies(tuple2[0], tuple1[0]))
                elif r1 == 2 and r2 == 1:
                    b_c = And(b_c, Implies(tuple2[0], tuple1[0]))
                elif r1 == 2 and r2 == 3:
                    b_c = And(b_c, Implies(tuple2[0], tuple1[0]))
                elif r1 == 3 and r2 == 1:
                    b_c = And(b_c, Implies(tuple1[0], tuple2[0]))
                elif r1 == 3 and r2 == 2:
                    b_c = And(b_c, Implies(tuple1[0], tuple2[0]))
        #print("b_c",b_c)
        # AGGREGATE
        col_c = True
        for tuple1 in self.first_AGGREGATE:
            #print(tuple1)
            for tuple2 in self.second_AGGREGATE:
                r1 = relationshipUsingSMT(tuple1[1], tuple2[1])
                if r1 == 1:
                    #(v4 = v5) && (n4 = n5)
                    col_c = And(col_c, Not(And(tuple1[0][0] == tuple2[0][0], tuple1[0][1] == tuple2[0][1])))



        return And(b_c, col_c)





#返回一个关系 1：eq    2：=》    3：《=    4：没关系
def relationshipUsingSMT(sr1, sr2):
    s1 = Solver()
    s2 = Solver()
    s3 = Solver()
    # (ASSIGN1 ∧ ASSIGN2) ∧ (COND1 ∧ ¬COND2)
    s1.add(And(And(sr1[2], sr2[2]), And(sr1[0], Not(sr2[0]))))
    # (ASSIGN1 ∧ ASSIGN2) ∧ (¬COND1 ∧ COND2)
    s2.add(And(And(sr1[2], sr2[2]), And(Not(sr1[0]), sr2[0])))
    # )(ASSIGN1 ∧ ASSIGN2) ∧ (COND2 ∧ COND1)∧¬(COLS⃗ 1 = COLS⃗ 2)
    s3_conditions = And(And(sr1[2], sr2[2]), And(sr1[0], sr2[0]), Not(COLSeq(sr1[1], sr2[1])))
    s3.add(s3_conditions)

    c1 = s1.check()
    c2 = s2.check()
    c3 = s3.check()

    if c1 == unsat and c2 == unsat and c3 == unsat:
        return 1
    elif c1 == sat and c2 == unsat and c3 == unsat:
        return 2
    elif c1 == unsat and c2 == sat and c3 == unsat:
        return 3
    else:
        return 4

# 返回COLS⃗ 1 = COLS⃗ 2 的z3表达式
# COLS是一个list，顺序一定要一致
def COLSeq(COLS1,COLS2):
    #数量相等：
    if len(COLS1) == len(COLS2):
        conditions = True
        for i in range(len(COLS1)):
            # # not null 看val
            # c1 = And(COLS1[i][1] == False,COLS1[i][0] == COLS2[i][0])
            # # null 不看val
            # (COLS1[i][1] == COLS1[i][1])
            # c2 = Or(COLS1[i][1] == True,c1)
            # c3 = And(COLS1[i][1] == COLS1[i][1],c2)
            c3 = And(COLS1[i][1] == COLS1[i][1], COLS1[i][0] == COLS2[i][0])
            #每列都and
            conditions = And(conditions, c3)
        return conditions
    else:
        return False


var_name = TVarName()
RC = RelationalConstraints()