#!/usr/bin/env python
# -*- coding: utf-8 -*-

# kongo 140602

import sys
import socket
import string
import time
import threading
import serial.serialposix
import mpd

HOST="efnet.portlane.se"
PORT=6667
NICK="MrCoffee"
IDENT="mrcoffee"
REALNAME="Mr. Coffee"
CHANNEL="#etf"

def cutetime(epoch):
    st = time.localtime(epoch)
    ast = time.gmtime(time.time() - epoch)
    ago = []
    if time.time() - epoch > 60*60*24*28:
        ago.append('en evighet')
    else:
        if ast.tm_mday > 2:
            ago.append('%d dagar' % (ast.tm_mday-1))
        elif ast.tm_mday == 2:
            ago.append('1 dag')
        if ast.tm_hour > 1:
            ago.append('%d timmar' % ast.tm_hour)
        elif ast.tm_hour == 1:
            ago.append('1 timme')
        if ast.tm_min > 1:
            ago.append('%d minuter' % ast.tm_min)
        elif ast.tm_min == 1:
            ago.append('1 minut')
    if len(ago) == 0:
        ago = 'typ nu'
    elif len(ago) == 1:
        ago = ago[0] + ' sedan'
    else:
        ago = ', '.join(ago[:-1]) + ' och ' + ago[-1] + ' sedan'
    if time.time() - epoch > 60*60*24:
        t = time.strftime('%d/%m %H:%M', st)
    else:
        t = time.strftime('%H:%M', st)
    return t + ', dvs. ' + ago

def reply(s, line, msg):
    if line[2] == CHANNEL:
        dst = CHANNEL
    else:
        dst = line[0][1:].split('!')[0]
    s.send('PRIVMSG %s :%s\r\n' % (dst, msg))

class CoffeeThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.sock = None
        self.last_start = 0
        self.last_stop = 0
        self.daemon = True

    def run(self):
        s = serial.serialposix.PosixSerial(0)
        s.setDTR(True)
        s.setRTS(False)
        time.sleep(30)
        last = s.getRI()
        #self.sock.send("PRIVMSG %s :%s\r\n" % (CHANNEL, "herro everyone!"))
        while True:
            if last ^ s.getRI():
                if s.getRI():
                    msg = "it's on!"
                    self.last_start = time.time()
                else :
                    self.last_stop = time.time()
                    msg = "kaffet e klart! (det tog %d sekunder)" % (self.last_stop-self.last_start)
                try:
                    if self.sock:
                        self.sock.send("PRIVMSG %s :%s\r\n" % (CHANNEL, msg))
                except:
                    pass
                last = s.getRI()
            time.sleep(2)

if __name__ == '__main__':
    c = CoffeeThread()
    c.start()

    while True:
        readbuffer=""

        try:
            s=socket.socket( )
            s.connect((HOST, PORT))
            s.send("NICK %s\r\n" % NICK)
            s.send("USER %s %s bla :%s\r\n" % (IDENT, HOST, REALNAME))
            s.send("JOIN %s\r\n" % CHANNEL)

            c.sock = s

            while 1:
                readbuffer=readbuffer+s.recv(1024)
                temp=string.split(readbuffer, "\n")
                readbuffer=temp.pop( )

                for line in temp:
                    line=string.rstrip(line)
                    line=string.split(line)
                    #print line

                    if line[0] == 'PING':
                        s.send("PONG %s\r\n" % line[1])
                    elif len(line) >= 4 and line[1] == 'PRIVMSG':
                        if line[3] == ':!kaffe':
                            if c.last_start == 0:
                                msg = 'vilket kaffe? hurr durr.'
                            elif c.last_start > c.last_stop:
                                msg = 'snart nytt kaffe... (startad %s)' % cutetime(c.last_start)
                            else:
                                msg = 'senaste kaffet bryggdes %s. det tog %d sekunder.' % (cutetime(c.last_stop), c.last_stop - c.last_start)
                            reply(s, line, msg)
                        elif line[3] == ':!what':
                            try:
                                m = mpd.MPDConn()
                                stat = m.query('status', True)
                                reply(s, line, 'state: %s' % (stat['state'] if 'state' in stat else 'N/A'))
                                cs = m.query('currentsong', True)
                                if 'Title' in cs:
                                    reply(s, line, 'title: %s' % cs['Title'])
                                if 'Name' in cs:
                                    reply(s, line, 'name: %s' % cs['Name'])
                                del m
                            except Exception as e:
                                reply(s, line, 'det gick fel.')
                                file('/tmp/bot.last','w').write(str(e))
                        elif line[3] == ':!help':
                            reply(s, line, '!kaffe, !play, !pause, !stop, !what, !sky <kanal>, !di <kanal>, !blipblop, !jul, !kohina, !slay')
                        elif line[3][2:] in ('stop','play','pause'):
                            try:
                                mpd.MPDConn().cmd(line[3][2:])
                            except Exception as e:
                                reply(s, line, 'aw.')
                                file('/tmp/bot.last','w').write(str(e))
                        elif line[3][2:] in ('sky','di','blipblop','kohina','slay'):
                            try:
                                streambase = {'sky': 'pub2.sky.fm/sky_',
                                            'di': 'pub6.di.fm/di_',
                                            'blipblop': 'radio.mojt.net/blop.php?',
                                            'jul': 'radio.mojt.net/merjul.php?',
                                            'kohina': 'kohina.radio.ethz.ch:8000/kohina.ogg?',
                                            'slay': 'relay1.slayradio.org:8000/?'}
                                m = mpd.MPDConn()
                                m.cmd('clear')
                                m.cmd('add http://%s%s' % (streambase[line[3][2:]], line[4] if len(line) >= 5 else ''))
                                m.cmd('play')
                                time.sleep(2)
                                cs = m.query('currentsong', True)
                                reply(s, line, 'spelas nu: ' + (cs['Name'] if 'Name' in cs else '<wtf>'))
                                del m
                            except Exception as e:
                                reply(s, line, 'attans.')
                                file('/tmp/bot.last','w').write(str(e))
        except:
            pass #yeah!
        time.sleep(30)
