def add(*args):
    result = 0
    for n in args:
        result += n
    return result

print(add(1,2,3,4,5,6,7,8,9,10))

def calc(n, **kwargs):
    
    for key,value in kwargs.items():
        print(key)
        print(value)

    n += kwargs["add"]
    print(n)
    n *= kwargs["multiply"]
    print(n)

calc(2, add=3, multiply=5)