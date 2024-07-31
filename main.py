with open('database/urls') as file:
    list_urls = []
    for i in range(25):
        list_urls.append([k for k in file.readline().split()])
print(list_urls)
# with open('test.txt', 'w') as file:
#     file.write('1')
