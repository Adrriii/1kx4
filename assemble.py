import os
import osrparse
from osrparse.enums import GameMode, Mod
import lzma, struct, datetime
import copy

def parse_timestamp_and_replay_length_new(self, replay_data):
    format_specifier = "<qi"
    (self.t, self.replay_length) = struct.unpack_from(format_specifier, replay_data, self.offset)
    self.timestamp = datetime.datetime.min + datetime.timedelta(microseconds=self.t/10)
    self.offset += struct.calcsize(format_specifier)

def parse_new(self, replay_data):
    offset_end = self.offset+self.replay_length
    self.parse_data_offset = self.offset
    if self.game_mode == GameMode.Standard or self.game_mode == GameMode.Osumania:
        datastring = lzma.decompress(replay_data[self.offset:offset_end], format=lzma.FORMAT_AUTO).decode('ascii')[:-1]
        events = [eventstring.split('|') for eventstring in datastring.split(',')]
        self.play_data = [osrparse.replay.ReplayEvent(int(event[0]), float(event[1]), float(event[2]), int(event[3])) for event in events]

    self.offset = offset_end
    self.offset_end = offset_end

def h_toString(self):
    return str(self.time_since_previous_action) +" | "+ str(self.x)

def newinit(self, replay_data):
        self.offset = 0
        self.game_mode = None
        self.game_version = None
        self.beatmap_hash = None
        self.player_name = None
        self.replay_hash = None
        self.number_300s = None
        self.number_100s = None
        self.number_50s = None
        self.gekis = None
        self.katus = None
        self.misses = None
        self.score = None
        self.max_combo = None
        self.is_perfect_combo = None
        self.mod_combination = None
        self.life_bar_graph = None
        self.timestamp = None
        self.play_data = None
        self.data = replay_data
        self.parse_replay_and_initialize_fields(replay_data)

osrparse.replay.Replay.parse_timestamp_and_replay_length = parse_timestamp_and_replay_length_new
osrparse.replay.Replay.parse_play_data = parse_new
osrparse.replay.Replay.__init__ = newinit
osrparse.replay.ReplayEvent.toString = h_toString
replays = list()

for file in os.listdir("replays/"):
    if file.endswith(".osr") and file != "src.osr" and file != "out.osr":
        replays.append(osrparse.replay.parse_replay_file("replays/"+file))

play_data_combined = list()

col = 1
current = 0
i = 0

def seekPreviousMs(liste, ms):
    last = liste[0]
    for l in liste:
        if(ms<l[0]):
            return last
        else:
            last = l
    return None

for event in replays[0].play_data:
    i+=1
    if i<3:
        continue
    if i==3:
        current = event.time_since_previous_action
        continue
    if i== len(replays[0].play_data):
        continue
    
    current += event.time_since_previous_action
    play_data_combined.append([current, event.x])


for k in range(1,4):
    i = 0
    for event in replays[k].play_data:
        i+=1
        if i<3:
            continue
        if i==3:
            current = event.time_since_previous_action
            continue
        if i== len(replays[k].play_data):
            continue

        current += event.time_since_previous_action
        
        if(event.x == 1.0):
            val = seekPreviousMs(play_data_combined, current)
            if val:
                if current-val[0] == 0:
                    val[1] += 2**k
                else:
                    play_data_combined.append([current, val[1] + 2**k])
            else:
                play_data_combined.append([current, 2**k])
            
    play_data_combined.sort(key=lambda x:x[0])

play_data_new = list()

play_data_new.append(['0', '256', '-500', '0'])
play_data_new.append(['-1', '256', '-500', '0'])

play_data_new.append([str(play_data_combined[0][0]), '0', '12.26994', '0'])

s = True
last = 0
for event in play_data_combined:
    if s:
        last = event[0]
        s = False
        pass

    diff = event[0] - last
    last = event[0]

    play_data_new.append([str(diff), str(event[1]), '12.26994', '0'])

play_data_new.append(['-12345', '0', '0', '3224846'])

lzma_play_data = lzma.compress((",".join(["|".join(data) for data in play_data_new]) + ",").encode('ascii'))

final = osrparse.replay.parse_replay_file("replays/src.osr")

final.data = final.data[0:final.parse_data_offset+1]
format_specifier = "<qi"
final.data = bytearray(final.data[:-struct.calcsize(format_specifier)])

final.data.extend(struct.pack(format_specifier, final.t, len(lzma_play_data)))
final.data.extend(lzma_play_data)

with open("replays/out.osr",'wb') as f:
    f.write(bytes(final.data))