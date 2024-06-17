import logging
from logging.handlers import TimedRotatingFileHandler
import os
import subprocess
import time
import wandb
import pycurl
from io import BytesIO

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
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(10002, url)
        c.setopt(10001, buffer)
        c.perform()
        body = buffer.getvalue()

        print('TOTAL_TIME: %f' % c.getinfo(c.TOTAL_TIME))
        print('CONNECT_TIME: %f' % c.getinfo(c.CONNECT_TIME))
        print('PRETRANSFER_TIME: %f' % c.getinfo(c.PRETRANSFER_TIME))
        print('STARTTRANSFER_TIME: %f' % c.getinfo(c.STARTTRANSFER_TIME))
        TOTAL_TIME = c.getinfo(c.TOTAL_TIME)
        CONNECT_TIME = c.getinfo(c.CONNECT_TIME)
        PRETRANSFER_TIME = c.getinfo(c.PRETRANSFER_TIME)
        STARTTRANSFER_TIME = c.getinfo(c.STARTTRANSFER_TIME)
        return {"TOTAL_TIME":TOTAL_TIME, "CONNECT_TIME":CONNECT_TIME, "PRETRANSFER_TIME":PRETRANSFER_TIME, "STARTTRANSFER_TIME":STARTTRANSFER_TIME}
    except:
        return {"TOTAL_TIME":1000.0, "CONNECT_TIME":1000.0, "PRETRANSFER_TIME":1000.0, "STARTTRANSFER_TIME":1000.0}


def log_result(timeResponses, logger):
    log_data = {}
    if timeResponses is not None:
        log_data = timeResponses
    wandb.log(log_data)
    logger.info(f"time_Responses:{timeResponses}")


def main():
    url = "https://www.google.com/"  # GoogleのDNSサーバー
    interval = 5  # 5秒ごとにpingを実行
    logger = setup_logger()

    while True:
        timeResponses = ping(url)
        log_result(timeResponses, logger)
        time.sleep(interval)
    wandb.finish()

if __name__ == "__main__":
    main()
