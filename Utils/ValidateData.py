# encoding=utf8


# if  str.strip() and str.isdigit():
#     print(111)

# if str.strip() and type(eval(str)) == decimal:
#     print(333)
# str.isdecimal 原生的是判断是否为10进制数！
def isdecimal(str):
    try:
        if type(eval(str)) == float or type(eval(str)) == int:
            return True
        else:
            return False
    except:
        return False

#
# str = '683.9999'
# print(isdecimal(str))
