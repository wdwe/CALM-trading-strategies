import logging
import redis
import yaml
import queue
import threading
import struct
import time
from collections import namedtuple
import strategy

logger = logging.getLogger(__name__)


def unpack_tick_msg(bin_msg):
    Tick = namedtuple("Tick", ["symbol", "price", "timestamp"])
    _symbol, price, timestamp = struct.unpack("@32sdq", bin_msg)
    _symbol = _symbol.decode()
    symbol = _symbol.split(b"\x00".decode())[0]
    tick = Tick._make((symbol, price, timestamp))
    return tick


def pack_action_msg(symbol, pos):
    timestamp = int(time.time())
    bin_reply = struct.pack("@32sdq", symbol.encode() + b"\x00", pos, timestamp)
    return bin_reply


class StrategyEngine:
    def __init__(self, cfg_path):
        self.cfg = yaml.safe_load(open(cfg_path))
        self.redis_client = redis.Redis(**self.cfg["redis_cfg"])
        self.q = queue.Queue()
        self.sub_thread = None
        self.running = False
        self.sentinel = self.cfg["mq"]["sentinel_token"].encode() + b"\x00"
        strat_cls = self.cfg["strategy"]["class"]
        cls = getattr(strategy, strat_cls)
        self.strategy = cls(**self.cfg["strategy"]["params"])

    def run(self):
        try:
            logger.info("Starting strategy engine...")
            self.running = True
            self.sub_thread = threading.Thread(target=self.poll_msg, daemon=True)
            self.sub_thread.start()

            channel = self.cfg["mq"]["channels"]["action"]
            while self.running:
                try:
                    bin_msg = self.q.get(timeout=1)
                    tick = unpack_tick_msg(bin_msg)
                    logger.debug(tick)
                    if not tick.symbol:  # empty symbol means uninitialised data
                        continue
                    pos = self.strategy.process(tick)
                    bin_reply = pack_action_msg(tick.symbol, pos)
                    self.redis_client.publish(channel, bin_reply)
                except queue.Empty:
                    pass

            self.sub_thread.join()
        except Exception as e:
            logger.exception(e)

    def poll_msg(self):
        try:
            sub = self.redis_client.pubsub()
            channel = self.cfg["mq"]["channels"]["tick"]
            sub.subscribe(channel)
            logger.info(f"Subscribed to channel:{channel}")

            for msg in sub.listen():
                if msg.get("type") == "message":
                    data = msg["data"]
                    if data == self.sentinel:
                        logger.info(f"Received sentinel:{data}")
                        break
                    self.q.put(data)
        except Exception as e:
            logger.exception(e)

        self.running = False
        logger.info("Stopping strategy engine...")
