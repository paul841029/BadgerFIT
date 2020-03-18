#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 20:43:12 2019

Python 3.6.6 |Anaconda, Inc.| (default, Jun 28 2018, 11:07:29)

@author: pilgrim.bin@gmail.com
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import argparse

from tqdm import tqdm

import csv
import pickle as pk

import numpy as np
from PIL import Image
import cv2


# usage: mkdir_if_not_exist([root, dir])
def mkdir_if_not_exist(path):
    if not os.path.exists(os.path.join(*path)):
        os.makedirs(os.path.join(*path))


# return all type filepath of this path
def get_filelist(path):
    filelist = []
    for root,dirs,filenames in os.walk(path):
        for fn in filenames:
            filelist.append(os.path.join(root,fn))
    return filelist


def is_valid_3_images(packshot, premium, style):
    try:
        ps_key, ps_color, ps_style = packshot.split('_')
        pr_key, pr_color, pr_style = premium.split('_')
        st_key, st_color, st_style = style.split('_')
    except: # ValueError: too many values to unpack
        # zalando/dress/9fashion-davea-cs_shift-dress-grey-9f029f00n-c11_grey_PACKSHOT.jpg
        kk = packshot.split('_')
        ps_key, ps_color, ps_style = '_'.join(kk[:-2]), kk[-2], kk[-1]
        kk = premium.split('_')
        pr_key, pr_color, pr_style = '_'.join(kk[:-2]), kk[-2], kk[-1]
        kk = style.split('_')
        st_key, st_color, st_style = '_'.join(kk[:-2]), kk[-2], kk[-1]
    if not ((ps_key==pr_key) and (ps_key==st_key)):
        return False
    if not ((ps_color==pr_color) and (ps_color==st_color)):
        return False
    if not (('PACKSHOT' in ps_style) and ('PREMIUM' in pr_style) and ('STYLE' in st_style)):
        return False
    try:
        for filename in [packshot, premium, style]:
            img = Image.open(filename)
            img.convert("RGB")
    except: # IOError: cannot identify image file '*.jpg'
        print("Got Shit! = {}".format(filename))
        return False
    return True

height = 512*2
width = 352*2

def distance(p1, p2):
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def is_pose_valid(cocokps):
    thresh_ratio = 0.3
    i,j = 1,3
    da = distance((cocokps[2*i],cocokps[2*i+1]),(cocokps[2*j],cocokps[2*j+1]))
    i,j = 3,5
    db = distance((cocokps[2*i],cocokps[2*i+1]),(cocokps[2*j],cocokps[2*j+1]))
    if db < thresh_ratio * da:
        print('may no foot = {}'.format(cocokps))
        return False
    
    i,j = 0,2
    da = distance((cocokps[2*i],cocokps[2*i+1]),(cocokps[2*j],cocokps[2*j+1]))
    i,j = 2,4
    db = distance((cocokps[2*i],cocokps[2*i+1]),(cocokps[2*j],cocokps[2*j+1]))
    if db < thresh_ratio * da:
        print('may no foot = {}'.format(cocokps))
        return False
    
    return True


