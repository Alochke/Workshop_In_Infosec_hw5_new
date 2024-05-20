import guesslang

for i in range(1, 5):
    with open("falsefalse" + str(i)) as file:
        print(guesslang.Guess().scores(file.read())['C'])