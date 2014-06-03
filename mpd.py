#!/usr/bin/env python

import socket

class MPDConn:

    def __init__(self, addr = 'localhost', port = 6600):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((addr, port))
        ver = self.s.recv(1024)
        if len(ver) < 0 or ver[:2] != 'OK':
            raise Exception('unexpected response on mpd connection')

    def cmd(self, cmd):
        self.s.send(cmd+'\n')
        response = self.s.recv(1024).strip()
        if response != 'OK':
            raise Exception('command failed: %s' % response)

    def query(self, cmd, secondsplit = False):
        self.s.send(cmd+'\n')
        response = self.s.recv(2048).split('\n')
        if response[-2] != 'OK':
            raise Exception('query failed: %s' % response[-2])
        response = response[:-2]
        if secondsplit:
            response = dict(map(lambda x: x.split(': ',1), response))
        return response

if __name__ == '__main__':
    mpd = MPDConn() 

    #mpd.cmd('clear')
    ##mpd.cmd('add http://pub2.sky.fm/sky_tophits')
    #mpd.cmd('add http://pub6.di.fm/di_nightcore')
    #mpd.cmd('play')

    #mpd.cmd('pause')
    cs = mpd.query('currentsong', True)
    print 'Title: ' + (cs['Title'] if 'Title' in cs else 'N/A')
    print 'Name: ' + (cs['Name'] if 'Name' in cs else 'N/A')
    #mpd.cmd('play')