def get_premium_image(img, fkps, cocokps, fy1ratio, by2ratio):
    # process: zoom based on fashion_upper to body_down

    # fkps = [[449, 393, 1], [896, 427, 1], [414, 1158, 1], [934, 1154, 1]]
    # cocokps = [806, 615, 530, 608, 895, 1286, 590, 1293, 1007, 1949, 664, 1919]
    x1,y1,_= fkps[0]
    x2,y2,_= fkps[1]
    x3,y3,_= fkps[2]
    x4,y4,_= fkps[3]
    cocoy = (cocokps[2*4+1] + cocokps[2*5+1])/2
    src_oh = cocoy - (y1+y2)/2
    dst_oh = height * (by2ratio - fy1ratio)
    zoom_ratio = dst_oh / src_oh
    
    fh = int((y3+y4-y1-y2)/2. * zoom_ratio) # fashion height
    w,h = img.size
    
    #img.show()
    imgz = img.resize((int(w * zoom_ratio), int(h * zoom_ratio)), Image.ANTIALIAS)
    #imgz.show()
    
    # padding img
    imgcv = cv2.cvtColor(np.asarray(imgz),cv2.COLOR_RGB2BGR)
    padding = 1000
    imgcv = cv2.copyMakeBorder(imgcv, padding, padding, padding, padding, cv2.BORDER_REPLICATE, value=0)
    blur = cv2.GaussianBlur(imgcv,(21,21),0)
    blurpil = Image.fromarray(cv2.cvtColor(blur, cv2.COLOR_BGR2RGB))
    #blurpil.show()
    blurpil.paste(imgz, (1000,1000))
    #blurpil.show()
    
    # crop
    wshift = int((x1+x2)/2 * zoom_ratio - width/2)
    hshift = int((y1+y2)/2 * zoom_ratio - height*fy1ratio)
    box = (1000+wshift, 1000+hshift, width+1000+wshift, height+1000+hshift)
    crop = blurpil.crop(box) # (left, top, right, bottom)
    #crop.show()
    
    fh = (y3+y4-y1-y2)/2 * zoom_ratio
    return crop, fh



def get_packshot_image(img, fkps, fy1ratio, fh):
    x1,y1,_= fkps[0]
    x2,y2,_= fkps[1]
    x3,y3,_= fkps[2]
    x4,y4,_= fkps[3]
    dst_oh = fh
    src_oh = (y3+y4-y1-y2)/2
    zoom_ratio = dst_oh / src_oh
    w,h = img.size
    
    #img.show()
    imgz = img.resize((int(w * zoom_ratio), int(h * zoom_ratio)), Image.ANTIALIAS)
    #imgz.show()
    
    # padding img
    imgcv = cv2.cvtColor(np.asarray(imgz),cv2.COLOR_RGB2BGR)
    padding = 1000
    imgcv = cv2.copyMakeBorder(imgcv, padding, padding, padding, padding, cv2.BORDER_REPLICATE, value=0)
    blur = cv2.GaussianBlur(imgcv,(21,21),0)
    blurpil = Image.fromarray(cv2.cvtColor(blur, cv2.COLOR_BGR2RGB))
    #blurpil.show()
    blurpil.paste(imgz, (1000,1000))
    #blurpil.show()
    
    # crop
    wshift = int((x1+x2)/2 * zoom_ratio - width/2)
    hshift = int((y1+y2)/2 * zoom_ratio - height*fy1ratio)
    box = (1000+wshift, 1000+hshift, width+1000+wshift, height+1000+hshift)
    crop = blurpil.crop(box) # (left, top, right, bottom)
    #crop.show()
    
    return crop

# target crop size = wh = 704*1024
def make_hq_data(img, xys, yu, yd):
    height = 512*2
    width = 352*2

    w,h = img.size
    # coco point = [1,2,15,16]
    x1,y1 = xys[1]
    x2,y2 = xys[2]
    x15,y15 = xys[15]
    x16,y16 = xys[16]
    dst_oh = 1024 * (yd-yu)
    src_oh = (y15+y16-y1-y2)/2
    zoom_ratio = dst_oh / src_oh
    w,h = img.size
    
    #img.show()
    imgz = img.resize((int(w * zoom_ratio), int(h * zoom_ratio)), Image.ANTIALIAS)
    #imgz.show()
    
    # padding img
    imgcv = cv2.cvtColor(np.asarray(imgz),cv2.COLOR_RGB2BGR)
    padding = 1000
    imgcv = cv2.copyMakeBorder(imgcv, padding, padding, padding, padding, cv2.BORDER_REPLICATE, value=0)
    blur = cv2.GaussianBlur(imgcv,(21,21),0)
    blurpil = Image.fromarray(cv2.cvtColor(blur, cv2.COLOR_BGR2RGB))
    #blurpil.show()
    blurpil.paste(imgz, (1000,1000))
    #blurpil.show()
    
    # crop
    wshift = int((x1+x2)/2 * zoom_ratio - width/2)
    hshift = int((y1+y2)/2 * zoom_ratio - height*yu)
    box = (1000+wshift, 1000+hshift, width+1000+wshift, height+1000+hshift)
    crop = blurpil.crop(box) # (left, top, right, bottom)
    #crop.show()
    
    return crop


