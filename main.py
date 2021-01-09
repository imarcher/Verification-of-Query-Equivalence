from moz_sql_parser import parse
from z3 import *
from ConstExpr import ConstExpr
from ConstPred import ConstPred
from colname_map import t1,t2,t3,colname_map,val_isnull_map,var_name,RC
import json
#gt > lt <
#sql = "SELECT favourite FROM happypeople WHERE favourite < 3 and color = 'golden'"

#sql = "SELECT * FROM EMP INNER JOIN EMP2 on EMP_ID = DEPT_ID"







#sr :(COND,COLS,ASSIGN)
# COND : t1>2 z3的式子
# COLS : [ ( t1 , b1 ), ...]一个元组的表示列的list
# ASSIGN : 一些关联关系，z3式子
#select
def Construct(q,table):

    #直接给表名
    if isinstance(q, str):
        col_list = table[q]
        new_cols = []
        for col in col_list:
            new_cols.append((col, val_isnull_map[col]))
            #new_cols.append((col, False))
        return (True, new_cols, True)


    if 'select' in q.keys():
        select_Column = q['select']
        new_COLS = []
        #print(select_Column)
        #递归
        del q['select']
        #print(q)
        ans = Construct(q,table)

        # 构造新COLS
        if isinstance(select_Column, str):
            # 全选：“*”
            if select_Column == '*':
                return ans
            # 错误
            return None
        elif isinstance(select_Column, dict):
            value = select_Column['value']
            # 选一个
            if isinstance(value, str):
                new_COLS.append(ConstExpr(value,ans[1]))
                return (ans[0],new_COLS,ans[2])
            #count,AGGREGATE以count为例
            elif isinstance(value, dict):
                count = value['count']
                if isinstance(count, str):
                    # *
                    if count == '*':
                        val_str = ""
                        for tuple in ans[1]:
                            for key in colname_map.keys():
                                if tuple[0] in colname_map[key]:
                                    val_str = val_str + key
                        # 约束
                        RC.addAGGREGATE((val_str, False),ans)
                        return (ans[0],[(val_str, False)],ans[2])
                    # 一个列
                    else:
                        mark = 0
                        for tuple in ans[1]:
                            if tuple[0] in colname_map[count]:
                                mark = 1
                                break
                        if mark == 0 :
                            print("count操作没有这个列")

                        # 约束
                        RC.addAGGREGATE((count, False), ans)
                        return (ans[0], [(count, False)], ans[2])
                #多个列
                if isinstance(count, list):
                    mark = 0
                    for s in count:
                        for tuple in ans[1]:
                            if tuple[0] in colname_map[s]:
                                mark = mark + 1
                                break
                    if mark != len(count):
                        print("count操作没有这个列")
                    val_str = ""
                    for s in count:
                        val_str = val_str + s
                    # 约束
                    RC.addAGGREGATE((val_str, False), ans)
                    return (ans[0], [(val_str, False)], ans[2])

        elif isinstance(select_Column, list):
            # 选多个
            for s_col in select_Column:
                new_COLS.append(ConstExpr(s_col['value'],ans[1]))
            return (ans[0],new_COLS,ans[2])

    elif 'where' in q.keys():

        filter_conditions = q['where']
        # 递归
        del q['where']
        #print(q)
        ans = Construct(q, table)
        f_conditions = And(ans[0], ConstPred(filter_conditions,ans[1]))
        return (f_conditions,ans[1],ans[2])

    elif 'from' in q.keys():

        fromtables = q['from']
        # 一个表，直接读
        if isinstance(fromtables, str):
            col_list = table[fromtables]
            new_cols = []
            for col in col_list:
                new_cols.append((col,val_isnull_map[col]))
                #new_cols.append((col, False))
            return (True,new_cols,True)

        # 是一个sql语句，递归求解, scan
        elif isinstance(fromtables, dict):
            return Construct(fromtables['value'],table)

        #join
        elif isinstance(fromtables,list):
            # inner join
            if 'inner join' in fromtables[1].keys():

                ans1 = Construct(fromtables[0], table)
                ans2 = Construct(fromtables[1]['inner join'],table)

                new_cols = ans1[1] + ans2[1]
                Key = ConstPred(fromtables[1]['on'],new_cols)
                return (And(ans1[0],ans2[0],Key),new_cols,And(ans1[2],ans2[2]))
            # left outer join
            elif 'left outer join' in fromtables[1].keys():

                ans1 = Construct(fromtables[0], table)
                ans2 = Construct(fromtables[1]['left outer join'], table)
                all_cols = ans1[1] + ans2[1]
                Key = ConstPred(fromtables[1]['on'], all_cols)
                tuple1 = fresh(all_cols)
                # 添加约束
                RC.addleft(tuple1[0],ans1, ans2)
                #(B∧(COND = COND1))∨(¬B∧(COND = (COND1∧COND2∧Key)))
                c11 = And(tuple1[0], (tuple1[1] == ans1[0]))
                c12 = And(Not(tuple1[0]), (tuple1[1] == (And(ans1[0], ans2[0], Key))))
                cstr1 = Or(c11,c12)
                #(B ∧ (COLS ⃗ = COLS⃗ 1 : NULL ⃗ ))∨ (¬B ∧ (COLS ⃗ = COLS⃗ 1 : COLS⃗ 2))
                NullCOLS = makeNULLCOLS(ans2[1])
                cols_c21 = ans1[1] + NullCOLS
                #print("cols_c21",cols_c21)
                cols_c22 = all_cols
                c21 = And(tuple1[0], COLSeq(tuple1[2], cols_c21))
                c22 = And(Not(tuple1[0]), COLSeq(tuple1[2], cols_c22))
                cstr2 = Or(c21, c22)
                #ASSIGN
                new_ASSIGN = And(ans1[2],ans2[2],cstr1,cstr2)
                return (tuple1[1],tuple1[2],new_ASSIGN)






