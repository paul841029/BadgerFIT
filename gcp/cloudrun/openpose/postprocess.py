from argparse import ArgumentParser
from json import load, dump
from os import listdir, path, mkdir
from pprint import pprint
from subprocess import run


parser = ArgumentParser()
parser.add_argument('src', help="input_folder")

args = parser.parse_args()
run(["mkdir", "-p", path.join(args.src, 'processed_kp')])
for fn in listdir(args.src):
    if fn[-5:] == '.json': 
        with open(path.join(args.src, fn), 'r') as f:
            obj = load(f)
        people = obj['people']
        for idx, _ in enumerate(people):
            kp = people[idx]['pose_keypoints_2d']
            people[idx] = {}
            people[idx]['pose_keypoints'] = kp
        
        with open(path.join(args.src, 'processed_kp', fn), 'w') as f:
            dump(obj, f, indent=4)

run(" ".join(["cp", path.join(args.src, 'processed_kp', "*.json"), args.src]), shell=True)
run(["rm", "-r", path.join(args.src, 'processed_kp')])

