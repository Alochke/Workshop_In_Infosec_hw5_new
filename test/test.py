from time import sleep


for i in range(1, 11):
    with open("false" + str(i)) as file:
        print("testing false"  + str(i))
        exec("curl server/idk?data=" + file.read())
        sleep(5)
        file.seek(0)
        exec("curl --upload-file false" + str(i)+  " server")
        sleep(5)

for i in range(1, 11):
    with open("true" + str(i)) as file:
        print("testing true"  + str(i))
        exec("curl server/idk?data=" + file.read())
        sleep(5)
        file.seek(0)
        exec("curl --upload-file true" + str(i)+  " server")
        sleep(5)
