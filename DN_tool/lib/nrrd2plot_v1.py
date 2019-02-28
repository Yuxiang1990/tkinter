import nibabel as nib
import nrrd
import numpy as np
from skimage.measure import find_contours, label, regionprops
import cv2
import os
import argparse


def parse_args():
    description = ("Diannei AI instructions: this system can be used for lung nodule detection")

    parser = argparse.ArgumentParser(description=description)

    parser.add_argument('-nrrd', '--nrrd',
                        help='nrrd input, mask')

    parser.add_argument('-nii', '--nii',
                        help='nii input, img')

    parser.add_argument('-o', '--output',
                        help='json_file must be provited')
    args = parser.parse_args()
    return args


def nrrd2nii(nrrd_path, nii_path):
    nrrd_file = nrrd.read(nrrd_path)
    nrrd_img = nrrd_file[0]
    nrrdxyz = nrrd_img.shape
    try:
        offx, offy, offz = nrrd_file[1]['keyvaluepairs']['Segmentation_ReferenceImageExtentOffset'].split(" ")
    except:
        offx, offy, offz = nrrd_file[1]['Segmentation_ReferenceImageExtentOffset'].split(" ")
    # print(nrrd_img)
    offx = int(float(offx) + 0.5)
    offy = int(float(offy) + 0.5)
    offz = int(float(offz) + 0.5)

    # arr
    nii_img = nib.load(nii_path)
    nii_data = nii_img.get_data()
    sizexyz = nii_data.shape
    spacezyx = nii_img.header['pixdim'][1:4][::-1]
    raw = np.transpose(nii_data, (2, 1, 0))
    # mask
    new_nrrd_img = np.zeros_like(nii_data)
    # print(nrrd_img)
    new_nrrd_img[offx: offx + nrrdxyz[0], offy: offy + nrrdxyz[1], offz: offz + nrrdxyz[2]] = nrrd_img
    mask = np.transpose(new_nrrd_img, axes=(2, 1, 0))
    return mask, raw, spacezyx


def _crop(raw, mask, win=[-1000, 400]):
    props = regionprops(label(mask))
    """
    get crop size
    """
    tmp = regionprops(mask)[0]['bbox']
    d = max(tmp[3]-tmp[0], tmp[4]-tmp[1], tmp[5]-tmp[2])
    d = d // 2 * 2 + 2
    cs = max(d, 96)

    centerzyx = np.array(props[0]['centroid']) + 0.5
    centerzyx = centerzyx.astype(np.int)
    raw_win = np.clip(raw, win[0], win[1])
    shapez, shapey, shapex = mask.shape
    cz, cy, cx = centerzyx
    crop_raw = raw_win[max(0, cz - cs // 2):min(cz + cs //2, shapez),
                       max(0, cy - cs // 2):min(cy + cs //2, shapey),
                       max(0, cx - cs // 2):min(cx + cs //2, shapex)]

    crop_mask = mask[max(0, cz - cs // 2):min(cz + cs //2, shapez),
                       max(0, cy - cs // 2):min(cy + cs //2, shapey),
                       max(0, cx - cs // 2):min(cx + cs //2, shapex)]

    padding_left = []
    padding_right = []
    for i in [cz, cy, cs]:
        left = i - cs // 2
        if left < 0:
            padding_left.append(np.abs(left))
        else:
            padding_left.append(0)

    for i, j in zip([cz, cy, cs], mask.shape):
        right = i + cs // 2 - j
        if right > 0:
            padding_right.append(np.abs(right))
        else:
            padding_right.append(0)

    crop_raw_pad = np.pad(crop_raw, ((padding_left[0], padding_right[0]),
                                    (padding_left[1], padding_right[1]),
                                    (padding_left[2], padding_right[2])), "minimum")

    crop_mask_pad = np.pad(crop_mask, ((padding_left[0], padding_right[0]),
                                    (padding_left[1], padding_right[1]),
                                    (padding_left[2], padding_right[2])), "minimum")

    """
    assert
    """
    pad = np.sum(padding_left) + np.sum(padding_right)
    assert crop_raw_pad.shape == (cs, cs, cs)
    assert crop_mask_pad.shape == (cs, cs, cs)
    # print(crop_raw_pad.shape, crop_mask_pad.shape, pad)
    return crop_raw_pad, crop_mask_pad, pad, cs

def normalize_hu(image):
    MIN_BOUND = -1000.0
    MAX_BOUND = 400.0
    image = (image - MIN_BOUND) / (MAX_BOUND - MIN_BOUND)
    image[image > 1] = 1.
    image[image < 0] = 0.
    return (image*255).astype(np.uint8)


def _plot(crop_raw, crop_mask, pad, title, outpath, crop_size):
    path = os.path.join(outpath, title + str(pad) + ".png")
    mask_indexes = np.where(crop_mask.sum(axis=(1,2)))[0]
    w = int(np.sqrt(len(mask_indexes))) + 1
    png = np.zeros((crop_size * w, ) * 2 + (3,))
    for index, mask_i in enumerate(mask_indexes):
        divide, remain = np.divmod(index, w)
        img = cv2.cvtColor(normalize_hu(crop_raw[mask_i]), cv2.COLOR_GRAY2BGR)
        contours = find_contours(crop_mask[mask_i], level=0.5)
        contours = [c.astype(np.int)[:, [1, 0]] for c in contours]
        cv2.drawContours(img, contours, -1, (0,255,0), thickness=1)
        png_w = divide * crop_size
        png_h = remain * crop_size
        png[png_w:png_w + crop_size, png_h:png_h+crop_size] = img
    cv2.imwrite(path, png)
    return png


def nrrd_draw(img_path, mask_path, out):
    mask, raw, spacezyx = nrrd2nii(mask_path, img_path)
    crop_raw_pad, crop_mask_pad, pad, cropsize = _crop(raw, mask)
    title = os.path.basename(mask_path)
    png = _plot(crop_raw_pad, crop_mask_pad, pad, title, out, cropsize)
    return png


if __name__ == "__main__":
    args = parse_args()
    mask, raw, spacezyx = nrrd2nii(args.nrrd, args.nii)
    crop_raw_pad, crop_mask_pad, pad, cropsize = _crop(raw, mask)
    title = os.path.basename(args.nrrd)
    png = _plot(crop_raw_pad, crop_mask_pad, pad, title, args.output, cropsize)

