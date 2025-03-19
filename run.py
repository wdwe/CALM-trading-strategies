import logging.config
from logging_config import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)

from strategy_engine import StrategyEngine


if __name__ == "__main__":
    strategy_engine = StrategyEngine("bollinger_band.yaml")
    strategy_engine.run()

