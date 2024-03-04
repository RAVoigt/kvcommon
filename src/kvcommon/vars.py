import os
import typing as t

KVC_LOG_FORMAT = os.getenv("KVC_LOG_FORMAT", "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")
KVC_LOG_DATEFMT = os.getenv("KVC_LOG_DATEFMT", "%Y-%m-%d %H:%M:%S")
