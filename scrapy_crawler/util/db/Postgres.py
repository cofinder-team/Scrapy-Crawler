# -*- coding: utf-8 -*-
import logging
import time
import psycopg2
from scrapy.utils import project


class PostgresClient(object):
    def __init__(self):
        self.settings = project.get_project_settings()
        self.host = self.settings.get('DB_HOST')
        self.port = self.settings.get('DB_PORT')
        self.user = self.settings.get('DB_USER')
        self.password = self.settings.get('DB_PASSWORD')
        self.database = self.settings.get('DB_DATABASE')
        self._conn()

    def _conn(self):
        while True:
            try:
                self.conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                break
            except Exception as e:
                logging.log(logging.WARNING, "Postgres connection failed, retrying...")
                logging.log(logging.WARNING, e)
                time.sleep(3)
                continue

    def getCursor(self):
        if not self.conn:
            self._conn()

        try:
            cur = self.conn.cursor()
        except:
            self._conn()
            cur = self.conn.cursor()
        return cur

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()