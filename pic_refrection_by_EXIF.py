#!/usr/bin/python
# -*- coding: utf-8; mode: python-mode; -*-
# Last Change:2009/8/2 02:50:25.

from __future__ import with_statement

import os
import sys
import time
import re
import shutil

import EXIF

pic_dir = os.path.expanduser("~/Pictures")

class NoPictError(Exception):
    pass

class CPicRefrection(object):

    log = os.path.join(pic_dir, 'PicRefrection.log')
    
    def __init__(self, _file):
        self.date = {}
        self.new_path = None

        fname = _file.encode('utf-8')
        
        self.full_name = os.path.abspath( fname )
        self.file_basename = os.path.basename( fname )

    def __getDataFile(self):
        with open(self.full_name, 'rb') as fp:
            tags = EXIF.process_file(fp)
            try:
                m = re.search(r'(\d\d\d\d):(\d\d):(\d\d) (\d\d):(\d\d):(\d\d)',\
                              tags['EXIF DateTimeOriginal'].values)
            
                if m:
                    self.date['year']  = m.group(1)
                    self.date['month'] = m.group(2)
                    self.date['day']   = m.group(3)
                    self.date['hour']  = m.group(4)
                    self.date['min']   = m.group(5)
                    self.date['sec']   = m.group(6)

            except KeyError, e:
                print(self.full_name)
                raise NoPictError
                
    """
    def __getDataCommand(self):
        import commands

        contents = commands.getoutput('exiftags %s' % self.full_name )
        lines = contents.splitlines()
        for line in lines:
            if  'Image Created' in line:
                m = re.search(r'(\d\d\d\d):(\d\d):(\d\d) (\d\d):(\d\d):(\d\d)', line)
                if m:
                    self.date['year']  = m.group(1)
                    self.date['month'] = m.group(2)
                    self.date['day']   = m.group(3)
                    self.date['hour']  = m.group(4)
                    self.date['min']   = m.group(5)
                    self.date['sec']   = m.group(6)

                    return True
    """

    def __makeDir(self):
        self.new_path = os.path.join(pic_dir, self.date['year'], self.date['month'])

        if os.access(self.new_path, os.F_OK and os.W_OK):
            return
        else:
            try:
                os.makedirs(self.new_path)
            except:
                print('Error:MakeDir')


    def __move(self):
        renamed = os.path.join( self.new_path, self.file_basename )
        (n, ext) = os.path.splitext( self.file_basename )

        new_name = self.date['year'] + self.date['month'] + self.date['day'] + '-' \
                   + self.date['hour'] + self.date['min'] + self.date['sec'] + ext.lower()

        date_name = os.path.join( self.new_path, new_name )
        
        try:
            #os.rename( self.full_name, renamed )
            shutil.copy2( self.full_name, renamed )
            os.rename( renamed, date_name )
            self._log( date_name )
            
        except IOError,e:
            print(e)
            

    def _log(self, _renamed, isSuccess=True):
        if isSuccess:
            string = "%s -> %s" % (self.full_name, _renamed)
        else:
            string = "Faild %s" % (self.full_name, )

        try:
            with open(self.log, 'a') as fp:
                fp.write(string)
                fp.write("\n")
                
        except IOError,e:
            print(e)


    def run(self):
        # if self.__getDataCommand():
        try:
            self.__getDataFile()
            self.__makeDir()
            self.__move()
        except NoPictError:
            self._log('', False)
            raise


class CPicRefrectionManager(object):
    def __init__(self, _argv):
        self.file_list = []
        
        dir_list = []
        for f in _argv:
            if os.path.isdir(f):
                dir_list.append(f)
            elif os.path.isfile(f):
                self.file_list.append(f)

        for d in dir_list:
            for root, dirs, files in os.walk(d):
                for f in files:
                    self.file_list.append(os.path.join(root, f))


    def run(self):
        for f in self.file_list:
            try:
                pr = CPicRefrection(f)
                pr.run()
            except NoPictError:
                continue    


def main():

    import optparse

    global pic_dir

    parser = optparse.OptionParser()
    parser.add_option("-d", "--dir", \
                      action="store", \
                      type="string", \
                      dest="dir",
                      help="set moving Dir(Top Level). Defalut '~/Pictures'")
    (options, args) = parser.parse_args()

    if options.dir:
        pic_dir = options.dir
    
    _list = sys.argv[1:]
    cpm = CPicRefrectionManager(_list)
    cpm.run()


if __name__ == '__main__': main()

