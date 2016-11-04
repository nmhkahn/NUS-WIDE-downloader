import os
import time
import argparse
import logging
import skimage.io
import numpy as np
from threading import Thread
from collections import defaultdict

MAX_RETRY = 3

def main( args ):
    
    logger = get_logger(args.log_dir)
    
    path = os.path.join(args.url_dir, "NUS-WIDE-urls.txt")
    fp = open(path, "r")
    fp.readline() # header
    
    junks = list()
    junks.append(skimage.io.imread("https://s.yimg.com/pw/images/en-us/photo_unavailable.png"))
    junks.append(skimage.io.imread("./junk.gif"))

    lines = list()
    line_counter = 2
    while True:
        line = fp.readline()
        if not line: break
        ctx = [line_counter, line]
        lines.append(ctx)
        line_counter += 1
    fp.close()

    threads  = [None] * args.num_threads
    counters = [defaultdict(lambda: 0)] * args.num_threads
    part = int(len(lines) / args.num_threads)
    
    t1 = time.time()
    for i in range(args.num_threads):
        # divide works
        start = part*i; end = part*(i+1)
        if i == args.num_threads-1:
            end = len(lines)

        threads[i] = Thread(target=download, 
            args=(lines[start:end], junks, counters[i], logger))
        threads[i].start()

    total = defaultdict(lambda: 0)

    for i in range(args.num_threads):
        threads[i].join()
        total["total"] += counters[i]["total"]
        total["weird"] += counters[i]["weird"]
        total["no_url"] += counters[i]["no_url"]
        total["na"] += counters[i]["na"]
    t2 = time.time()   

    logger.info("===========================================================")
    logger.info("Download image complete! ({0:.1f}s)" .format(t2-t1))
    logger.info("[total]: {0}, [weird]: {1}" 
        .format(total["total"], total["weird"])) 
    logger.info("[no_url]: {0}, [NA]: {1}"
        .format(total["no_url"], total["na"]))
    logger.info("===========================================================")


def download( urls,
              junks,
              counter,
              logger ):
    
    for ctx in urls:
        line_num, line = ctx[0], ctx[1]
        counter["total"] += 1
        
        try:
            name, id, _, url_m, _, _ = line.split()
        except:
            # format of line is wierd
            counter["weird"] += 1
            logger.info("[weird] line #{0}" .format(line_num))
            continue
    
        if url_m == "null":
            # there is no image url
            counter["no_url"] += 1
            logger.info("[no-url] line #{0}" .format(line_num))
            continue
        
        for i in range(MAX_RETRY):
            try:
                im = skimage.io.imread(url_m)
            except:
                continue
            break
        
        # check image is not available image or not
        is_na = False
        for junk in junks:
            if np.array_equal(junk, im): 
                is_na = True
                break
        if is_na:
            counter["na"] += 1
            logger.info("[NA] line #{0}" .format(line_num))
            continue

        im_dir, im_name = name.split("Flickr\\")[1].split("\\")
        if not os.path.exists(os.path.join(args.save_dir, im_dir)):
            os.makedirs(os.path.join(args.save_dir, im_dir))
        
        im_loc = os.path.join(im_dir, im_name)
        save_path = os.path.join(args.save_dir, im_loc)
        skimage.io.imsave(save_path, im)


def get_logger( log_dir ):
    
    path = os.path.join(log_dir, "log.txt")
    logger = logging.getLogger("logger")
    logger.addHandler(logging.FileHandler(path))
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    return logger


def parse_args():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_threads",
        type=int,
        default=1,
        help="Number of thread to run.")
    parser.add_argument("--url_dir",
        type=str,
        default="./",
        help="Dir which NUS-WIDE-urls file located. \
              (default is ./)")
    parser.add_argument("--save_dir",
        type=str,
        default="./image",
        help="Dir which images are saved. \
              (default is ./image)")
    parser.add_argument("--log_dir",
        type=str,
        default="./",
        help="Dir which log file is saved. \
              (default is ./)")
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
