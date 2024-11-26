# The point of this file is to remember data, as global variable works only inside a same file
# Thus, everytime we want a global variable for the whole programm, we will store it in d
# The value of a variable will be the value in d with as a key the string of the name of the variable

if "d" in globals():
    pass
else:
    d = dict()


def global_variable(name, value=None, delete=False):
    global d
    if delete:
        d.pop(name)
    if value is None:
        return d[name]
    else:
        d[name] = value
