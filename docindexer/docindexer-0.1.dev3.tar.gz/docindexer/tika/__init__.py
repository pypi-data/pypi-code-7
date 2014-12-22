# -*- coding: utf-8 -*-

import os
import json
import logging
import subprocess

logger = logging.getLogger(__name__)

JAR_PATH = os.path.join(os.path.dirname(__file__), "tika-app.jar")


def get_content(filepath):
    """Returns document plain-text content"""
    logger.debug("Getting plain-text content from %s with Tika", filepath)
    args = ['java', '-jar', JAR_PATH, '--text', filepath]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if err:
        logger.error(err)
    text = out
    return text

def get_metadata(filepath):
    """Returns a dict containing document metadata"""
    logger.debug("Getting json metadata from %s with Tika", filepath)
    args = ['java', '-jar', JAR_PATH, '--json', filepath]
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE)
    out, err = proc.communicate()
    if err:
        logger.error(err)
    metadata = json.loads(out)
    return metadata