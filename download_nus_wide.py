import os
import argparse
import logging
import skimage.io
import numpy as np
from collections import defaultdict

def main( args ):
    
    logger = get_logger(args.log_dir)
    counter = defaultdict(lambda: 0)
    
    path = os.path.join(args.url_dir, "NUS-WIDE-urls.txt")
    fp = open(path, "r")
    fp.readline() # header
    
    junk = skimage.io.imread(args.junk_file)
    while True:
        line = fp.readline()
        if not line: break
        counter["total"] += 1
        
        try:
            name, id, _, url_m, _, _ = line.split()
        except:
            # format of line is wierd
            counter["weird"] += 1
            logger.info("[weird] @ line# {0}" .format(counter["total"]))
            continue
    
        if url_m == "null":
            # there is no image url
            counter["no_url"] += 1
            logger.info("[null] @ line# {0}" .format(counter["total"]))
            continue
        
        """        
        Only save large image. So missing image is around 10,000
        """
        im = skimage.io.imread(url_m)
        if np.array_equal(junk, im): 
            logger.info("[NA] @ line# {0}" .format(counter["total"]))
            continue
        im_dir, im_name = name.split("Flickr\\")[1].split("\\")
        
        if not os.path.exists(os.path.join(args.save_dir, im_dir)):
            os.makedirs(os.path.join(args.save_dir, im_dir))
        im_loc = os.path.join(im_dir, im_name)
        save_path = os.path.join(args.save_dir, im_loc)
        skimage.io.imsave(save_path, im)
    
    fp.close()


def get_logger( log_dir ):
    
    path = os.path.join(log_dir, "log.txt")
    logger = logging.getLogger("logger")
    logger.addHandler(logging.FileHandler(path))
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)

    return logger


def parse_args():
    
    parser = argparse.ArgumentParser()
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
    parser.add_argument("--junk_file",
        type=str,
        default="junk.jpg",
        help="Junk image path to match wheter cralwed image is junk or not")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
