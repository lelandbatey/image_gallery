import subprocess
import argparse
import os.path
import os


class Picture(object):
    '''Picture represents the portions of a picture we're interested in.'''

    def __init__(self, name, diskpath, relpath, thumbpath):
        self.name = name
        self.diskpath = diskpath
        self.relpath = relpath
        self.thumbpath = thumbpath


def make_thumbnail(diskpath, thumbfolder, maxsize=800):
    '''Takes the path to an image on disk and the path to the output thumbnail
    folder and creates a thumbnail image in the thumbnail directory. If the
    thumbnail directory doesn't exist, it's created.'''
    if not os.path.exists(thumbfolder):
        os.makedirs(thumbfolder)
    # Use imagemagick for thumbnail creation
    thumbpath = os.path.join(
        os.path.abspath(thumbfolder), os.path.basename(diskpath))
    args = ['convert', "'{}'".format(diskpath),
            '-resize 800x800^ -gravity Center -crop 800x800+0+0 ', '-quality',
            '80', "'{}'".format(thumbpath)]
    if os.path.exists(thumbpath):
        print("Thumbnail path '{}' already exists, skipping".format(thumbpath))
        return thumbpath
    os.system(" ".join(args))
    return thumbpath


def link_image(diskpath, output_dir):
    '''Creates a symbolic link in the output_dir pointing to the diskpath. The
    name of the symbolic link is the basename of the diskpath.'''
    source = os.path.abspath(diskpath)
    dest = os.path.join(output_dir, os.path.basename(diskpath))
    if os.path.exists(dest):
        print("Symlink '{}' already exists, skipping".format(dest))
        return dest
    os.symlink(source, dest)
    return dest


def group_rows(pictures):
    rv = ""
    cells = []
    for pic in pictures:
        cell = "<div class='cell'><p>{}</p><a href='{}'><img src='{}'></a></div>".format(
            pic.name, pic.relpath, pic.thumbpath)
        cells.append(cell)
    rv = "\n".join(cells)
    return rv


def create_page(images, output_dir):
    thumbfolder = os.path.join(os.path.abspath(output_dir), "thumbnails")
    pictures = []
    for img in images:
        abs_thumbpath = make_thumbnail(img, thumbfolder)
        rel_thumbpath = os.path.relpath(abs_thumbpath, output_dir)
        # relpath is the path to the full-resolution image, relative to the
        # output directory. Will point to a symlink, usually.
        fullres_link = link_image(img, output_dir)
        relpath = os.path.relpath(fullres_link, output_dir)
        pic = Picture("", os.path.abspath(img), relpath, rel_thumbpath)
        pictures.append(pic)

    page = """<!DOCTYPE html>
<html>
<style type="text/css">
{}
</style>
<body>
<div class='copy'>
{}
</div>
{}
</body>
</html>"""
    table = '<div class="lfbtable">{}\n</div>'
    rows = group_rows(pictures)
    table = table.format(rows)

    rv = ""
    with open('style.css') as style:
        rv = page.format(style.read(), "", table)

    with open(os.path.join(output_dir, 'index.html'), 'w+') as index:
        index.write(rv)

    return rv


def main():
    parser = argparse.ArgumentParser(
        description='Create a web-page with nice tiled links to all the images provided.'
    )
    parser.add_argument('--destdir', type=str, default="./gallery/")
    parser.add_argument('images', type=str, nargs='+')
    args = parser.parse_args()

    _ = create_page(args.images, args.destdir)


if __name__ == '__main__':
    main()
