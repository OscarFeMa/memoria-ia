import os
import sys

# Redirige HuggingFace cache al directorio empaquetado dentro del exe
if getattr(sys, 'frozen', False):
    cache_path = os.path.join(sys._MEIPASS, "huggingface_cache")
    os.environ["HF_HOME"]                  = cache_path
    os.environ["HF_DATASETS_CACHE"]        = cache_path
    os.environ["TRANSFORMERS_CACHE"]       = cache_path
    os.environ["SENTENCE_TRANSFORMERS_HOME"] = cache_path
    os.environ["HUGGINGFACE_HUB_CACHE"]    = cache_path
