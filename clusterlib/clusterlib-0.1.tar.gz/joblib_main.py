# joblib_main.py

import os
from joblib import Memory
from main import main

CACHE_DIR = os.path.join(os.environ["HOME"], "joblib_cache_dir")
memory = Memory(cachedir=CACHE_DIR, verbose=0)
main = memory.cache(main)

if __name__ == "__main__":
    main()
