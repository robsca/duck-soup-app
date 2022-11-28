def testing_1():
    assert sum([1, 2, 3]) == 6, "Should be 6"

def testing_2():
    assert sum((1, 2, 2)) == 6, "Should be 6"

if __name__ == "__main__":
    testing_1()
    testing_2()
    print("Everything passed")