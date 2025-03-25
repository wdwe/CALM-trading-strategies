import logging.config
from logging_config import LOGGING_CONFIG
logging.config.dictConfig(LOGGING_CONFIG)
import argparse
from strategy_engine import StrategyEngine



if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--cfg", "-c", default="/home/wayne/calm/bollinger_band.yaml")
    args = arg_parser.parse_args()

    strategy_engine = StrategyEngine(args.cfg)
    strategy_engine.run()

