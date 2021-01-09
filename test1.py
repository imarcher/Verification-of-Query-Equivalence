from main import isSqlEqual
from colname_map import t1,t2,t3,colname_map,val_isnull_map,var_name,RC

#test ex1
# sql = "SELECT EMP_ID FROM (SELECT * FROM EMP WHERE DEPT_ID = 10) WHERE DEPT_ID + 5 > EMP_ID "
# sql1 = "SELECT EMP_ID FROM (SELECT * FROM EMP WHERE DEPT_ID = 10) WHERE 15 > EMP_ID"

#test ex2
# sql = "SELECT EMP_ID FROM EMP WHERE EMP_ID = 10 AND NOT EMP_ID IS NULL"
# sql1 = "SELECT EMP_ID FROM EMP WHERE EMP_ID = 10"

#test ex3
# sql = "SELECT EMP_ID, DEPT_ID FROM EMP INNER JOIN DEPT ON EMP_ID = DEPT_ID"
# sql1 = "SELECT * FROM (SELECT EMP_ID, DEPT_ID FROM EMP LEFT OUTER JOIN DEPT ON EMP_ID = DEPT_ID ) WHERE DEPT_ID IS NOT NULL"

#test ex4
# sql = "SELECT COUNT(*) FROM(SELECT * FROM (SELECT * FROM EMP WHERE DEPT_ID = 10) WHERE DEPT_ID + 5 > EMP_ID)"
# sql1 = "SELECT COUNT(*) FROM(SELECT * FROM (SELECT * FROM EMP WHERE DEPT_ID = 10) WHERE 15 > EMP_ID)"

#test ex6
# sql = "SELECT EMP_ID FROM (SELECT * FROM EMP WHERE DEPT_ID = 10) WHERE DEPT_ID + 5 > EMP_ID and true"
# sql1 = "SELECT EMP_ID FROM EMP WHERE DEPT_ID = 10 and DEPT_ID + 5 > EMP_ID and true"

# 比较spark重写的
#test ex5
# sql = "SELECT EMP_ID FROM (SELECT * FROM EMP WHERE DEPT_ID = 10) WHERE DEPT_ID + 5 > EMP_ID"
# sql1 = "SELECT EMP_ID FROM EMP WHERE DEPT_ID is NOT NULL and EMP_ID is NOT NULL and DEPT_ID = 10 and DEPT_ID + 5 > EMP_ID"

#test ex6
# sql = "SELECT EMP_ID FROM (SELECT * FROM EMP WHERE DEPT_ID = 10) WHERE DEPT_ID + 5 > EMP_ID and true"
# sql1 = "SELECT EMP_ID FROM EMP WHERE DEPT_ID = 10 and DEPT_ID + 5 > EMP_ID "

#test ex7
# sql = "SELECT * FROM EMP WHERE 1 > 0"
# sql1 = "SELECT * FROM EMP  "

#test ex8
# sql = "select EMP_ID from EMP WHERE DEPT_ID > 3"
# sql1 = "select EMP_ID from EMP WHERE DEPT_ID >= 4"

#test ex9
# sql = "select EMP_ID from EMP WHERE DEPT_ID > 3"
# sql1 = "select EMP_ID from EMP WHERE DEPT_ID > 5"
#
# test ex10
# sql = "select EMP_ID from EMP WHERE DEPT_ID > 3"
# sql1 = "select EMP_ID from EMP WHERE EMP_ID > 3"
#
# test ex11
# sql = "select EMP_ID from EMP WHERE DEPT_ID > 3"
# sql1 = "select DEPT_ID from EMP WHERE DEPT_ID > 3"


#test ex12
sql = "SELECT EMP_ID, DEPT_ID FROM EMP INNER JOIN DEPT ON EMP_ID = DEPT_ID"
sql1 = "SELECT EMP_ID, DEPT_ID FROM EMP LEFT OUTER JOIN DEPT ON EMP_ID = DEPT_ID"


#table = {'EMP':[t1, t2, t3]}
table = {'EMP':[t1, t2],'DEPT':[t3]}


isSqlEqual(sql,sql1,table)

