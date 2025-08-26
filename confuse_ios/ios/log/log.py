import logging


logging.basicConfig(level=logging.INFO)

file_handler = logging.FileHandler("./ios/log/output/log1.txt")
file_handler2 = logging.FileHandler("./ios/log/output/log2.txt")

formatter = logging.Formatter("%(message)s")
# formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

formatter2 = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler2.setFormatter(formatter2)

logger = logging.getLogger()
logger.addHandler(file_handler)

logger2 = logging.getLogger(name="second.result")
logger2.addHandler(file_handler2)


# 清空日志
def clear():
    with open("./ios/log/output/log1.txt", "w") as f:
        f.write("")


if __name__ == "__main__":
    logger.info("这是一条日志消息")
    logger.error("这是一个错误")

    logger2.info("这是logger2的日志文件系统")
