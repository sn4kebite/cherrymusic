#!/usr/bin/python3
#
# CherryMusic - a standalone music server
# Copyright (c) 2012 Tom Wallroth & Tilman Boerner
#
# Project page:
#   http://fomori.org/cherrymusic/
# Sources on github:
#   http://github.com/devsnd/cherrymusic/
#
# CherryMusic is based on
#   jPlayer (GPL/MIT license) http://www.jplayer.org/
#   CherryPy (BSD license) http://www.cherrypy.org/
#
# licensed under GNU GPL version 3 (or later)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
#

from cherrymusicserver import log
import sys, os

#check for meta info libraries
if sys.version_info >= (3,):
    #stagger is only for python 3
    try:
        import stagger
        has_stagger = True
    except ImportError:
        log.w('''python library "stagger" not found: There will be no ID-tag support!''')
        has_stagger = False
else:
    has_stagger = False

try:
    import audioread
    has_audioread = True
except ImportError:
    log.w('''python library "audioread" not found!
-Audio file length can't be determined without it!''')
    has_audioread = False
    
class Metainfo():
    def __init__(self, artist, album, title, track, length):
        self.artist = artist
        self.album = album
        self.title = title
        self.track = track
        self.length = length
    def dict(self):
        return {
        'artist': self.artist,
        'album': self.album,
        'title': self.title,
        'track': self.track,
        'length': self.length
        }
#
# Mock implementation for faild import (might be handy if
# multiple libs are used to determine metainfos)
#

#stagger
        
class MockTag():
    def __init__(self):
        self.artist = '-'
        self.album = '-'
        self.title = '-'
        self.track = '-'
       
def getSongInfo(filepath, _track = None):
    ext = os.path.splitext(filepath)[1]
    if ext == '.cue' and _track:
        from cherrymusicserver.cuesheet import Cuesheet
        cue = Cuesheet(filepath)
        info = cue.info[0]
        artist = info.performer or '-'
        album = info.title or '-'
        title = '-'
        _track = int(_track)
        track = cue.tracks[_track-1]
        artist = track.performer or artist
        title = track.title or title
        if _track < len(cue.tracks) + 1:
            track.nextstart = cue.get_next(track).get_start_time()
            audiolength = track.get_length()
        elif has_audioread:
            lasttrack = cue.tracks[-1]
            try:
                with audioread.audio_open(info.file[0]) as f:
                    lasttrack.nextstart = f.duration
            except Exception:
                log.e('audioread failed! (%s)', filepath)
                audiolength = 0
            else:
                track.nextstart = cue.get_next(track).get_start_time()
                audiolength = track.get_length()
        else:
            audiolength = 0
        return Metainfo(artist, album, title, _track, audiolength)
    if has_stagger:
        try:
            tag = stagger.read_tag(filepath)
        except Exception:
            tag = MockTag()
    else:
        tag = MockTag()
            
    if has_audioread:
        try:
            with audioread.audio_open(filepath) as f:
                audiolength = f.duration
        except Exception:
            log.e('audioread failed! (%s)', filepath)
            audiolength = 0
    else:
        audiolength = 0
    return Metainfo(tag.artist, tag.album, tag.title, tag.track, audiolength)

    
