#!/etc/python

import curses
from threading import *
import time
import select
import sys

class interface:
    INPUT_HEIGHT = 1
    INPUT_WIDTH = 1000
    DISPLAY_HEIGHT = 1000
    DISPLAY_WIDTH = 1000
    in_buffer = []
    rooms = dict()
    


    def __init__(self):
        self.main_win = curses.initscr()
        curses.curs_set(1)
        curses.cbreak()
        self.main_win.nodelay(1)

        self.main_win.keypad(1)
        maxyx = self.main_win.getmaxyx()
        
        self.main_win_size_y = maxyx[0]
        self.main_win_size_x = maxyx[1]
        
        self.input_pad_size_y = self.INPUT_HEIGHT
        self.input_pad_size_x = self.INPUT_WIDTH
        
        self.display_pad_size_y = self.DISPLAY_HEIGHT
        self.display_pad_size_x = self.DISPLAY_WIDTH
        
        self.input_pad = curses.newpad(10, 100)
        self.input_pad_count = 0
    
        self.prompt = 'command-> '
        self.cursor_limit_left = len(self.prompt) + 1
        self.cursor_limit_right = self.main_win_size_x - 1
        self.cursor_pos_y = self.main_win_size_y -2

        input_thread = Thread(target=self.keyboard_input)
        input_thread.daemon = True
        input_thread.start()

    def keyboard_input(self):
        string = ''
        while True:
            try:
                c = self.main_win.getkey()
                if c == '\n':
                    self.in_buffer.append(string)
                    string = ''
                    #self.main_win.addstr(10,10, string)
                else:
                    string = string + c
            except:
                pass
        
            



   
    #creates a new pad for the room_name

    def draw_screen(self, room_name):
        self.main_win.clear()
        self.main_win.box()
        self.main_win.addstr(2,2, room_name)
        self.main_win.hline(self.main_win_size_y - 3, 1, curses.ACS_BSBS, self.main_win_size_x - 2)
        self.main_win.addstr(self.main_win_size_y - 2, 1, self.prompt)
        self.main_win.move(self.cursor_pos_y, self.cursor_limit_left)
        #self.main_win.refresh()
    


    def create_room(self, room_name):
        room_pad = curses.newpad(self.display_pad_size_y, self.display_pad_size_x)
        num_msgs = 0
        self.rooms[room_name] = (room_pad, num_msgs)
        

    def get_user_input(self):
        string = ''
        if self.in_buffer:
            string = self.in_buffer[0]
            self.in_buffer.remove(self.in_buffer[0])
            return string
        else:
            return None        
       


    def post_to_room(self, current_room, room_to_post, msg):
        #post message to display_pad corresponding to room_name
        room = self.rooms[room_to_post]
        room[0].addstr(room[1], 0, msg)
        i = 1 + room[1] 
        self.rooms[room_to_post] = (room[0], i)
        if room_to_post == current_room:
            room[0].noutrefresh(0,0,10,0,room[1],self.main_win_size_x)
        #if room_name is the current_room name redraw pad to screen


    def switch_room(self):
        pass

    def refresh_display(self):
        #redraw the current rooms display
        pass

    def close_interface(self):
        curses.echo()
        curses.endwin()

if __name__ == '__main__':

        gui = interface()
        gui.draw_screen('')
        gui.create_room('dude room')
        time.sleep(.02)
        while True:
            string = gui.get_user_input()
            if string != None:
                if string == 'quit':
                    gui.draw_screen('good bye')
                    time.sleep(.2)
                    break
                gui.post_to_room('dude room', 'dude room', string)
                gui.draw_screen('dude room')
                #time.sleep(2)
            

        gui.close_interface()
        
        '''
        while True:
            feet = gui.get_user_input()
            if feet != None:
                gui.draw_screen('happy')
















                feet = None
            else:
                gui.draw_screen('sad')

        gui.close_interface()

        '''
