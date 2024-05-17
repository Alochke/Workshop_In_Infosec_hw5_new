url = 'https://www.example.com?param=special char&another=char'
encoded_url = requests.utils.requote_uri(url)
print(encoded_url)