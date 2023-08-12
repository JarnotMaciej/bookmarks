import os

class Config:
    MONGO_HOST = os.getenv("MONGODB_HOST") or "localhost"
    MONGO_PORT = os.getenv("MONGODB_PORT") or 27017
    DATABASE = os.getenv("MONGODB_DB") or "bookmarks_db"
    BOOKMARKS_COLLECTION = os.getenv("BOOKMARKS_COLLECTION") or "bookmarks"
    TAGS_COLLECTION = os.getenv("TAGS_COLLECTION") or "tags"
    TOPICS_COLLECTION = os.getenv("TOPICS_COLLECTION") or "topics"
    TOPICS_METHOD = os.getenv("TOPICS_METHOD") or "random"
    APP_PORT = os.getenv("APP_PORT") or 5000
    TIME_ZONE = os.getenv("TZ") or "UTC"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}