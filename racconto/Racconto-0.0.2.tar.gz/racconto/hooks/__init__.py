from datetime import datetime as d
from distutils.dir_util import copy_tree
import os

from racconto.generator import Generator
from racconto.settings_manager import SettingsManager as SETTINGS

def generate_archive(pages, posts):
    """
    Generate archive from posts. Assumes posts have been generated (i.e directories)
    posts - a sorted list of Post objects
    """
    # Dict with nested dicts: {year: {month: {day: [list, of, posts] } }
    archive = {}
    for post in posts:
        timestamp = post.date.isoformat()
        year = post.date.strftime("%Y")
        month = post.date.strftime("%m")
        day = post.date.strftime("%d")

        # Setup data structures
        if year not in archive:
            archive[year] = {}
        if month not in archive[year]:
            archive[year][month] = {}
        if day not in archive[year][month]:
            archive[year][month][day] = []
        # Populate with post
        archive[year][month][day].append(post)

    year_template = SETTINGS.get("YEAR_TEMPLATE")
    month_template = SETTINGS.get("MONTH_TEMPLATE")
    day_template = SETTINGS.get("DAY_TEMPLATE")

    BLOGDIR = SETTINGS.get('BLOGDIR')
    for year in archive:
        path = "%s/%s" % (BLOGDIR, year)
        Generator.generate_index_file(path, year_template, **{"post_dict": archive[year], "year": year})
        for month in archive[year]:
            path = "%s/%s/%s" % (BLOGDIR, year, month)
            Generator.generate_index_file(path, month_template, **{"post_dict": archive[year][month], "year": year, "month": month})
            for day in archive[year][month]:
                path = "%s/%s/%s/%s" % (BLOGDIR, year, month, day)
                Generator.generate_index_file(path, day_template, **{"post_list": archive[year][month][day], "year": year, "month": month, "day": day})

def copy_static_files(*args):
    """Copy static files and move favicon and apple-touch-icon to site root
    """
    TEMPLATEDIR = SETTINGS.get('TEMPLATEDIR')
    STATICDIR = SETTINGS.get('STATICDIR')
    SITEDIR = SETTINGS.get('SITEDIR')
    static_site = "%s/%s" % (SITEDIR, STATICDIR)

    copy_tree(STATICDIR, static_site)
    try:
        os.rename("%s/favicon.ico" % static_site, "%s/favicon.ico" % SITEDIR)
        os.rename("%s/apple-touch-icon.png" % static_site,
                  "%s/apple-touch-icon.png" % SITEDIR)
    except OSError, e:
        print "[Warning] Could not copy favicon and apple-touch-icon."

# FIXME consolidate these two methods
def generate_blog_index_file_10(pages, posts):
    """Creates an index file with the 10 latest blog posts
    """
    SITEDIR = SETTINGS.get('SITEDIR')
    Generator.generate_index_file(SITEDIR, "index.html", **{"post_list": posts[0:10]})

def generate_blog_index_file(pages, posts):
    # FIXME make this a bit more flexible
    BLOGDIR = SETTINGS.get('BLOGDIR')
    TEMPLATE = SETTINGS.get('BLOG_INDEX_TEMPLATE')
    Generator.generate_index_file(BLOGDIR, TEMPLATE, **{"post_list": posts[0:5]})
