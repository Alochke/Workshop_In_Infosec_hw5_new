import guesslang

with open("false1") as file:
    print(guesslang.Guess().scores(file.read()))