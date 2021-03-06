import numpy as np
import pandas as pd
from pandas.tseries.frequencies import to_offset
from sklearn.metrics import fbeta_score, precision_score, recall_score, accuracy_score, confusion_matrix, normalized_mutual_info_score, mean_squared_error
from sklearn.preprocessing import minmax_scale
from vadetisweb.parameters import *
from .helper_function_utils import *


def min_max_normalization(scores):
    #return (scores - np.min(scores)) / (np.max(scores) - np.min(scores))
    return minmax_scale(scores)


def get_detection_choices(dataset, with_empty=True):
    empty_choice = ('', '----')
    has_training_data = dataset.number_of_training_datasets() > 0
    if dataset is not None:
        if dataset.is_spatial() and has_training_data:
            if with_empty:
                return (empty_choice,) + ANOMALY_DETECTION_ALGORITHMS
            else:
                return ANOMALY_DETECTION_ALGORITHMS

        elif dataset.is_spatial() and not has_training_data:
            if with_empty:
                return (empty_choice,) + ANOMALY_DETECTION_ALGORITHMS_NON_TRAINING
            else:
                return ANOMALY_DETECTION_ALGORITHMS_NON_TRAINING

        elif not dataset.is_spatial() and has_training_data:
            if with_empty:
                return (empty_choice,) + ANOMALY_DETECTION_ALGORITHMS_NON_SPATIAL
            else:
                return ANOMALY_DETECTION_ALGORITHMS_NON_SPATIAL

        else:
            if with_empty:
                return (empty_choice,) + ANOMALY_DETECTION_ALGORITHMS_NON_SPATIAL_NON_TRAINING
            else:
                return ANOMALY_DETECTION_ALGORITHMS_NON_SPATIAL_NON_TRAINING
    else:
        if with_empty:
            return empty_choice
        else:
            raise ValueError('Could not determine supported outlier algorithms.')


def get_preselected_detection_choices(detection_choices):
    preselected = [LISA_PEARSON]

    if (RPCA_HUBER_LOSS, RPCA_HUBER_LOSS) in detection_choices and (SVM, SVM) in detection_choices:
        preselected.append(RPCA_HUBER_LOSS)
        preselected.append(SVM)

    else:
        preselected.append(LISA_DTW_PEARSON)

    return preselected


def _add(x, y):
    """
    Adds to values
    :param x: first value
    :param y: second value
    :return: result of the addition
    """

    return x + y

def _subtract(x, y):
    """
    Subtracts two values
    :param x: first value
    :param y: second value
    :return: result of the subtraction
    """

    return x - y


def next_dt(dt, f, inferred_freq, size=1):
    """
    Provides a later or earlier datetime from the given datetime that corresponds
    to a certain frequency and size.

    :param dt: a datetime object
    :param f: a function to either subtract or add two datetime object
    :param freq: the frequency for the timedelta
    :param size: the size of the window (that is applied with the frequency)
    :return: the next later or earlier datetime
    """

    # some freqs require relative offset, others can be computed with timedelta
    if inferred_freq.endswith(('MS', 'AS', 'B', 'W', 'M', 'SM', 'BM', 'CBM', 'SMS', 'BMS', 'CBMS', 'Q', 'BQ', 'QS', 'BQS', 'A', 'Y', 'BA', 'BY', 'YS', 'BAS', 'BYS', 'BH')):
        next_dt = (f(dt, to_offset(inferred_freq) * size)).to_pydatetime()
    else:
        next_dt = f(dt, pd.to_timedelta(to_offset(inferred_freq)) * size)

    return next_dt


def next_earlier_dt(dt, inferred_freq, size=1):
    return next_dt(dt, lambda x, y: _subtract(x,y), inferred_freq, size)


def next_later_dt(dt, inferred_freq, size=1):
    return next_dt(dt, lambda x, y: _add(x,y), inferred_freq, size)


def zscore_for_column(column, index, skipna=True):
    """
    Returns the Z Scores of a pandas dataframe column. Mean and std will handle NaN values by default

    :param column: the column
    :param index: the index
    :param skipna: defines if to skip NaN values
    :return: Z-Score for column
    """

    # ddof = 0: population standard deviation using n; ddof = 1: sample std deviation using n-1
    return (column - column.mean(skipna=skipna)) / column.std(skipna=skipna, level=None, ddof=0)


def df_zscore(df, skipna=True):
    """
    Transforms a dataframe to z-score values

    :param df: the dataframe of raw data
    :param skipna: defines if to skip NaN values
    :return: a dataframe of Z-Score values
    """

    df_zscore = df.apply(lambda column: zscore_for_column(column, column.name, skipna), axis=0)
    return df_zscore


def get_threshold_scores(thresholds, y_scores, valid, upper_boundary=False):
    """
    Computes for each possible threshold the score for the performance metrics

    :param thresholds: a list of possible thresholds
    :param y_scores: the list of computed scores by the detection algorithm
    :param valid: the true class values to run the performance metric against
    :param upper_boundary: determines if score higher than thresholds are anomalies or not

    :return: array of scores for each threshold for each performance metric
    """
    scores = []

    # any comparison (other than !=) of a NaN to a non-NaN value will always return False,
    # and therefore will not be detected as anomaly
    with np.errstate(invalid='ignore'):

        for threshold in thresholds:
            y_hat = np.array(y_scores < threshold).astype(int) if upper_boundary == False else np.array(y_scores > threshold).astype(int)

            scores.append([recall_score(y_true=valid.values, y_pred=y_hat, zero_division=0),
                           precision_score(y_true=valid.values, y_pred=y_hat, zero_division=0),
                           fbeta_score(y_true=valid.values, y_pred=y_hat, beta=1, zero_division=0),
                           accuracy_score(y_true=valid.values, y_pred=y_hat),
                           normalized_mutual_info_score(valid.values, y_hat, average_method='arithmetic'),
                           mean_squared_error(valid.values, y_hat, sample_weight=None, multioutput='uniform_average', squared=True)])

    return np.array(scores)


def get_detection_meta(threshold, y_hat_results, y_truth, upper_boundary=False):
    info = {}

    accuracy = accuracy_score(y_pred=y_hat_results, y_true=y_truth)
    recall = recall_score(y_pred=y_hat_results, y_true=y_truth, zero_division=0)
    precision = precision_score(y_pred=y_hat_results, y_true=y_truth, zero_division=0)
    f1_score = fbeta_score(y_pred=y_hat_results, y_true=y_truth, beta=1, zero_division=0)

    nmi = normalized_mutual_info_score(y_truth.flatten(), y_hat_results, average_method='arithmetic')
    rmse = mean_squared_error(y_truth, y_hat_results, sample_weight=None, multioutput='uniform_average', squared=True)

    # we set labels 0,1 manually because the dataset could contain only one class
    cnf_matrix = confusion_matrix(y_truth, y_hat_results, labels=[0,1])
    info['cnf_matrix'] = cnf_matrix.tolist()

    info['threshold'] = threshold
    info['accuracy'] = accuracy
    info['recall'] = recall
    info['precision'] = precision
    info['f1_score'] = f1_score

    info['nmi'] = nmi
    info['rmse'] = rmse

    info['upper_boundary'] = upper_boundary

    logging.debug('Threshold: %.3f' % threshold)
    logging.debug('Accuracy Score: %.3f' % accuracy)
    logging.debug('Recall Score: %.3f' % recall)
    logging.debug('Precision Score: %.3f' % precision)
    logging.debug('F1 Score: %.3f' % f1_score)

    logging.debug('NMI Score: %.3f' % nmi)
    logging.debug('RMSE Score: %.3f' % rmse)

    return info
