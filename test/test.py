import guesslang

false_max = 0
true_min = 1

for i in range(1, 11):
    with open("false" + str(i)) as file:
        temp = guesslang.Guess().scores(file.read())['C']
        if temp > false_max:
            false_max = temp

print("Max false score is: " + str(false_max))

for i in range(1, 6):
    with open("true" + str(i)) as file:
        temp = guesslang.Guess().scores(file.read())['C']
        if temp < true_min:
            true_min = temp

print("Min true score is: " + str(true_min))