def is_feet_valid(xys):
    thresh_ratio = 0.3 # 0.2 seems too small, and those conditions is not enough.
    i,j = 11,13
    da = distance(xys[i],xys[j])
    i,j = 13,5
    db = distance(xys[i],xys[j])
    if db < thresh_ratio * da:
        print('may no foot = {}'.format(xys))
        return False
    
    i,j = 11,13
    da = distance(xys[i],xys[j])
    i,j = 13,15
    db = distance(xys[i],xys[j])
    if db < thresh_ratio * da:
        print('may no foot = {}'.format(xys))
        return False
    
    return True


def result_verbose():
    filename = 'data/test_pairs.txt'
    filelist = open(filename).readlines()
    
    paths_dict = {'data/test/cloth' : 1,
                  'data/test/cloth-mask' : 1,
                  'data/test/image' : 0,
                  'data/test/image-parse' : 0, # png
                  #'data/test/pose' : 0, # NA
                  'result/gmm_final.pth/test/warp-cloth' : 1,
                  'result/gmm_final.pth/test/warp-mask' : 1,
                  'result/tom_final.pth/test/try-on' : 0,
                  }
    
    width = 192
    height = 256
    nimgs = len(paths_dict.keys())
    for fn in tqdm(filelist):
        src, dst = fn.strip().split(' ')
        src = src.split('_')[0] # '019590_0.jpg'
        dst = dst.split('_')[0] # '012964_1.jpg'
        paddingimgs = Image.fromarray(np.zeros((height*2, width * nimgs,3)), mode='RGB')
        i = 0
        for path in paths_dict.keys():
            imgname = os.path.join(path, src + "_{}.jpg".format(paths_dict[path]))
            if 'image-parse' in path:
                imgname = os.path.join(path, src + "_{}.png".format(paths_dict[path]))
            img = Image.open(imgname).convert('RGB')
            #img.show()
            paddingimgs.paste(img, (width*i, 0))
            i += 1
        i = 0
        for path in paths_dict.keys():
            imgname = os.path.join(path, dst + "_{}.jpg".format(paths_dict[path]))
            if 'image-parse' in path:
                imgname = os.path.join(path, dst + "_{}.png".format(paths_dict[path]))
            img = Image.open(imgname).convert('RGB')
            #img.show()
            paddingimgs.paste(img, (width*i, height))
            i += 1
        #paddingimgs.show()
        paddingimgs.save('result_verbose/src_{}_dst_{}.png'.format(src, dst))


def result_simple():
    filename = 'data/test_pairs.txt'
    filelist = open(filename).readlines()
    
    paths_dict = {'data/test/cloth' : 1,
                  'data/test/cloth-mask' : 1,
                  'data/test/image' : 0,
                  'data/test/image-parse' : 0, # png
                  #'data/test/pose' : 0, # NA
                  'result/gmm_final.pth/test/warp-cloth' : 1,
                  'result/gmm_final.pth/test/warp-mask' : 1,
                  'result/tom_final.pth/test/try-on' : 0,
                  }
    
    width = 192
    height = 256
    nimgs = len(paths_dict.keys())
    for fn in tqdm(filelist):
        src, dst = fn.strip().split(' ')
        src = src.split('_')[0] # '019590_0.jpg'
        dst = dst.split('_')[0] # '012964_1.jpg'
        paddingimgs = Image.fromarray(np.zeros((height, width * nimgs,3)), mode='RGB')
        i = 0
        for path in paths_dict.keys():
            if i in [0,1,4,5]:
                fn = dst
            else:
                fn = src
            imgname = os.path.join(path, fn + "_{}.jpg".format(paths_dict[path]))
            if 'image-parse' in path:
                imgname = os.path.join(path, fn + "_{}.png".format(paths_dict[path]))
            img = Image.open(imgname).convert('RGB')
            #img.show()
            paddingimgs.paste(img, (width*i, 0))
            i += 1
        '''
        i = 0
        for path in paths_dict.keys():
            imgname = os.path.join(path, dst + "_{}.jpg".format(paths_dict[path]))
            if 'image-parse' in path:
                imgname = os.path.join(path, dst + "_{}.png".format(paths_dict[path]))
            img = Image.open(imgname).convert('RGB')
            #img.show()
            paddingimgs.paste(img, (width*i, height))
            i += 1
        '''
        #paddingimgs.show()
        paddingimgs.save('result_simple/src_{}_dst_{}.png'.format(src, dst))



