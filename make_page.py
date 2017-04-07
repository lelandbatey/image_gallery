#! /usr/bin/env python3
import subprocess
import argparse
import os.path
import os

css = '''
body {
    font-family: helvetica, arial, freesans, clean, sans-serif;
    font-size: 18px;
    color: #222;
    background-color: lightgrey;
}
.lfbtable {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-around;
}

.row {
    display: flex;
    flex-direction: row;
}

.cell {
    max-width: 24.9%;
    max-height: 24.9%;
    width: auto;
    height: auto;
    background-position: center center;
    background-repeat: no-repeat;
    background-size: cover;
    overflow: hidden;
    transition: .2s ease opacity;
}

.cell > p {
    margin-bottom: 0;
}

img {
    max-width: 100%;
    display: block;
    padding-bottom: 2px;
}

.cell:hover {
    opacity: 0.8;
}
.cell:hover:after {
    opacity: 1;
}

.copy {
    font-size: 1.2rem;
}

h1 {
    font-size: 1.8rem;
    margin-bottom: 0.63rem;
}

h2 {
    font-size: 1.6rem;
    margin-bottom: 0.86rem;
}

h3 {
    font-size: 1.4rem;
}

h4 {
    font-size: 1.2rem;
}
@media screen and (max-width: 990px) {
    .cell {
        max-width: 33.15%;
        max-height: 33.15%;
    }
}
@media screen and (max-width: 640px) {
    .cell {
        max-width: 49.9%;
        max-height: 49.9%;
    }
}
'''


class Picture(object):
    '''Picture represents the portions of a picture we're interested in.'''

    def __init__(self, name, diskpath, relpath, thumbpath):
        self.name = name
        self.diskpath = diskpath
        self.relpath = relpath
        self.thumbpath = thumbpath


def make_thumbnail(diskpath, thumbfolder, maxsize=640):
    '''Takes the path to an image on disk and the path to the output thumbnail
    folder and creates a thumbnail image in the thumbnail directory. If the
    thumbnail directory doesn't exist, it's created.'''
    if not os.path.exists(thumbfolder):
        os.makedirs(thumbfolder)
    # Use imagemagick for thumbnail creation
    thumbpath = os.path.join(
        os.path.abspath(thumbfolder), os.path.basename(diskpath))
    resize_opts = '-resize {size}x{size}^ -gravity Center -crop {size}x{size}+0+0 '.format(
        size=maxsize)
    args = ['convert', "'{}'".format(diskpath), resize_opts, '-quality', '60',
            "'{}'".format(thumbpath)]
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

def render_markdown(md):
    '''Calls out to pandoc to render markdown. '''
    args = ['pandoc', '-f', 'markdown', '-t', 'html']
    pandoc = subprocess.Popen(
        args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)
    output = pandoc.communicate(input=md)[0]
    return output

def group_rows(pictures):
    rv = ""
    cells = []
    for pic in pictures:
        cell = "<div class='cell'><a href='{}'><img src='{}'></a></div>".format(
            pic.relpath, pic.thumbpath)
        cells.append(cell)
    rv = "\n".join(cells)
    return rv


def create_page(images, output_dir, copy_path):
    '''Create_page accepts a list of paths to images and the location of the
    directory to place the gallery within. Each image must have an extension of
    one of the following:
        .jpg
        .jpeg
        .png
        .gif
    Any file that lacks those extensions will be ignored.
    '''
    thumbfolder = os.path.join(os.path.abspath(output_dir), "thumbnails")
    pictures = []

    accepted_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    images = [img for img in images if img.endswith(
        tuple(accepted_extensions))]
    for idx, img in enumerate(images):
        abs_thumbpath = make_thumbnail(img, thumbfolder)
        rel_thumbpath = os.path.relpath(abs_thumbpath, output_dir)
        # relpath is the path to the full-resolution image, relative to the
        # output directory. Will point to a symlink, usually.
        fullres_link = link_image(img, output_dir)
        relpath = os.path.relpath(fullres_link, output_dir)
        pic = Picture("", os.path.abspath(img), relpath, rel_thumbpath)
        pictures.append(pic)

        print("{}% complete\r".format(int(100 * (idx / len(images)))), end="")
    print()

    body_md = ""
    if copy_path and os.path.exists(copy_path):
        with open(copy_path) as c:
            body_md = render_markdown(c.read())
    if copy_path and not os.path.exists(copy_path):
        print("The provided path '{}' to a markdown file for the body text does not exist".format(copy_path))


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
    rv = page.format(css, body_md, table)

    with open(os.path.join(output_dir, 'index.html'), 'w+') as index:
        index.write(rv)

    return rv


def main():
    parser = argparse.ArgumentParser(
        description='Create a web-page with nice tiled links to all the images provided.'
    )
    parser.add_argument('--destdir', type=str, default="./gallery/")
    parser.add_argument('--bodymarkdown', type=str, help='Location of markdown file to use for the body text.')
    parser.add_argument('images', type=str, nargs='+')
    args = parser.parse_args()

    _ = create_page(args.images, args.destdir, args.bodymarkdown)


if __name__ == '__main__':
    main()
