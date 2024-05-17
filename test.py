from urllib.parse import unquote_plus

# print(len("fuck=&idk=&a=&cfg_id=%5C%3Btouch+idk+%5C%26%5C%26+cat+idk%5C%3B"))

a = b'a'
b = a
a = b'b'

print(a == b)