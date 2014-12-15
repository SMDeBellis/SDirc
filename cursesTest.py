#!/etc/python

import curses
import time
import traceback

try:
    screen = curses.initscr()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_WHITE , curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.curs_set(1)
    curses.cbreak()
    #curses.noecho()
    screen.keypad(1)
    screen_max_yx = screen.getmaxyx()
    msg_start_x = 1
    msg_start_y = 1
    curr_msg_x = msg_start_x
    curr_msg_y1 = msg_start_y
    curr_msg_y2 = msg_start_y
    command_prompt_yxpos = (screen_max_yx[0] -2, 2)
    command_prompt = 'command-> '
    cursor_start_yxpos = (screen_max_yx[0] -2, len(command_prompt) + 2)
    screen.box()
    screen.refresh()
    pad = curses.newpad(100,100)
    pad2 = curses.newpad(100,100)
    switch = 0
        #screen.bkgd(' ', curses.color_pair(3))

    screen.hline(screen_max_yx[0] - 3, 1, curses.ACS_BSBS, screen_max_yx[1]-2)
    screen.move(command_prompt_yxpos[0],command_prompt_yxpos[1])
    screen.addstr(command_prompt)
    while True:
        in_str = screen.getstr(cursor_start_yxpos[0], cursor_start_yxpos[1])
        #in_str = pad.getstr(0,0)
        if in_str == 'quit': break
        #screen.addstr(curr_msg_y, curr_msg_x, in_str)
        #screen.noutrefresh()
        #screen.move(curr_msg_y, curr_msg_x)
        #print in_str
        #screen.refresh()
        screen.move(cursor_start_yxpos[0], cursor_start_yxpos[1])
        screen.clrtoeol()
        #screen.box()
        if in_str != 'switch':
            if switch == 0:
                pad.addstr(curr_msg_y1,curr_msg_x,in_str)
            else:
                pad2.addstr(curr_msg_y2,curr_msg_x,in_str)
        else:
            if switch == 0:
                switch = 1
            else:
                switch = 0

        if switch == 0:
            pad.refresh(0,0,1,1,20,27)
            curr_msg_y1 += 1

        else:
            pad2.refresh(0,0,1,1,20,27)
            curr_msg_y2 += 1




#    nwin.bkgd(' ',curses.color_pair(1)|curses.A_BOLD)
    


    #while True:
    #    event = screen.getch()
    #    if event == ord("q"): 
    #        break

    curses.endwin()
except:
    curses.endwin()
