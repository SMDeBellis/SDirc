#!/etc/python

import curses
from threading import *
import time
import sys
import math

#Gui for sdirc program


#******************* Issues/ todo's *********************
# determine which dimension data members are needed and which
#   ones can be removed
# fixed - the users display will write over the right side border
# make diplay box scrollable
# make users box scrollable
# add room display selection
# figure out how users input is going to be handled from server 
# -probably going to have to modify how the server sends this message
#   and how the client handles the received message.
#
# Am able to continue writing lines past the low point but and it scrolls
# correctly. Now I need to to be able to scroll up and down with the arrow keys.

class interface:
    INPUT_HEIGHT = 1
    INPUT_WIDTH = 1000
    DISPLAY_HEIGHT = 1000
    DISPLAY_WIDTH = 1000
    MESSAGE_BASE = 0
    USER_BASE = 0
    in_buffer = []
    rooms = dict()
    


    def __init__(self):
        self.main_win = curses.initscr()
        curses.curs_set(1)
        curses.cbreak()
        self.main_win.nodelay(1)

        self.main_win.keypad(1)
        self.main_win_size_y, self.main_win_size_x = self.main_win.getmaxyx()
        
        self.input_pad_size_y = self.INPUT_HEIGHT
        self.input_pad_size_x = self.INPUT_WIDTH
        
        self.display_pad_size_y = self.DISPLAY_HEIGHT
        self.display_pad_size_x = self.DISPLAY_WIDTH
        
        #used to determine the size of the display box for the message display
        self.msg_display_size_y = self.main_win_size_y - 4
        self.msg_display_size_x = self.main_win_size_x - int(self.main_win_size_x * .25)

        #message display box parameters for calling overlay
        # need to first check that the window dimensions are capable of displaying this
        #   else need to abort gui and go back to command line interface
        self.msg_display_min_row = 5
        self.msg_display_min_col = 1
        self.msg_display_max_row = self.main_win_size_y - 4
        self.msg_display_max_col = self.main_win_size_x - int(self.main_win_size_x * .25)
        
        #users display box parameters for calling overlay
        self.users_display_min_row = 5
        self.users_display_min_col = self.msg_display_max_col + 2
        self.users_display_max_row = self.main_win_size_y - 4
        self.users_display_max_col = self.main_win_size_x - 2#1
        
        #used to determine the size of the display box for the user display
        self.users_display_min_y = 5
        self.users_display_min_x = self.msg_display_size_x + 2
        self.users_display_size_y = self.main_win_size_y - 4
        self.users_display_size_x = self.main_win_size_x - self.msg_display_size_x - 2
        self.users_display_height = self.users_display_min_y + self.users_display_size_y
        self.users_display_width = self.users_display_min_x + self.users_display_size_x -2 

           

        self.prompt = 'command-> '
        self.cursor_limit_left = len(self.prompt) + 1 # place cursor with one space after prompt
        self.cursor_limit_right = self.main_win_size_x - 1 
        self.cursor_pos_y = self.main_win_size_y -2 # n +1 for border +1 for cursor

        #To Handle user input while gui functions
        input_thread = Thread(target=self.keyboard_input)
        input_thread.daemon = True
        input_thread.start()
    
        self.current_room = 'Lobby'
        self.create_room(self.current_room)
        self.draw_screen()

        self.msg_win_top = 0;
        self.msg_win_total_lines = self.msg_display_max_row - self.msg_display_min_row
        self.track_i = 0;
    #for debugging purposes, draws all dimensional values into a special purpose room for evaluation
    def dump_val(self):
        room = 'dump room'
        self.create_room(room)
        self.post_to_room(room, 'self.main_win_size_y = ' + str(self.main_win_size_y))
        self.post_to_room(room, 'self.main_win_size_x = ' + str(self.main_win_size_x))
        self.post_to_room(room, 'self.input_pad_size_y = ' + str(self.input_pad_size_y))
        self.post_to_room(room, 'self.input_pad_size_x = ' + str(self.input_pad_size_x))
        self.post_to_room(room, 'self.display_pad_size_y = ' + str(self.display_pad_size_y))
        self.post_to_room(room, 'self.display_pad_size_x = ' + str(self.display_pad_size_x))
        self.post_to_room(room, 'self.msg_display_size_y = ' + str(self.msg_display_size_y))
        self.post_to_room(room, 'self.msg_display_size_x = ' + str(self.msg_display_size_x))
        self.post_to_room(room, 'self.users_display_min_y = ' + str(self.users_display_min_y))
        self.post_to_room(room, 'self.users_display_min_x = ' + str(self.users_display_min_x))
        self.post_to_room(room, 'self.users_display_size_y = ' + str(self.users_display_size_y))
        self.post_to_room(room, 'self.users_display_size_x = ' + str(self.users_display_size_x))
        self.post_to_room(room, 'self.users_display_height = ' + str(self.users_display_height))
        self.post_to_room(room, 'self.users_display_width = ' + str(self.users_display_width))
        self.switch_room(room)
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
                if c == 'KEY_UP':
                    self.msg_scroll_up()
                elif c == 'KEY_DOWN':
                    self.msg_scroll_down()
                elif c == '\n':
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
            self.main_win.addstr(1, (self.main_win_size_x/2) - (len(self.current_room)/2), self.current_room)
        else:
            self.main_win.addstr(2, (self.main_win_size_x/2) - (len('lobby')/2), 'Lobby')
        
        self.refresh_current_room()
        #line seperating room name
        self.main_win.hline(2,1, curses.ACS_BSBS, self.main_win_size_x -2)                      

        #displaying message label and line seperating label from msg box
        self.main_win.addstr(3, self.msg_display_size_x / 2 - len('messages')/2, 'Messages')    
        #self.main_win.hline(4, 1, curses.ACS_BSBS, self.msg_display_size_x)

        #displaying users label and line seperating label from users box
        self.main_win.addstr(3, self.users_display_min_x + (self.users_display_size_x /2 - len('users')/2), 'Users')
        self.main_win.hline(4, 1, curses.ACS_BSBS, self.main_win_size_x - 2)
        self.main_win.vline(3,self.msg_display_size_x + 1, curses.ACS_SBSB, self.main_win_size_y - 6)
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
            room[0].overlay(self.main_win, self.msg_win_top, 0, self.msg_display_min_row, self.msg_display_min_col, self.msg_display_max_row, self.msg_display_max_col)
            room[2].overlay(self.main_win, 0,0, self.users_display_min_row, self.users_display_min_col, self.users_display_max_row, self.users_display_max_col)
        except:
            #this needs to be changed so that if the terminal size
            #cannot handle the gui that the gui closes gracefully and
            # the command line is functional for the irc
            pass

    
    #updates the users list for a given room. 
    def update_user_list(self, room_name, user):
        room = self.rooms[room_name]
        if room:
            room[2].addstr(room[3],0, user)
            i = room[3] + 1
            self.rooms[room_name] = (room[0],room[1],room[2],i)
        self.draw_screen()
       
    
    def create_room(self, room_name):
        rooms = self.rooms.keys()
        if room_name not in rooms:
            # create the pad to store each rooms messages
            room_pad = curses.newpad(self.display_pad_size_y, self.display_pad_size_x)
            user_pad = curses.newpad(self.display_pad_size_y, self.display_pad_size_x)
            num_msgs = self.MESSAGE_BASE
            num_users = self.USER_BASE
            user_pad.addstr(num_users, 0, 'me')
            num_users += 1
            self.rooms[room_name] = (room_pad, num_msgs, user_pad, num_users)
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
        room[0].addstr(room[1], 0, msg)
        i = 1 + room[1] 
        self.rooms[room_to_post] = (room[0], i, room[2], room[3])
        if room_to_post is self.current_room:
            if (i - 1) > self.msg_win_total_lines:
                self.msg_win_top += 1

    
    #scrolls up on the message screen window when the number of messages
    #are greater than the number of displayable lines in the window up to the
    #first message.
    def msg_scroll_up(self):
        if self.current_room is 'Lobby':
            return None
        room = self.rooms[self.current_room]
        if room[1] > self.msg_win_total_lines and self.msg_win_top > 0:            
            self.msg_win_top -= 1
            self.draw_screen()

    #scrolls down on the message screen window when the number of messages
    #are greater than the number of displayable lines in the window up to
    #the last message.
    def msg_scroll_down(self):
        if self.current_room is 'Lobby':
            return None
        room = self.rooms[self.current_room]
        self.track_i = room[1]
        if room[1] > self.msg_win_total_lines:
            if self.msg_win_top < room[1] - self.msg_win_total_lines - 1:
                self.msg_win_top += 1
                self.draw_screen()


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
        #gui.dump_val()                     #uncomment for debugging values
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
                    #gui.dump_val()
                    gui.update_user_list(current_room, string)
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
