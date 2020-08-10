import zipfile
import sys
import os
import shutil
import copy

input_dir = "input/"
working_dir = "working/"
output_dir = "output/"

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
            
        dest = "./working/"
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
        category = None
        self.data = dict()
        self.copy = dict()
        self.objects = list()

        with open(self.path, 'r') as file:
            for line in file.readlines():
                line = line.split("\n")[0]

                if(line == "[General]"):
                    mode = "data"
                    category = "[General]"
                    self.data[category] = dict()
                elif(line == "[Editor]"):
                    mode = "data"
                    category = "[Editor]"
                    self.data[category] = dict()
                elif(line == "[Metadata]"):
                    mode = "data"
                    category = "[Metadata]"
                    self.data[category] = dict()
                elif(line == "[Difficulty]"):
                    mode = "data"
                    category = "[Difficulty]"
                    self.data[category] = dict()
                elif(line == "[Events]"):
                    mode = "copy"
                    category = "[Events]"
                    self.copy[category] = list()
                elif(line == "[TimingPoints]"):
                    mode = "copy"
                    category = "[TimingPoints]"
                    self.copy[category] = list()
                elif(line == "[HitObjects]"):
                    mode = "objects"
                elif(not mode):
                    continue
                else:
                    if(mode == "data"):
                        s = line.split(":")
                        if(len(s)>1):
                            key = s.pop(0)
                            self.data[category][key] = ":".join(s)
                    elif(mode == "copy"):
                        self.copy[category].append(line)
                    elif(mode == "objects"):
                        self.objects.append(HitObject(line))
        self.read = True

    def writefile(self):
        filename = self.data["[Metadata]"]["ArtistUnicode"] + " - " + self.data["[Metadata]"]["TitleUnicode"] + " (" + self.data["[Metadata]"]["Creator"] + ") [" + self.data["[Metadata]"]["Version"] + "].osu"

        with open("working/"+filename,"w") as file:
            file.write("osu file format v14\n")
            file.write("\n")
            for categ,datas in self.data.items():
                file.write(categ+"\n")
                for key,data in datas.items():
                    self.writeData(file,key,data)
                file.write("\n")
            for categ,lines in self.copy.items():
                file.write(categ+"\n")
                for line in lines:
                    file.write(line+"\n")
                file.write("\n")
            file.write("[HitObjects]\n")
            for obj in self.objects:
                file.write(",".join(obj.args)+"\n")

    def writeData(self, file, key, data):
        file.write(key + ":" + data + "\n")

    def getHitObjectsColumn(self, column):
        objects = list()

        for obj in self.objects:
            if((int(obj.args[0])-64) / 4 < 16):
                if(column == 1):
                    objects.append(obj)
            elif((int(obj.args[0])-64) / 4 < 48):
                if(column == 2):
                    objects.append(obj)
            elif((int(obj.args[0])-64) / 4 < 80):
                if(column == 3):
                    objects.append(obj)
            elif((int(obj.args[0])-64) / 4 < 112):
                if(column == 4):
                    objects.append(obj)

        return objects

class HitObject:

    def __init__(self,line):
        self.args = line.split(",")

def copy1kBeatmap(beatmap, column):
    b = copy.deepcopy(beatmap)

    b.data["[Metadata]"]["Version"] += " 1k" + str(column)
    b.data["[Difficulty]"]["CircleSize"] = "1"
    b.objects = b.getHitObjectsColumn(column)
    b.writefile()

def packWorkingBeatmap(beatmap):
    dest = "output/"+beatmap.data["[Metadata]"]["ArtistUnicode"] + " - " + beatmap.data["[Metadata]"]["TitleUnicode"] + " (" + beatmap.data["[Metadata]"]["Creator"] + ").osz"
    shutil.make_archive(dest, 'zip', "working/")
    shutil.move(dest+".zip",dest)

if len(sys.argv) < 2:
    sys.exit("You need to specify at least one beatmapset's path")

for i in range(1,len(sys.argv)):
    if not os.path.isfile(sys.argv[i]):
        sys.exit(sys.argv[i]+" was not found")
    if os.path.splitext(sys.argv[i])[1] != ".osz":
        sys.exit(sys.argv[i]+" is not a .osz file")

try:
    os.mkdir(output_dir)
except:
    pass

beatmapsets = list()

for i in range(1,len(sys.argv)):
    beatmapsets.append(Beatmapset(sys.argv[i]))

for beatmapset in beatmapsets:
    try:
        shutil.rmtree(working_dir)
    except:
        pass
    try:
        os.mkdir(working_dir)
    except:
        pass
    for beatmap in beatmapset.getBeatmaps():
        beatmap.readfile()

        copy1kBeatmap(beatmap, 1)
        copy1kBeatmap(beatmap, 2)
        copy1kBeatmap(beatmap, 3)
        copy1kBeatmap(beatmap, 4)

        packWorkingBeatmap(beatmap)
    
try:
    shutil.rmtree(working_dir)
except:
    pass