if __name__ == '__main__':
    '''
    fuc = 'result_verbose'
    mkdir_if_not_exist([fuc])
    result_verbose()
    '''
    
    fuc = 'result_simple'
    mkdir_if_not_exist([fuc])
    result_simple()



if 0: # __name__ == '__main__':
    parser = argparse.ArgumentParser(description='python main.py --srcpath=srcpath')
    parser.add_argument("--srcpath", default='dress', type=str)
    args = parser.parse_args()
    srcpath = args.srcpath
    
    # input = srcpath, 'coco_keypoints_dress_6.txt', ==> output = alligned data
    # (0.8737130034184978 + 0.8725514402694093)/2 = 0.8731322218439536 = 0.873
    # (0.11956478391510636 + 0.10249740025997915 + 0.10232775845615594)/3 = 0.10812998087708048 = 0.108
    
    '''--------------------------------------'''
    
    dstfoler = srcpath + '_hq'
    mkdir_if_not_exist([dstfoler])
    dstfoler_invalid = srcpath + '_hq_invalid'
    mkdir_if_not_exist([dstfoler_invalid])
    
    # load coco kp data as cocokp_dict
    filename = 'coco_keypoints_dress_6.txt'
    lines = open(filename).readlines()
    cocokp_dict = {}
    for line in lines:
        vals = line.strip().split(' ')
        fn = vals[0]
        kp = vals[1:]
        cocokp_dict[fn] = kp
    
    # scanning all the paires
    yu, yd = 0.108, 0.873 # upper y, down y
    for fn in tqdm(cocokp_dict.keys()):
        if 'STYLE' in fn or 'PREMIUM' in fn: # 'PACKSHOT','PREMIUM'  'STYLE'
            fnshow = fn
            img = Image.open(os.path.join(srcpath, fnshow)).convert('RGB')
            #img.show()
            w,h = img.size
            vals = cocokp_dict[fnshow]
            xys = [(int(vals[2*i]),int(vals[2*i+1])) for i in range(len(vals)//2)]
            imghq = make_hq_data(img, xys, yu, yd)
            #imghq.show()
            if is_feet_valid(xys):
                save_fn = os.path.join(dstfoler, fn)
                imghq.save(save_fn)
            else:
                save_fn = os.path.join(dstfoler_invalid, fn)
                imghq.save(save_fn)
            

    aazz
    
    # load coco kp data as cocokp_dict
    filename = 'coco_keypoints_skirt_6.txt'
    lines = open(filename).readlines()
    cocokp_dict = {}
    for line in lines:
        vals = line.strip().split(' ')
        fn = vals[0]
        kp = vals[1:]
        cocokp_dict[fn] = kp
    
    # cocokp_dict --> filename_paires
    filename_paires = []
    for fn in cocokp_dict.keys():
        if 'PACKSHOT' in fn:
            fnp = fn.replace('PACKSHOT','PREMIUM')
            if cocokp_dict.get(fnp) is not None:
                filename_paires.append((fn,fnp))
    print('len(filename_paires) = {}'.format(len(filename_paires)))
    
    
    # load fashion keypoints
    filename = 'kp_skirt_fashionai.csv'
    csv_reader = csv.reader(open(filename))
    csv_lines = [line for line in csv_reader]
    header = csv_lines[0]
    fnidx = header.index('image_id')
    kp1 = header.index('waistband_left')
    kp2 = header.index('waistband_right')
    kp3 = header.index('hemline_left')
    kp4 = header.index('hemline_right')
    fashionkp_dict = {}
    for line in csv_lines[1:]:
        filename = line[fnidx]
        kp1s = [int(v) for v in line[kp1].split('_')]
        kp2s = [int(v) for v in line[kp2].split('_')]
        kp3s = [int(v) for v in line[kp3].split('_')]
        kp4s = [int(v) for v in line[kp4].split('_')]
        fashionkp_dict[os.path.split(filename)[-1]] = [kp1s, kp2s, kp3s, kp4s]
    print('len(fashionkp_dict) = {}'.format(len(fashionkp_dict)))
    
    # scanning all the paires
    for fns in tqdm(filename_paires):
        fna,fnb = fns
        fkpsa = fashionkp_dict[fna]
        fkpsb = fashionkp_dict[fnb]
        vals = cocokp_dict[fnb]
        vals = [int(v) for v in vals]
        
        cocokps = vals
        imga = Image.open(os.path.join(srcpath, fna)).convert('RGB')
        imgb = Image.open(os.path.join(srcpath, fnb)).convert('RGB')
        fy1ratio = 0.1 # fashion y1-upside position point mean position ratio
        # fashion_ymiu = 0.09027145875866845
        by2ratio = 0.84 # body y2-downside positon
        # body_ymiu = 0.8392617355983812
        imgb, fh = get_premium_image(imgb, fkpsb, cocokps, fy1ratio, by2ratio)
        imga = get_packshot_image(imga, fkpsa, fy1ratio, fh)
        
        image = Image.new(imga.mode, (width*2, height))
        image.paste(imga, (0,0,width,height))
        image.paste(imgb, (width,0,width*2,height))
        
        paired_filename = os.path.split(fnb)[-1].replace('PREMIUM', 'PR-ST')
        if is_pose_valid(cocokps):
            image.save(os.path.join(dstfoler, paired_filename))
        else:
            image.save(os.path.join(dstfoler_invalid, paired_filename))
        
    '''---------------------------------------------'''

    '''
    a = [(i,2**i) for i in range(12)]
    
    [(0, 1),
     (1, 2),
     (2, 4),
     (3, 8),
     (4, 16),
     (5, 32),
     (6, 64),
     (7, 128),
     (8, 256),
     (9, 512),
     (10, 1024),
     (11, 2048)]
    
    a = [(i,32*i) for i in range(50)]
    
    [(0, 0),
     (1, 32),
     (2, 64),
     (3, 96),
     (4, 128),
     (5, 160),
     (6, 192),
     (7, 224),
     (8, 256),
     (9, 288),
     (10, 320),
     (11, 352),
     (12, 384),
     (13, 416),
     (14, 448),
     (15, 480),
     (16, 512),
     (17, 544),
     (18, 576),
     (19, 608),
     (20, 640),
     (21, 672),
     (22, 704),
     (23, 736),
     (24, 768),
     (25, 800),
     (26, 832),
     (27, 864),
     (28, 896),
     (29, 928),
     (30, 960),
     (31, 992),
     (32, 1024),
     (33, 1056),
     (34, 1088),
     (35, 1120),
     (36, 1152),
     (37, 1184),
     (38, 1216),
     (39, 1248),
     (40, 1280),
     (41, 1312),
     (42, 1344),
     (43, 1376),
     (44, 1408),
     (45, 1440),
     (46, 1472),
     (47, 1504),
     (48, 1536),
     (49, 1568)]

    '''
    
    
