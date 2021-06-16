def change_var(a):
    global x
    x=a
    return x
def change_var2(b):
    x=b
    return x
change_var(3)
print(x)
