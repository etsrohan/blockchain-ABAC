s = ';NexG;;Manager;;:;;;;;:true;true;true:0:0;0'


s = s.split(':')
print(s)
for i in range(5):
    if i == 3:
        continue
    s[i] = s[i].split(';')
    
print(s)