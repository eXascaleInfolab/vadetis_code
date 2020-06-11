import collections, logging
import pandas as pd, numpy as np
from celery.task import Task
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.conf import settings

from vadetisweb.models import User, Location, TimeSeries, DataSet
from vadetisweb.parameters import *
from vadetisweb.utils import iso_format_time, silent_remove


class TaskImportData(Task):
    """
    Task to insert a dataset into database
    """

    def run(self, owner_username, dataset_file_name, title, type, spatial_data, **kwargs):
        """
        The execution method of this task. We read the csv with the pandas lib, it's fast!

        :param owner_username: the owner of the dataset
        :param dataset_file_name: CSV file name of the time series
        :param title: Human readable title of the dataset
        :param type: real world or synthetic
        :param spatial_data: whether its spatial data or not
        :param kwargs: provide kwarg 'spatial_file_name' when inserting spatial data
        :return: results of the tasks as json
        """

        # set start time
        start_time = timezone.now()

        self.dataset_csv_name = dataset_file_name

        if spatial_data == SPATIAL:
            if 'spatial_file_name' in kwargs:
                self.spatial_csv_name = kwargs['spatial_file_name']
            else:
                logging.warning('No locations file provided for spatial dataset, will change to non spatial dataset')
                spatial_data = NON_SPATIAL
        else:
            self.spatial_csv_name = None

        user = User.objects.get(username=owner_username)

        # import time series
        with open(self.dataset_csv_name, 'r') as file_csv, transaction.atomic():

            # get flatten df
            df_read = pd.read_csv(file_csv,
                                  sep=';',
                                  parse_dates=['time'],
                                  infer_datetime_format=True,
                                  index_col='time')

            # check number of values (row counts)
            num_values = df_read.shape[0]
            if num_values > settings.DATASET_MAX_VALUES:
                raise ValueError("Dataset exceeds value limit {} ({} values provided)".format(num_values, settings.DATASET_MAX_VALUES))

            # check each series must have same unit
            group_by_ts_name = df_read.groupby('ts_name')
            df_ts_unit = group_by_ts_name.apply(lambda x: x['unit'].unique())

            for idx, row in df_ts_unit.items():  # check length of units at each series must be 1
                if not len(row) == 1:
                    err_msg = "Series {0} has multiple units".format(idx)
                    raise ValueError(err_msg)

            # check each series distinct name => each series has only one value for a given index
            group_by_index = df_read.groupby(level=0)
            if group_by_index.apply(lambda x: x[
                'ts_name'].duplicated()).any():  # true if any value is true => at least one duplicated index for a time series name
                err_msg = "Duplicated index for a time series found"
                raise ValueError(err_msg)

            # unflatten dataframe
            df = df_read.pivot(columns='ts_name', values='value')

            # check if same frequency => pandas can infer a frequency
            freq = df.index.inferred_freq
            if freq is None:
                err_msg = "Series do not have same frequency"
                raise ValueError(err_msg)

            # get anomaly df
            df_class = df_read.pivot(columns='ts_name', values='class')
            df_class = df_class.applymap(lambda x: True if x == 1 else False)

            # check for NaN values, we need complete data for some algorithms
            if df.isnull().values.any() or df_class.isnull().values.any():
                err_msg = "Some values are missing"
                raise ValueError(err_msg)

            # check if different units
            units = []
            for idx, row in df_ts_unit.items():
                unit = row[0]
                if unit not in units:
                    units.append(unit)

            if len(units) > 1:
                raise ValueError('Different types of values provided')

            dataset = DataSet.objects.create(title=title,
                                             owner=user,
                                             type=type,
                                             frequency=freq,
                                             spatial_data=spatial_data)
            logging.info("New dataset {0} added".format(dataset))

            # for each series create a time series object
            for idx, row in df_ts_unit.items():
                ts = TimeSeries.objects.create(name=idx,
                                               unit=row[0], # safe to get single element as previously checked for consistency
                                               is_spatial=True if spatial_data == SPATIAL else False)
                logging.debug("New time series: {0} added".format(idx))
                ts.datasets.add(dataset)
                ts.save()
                # replace column in dataframe by time series database id
                df = df.rename(columns={idx: ts.id})

            # localize to UTC
            df.index.tz_localize('UTC')
            df_class.tz_localize('UTC')

            # rename df class before assign
            for idx, row in df_ts_unit.items():
                ts = TimeSeries.objects.get(name=idx,
                                            datasets__id=dataset.id)
                # replace column in dataframe by time series database id
                df_class = df_class.rename(columns={idx: ts.id})

            # set dfs
            dataset.dataframe = df
            dataset.dataframe_class = df_class

            dataset.save()

            if spatial_data == SPATIAL:
                with open(self.spatial_csv_name, 'r') as locations_csv:

                    # get location df
                    df_loc = pd.read_csv(locations_csv,
                                         sep=';',
                                         index_col='ts_name')

                    # check if locations for all series are provided
                    ts_dataset = TimeSeries.objects.filter(datasets__id=dataset.id)
                    ts_names = ts_dataset.values_list('name', flat=True)
                    if not np.all(df_loc.index.isin(ts_names) == True):
                        err_msg = "Some time series are missing: %s " % ', '.join(
                            str(x) for x in df_loc[~df_loc.index.isin(ts_names)].index.values)
                        raise ValueError(err_msg)

                    # check if needed columns are present and check if values complete
                    required_cols = pd.Series(['l_name', 'lon', 'lat', 'height'])
                    if not required_cols.isin(df.columns).all() or df_loc.loc[
                        ts_names, required_cols].isnull().values.any():
                        err_msg = "Some required values are missing"
                        raise ValueError(err_msg)

                    # for each series create a location object
                    for idx, row in df_loc.iterrows():
                        ts = TimeSeries.objects.get(datasets__id=dataset.id, name=idx)
                        l_name = row['l_name']
                        lon = row['lon']
                        lat = row['lat']
                        ch1903_e = row['ch1903_e']
                        ch1903_n = row['ch1903_n']
                        height = row['height']

                        location = Location.objects.create(label=l_name,
                                                           lon=lon,
                                                           lat=lat,
                                                           ch1903_easting=ch1903_e,
                                                           ch1903_northing=ch1903_n,
                                                           height=height)
                        ts.location = location
                        ts.is_spatial = True
                        ts.save()
                        location.save()

        execution_time = iso_format_time(timezone.now() - start_time)
        result = {'measurements_added': int(df.count().sum()), 'time_series_added:': len(df.columns),
                  'execution_time': execution_time}

        return result

    def on_success(self, retval, task_id, args, kwargs):
        # remove temp files from storage after task is finished
        silent_remove(self.dataset_csv_name)
        if self.spatial_csv_name and self.spatial_csv_name is not None:
            silent_remove(self.spatial_csv_name)


