
def double(a, b):
    for element in a: 
        b.append(element*2)

def main():
    array1 = [1,4,7,5,9,8,2]
    array2 = []
    double(array1, array2)
    print(array2)


if __name__ == "__main__":
    main()


