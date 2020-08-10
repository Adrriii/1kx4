import zipfile
import sys
import os
import shutil

input_dir = "./input/"
output_dir = "./output/"

class Beatmapset:

    def __init__(self, path = None):
        self.files = list()
        self.extracted = False
        self.path = path

    def extract(self,path = None):
        if not path and not self.path:
            sys.exit("You need to specify a path to extract a beatmapset")

        if not self.path:
            self.path = path
            
        dest = "./output/"+os.path.splitext(os.path.basename(self.path))[0]
        with zipfile.ZipFile(self.path, 'r') as zip_ref:
            if not zip_ref:
                sys.exit(self.path+" is not a valid beatmapset file")
            zip_ref.extractall(dest)

        for file in os.listdir(dest):
            if file.endswith(".osu"):
                self.files.append(os.path.join(dest,file))
        self.extracted = True

    def getBeatmaps(self):
        if not self.extracted:
            self.extract()
        
        returned = list()

        for path in self.files:
            returned.append(Beatmap(path))
        
        return returned

class Beatmap:

    def __init__(self, path = None):
        self.read = False
        self.path = path

    def readfile(self,path = None):
        if not path and not self.path:
            sys.exit("You need to specify a path to read a beatmap")

        mode = None
        self.data = dict()
        self.copy = list()
        self.objects = list()

        with open(self.path, 'r') as file:
            for line in file.readlines():
                line = line.split("\n")[0]

                if(line == "[General]"):
                    mode = "data"
                elif(line == "[Editor]"):
                    mode = "data"
                elif(line == "[Metadata]"):
                    mode = "data"
                elif(line == "[Difficulty]"):
                    mode = "data"
                elif(line == "[Events]"):
                    mode = "copy"
                    self.copy.append(line)
                elif(line == "[TimingPoints]"):
                    mode = "copy"
                    self.copy.append(line)
                elif(line == "[HitObjects]"):
                    mode = "objects"
                elif(not mode):
                    continue
                else:
                    if(mode == "data"):
                        s = line.split(":")
                        if(len(s)>1):
                            key = s.pop(0)
                            self.data[key] = ":".join(s)
                    elif(mode == "copy"):
                        self.copy.append(line)
                    elif(mode == "objects"):
                        self.objects.append(HitObject(line))

class HitObject:

    def __init__(self,line):
        self.args = line.split(",")

        

          


if len(sys.argv) < 2:
    sys.exit("You need to specify at least one beatmapset's path")

for i in range(1,len(sys.argv)):
    if not os.path.isfile(sys.argv[i]):
        sys.exit(sys.argv[i]+" was not found")
    if os.path.splitext(sys.argv[i])[1] != ".osz":
        sys.exit(sys.argv[i]+" is not a .osz file")

shutil.rmtree(output_dir)
os.mkdir(output_dir)

beatmapsets = list()

for i in range(1,len(sys.argv)):
    beatmapsets.append(Beatmapset(sys.argv[i]))

for beatmapset in beatmapsets:
    for beatmap in beatmapset.getBeatmaps():
        beatmap.readfile()