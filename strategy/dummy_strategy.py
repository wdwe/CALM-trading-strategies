import logging
import random

logger = logging.getLogger(__name__)


class DummyStrategy:
    def __init__(self, quantity):
        logger.info(f"initializing dummy strategy")
        self.qty = quantity

    def process(self, tick):
        try:
            mult = random.randint(-2, 2)
            return self.qty * mult
        except Exception as e:
            logger.exception(e)
            raise