class TaskImportTrainingData(Task):
    """
    Task to insert a test dataset into database
    """
    def run(self, owner_username, original_dataset_id, training_dataset_file_name, title):

        # set start time
        start_time = timezone.now()

        self.filename = training_dataset_file_name

        user = User.objects.get(username=owner_username)

        # import time series
        with open(self.filename, 'r') as file_csv, transaction.atomic():

            # get flatten df
            df_read = pd.read_csv(file_csv,
                                  sep=';',
                                  parse_dates=['time'],
                                  infer_datetime_format=True,
                                  index_col='time')

            # check number of values (row counts)
            num_values = df_read.shape[0]
            if num_values > settings.DATASET_MAX_VALUES:
                raise ValueError("Dataset exceeds value limit {} ({} values provided)".format(num_values, settings.DATASET_MAX_VALUES))

            # check each series must have same unit
            group_by_ts_name = df_read.groupby('ts_name')
            df_ts_unit = group_by_ts_name.apply(lambda x: x['unit'].unique())

            for idx, row in df_ts_unit.items():  # check length of units at each series must be 1
                if not len(row) == 1:
                    err_msg = "Series {0} has multiple units".format(idx)
                    raise ValueError(err_msg)

            # check if all time series from original dataset provided, and not more or less
            ts_names_from_original = TimeSeries.objects.filter(datasets__id=original_dataset_id).values_list('name', flat=True)
            compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
            if not compare(list(ts_names_from_original), df_ts_unit.index.tolist()):
                err_msg = "Either some series are missing or some series are provided that are not in the original dataset."
                raise ValueError(err_msg)

            # check each series distinct name => each series has only one value for a given index
            group_by_index = df_read.groupby(level=0)
            if group_by_index.apply(lambda x: x[
                'ts_name'].duplicated()).any():  # true if any value is true => at least one duplicated index for a time series name
                err_msg = "Duplicated index for a time series found"
                raise ValueError(err_msg)

            # unflatten dataframe
            df = df_read.pivot(columns='ts_name', values='value')

            # check if same frequency => pandas can infer a frequency
            freq = df.index.inferred_freq
            if freq is None:
                err_msg = "Series do not have same frequency"
                raise ValueError(err_msg)

            # get anomaly df
            df_class = df_read.pivot(columns='ts_name', values='class')
            df_class = df_class.applymap(lambda x: True if x == 1 else False)

            # check for NaN values, we need complete data for some algorithms
            if df.isnull().values.any() or df_class.isnull().values.any():
                err_msg = "Some values are missing"
                raise ValueError(err_msg)

            # check if different units
            units = []
            for idx, row in df_ts_unit.items():
                unit = row[0]
                if unit not in units:
                    units.append(unit)

            if len(units) > 1:
                raise ValueError('Different types of values provided')

            original_dataset = DataSet.objects.get(id=original_dataset_id)

            # create (and saves) training dataset
            training_dataset = DataSet.objects.create(title=title,
                                                      owner=user,
                                                      type=original_dataset.type,
                                                      spatial_data=original_dataset.spatial_data,
                                                      frequency=freq,
                                                      is_training_data=True,
                                                      original_dataset=original_dataset)

            logging.info("Test dataset {0} added".format(training_dataset))

            # for each series get the time series object
            for idx, row in df_ts_unit.items():
                ts = TimeSeries.objects.get(name=idx,
                                            datasets__id=original_dataset.id)

                logging.debug("Time series: {0} fetched".format(idx))
                ts.datasets.add(training_dataset)
                ts.save()
                # replace column in dataframe by time series database id
                df = df.rename(columns={idx : ts.id})

            # localize to UTC
            df.index.tz_localize('UTC')
            df_class.tz_localize('UTC')

            # rename df class before assign
            for idx, row in df_ts_unit.items():
                ts = TimeSeries.objects.get(name=idx,
                                            datasets__id=original_dataset.id)
                # replace column in dataframe by time series database id
                df_class = df_class.rename(columns={idx: ts.id})

            # set dfs
            training_dataset.dataframe = df
            training_dataset.dataframe_class = df_class

            training_dataset.save()

        execution_time = iso_format_time(timezone.now() - start_time)
        result = {'measurements_added': int(df.count().sum()), 'execution_time': execution_time }

        return result

    def on_success(self, retval, task_id, args, kwargs):
        #usually tempfile is removed as soon as closed, but just to make sure
        silent_remove(self.filename)
