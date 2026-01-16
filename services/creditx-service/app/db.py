import os
import databases

DATABASE_URL = os.getenv("DATABASE_URL")

database = databases.Database(DATABASE_URL)
