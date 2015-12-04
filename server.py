"""
This is an IRC server developed in python 2.7
This is for a CS494 project

Copyright (C) 2015 Ahmed Abdulkareem, Portland State University

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

"""
========================================================================
			Start of Program Here
========================================================================
"""


"""
=======================================================
Global Variables
=======================================================
"""
CONNECTIONS = []
USERS = []
ACCOUNTS = {}
CHANNELS = []
REC_BUFFER = 1024
HOST = ''
PORT = 1234


"""
=======================================================
Importing modules
=======================================================
"""

import select   # for the select function
import socket   # to make socket objects
import signal   # to handle signal interrupts
import sys      # for system calls (errors for example)
import logging  # for logging


"""
=======================================================================
Function definitions and implementations
=======================================================================
"""

"""
=======================================================
This function takes care of the exit command
its job is to log a client off the server
It removes the client from each channel they're in
it removes the user from the list
closes socket and removes it from conn list
sock --> socket object
=======================================================
"""
def logoff(sock):

    user = ACCOUNTS[sock]['username'] # get user name
    channels = ACCOUNTS[sock]['channels'] # get channels 

    broadcast_message('\n%s is now offline\r\n' % user)

    # remove user from the channels they were in
    for i in xrange(len(channels) - 1, -1, -1):
        leave_channel(channels[i], sock)

    # for the server log
    logging.info('%s is now offline' % user)

    # remove user from list
    USERS.remove(user)

    logging.info('Updated user list: %s' % USERS)

    sock.close()
    
    # remove socket from connection list
    CONNECTIONS.remove(sock)

    # remove account
    del ACCOUNTS[sock]



"""
=======================================================
This function removes sock from channel
channel --> channel name to leave
sock    --> socket object
=======================================================
"""
def leave_channel(channel, sock):
 
    user = ACCOUNTS[sock]['username'] # get user name
    channels = ACCOUNTS[sock]['channels'] # get channels 

    # check if user in the channel
    if channel in channels:

        broadcast_message('\n%s has left %s' % (user, channel))

        # check to see if its their current channel
        if ACCOUNTS[sock]['current'] == channel:
 
            # reset current channel
            ACCOUNTS[sock]['current'] = ''
 
            # remove channel from user's
            # channel list
            ACCOUNTS[sock]['channels'].remove(channel)
 
            # notify user
            sock.send('\nYou left %s\r\n' % channel)
 
            # update channels variable
            channels = accounts[sock]['channels']
 
            # update current channel by
            # randomly selecting a channel from their list
            if len(channels) > 0:
                current = random.choice(channels)
                ACCOUNTS[sock]['current'] = current
                sock.send('\nCurrent channel is now %s\r\n' % current)

        # if not user's current channel
        else:

            # remove channel from user's
            # channel list
            ACCOUNTS[sock]['channels'].remove(channel)
 
            # notify user
            sock.send('\nYou left %s\r\n' % channel)
 
        # Now we need to check to
        # see if we should remove that channel
        # from the channel list
 
        # counter variable
        count = 0
 
        # go through the ACCOUNTS
        for key in ACCOUNTS:
 
            # found ACCOUNTS in channel
            if channel in ACCOUNTS[key]['channels']:
 
                # count em up
                count += 1
 
        # count is equal to 0 so no one in channel
        if count == 0:
 
            # remove from channel list
            CHANNELS.remove(channel)
 
            # log info for server
            logging.info('%s removed from channel list' % channel)
            logging.info('Updated channel list: %s' % CHANNELS)
 
    # user isn't in that channel
    else:
 
        # tell user they are stupid
        sock.send('\nNot in channel\nMust be in a channel to leave\r\n')




"""
=======================================================
This function parses the data and performs the appropr-
iate action based on the data
sock    --> socket object
message --> the data
=======================================================
"""
def parse_message(message, sock):

    # remove all white space in case there is any
    message = message.strip().split()

    if len(message) == 1:
        
        # who command
        if message[0] == '/who':
            pass

        # list command
        elif message[0] == '/list':
            pass

        # nick command
        elif message[0] == '/nick':
            pass

        # help command
        elif message[0] == '/help':
            pass

        # exit command
        elif message[0] == '/exit':
            pass

        # invalid command
        else:
            sock.send('\nInvalid Command\n')

    elif len(message) == 2:

         # whois command
         if message[0] == '/whois':
            pass
 
         # peek command
         elif message[0] == '/who':
            pass
 
         # join command
         elif message[0] == '/join':
            pass
 
         # leave command
         elif message[0] == '/leave':
            pass
 
         # current command
         elif message[0] == '/current':
            pass
 
         # nick command
         elif message[0] == '/nick':
            pass
 
         # invalid
         else:
             sock.send('\nInvalid command\n')

    else:
        sock.send('\nInvalid Command!\n')




"""
=======================================================
Help function 
this will show a list of options based on the 
help command
sock    --> socket object
command --> optional argument to give info about 
            specific command 
