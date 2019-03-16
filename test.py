import random


x = random.randint(1, 100)
y = random.randint(1, 100)

while x <= y:
    print x
    print y
    x = random.randint(1, 100)
    y = random.randint(1, 100)

print "-----"
print x
print y

print "-----"
print x - y