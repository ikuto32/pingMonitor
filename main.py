import logging
from logging.handlers import TimedRotatingFileHandler
import os
import subprocess
import time
from datetime import datetime
import wandb
import requests

wandb.init(project="ping_monitor", entity="ikuto0894")  # プロジェクト名とWandBユーザー名を設定

def setup_logger(log_dir="logs", log_filename="app.log"):
    # Create logs directory if it doesn't exist
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create a logger
    logger = logging.getLogger("my_logger")
    logger.setLevel(logging.DEBUG)
    
    # Create a file handler that logs messages with a rotating log file
    log_path = os.path.join(log_dir, log_filename)
    handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1)
    handler.suffix = "%Y-%m-%d"  # Adds the date to the log file name
    handler.setLevel(logging.DEBUG)
    
    # Create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(handler)
    
    return logger


def ping(url):
    try:
        res = requests.get(url)
        response_time = res.elapsed.total_seconds() * 1000
        return True, response_time
    except subprocess.CalledProcessError:
        return False, 2000


def log_result(response_time):
    log_data = {}
    if response_time is not None:
        log_data["response_time_ms"] = response_time
    wandb.log(log_data)
    print(response_time)
    logger = setup_logger()
    logger.info(f"response_time_ms:{response_time}")


def main():
    url = "https://www.google.com/"  # GoogleのDNSサーバー
    interval = 1  # 60秒ごとにpingを実行

    while True:
        success, response_time = ping(url)
        log_result(response_time)
        time.sleep(interval)
    wandb.finish()

if __name__ == "__main__":
    main()
