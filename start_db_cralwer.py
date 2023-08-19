#!/usr/bin/python
import sys

from scrapy import cmdline

cmdline.execute(f"scrapy crawl {sys.argv[1]}".split())
