from colname_map import colname_map,t1,t2,t3
from z3 import *
#return tuple
def ConstExpr(e,COLS):

    #情况3 null
    if e == None:
        return (0,True)

    if isinstance(e, str):
        # 一个列 情况1
        for col in COLS:
            if col[0] in colname_map[e]:
                return col
        print("错误：所选列不存在")
    elif isinstance(e,int):
        #一个整数
        return ( e , False )

    elif isinstance(e, dict):
        #情况4，+-x/%
        # +
        if 'add' in e.keys():
            list_toop = e['add']
            tuple0 = ConstExpr(list_toop[0], COLS)
            tuple1 = ConstExpr(list_toop[1], COLS)
            val = tuple0[0] + tuple1[0]
            return ( val , Or(tuple0[1],tuple1[1]))
        # -
        elif 'sub' in e.keys():
            list_toop = e['sub']
            tuple0 = ConstExpr(list_toop[0], COLS)
            tuple1 = ConstExpr(list_toop[1], COLS)
            val = tuple0[0] - tuple1[0]
            return ( val , Or(tuple0[1],tuple1[1]))
        # *
        elif 'mul' in e.keys():
            list_toop = e['mul']
            tuple0 = ConstExpr(list_toop[0], COLS)
            tuple1 = ConstExpr(list_toop[1], COLS)
            val = tuple0[0] * tuple1[0]
            return (val, Or(tuple0[1], tuple1[1]))
        # /
        elif 'div' in e.keys():
            list_toop = e['div']
            tuple0 = ConstExpr(list_toop[0], COLS)
            tuple1 = ConstExpr(list_toop[1], COLS)
            val = tuple0[0] / tuple1[0]
            return (val, Or(tuple0[1], tuple1[1]))
        # %
        elif 'mod' in e.keys():
            list_toop = e['mod']
            tuple0 = ConstExpr(list_toop[0], COLS)
            tuple1 = ConstExpr(list_toop[1], COLS)
            val = tuple0[0] % tuple1[0]
            return (val, Or(tuple0[1], tuple1[1]))
