from base64 import b64decode
import base64
import gzip
from time import time

import models
from fastapi.responses import HTMLResponse
from database import Database
import utils

perms = {
    1: ["suggest", "daily", "status", "color"],
    2: ["rate", "daily", "status", "color", "ban", "promote"],
    -1: ["status", "color"]
}