def makeNULLCOLS(old_COLS):
    new_COLS = []
    for i in range(len(old_COLS)):
        new_COLS.append((0,True))
    return new_COLS


# 返回一个(B, COND, COLS ⃗ )，其中全是变量
# 并且在colname_map中添加COLS声明
def fresh(old_COLS):
    B_name = 'B'+str(var_name.B_id)
    var_name.addB()
    new_B = Bool(B_name)
    COND_name = 'COND' + str(var_name.COND_id)
    var_name.addCOND()
    new_COND = Bool(COND_name)

    # new_COLS = []
    # for i in range(len(old_COLS)):
    #     v_name = 'v' + str(var_name.v_id)
    #     isnull_name = 'n' + str(var_name.isnull_id)
    #     var_name.add_vandisnull()
    #     v = Int(v_name)
    #     n = Bool(isnull_name)
    #     #添加colname_map标志
    #     for key in colname_map.keys():
    #         if old_COLS[i][0] in colname_map[key]:
    #             colname_map[key].append(v)
    #             break
    #
    #     new_COLS.append((v, n))

    return (new_B,new_COND,old_COLS)





# 返回COLS⃗ 1 = COLS⃗ 2 的z3表达式
# COLS是一个list，顺序一定要一致
def COLSeq(COLS1,COLS2):
    #数量相等：
    if len(COLS1) == len(COLS2):
        conditions = True
        for i in range(len(COLS1)):
            # not null 看val
            # c1 = And(COLS1[i][1] == False,COLS1[i][0] == COLS2[i][0])
            # # null 不看val
            # (COLS1[i][1] == COLS1[i][1])
            # c2 = Or(COLS1[i][1] == True,c1)
            # c3 = And(COLS1[i][1] == COLS1[i][1],c2)

            c3 = And(COLS1[i][1] == COLS2[i][1],COLS1[i][0] == COLS2[i][0])

            #每列都and
            conditions = And(conditions, c3)
        return conditions

    else:
        return False

#调用接口判定sql
def isSqlEqual(sql1,sql2,table):
    q1 = parse(sql1)
    q2 = parse(sql2)
    sr1 = Construct(q1, table)
    #切换约束
    RC.change()
    sr2 = Construct(q2, table)
    print(sr1)
    print(sr2)

    rc = RC.get_rc_condition()

    if isEqualUsingSMT(sr1,sr2,rc) == False:
        print("not equal")
    else:
        print("equal")




def isEqualUsingSMT(sr1,sr2,rc=True):
    #print(rc)
    s1 = Solver()
    s2 = Solver()
    s3 = Solver()
    # (ASSIGN1 ∧ ASSIGN2) ∧ (COND1 ∧ ¬COND2)
    c1 = And(And(sr1[2], sr2[2]), And(sr1[0], Not(sr2[0])), rc)
    s1.add(c1)
    # (ASSIGN1 ∧ ASSIGN2) ∧ (¬COND1 ∧ COND2)
    #print(And(And(sr1[2], sr2[2]), And(Not(sr1[0]), sr2[0]), rc))
    c2 = And(And(sr1[2], sr2[2]), And(Not(sr1[0]), sr2[0]), rc)
    s2.add(c2)
    # )(ASSIGN1 ∧ ASSIGN2) ∧ (COND2 ∧ COND1)∧¬(COLS⃗ 1 = COLS⃗ 2)
    s3_conditions = And(And(sr1[2], sr2[2]), And(sr1[0], sr2[0]), Not(COLSeq(sr1[1], sr2[1])), rc)
    #print(s3_conditions)
    s3.add(s3_conditions)

    if s1.check() == unsat and s2.check() == unsat and s3.check() == unsat:
        return True

    else:
        # if s1.check() == sat:
        #     print("s1")
        #     print(s1.model())
        # if s2.check() == sat:
        #     print("s2")
        #     print(s2.model())
        # if s3.check() == sat:
        #     print("s3")
        #     print(s3.model())
        return False













#a = Construct(q1,table1)
#print(a)

