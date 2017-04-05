#!/usr/bin/env python3

import collections
import subprocess
import argparse
import os.path
import os


# Taken from here:
#     http://stackoverflow.com/a/1094933
def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            # return "%3.1f%s%s" % (num, unit, suffix)
            return "{:3.1f} {}{}".format(num, unit, suffix)
        num /= 1024.0
    # return "%.1f%s%s" % (num, 'Yi', suffix)
    return "{:.1f} {}{}".format(num, 'Yi', suffix)


class Picture(object):
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.size = os.stat(path).st_size
        self.size_str = sizeof_fmt(self.size)


class Comparison(object):
    """Comparisons of different levels of compression for a single photo."""

    def __init__(self, pictures):
        self.pictures = pictures

    def print_rowonly(self):
        rv = "<div class='row'>\n"
        for p in self.pictures:
            cell = "<div class='cell'><p>{}</p><a href='{}'><img src='{}'></a></div>\n".format(
                p.size_str, p.path, p.path)
            rv += cell
        rv += "</div>\n"
        return rv
    # Method to print an html table to be added


def render_markdown(md):
    '''Calls out to pandoc to render markdown. '''
    args = ['pandoc', '-f', 'markdown', '-t', 'html']
    pandoc = subprocess.Popen(
        args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    output = pandoc.communicate(input=md)[0]
    return output


def create_compare_page(output_dir):
    good_images = [
        "2016-07-01_21.32.38.jpg",  # Baseball game
        "2016-07-02_14.09.22.jpg",  # Tomatoes
        "2016-07-03_14.04.36.jpg",  # Backyard
        "2016-07-03_21.39.05.jpg",  # Campfire
        "2016-07-06_18.50.25.jpg",  # Plums
        "2016-07-07_14.58.23.jpg",  # Lake
        "2016-07-08_10.32.01.jpg",  # Canadian bike shop
        "2016-07-16_20.14.09.jpg",  # Crowd at Phish
        "2016-07-20_19.41.00.jpg",  # Seattle
        "2016-07-23_18.47.01.jpg",  # Ducks
        "2016-07-23_19.12.55.jpg",  # Fremont
    ]
    img_directories = [
        "month_07",
        "month_07_compressed_80",
        "month_07_compressed_60",
        "month_07_compressed_40",
    ]
    # img_directories = [os.path.abspath(d) for d in img_directories]
    comparisons = []
    for img in good_images:
        pictures = []
        name = img
        for d in img_directories:
            source = os.path.join(d, img)
            pic = Picture(name, source)
            # Create the directories mirroring the filestructure here, but in
            # the output directory
            img_output_dir = os.path.join(output_dir, d)
            if not os.path.exists(img_output_dir):
                os.makedirs(img_output_dir)
            # Symlink our file to the output directory, if there isn't a symlink already
            if not os.path.exists(os.path.join(output_dir, source)):
                os.symlink(
                    os.path.abspath(source), os.path.join(output_dir, source))
            pictures.append(pic)
        comp = Comparison(pictures)
        comparisons.append(comp)
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
    table = '<div class="lfbtable">'
    table += '''
<div class='row'>
    <div class='cell'><h1>Original</h1></div>
    <div class='cell'><h1>80% quality</h1></div>
    <div class='cell'><h1>60% quality</h1></div>
    <div class='cell'><h1>40% quality</h1></div>
</div>
    '''
    for comp in comparisons:
        table += comp.print_rowonly()
    table += "</div>"

    copy = ""
    with open('copy.md') as c:
        copy = render_markdown(c.read())

    rv = ""
    with open('style.css') as style:
        rv = page.format(style.read(), copy, table)
    return rv


def main():
    output_dir = "/home/leland/scrap/jpeg_compress_test/comparisons"
    html = create_compare_page(output_dir)
    page_path = os.path.join(output_dir, "index.html")
    with open(page_path, 'w+') as page:
        page.write(html)


main()
