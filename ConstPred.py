from z3 import *
from ConstExpr import ConstExpr

#p是一个字典：{'gt': [{'add': ['DEPT_ID', 5]}, 'EMP_ID']}
#return 一个条件
def ConstPred(p,COLS):

    ans = ConstPredAux(p,COLS)
    return And(ans[0],Not(ans[1]))


def ConstPredAux(p,COLS):
    #情况1 > | < | = | ≤ | ≥
    # >
    if True == p:
        return (True,False)
    if False == p:
        return (False,False)

    if 'gt' in p.keys():
        list_tocp = p['gt']
        tuple0 = ConstExpr(list_tocp[0], COLS)
        tuple1 = ConstExpr(list_tocp[1], COLS)
        val = (tuple0[0] > tuple1[0])
        return (val, Or(tuple0[1], tuple1[1]))
    # <
    elif 'lt' in p.keys():
        list_tocp = p['lt']
        tuple0 = ConstExpr(list_tocp[0], COLS)
        tuple1 = ConstExpr(list_tocp[1], COLS)
        val = (tuple0[0] < tuple1[0])
        return (val, Or(tuple0[1], tuple1[1]))
    # =
    elif 'eq' in p.keys():
        list_tocp = p['eq']
        tuple0 = ConstExpr(list_tocp[0], COLS)
        tuple1 = ConstExpr(list_tocp[1], COLS)
        val = (tuple0[0] == tuple1[0])
        return (val, Or(tuple0[1], tuple1[1]))
    # >=
    elif 'gte' in p.keys():
        list_tocp = p['gte']
        tuple0 = ConstExpr(list_tocp[0], COLS)
        tuple1 = ConstExpr(list_tocp[1], COLS)
        val = (tuple0[0] >= tuple1[0])
        return (val, Or(tuple0[1], tuple1[1]))
    # <=
    elif 'lte' in p.keys():
        list_tocp = p['lte']
        tuple0 = ConstExpr(list_tocp[0], COLS)
        tuple1 = ConstExpr(list_tocp[1], COLS)
        val = (tuple0[0] <= tuple1[0])
        return (val, Or(tuple0[1], tuple1[1]))
    #情况2 ：and or
    # and,可以有多个
    elif 'and' in p.keys():
        list_tologic = p['and']
        tuple0 = ConstPredAux(list_tologic[0], COLS)
        tuple1 = ConstPredAux(list_tologic[1], COLS)
        res = ConstLogic('and',tuple0,tuple1)
        for i in range(2,len(list_tologic)):
            tuplei = ConstPredAux(list_tologic[i], COLS)
            res = ConstLogic('and',res,tuplei)
        return res
    # or,可以有多个
    elif 'or' in p.keys():
        list_tologic = p['or']
        tuple0 = ConstPredAux(list_tologic[0], COLS)
        tuple1 = ConstPredAux(list_tologic[1], COLS)
        res = ConstLogic('or', tuple0, tuple1)
        for i in range(2, len(list_tologic)):
            tuplei = ConstPredAux(list_tologic[i], COLS)
            res = ConstLogic('or', res, tuplei)
        return res

    # 情况3 ：not
    # not
    elif 'not' in p.keys():
        tuple = ConstPredAux(p['not'], COLS)
        return (Not(tuple[0]), tuple[1])

    # 情况4 ：IS NULL
    # IS NULL
    elif 'missing' in p.keys():
        tuple = ConstExpr(p['missing'], COLS)
        return (tuple[1],False)
    # IS NOT NULL
    elif 'exists' in p.keys():
        tuple = ConstExpr(p['exists'], COLS)
        tuple1 = (tuple[1], False)
        return (Not(tuple1[0]), tuple1[1])


#运用3值逻辑返回一个tuple
def ConstLogic(op,tuple0,tuple1):
    #and
    if op == 'and':
        val = And(tuple0[0],tuple1[0])
        #2种情况为null
        #都为null
        c1 = And(tuple0[1], tuple1[1])
        #一个为null，另一个为True
        c2 = And(tuple0[1] == True, tuple1[0] == True)
        c3 = And(tuple1[1] == True, tuple0[0] == True)

        isnull = Or(c1,c2,c3)
        return (val, isnull)
    #or 相反
    elif op == 'or':
        val = Or(tuple0[0], tuple1[0])
        # 2种情况为null
        # 都为null
        c1 = And(tuple0[1], tuple1[1])
        # 一个为null，另一个为False
        c2 = And(tuple0[1] == True, tuple1[0] == False)
        c3 = And(tuple1[1] == True, tuple0[0] == False)

        isnull = Or(c1, c2, c3)
        return (val, isnull)