=======================================================
"""
def help(sock, command):

    if command is None:
        sock.send('\nList of commands\n')
        sock.send('/help -- shows valid commands\n')
        sock.send('/nick <nickname> -- show/change username\n')
        sock.send('/who <channel> -- shows users\n')
        sock.send('/list -- shows channels on server\n')
        sock.send('/exit -- logoff\n')
        sock.send('/whois <username> -- info about user\n')
        sock.send('/join <channel> -- join channel\n')
        sock.send('/leave <channel> -- leave channel\n')
        sock.send('/current <channel> -- change current channel\n')
        sock.send('/msg <user> <message> -- send user private message\n')
        sock.send('/help <command> -- more info on command\n')

    else:
         if command == 'nick':
             sock.send('\nCommand: /nick\n')
             sock.send('Arguments: <nickname> (optional)\n')
             sock.send('Description: The nick command will'
                       ' change your username to <nickname>\n')
             sock.send('If <nickname> is not provided,'
                       ' current username is echoed\n')
 
         elif command == 'who':
             sock.send('\nCommand: /who\n')
             sock.send('Arguments: <channel> (optional)\n')
             sock.send('Description: The who command will show'
                       'you all the users on the server\n')
             sock.send('when channel is not provided.'
                       'When channel provided it will show you\n')
             sock.send('the users in that channel\n')
 
         elif command == 'list':
             sock.send('\nCommand: /list\n')
             sock.send('Arguments: none\n')
             sock.send('Description: The list command will show'
                       'you a list of the current channels on the server\n')
 
         elif command == 'exit':
             sock.send('\nCommand: /exit\n')
             sock.send('Arguments: none\n')
             sock.send('Description: The exit command will log'
                       'you off the server\n')
 
         elif command == 'whois':
             sock.send('\nCommand: /whois\n')
             sock.send('Arguments: <username> (required)\n')
             sock.send('Description: The whois command will display basic'
                       'info about the user specified with <username>\n')
             sock.send('Ex: /whois billy\n')
 
         elif command == 'join':
             sock.send('\nCommand: /join\n') 
             sock.send('Arguments: <channel> (required)\n')
             sock.send('Description: The join command will place'
                       'you in the channel specified with <channel>\n')
             sock.send('If the channel does not exist yet,'
                       'it will be created\n')
             sock.send('By default the most recent channel you have'
                       'joined becomes your current channel\n')
             sock.send('Channel names must start with # and '
                       'contain no spaces or other illegal characters\n')
             sock.send('Ex: /join #channel_one\n')
 
         elif command == 'leave':
             sock.send('\nCommand: /leave\n')
             sock.send('Arguments: <channel> (required)\n')
             sock.send('Description: The leave command will take you out '
                       'of the channel specified by <channel>\n')
             sock.send('You must be in a channel in order to leave it.\n')
             sock.send('If you are the last person in the channel, '
                       'once you leave it will be deleted\n')
             sock.send('Ex: /leave #channel_one\n')
 
         elif command == 'current':
             sock.send('\nCommand: /current\n')
             sock.send('Arguments: <channel> (required)\n')
             sock.send('Description: The current command will switch your '
                       'current channel\n')
             sock.send('You must be in the channel specified by <channel>\n')
             sock.send('Ex: /current #channel_one\n')
 
         elif command == 'msg':
             sock.send('\nCommand: /msg\n')
             sock.send('Arguments: <user>, <message> (required)\n')
             sock.send('Description: Send private message '
                       '<message> to <user>\n')



"""
=======================================================
Function to send chat messages to all connected
users. 
This function sends the message to all connected users
in the current channel in which the sender is in
sock    --> socket object
message --> the message to send
=======================================================
"""
def broadcast_message(message, sock):
    
    # sockets with non-empty current field
    users = []

    # go through each socket 
    for s in CONNECTIONS:
    
        # don't store client who is sending message
        # or master socket
        if s != sock and s != server_socket:
    
            # sockets with non-empty current channel
            if ACCOUNTS[s]['current'] != '':
                users.append(s)

    
    # now go through each valid socket 
    for user in users:

        # send message to sockets who are in the same channel
        if ACCOUNTS[s]['current'] == ACCOUNTS[sock]['current']:

            # try to send before timeout otherwise log user off
            try:
                s.send(message)
            except:
                logoff(socket)
    

"""
=======================================================
Program starts here when excuted on its own 
=======================================================
"""
if __name__ == "__main__":

    # logging info on server
    logging.basicConfig(level=logging.INFO,
			format='[%(asctime)s] %(levelname)s: %(message)s',
			datefmt='%d/%m/%Y %I:%M:%S %p')


    # create TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # socket options
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)

    # bind the socket
    server_socket.bind((HOST, PORT))

    # start listening
    server_socket.listen(12)

    #broadcast_message('hi', server_socket)

    # add this socket to the list of connections
    CONNECTIONS.append(server_socket)

    # get the ip address of server and port
    server_IP = socket.gethostbyname(socket.gethostname())
    server_port = str(PORT)

    logging.info('Successfully started chat server [%s:%s]' % (server_IP, server_port))

    while True:
        
        # get list of sockets 
	    read_sockets, write_sockets, error_sockets = select.select(CONNECTIONS,
								   [],
								   [])
	
	    # go through each read socket
	    for sock in read_sockets:
	    
	        # if we have a new connection
	        if sock == server_socket:

		        # accept the new connection 
		        conn, addr = server_socket.accept()

		        # append the new connection to the list
		        CONNECTIONS.append(conn)

		        # make a new account for the connection
		        ACCOUNTS[conn] = { 'username': '',
				               'ip': addr[0] ,
				               'channels': [],
				               'current': ''
				             }

		        # get the name of the client
		        client_name = conn.recv(REC_BUFFER)

		        # make sure it's not already in use
		        if client_name in USERS:
		
		            conn.send('\nUsername already in use\n')
		            conn.close()
		            CONNECTIONS.remove(conn)

		        else:
		
		            conn.send('\nUsername accepted\nWelcome to the Internet Relay Chat\n')
		            conn.send('Type /help for help')

		            # set username
		            ACCOUNTS[conn]['username'] = client_name 
		            logging.info('%s has joined. Known as %s' % (addr, client_name))

		    # else we have a message from a client
	        else:
					
		        try:

		            # receiving data
		            data = sock.recv(REC_BUFFER)

		            if data:
								
		                # is it a command?
		                if data.find('/') == 0:
		                    parse_data(data, sock)

		        except:
		            logoff(sock)
		            continue
