#!/etc/python

import curses
from threading import *
import time
import sys
import math

#Gui for sdirc program

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
        
        #used to determine the size of the display box for the room display
        self.display_size_y = self.main_win_size_y - 4
        self.display_size_x = self.main_win_size_x - int(self.main_win_size_x * .25)

        self.prompt = 'command-> '
        self.cursor_limit_left = len(self.prompt) + 1
        self.cursor_limit_right = self.main_win_size_x - 1
        self.cursor_pos_y = self.main_win_size_y -2

        input_thread = Thread(target=self.keyboard_input)
        input_thread.daemon = True
        input_thread.start()
    
        self.current_room = 'Lobby'
        self.create_room(self.current_room)
        self.draw_screen()

    #function to be used in thread to read input from the keyboard and 
    #   then send input line to input buffer for displaying to the screen.
    #Issues:
    #   -Need to figure out how to handle handing the input string to the
    #   using program for use in its methods. Possible have a get_input
    #   method that passes the input from the buffer to the user for
    #   processing and then they would pass into the post_to_room function
    #   -Need to deal with non-letter/number/punctuation input
    def keyboard_input(self):
        string = ''
        while True:
            try:
                c = self.main_win.getkey()
                if c == '\n':
                    self.in_buffer.append(string)
                    string = ''
                else:
                    string = string + c
            except:
                pass
        
    #method - refreshes the screen first clearing the main window, redraws the border, 
    #   then redraw the Room Label, then output any text to the screen that exists
    #   in the current room if valid. Then redraws the user prompt and positions the cursor.
    def draw_screen(self):
        self.main_win.clear()
        self.main_win.box()
        if self.current_room:
            self.main_win.addstr(2, (self.main_win_size_x/2) - (len(self.current_room)/2), self.current_room)
            self.refresh_current_room()
        else:
            self.main_win.addstr(2, (self.main_win_size_x/2) - (len('lobby')/2), 'Lobby')
        self.main_win.hline(3,1, curses.ACS_BSBS, self.main_win_size_x -2)
        self.main_win.vline(4,self.display_size_x + 1, curses.ACS_SBSB, self.main_win_size_y - 7)
        self.main_win.hline(self.main_win_size_y - 3, 1, curses.ACS_BSBS, self.main_win_size_x - 2)
        self.main_win.addstr(self.main_win_size_y - 2, 1, self.prompt)
        self.main_win.move(self.cursor_pos_y, self.cursor_limit_left)
    
    #method - redraws to the screen the content of the current room overlaying
    #   it on the main screen.
    def refresh_current_room(self):
        room = self.rooms[self.current_room]
        
        #redraw the current room if possible. Exception is thrown when the room is new and
        #   has nothing to draw to the screen. In that case we can just pass as it doesn't
        #   have any effect on the screen.
        try:
            room[0].overlay(self.main_win,2,2,3,2,room[1], self.main_win_size_x - 10)
        except:
            pass

    
    def create_room(self, room_name):
        rooms = self.rooms.keys()
        if room_name not in rooms:
            room_pad = curses.newpad(self.display_pad_size_y, self.display_pad_size_x)
            num_msgs = 3
            self.rooms[room_name] = (room_pad, num_msgs)
            self.current_room = room_name
            self.draw_screen()

    def leave_room(self, room_name):
        rooms = self.rooms.keys()
        if room_name in rooms:
            room = self.rooms[room_name]
            del self.rooms[room_name]
            
    
    #ircClient will be responsible for making sure
    #   that the room exists and for keeping a list
    #   of all of the rooms that user belongs to.
    def switch_room(self, room_name):
        self.current_room = room_name

    def get_user_input(self):
        string = ''
        if self.in_buffer:
            string = self.in_buffer[0]
            self.in_buffer.remove(self.in_buffer[0])
            return string
        else:
            return None        
       

    def post_to_room(self, room_to_post, msg):
        #post message to display_pad corresponding to room_name
        if room_to_post is None:
            room_to_post = 'Lobby'
        room = self.rooms[room_to_post]
        room[0].addstr(room[1], 2, msg)
        i = 1 + room[1] 
        self.rooms[room_to_post] = (room[0], i)


    def close_interface(self):
        curses.echo()
        curses.endwin()

'''    
if __name__ == '__main__':
#Having trouble with switch, not sure where the problems are
#   I need to to create test functions that to determine what being stored in the
#   rooms and current_room and room_stack variable.
    
        gui = interface()
        gui.create_room('beef room')
        gui.create_room('dude room')
        current_room = 'dude room'
        time.sleep(.02)
        while True:
            string = gui.get_user_input()
            if string != None:
                if string == 'quit':
                    time.sleep(.2)
                    break 
                if string == 'switch':
                    if current_room == 'dude room':
                        gui.switch_room('beef room')
                        current_room = 'beef room'
                    else:
                        gui.switch_room('dude room')
                        current_room = 'dude room'
                else:
                    gui.post_to_room(current_room, string)
                gui.draw_screen()
        

        gui.close_interface()
   
        
        while True:
            feet = gui.get_user_input()
            if feet != None:
                gui.draw_screen('happy')
















                feet = None
            else:
                gui.draw_screen('sad')

        gui.close_interface()

'''
