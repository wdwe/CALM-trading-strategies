import logging
from collections import deque
import numpy as np

logger = logging.getLogger(__name__)

class BollingerBandStrategy:
    def __init__(self, lookback, z_thr, quantity):
        logger.info(f"initializing bollinger band strategy - lookback:{lookback}, z_thr:{z_thr}, quantity:{quantity}")
        self.lookback = lookback
        self.z_thr = z_thr
        self.qty = quantity
        self.past_px = deque()
        self.mean = None
        self.std = None
        self.pos = 0

    def process(self, tick):
        try:
            px = tick.price

            # collecting lookback data
            if len(self.past_px) < self.lookback:
                self.past_px.append(px)
                return self.pos

            # if mean/std was not computed
            if self.mean is None:
                self.mean = np.mean(self.past_px)
                self.std = np.std(self.past_px)

            # compute z-score
            z = (px - self.mean) / self.std

            # compute new pos
            if z > self.z_thr:
                self.pos = -self.qty
            elif z < -self.z_thr:
                self.pos = self.qty
            elif z >= 0 and self.pos == self.qty or z <= 0 and self.pos == -self.qty:
                self.pos = 0

            # compute new mean and std
            oldest_px = self.past_px.popleft()
            new_mean = self.mean + (px - oldest_px) / self.lookback
            new_std = self.std + (new_mean - self.mean) ** 2 + ((px - self.mean) ** 2 - (oldest_px - new_mean) ** 2) / self.lookback
            self.mean = new_mean
            self.std = new_std

            return self.pos
        except Exception as e:
            logger.exception(e)
            raise

