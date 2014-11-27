from ghost import Ghost

g = Ghost()

for i in range(0, 200):
    g.open('http://www.apple.com')
    g.capture_to('apple/%s.png' % i)
    i += 1
