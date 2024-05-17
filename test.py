from urllib.parse import unquote_plus

print(unquote_plus("a=%5E%24+d&logfile=%5C%3Becho+%22fuck%22+%5C%7C+sed+%22s%5C%5Cf%5C%5Cd%5C%5C%22%5C%3B&fuck=%25%24%24%25+%26%2A%5E%24%2A%26%5E%24%2A&idk=b+%25%24%23%23"))