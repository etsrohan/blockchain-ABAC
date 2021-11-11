with open('subjects.txt', 'r') as file_obj:
    sub_info = file_obj.readlines()

for n in range(len(sub_info)):
    if sub_info[n][-1] == '\n':
        sub_info[n] = sub_info[n][:-1]
    print(sub_info[n].split(';'))