import guesslang

false_max = 0
true_min = 1

for i in range(10):
    with open("false" + str(i)) as file:
        temp = guesslang.Guess().scores(file.read())['C']
        if temp > false_max:
            false_max = temp

print("Max false score is: " + false_max)

for i in range(5):
    with open("true" + str(i)) as file:
        temp = guesslang.Guess().scores(file.read())['C']
        if temp < true_min:
            true_min = temp

print("Min true score is: " + true_min)
