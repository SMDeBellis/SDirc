#!/etc/python python

from curses import *

try:
    screen1 = initscr()
    screen1.keypad(1)
    noecho()
    cbreak()
    screen1.box()

    pad = newpad(1,100)
    pad2 = newpad(1,100)
    pad2.addstr('zyxwutsrqponmlkjihgfedcba')
    pad.addstr('abcdefghijklmnopqrstuwxyz')
    screen1.refresh()
    y = 0
    pad.refresh(y,0,1,1,26,26)
    while y < 26 and y >= 0:
        event = screen1.getch()
        screen1.addstr(10,2,str(event))
        screen1.addstr(11,2,str(KEY_LEFT))
        screen1.addstr(12,2,str(KEY_RIGHT))
        screen1.refresh()
        if event == KEY_LEFT:
            y += 1
        #elif event == 66:
        #    y -= 1
        #elif event == ord('a'):
        #    pad.clear()
        #screen1.refresh()
        #pad.refresh(0, y, 1, 1, 26, 26)
        if event == ord('a'):
            pad.refresh(0,0,1,1,26,26)
        elif event == ord('b'):
            pad2.refresh(0,0,1,1,26,26)

            
    #pad.setsyx(1,1)
    #screen1.refresh()

    while True:
        event = screen1.getch()
        if event == ord('q'): break

    endwin()
except:
    endwin()

