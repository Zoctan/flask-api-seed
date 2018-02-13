#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

setting = 'charset=utf8'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or \
                 'the quick brown fox jumps over the lazy dog'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    host = '127.0.0.1'
    port = '3306'
    mysql = 'mysql+pymysql'
    username_password = 'root:root'
    database = 'seed_dev'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
                              '{}://{}@{}:{}/{}?{}'.format(
                                      mysql, username_password, host, port, database, setting)


class TestingConfig(Config):
    TESTING = True
    host = '127.0.0.1'
    port = '3306'
    mysql = 'mysql+pymysql'
    username_password = 'root:root'
    database = 'seed_test'
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
                              '{}://{}@{}:{}/{}?{}'.format(
                                      mysql, username_password, host, port, database, setting)


class ProductionConfig(Config):
    host = '127.0.0.1'
    port = '3306'
    mysql = 'mysql+pymysql'
    username_password = 'root:root'
    database = 'seed_prod'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              '{}://{}@{}:{}/{}?{}'.format(
                                      mysql, username_password, host, port, database, setting)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}
