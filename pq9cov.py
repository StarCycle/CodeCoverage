import os
import re
import sys
import csv

def FindAllFiles(path):
    '''
    A genarator that looks for full paths of all files under a directory
    Some files will be skiped
    Input:
        path        A file or a directory
    Output:
        location    path of a file under the directory
    '''
    if path.endswith('.c') or path.endswith('.cpp') or path.endswith('.h') or path.endswith('.hpp'):
        location = path
        yield location
    else:
        for root, dirList, fileList in os.walk(path):
            for f in fileList:
                if (not f.startswith('startup_')) and (not f.startswith('system_')) and (not f.startswith('SLOT_SELECT')) and (not f.startswith('md5')):
                    if f.endswith('.c') or f.endswith('.cpp') or f.endswith('.h') or f.endswith('.hpp'):
                        location = os.path.join(root, f)
                        yield location

def Instrument(matched):
    '''
    Add 'CodeCount' in the source code
    The instrumentation may not be very precise, so users can delete or add 'CodeCount' manually
    '''
    if 'switch' in matched.group() or r'//' in matched.group():
        return matched.group()
    else:
        return matched.group() + '\nCodeCount'

class Label():
    '''
    Replace 'CodeCount' with CodeCount(x) in the source code, where x is a unique label
    '''
    def __init__(self):
        self.count = -1

    def AddLabel(self, matched):
        self.count += 1
        return r'CodeCount(' + str(self.count) + r');'

class Analyser():
    '''
    Analyse and display the coverage result
    '''
    def __init__(self, rawCovFile):
        '''
        rawCovFile data format: 'nr nr nr nr ...', where nr represents a byte that shows 8 CodeCounts
        '''
        with open(rawCovFile, 'r') as rcfile:
            rawCov = rcfile.read().split()
            self.binCov = '' # A binary string, where each bit contains a CodeCount result
            for rawData in rawCov:
                self.binCov = self.binCov + bin(int(rawData))[2:].rjust(8, '0')
        self.covDetails = []

    def SetPath(self, path):
        self.path = path

    def LocateResult(self, matched):
        ID = int(matched.group(1))
        if self.binCov[ID] == '0':
            self.covDetails.append([self.path, ID, 0])
            return r'CodeCount(' + str(ID) + r') NOT EXECUTED'
        elif self.binCov[ID] == '1':
            self.covDetails.append([self.path, ID, 1])
            return r'CodeCount(' + str(ID) + r') EXECUTED'

    def WriteCSV(self):
        with open('CoverageOverview.csv', 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(['path', 'ID', 'executed']) # csv head
            for row in self.covDetails:
                writer.writerow(row)

if __name__ == "__main__":
    # Instrument the code. You can modify the result manually
    if sys.argv[1] == '-i': 
        for path in sys.argv[2:]:
            for file in FindAllFiles(path):
                with open(file, 'r') as f:
                    string = f.read()
                # Instrument at every check point
                string = re.sub(r'\n[\s]*if\s*\(.+\)[\s\n]*{', Instrument, string)
                string = re.sub(r'\n[\s]*else if\s*\(.+\)[\s\n]*{', Instrument, string)
                string = re.sub(r'\n[\s]*else[\s\n]*{', Instrument, string)
                string = re.sub(r'\n[\s]*case .+\:', Instrument, string)
                string = re.sub(r'\n[\s]*default\s*:', Instrument, string)
                string = re.sub(r'\n[\s]*for\s*\(.+\)[\s\n]*{', Instrument, string)
                string = re.sub(r'\n[\s]*while\s*\(.+\)[\s\n]*{', Instrument, string)
                string = re.sub(r'\n[\s]*do[\s\n]*{', Instrument, string)
                with open(file, 'w') as f:
                    f.write(string)
    # Give each CodeCount a unique label, start from 0
    elif sys.argv[1] == '-l':
        label = Label()
        for path in sys.argv[2:]:
            for file in FindAllFiles(path):
                with open(file, 'r') as f:
                    string = f.read()
                string = re.sub(r'^CodeCount', label.AddLabel, string, flags=re.M)
                with open(file, 'w') as f:
                    # include CodeCoverageArray.h at the beginning of source code files
                    f.write('#include "CodeCoverageArray.h"\n')
                    f.write(string)
        print('Final label number: ', label.count+1)
    # Analyse and display the code coverage array
    elif sys.argv[1] == '-a':
        rawCovFile = sys.argv[2] 
        analyser = Analyser(rawCovFile)
        for path in sys.argv[3:]:
            for file in FindAllFiles(path):
                with open(file, 'r') as f:
                    string = f.read()
                analyser.SetPath(file)
                string = re.sub(r'^CodeCount\((\d+)\);', analyser.LocateResult, string, flags=re.M)
                with open(file, 'w') as f:
                    f.write(string)
        analyser.WriteCSV()
    # Clear execution information in the source code
    elif sys.argv[1] == '-c':
        for path in sys.argv[2:]:
            for file in FindAllFiles(path):
                with open(file, 'r') as f:
                    string = f.read()
                string = re.sub(r' NOT EXECUTED', ';', string)
                string = re.sub(r' EXECUTED', ';', string)
                with open(file, 'w') as f:
                    f.write(string)
    # Delete all CodeCounts and execution information from the source code
    elif sys.argv[1] == '-d':
        for path in sys.argv[2:]:
            for file in FindAllFiles(path):
                with open(file, 'r') as f:
                    string = f.read()
                string = re.sub(r'\nCodeCount\(\d*\);', '', string)
                string = re.sub(r'\nCodeCount\(\d*\) EXECUTED', '', string)
                string = re.sub(r'\nCodeCount\(\d*\) NOT EXECUTED', '', string)
                string = re.sub(r'#include \"CodeCoverageArray.h\"\n', '', string)
                with open(file, 'w') as f:
                    f.write(string)
    else:
        print('Error: please use')
        print('python3 pq9cov.py -i <path1> <path2> ... to instrument the code')
        print ('python3 pq9cov.py -l <path1> <path2> ... to add labels')
        print ('python3 pq9cov.py -a <coverage result> <path1> <path2> ... to analyse and display coverage result')
        print ('python3 pq9cov.py -c <path1> <path2> ... to clean the source code, i.e., just remove information like EXECUTED')
        print ('python3 pq9cov.py -d <path1> <path2> ... to delete all CodeCounts and information like EXECUTED in the source code')
