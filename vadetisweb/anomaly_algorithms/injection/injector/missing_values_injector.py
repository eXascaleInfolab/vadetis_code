import numpy as np
import pandas as pd

from vadetisweb.parameters import ANOMALY_INJECTION_SCALE_SMALL, ANOMALY_INJECTION_SCALE_MEDIUM, ANOMALY_INJECTION_SCALE_HIGH, ANOMALY_INJECTION_SCALE_RANDOM
from vadetisweb.utils import next_later_dt
from .base import OutlierInjector


class MissingValuesInjector(OutlierInjector):

    def __init__(self, validated_data):
        super().__init__(validated_data)


    def get_factor(self):
        anomaly_scale = self.validated_data['anomaly_scale']
        if anomaly_scale == ANOMALY_INJECTION_SCALE_SMALL:
            return 1

        elif anomaly_scale == ANOMALY_INJECTION_SCALE_MEDIUM:
            return 4

        elif anomaly_scale == ANOMALY_INJECTION_SCALE_HIGH:
            return 9

        elif anomaly_scale == ANOMALY_INJECTION_SCALE_RANDOM:
            return np.random.choice([1, 4, 9])

        else:
            raise ValueError


    def inject(self, range):
        ts_id = self.get_time_series().id
        inject_at_index = self.next_injection_index(range)
        if inject_at_index is not None:

            upper_boundary = min(next_later_dt(inject_at_index, self.df.index.inferred_freq, self.get_factor()), self.df.index.max())
            trend_indexes = pd.date_range(inject_at_index, upper_boundary, freq=self.df.index.inferred_freq)

            # injection
            self.df_inject.loc[trend_indexes, ts_id] = 0
            self.df_inject_class.loc[trend_indexes, ts_id] = 1
