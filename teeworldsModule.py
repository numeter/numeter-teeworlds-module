#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Gaël Lambert (gaelL) <gael.lambert@netwiki.fr>
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
import re
import os, sys 
import operator
from pprint import pprint
import subprocess
import logging

class teeworldsModule: 
    "Module generic"

    def  __init__(self,configParser=None): 
        "Load configuration and start connexion"
        self._logger= logging.getLogger(__name__)
        self._logger.info("Plugin Munin start")
        self._configParser=configParser

        self._logfile = 'teeworlds.log'
        self._logtail = '/usr/sbin/logtail'
        self._statefile = '/var/tmp/teeworlds_stats.statefile'
        self._cachefile = '/var/cache/teeworlds_stats.cache'
        self._STATUS = {}

        if configParser:
            # Get logfile
            if self._configParser.has_option('teeworldsModule', 'logfile') \
            and self._configParser.get('teeworldsModule', 'logfile'):
                self._logfile = self._configParser.get('teeworldsModule'
                                            , 'logfile')
            # Get logtail
            if self._configParser.has_option('teeworldsModule', 'logtail') \
            and self._configParser.get('teeworldsModule', 'logtail'):
                self._logtail = self._configParser.get('teeworldsModule'
                                            , 'logtail')


    def _getStatus(self):
        # Get current status
        if os.path.exists(self._cachefile):
            cf = open(self._cachefile, 'r')
            tmpstatus = cf.read()
            self._STATUS = {} if tmpstatus == '' else eval(tmpstatus)

    def _writeStatus(self):
        cf = open(self._cachefile, 'w')
        cf.write(str(self._STATUS))


    def _getoffset(self):
        try:
            process = subprocess.Popen([self._logtail, self._logfile,
                                    self._statefile],stdout=subprocess.PIPE)
            (stdout, stderr) = process.communicate()
            # Devel disable statefile
            #os.system('rm '+self._statefile)
            return stdout.rsplit('\n')
        except:
            self._logger.critical("Can't launch logtail, check if logtail is installed or your PATH")
            return ''

    def _parseLogs(self):
        f = self._getoffset()
        for line in f:
            #[51309e5c][game]: kill killer='1:talset' victim='0:RaoH' weapon=3 special=0

            pickup = re.search(r'pickup player=\'[0-9]+:([^\']+)\' item=([0-9]/[0-9])', line)
            if pickup is not None:
                player = pickup.group(1)
                item   = pickup.group(2)
                if item == '1/0': item = 'shield'
                elif item == '0/0': item = 'life'
                elif item == '2/2': item = 'shotgun'
                elif item == '2/3': item = 'rocket'
                elif item == '2/4': item = 'laser'
                elif item == '3/5': item = 'ninja'
                else: continue

                # Init tab
                if not 'player_items' in self._STATUS:
                    self._STATUS['player_items'] = {}

                # Player items
                if not player in self._STATUS['player_items']:
                    self._STATUS['player_items'][player] = {}
                if not item in self._STATUS['player_items'][player]:
                    self._STATUS['player_items'][player][item] = 1
                else:
                    self._STATUS['player_items'][player][item] += 1

                continue

            m = re.search(r'kill killer=\'[0-9]+:([^\']+)\' victim=\'[0-9]+:([^\']+)\' weapon=(\-?[0-9]+)', line)
            if m is not None:
                player = m.group(1)
                killed = m.group(2)
                weapon = m.group(3)
                if m.group(3) == '0': weapon = 'hammer'
                elif m.group(3) == '1': weapon = 'gun'
                elif m.group(3) == '2': weapon = 'shotgun'
                elif m.group(3) == '3': weapon = 'rocket'
                elif m.group(3) == '4': weapon = 'laser'
                elif m.group(3) == '5': weapon = 'ninja'
                elif m.group(3) == '-1': weapon = 'sucide'
                elif m.group(3) == '-3': continue
                if player == killed: weapon = 'sucide'

                # Init tab
                if not 'player_kills' in self._STATUS:
                    self._STATUS['player_kills'] = {}
                if not 'player_rate' in self._STATUS:
                    self._STATUS['player_rate'] = {}
                if not 'player_weapons' in self._STATUS:
                    self._STATUS['player_weapons'] = {}
                if not 'player_weapons_killedby' in self._STATUS:
                    self._STATUS['player_weapons_killedby'] = {}
                if not 'player_killedby' in self._STATUS:
                    self._STATUS['player_killedby'] = {}
    
                # Player kills
                if not player in self._STATUS['player_kills']:
                    self._STATUS['player_kills'][player] = {}
                if not killed in self._STATUS['player_kills'][player]:
                    self._STATUS['player_kills'][player][killed] = 1
                else:
                    self._STATUS['player_kills'][player][killed] += 1
                # Player killedby
                if not killed in self._STATUS['player_killedby']:
                    self._STATUS['player_killedby'][killed] = {}
                if not player in self._STATUS['player_killedby'][killed]:
                    self._STATUS['player_killedby'][killed][player] = 1
                else:
                    self._STATUS['player_killedby'][killed][player] += 1
                # Player weapon
                if weapon != 'sucide':
                    if not player in self._STATUS['player_weapons']:
                        self._STATUS['player_weapons'][player] = {}
                    if not weapon in self._STATUS['player_weapons'][player]:
                        self._STATUS['player_weapons'][player][weapon] = 1
                    else:
                        self._STATUS['player_weapons'][player][weapon] += 1
                # Player weapon killedby
                if not killed in self._STATUS['player_weapons_killedby']:
                    self._STATUS['player_weapons_killedby'][killed] = {}
                if not weapon in self._STATUS['player_weapons_killedby'][killed]:
                    self._STATUS['player_weapons_killedby'][killed][weapon] = 1
                else:
                    self._STATUS['player_weapons_killedby'][killed][weapon] += 1
                # Player rate
                if not player in self._STATUS['player_rate']:
                    self._STATUS['player_rate'][player] = {'kills': 0, 'death': 0}
                if not killed in self._STATUS['player_rate']:
                    self._STATUS['player_rate'][killed] = {'kills': 0, 'death': 0}

                self._STATUS['player_rate'][killed]['death'] += 1
                if player != killed:
                    self._STATUS['player_rate'][player]['kills'] += 1


    def _lifeItemPlugin(self,mode):
        "Rate plugin"
        now = time.strftime("%Y %m %d %H:%M", time.localtime())
        nowTimestamp = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M'))
        if mode == 'fetch': # DATAS
            values = {}
            for player in sorted(self._STATUS['player_items']):
                number = 0
                if 'life' in self._STATUS['player_items'][player]:
                    number += self._STATUS['player_items'][player]['life']
                if 'shield' in self._STATUS['player_items'][player]:
                    number += self._STATUS['player_items'][player]['shield']
                values[player] = number

            DATAS = {
                'TimeStamp': nowTimestamp,
                'Plugin': 'lifeItem',
                'Values': values,
            }
            return DATAS
        else: # INFOS
            dsInfos = {}
            for player in sorted(self._STATUS['player_items']):
                dsInfos[player] = {
                    "type": "GAUGE",
                    "id": player,
                    "draw": 'line',
                    "label": player}
            INFOS = {
                'Plugin': 'lifeItem',
                'Describ': 'Number of life item for each players', 
                'Category': 'Teeworlds',
                'Order': ' '.join(sorted(self._STATUS['player_items'])),
                'Base': '1000', 
                'Title': 'Players life item',
                'Vlabel': 'number',
                'Infos': dsInfos,
            }
            return INFOS


    def _ratesPlugin(self,mode):
        "Rate plugin"
        now = time.strftime("%Y %m %d %H:%M", time.localtime())
        nowTimestamp = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M'))
        if mode == 'fetch': # DATAS
            values = {}
            for player in sorted(self._STATUS['player_rate']):
                if self._STATUS['player_rate'][player]['death'] == 0:
                    rate = (self._STATUS['player_rate'][player]['kills'])
                else:
                    rate = (float(self._STATUS['player_rate'][player]['kills']) /
                            float(self._STATUS['player_rate'][player]['death']))
                values[player] = rate

            DATAS = {
                'TimeStamp': nowTimestamp,
                'Plugin': 'rates', 
                'Values': values,
            }
            return DATAS

        else: # INFOS
            dsInfos = {}
            for player in sorted(self._STATUS['player_rate']):
                dsInfos[player] = {
                    "type": "GAUGE",
                    "id": player,
                    "draw": 'line',
                    "label": player}
            INFOS = {
                'Plugin': 'rates',
                'Describ': 'rate kill / death', 
                'Category': 'Teeworlds',
                'Order': ' '.join(sorted(self._STATUS['player_rate'])),
                'Base': '1000', 
                'Title': 'Players rate',
                'Vlabel': 'rate', 
                'Infos': dsInfos,
            }
            return INFOS

    def _killsDeath(self,mode):
        "Kills / death plugin"
        now = time.strftime("%Y %m %d %H:%M", time.localtime())
        nowTimestamp = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M'))
        DATAS = []
        if mode == 'fetch': # DATAS
            for player in sorted(self._STATUS['player_rate']):
                kills = self._STATUS['player_rate'][player]['kills']
                death = self._STATUS['player_rate'][player]['death']
                DATAS.append({
                    'TimeStamp': nowTimestamp,
                    'Plugin': 'kills_death_' + player,
                    'Values': { 'kills': kills, 'death': death }
                })

            return DATAS
        else: # INFOS
            dsInfos = {}
            INFOS = []
            for player in sorted(self._STATUS['player_rate']):
                dsInfos['kills'] = {
                    "type": "GAUGE",
                    "id": 'kills',
                    "draw": 'line',
                    "color": '#0000FF',
                    "label": player + ' kills'}
                dsInfos['death'] = {
                    "type": "GAUGE",
                    "id": 'death',
                    "draw": 'line',
                    "color": '#B40404',
                    "label": player + ' death'}
                INFOS.append({
                    'Plugin': 'kills_death_' + player,
                    'Describ': 'kill / death', 
                    'Category': 'Teeworlds',
                    'Base': '1000', 
                    'Title': 'kills /death - ' + player,
                    'Vlabel': 'Number', 
                    'Infos': dsInfos,
                })
            return INFOS

    def _kills(self,mode):
        "Kills plugin"
        now = time.strftime("%Y %m %d %H:%M", time.localtime())
        nowTimestamp = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M'))
        DATAS = []
        if mode == 'fetch': # DATAS
            for player in sorted(self._STATUS['player_kills']):
                values = {}
                for killed,nbr in sorted(self._STATUS['player_kills'][player].iteritems()):
                    values[killed] = nbr

                DATAS.append({
                    'TimeStamp': nowTimestamp,
                    'Plugin': 'kills_' + player,
                    'Values': values
                })

            return DATAS
        else: # INFOS
            dsInfos = {}
            INFOS = []
            for player in sorted(self._STATUS['player_kills']):
                dsInfos = {}
                for killed,nbr in sorted(self._STATUS['player_kills'][player].iteritems()):
                    dsInfos[killed] = {
                        "type": "GAUGE",
                        "id": killed,
                        "draw": 'line',
                        "label": killed}
                INFOS.append({
                    'Plugin': 'kills_' + player,
                    'Describ': 'How many time you have kill others players', 
                    'Category': 'Teeworlds',
                    'Base': '1000', 
                    'Title': 'kills - ' + player,
                    'Vlabel': 'Number of kill',
                    'Infos': dsInfos,
                })
            return INFOS

    def _killedBy(self,mode):
        "Killed by plugin"
        now = time.strftime("%Y %m %d %H:%M", time.localtime())
        nowTimestamp = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M'))
        DATAS = []
        if mode == 'fetch': # DATAS
            for player in sorted(self._STATUS['player_killedby']):
                values = {}
                for killed,nbr in sorted(self._STATUS['player_killedby'][player].iteritems()):
                    values[killed] = nbr

                DATAS.append({
                    'TimeStamp': nowTimestamp,
                    'Plugin': 'killed_' + player,
                    'Values': values
                })

            return DATAS
        else: # INFOS
            dsInfos = {}
            INFOS = []
            for player in sorted(self._STATUS['player_killedby']):
                dsInfos = {}
                for killed,nbr in sorted(self._STATUS['player_killedby'][player].iteritems()):
                    dsInfos[killed] = {
                        "type": "GAUGE",
                        "id": killed,
                        "draw": 'line',
                        "label": killed}
                INFOS.append({
                    'Plugin': 'killed_' + player,
                    'Describ': 'Who kill you ?', 
                    'Category': 'Teeworlds',
                    'Base': '1000', 
                    'Title': 'Who killed - ' + player,
                    'Vlabel': 'Number of kill',
                    'Infos': dsInfos,
                })
            return INFOS

    def _weapons(self,mode):
        "weapons plugin"
        now = time.strftime("%Y %m %d %H:%M", time.localtime())
        nowTimestamp = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M'))
        DATAS = []
        if mode == 'fetch': # DATAS
            for player in sorted(self._STATUS['player_weapons']):
                values = {}
                for weapon,nbr in sorted(self._STATUS['player_weapons'][player].iteritems()):
                    values[weapon] = nbr

                DATAS.append({
                    'TimeStamp': nowTimestamp,
                    'Plugin': 'weapons_' + player,
                    'Values': values
                })

            return DATAS
        else: # INFOS
            dsInfos = {}
            INFOS = []
            for player in sorted(self._STATUS['player_weapons']):
                dsInfos = {}
                for weapon,nbr in sorted(self._STATUS['player_weapons'][player].iteritems()):
                    dsInfos[weapon] = {
                        "type": "GAUGE",
                        "id": weapon,
                        "draw": 'line',
                        "label": weapon}
                INFOS.append({
                    'Plugin': 'weapons_' + player,
                    'Describ': 'How many frags with each ammo', 
                    'Category': 'Teeworlds',
                    'Base': '1000', 
                    'Title': 'weapons - ' + player,
                    'Vlabel': 'Number of kill',
                    'Infos': dsInfos,
                })
            return INFOS

    def _weaponsKilledBy(self,mode):
        "weapons killed by plugin"
        now = time.strftime("%Y %m %d %H:%M", time.localtime())
        nowTimestamp = "%.0f" % time.mktime(time.strptime(now, '%Y %m %d %H:%M'))
        DATAS = []
        if mode == 'fetch': # DATAS
            for player in sorted(self._STATUS['player_weapons_killedby']):
                values = {}
                for weapon,nbr in sorted(self._STATUS['player_weapons_killedby'][player].iteritems()):
                    values[weapon] = nbr

                DATAS.append({
                    'TimeStamp': nowTimestamp,
                    'Plugin': 'killed_by_weapons_' + player,
                    'Values': values
                })

            return DATAS
        else: # INFOS
            dsInfos = {}
            INFOS = []
            for player in sorted(self._STATUS['player_weapons_killedby']):
                dsInfos = {}
                for weapon,nbr in sorted(self._STATUS['player_weapons_killedby'][player].iteritems()):
                    dsInfos[weapon] = {
                        "type": "GAUGE",
                        "id": weapon,
                        "draw": 'line',
                        "label": weapon}
                INFOS.append({
                    'Plugin': 'killed_by_weapons_' + player,
                    'Describ': 'How you die ?', 
                    'Category': 'Teeworlds',
                    'Base': '1000', 
                    'Title': 'weapons killed - ' + player,
                    'Vlabel': 'Number of kill',
                    'Infos': dsInfos,
                })
            return INFOS

    def getData(self):
        "get and return all data collected"
        # Refresh status
        self._getStatus()
        self._parseLogs()
        self._writeStatus()
        DATAS = []

        # Rates plugin
        DATAS.append(self._ratesPlugin('fetch'))

        # kills death plugins
        DATAS.extend(self._killsDeath('fetch'))

        # kills plugins
        DATAS.extend(self._kills('fetch'))

        # weapons plugins
        DATAS.extend(self._weapons('fetch'))

        # weapons killed by plugins
        DATAS.extend(self._weaponsKilledBy('fetch'))

        # killed by plugins
        DATAS.extend(self._killedBy('fetch'))

        # life item plugins
        DATAS.append(self._lifeItemPlugin('fetch'))

        return DATAS



    def getInfo(self):
        "Return plugins info for refresh"
        # Refresh status
        self._getStatus()
        INFOS = []

        # Rates plugin
        INFOS.append(self._ratesPlugin('config'))

        # kills death plugins
        INFOS.extend(self._killsDeath('config'))

        # kills plugins
        INFOS.extend(self._kills('config'))

        # weapons plugins
        INFOS.extend(self._weapons('config'))

        # weapons killed by plugins
        INFOS.extend(self._weaponsKilledBy('config'))

        # killed by plugins
        INFOS.extend(self._killedBy('config'))

        # life item plugins
        INFOS.append(self._lifeItemPlugin('config'))

        return INFOS

if __name__ == "__main__":
    _logger = logging.getLogger()
    ch = logging.StreamHandler(stream=sys.stdout)
    _logger.addHandler(ch)
    _logger.setLevel(logging.DEBUG)
    stats = teeworldsModule(None)
    print str(stats.getData())
    print str(stats.getInfo())

