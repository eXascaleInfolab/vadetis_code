
#########################################################
# Anomaly Detection Algorithms
#########################################################

LISA = 'LISA'
HISTOGRAM = 'Histogram'
CLUSTER_GAUSSIAN_MIXTURE = 'Cluster (Gaussian Mixture)'
SVM = 'SVM'
ISOLATION_FOREST = 'Isolation Forest'

ANOMALY_DETECTION_ALGORITHMS = (
    (LISA, LISA),
    (HISTOGRAM, HISTOGRAM),
    (CLUSTER_GAUSSIAN_MIXTURE, CLUSTER_GAUSSIAN_MIXTURE),
    (SVM, SVM),
    (ISOLATION_FOREST, ISOLATION_FOREST),
)

#########################################################
# Anomaly Detection Score Types
#########################################################

F1_SCORE = 'F1-Score'
PRECISION = 'Precision'
RECALL = 'Recall'
ACCURACY = 'Accuracy'

ANOMALY_DETECTION_SCORE_TYPES = (
    (F1_SCORE, F1_SCORE),
    (PRECISION, PRECISION),
    (RECALL, RECALL),
    (ACCURACY, ACCURACY),
)

#########################################################
# Supported SVM Kernels
#########################################################

KERNEL_RBF = 'rbf'
KERNEL_LINEAR = 'linear'
KERNEL_POLY = 'poly'
KERNEL_SIGMOID = 'sigmoid'

SVM_KERNELS = (
    (KERNEL_RBF, KERNEL_RBF),
    (KERNEL_LINEAR, KERNEL_LINEAR),
    (KERNEL_POLY, KERNEL_POLY),
    (KERNEL_SIGMOID, KERNEL_SIGMOID),
)


#########################################################
# Units for the datasets
#########################################################

QUANTITY = 'Quantity'
BOOLEAN = 'Boolean'
KG = 'Kilogram'
G = 'Gram'
AMPERE = 'Ampere'
VOLT = 'Volt'
JOULE = 'Joule'
CELSIUS = 'Celsius'
KELVIN = 'Kelvin'
KMH = 'KM/H'
MS = 'M/S'
HPA = 'hPa'
KNOTS = 'Knots'
LUX = 'Lux'
MILLIMETER = 'Millimeter'
MILLIMETER_PER_DAY = 'Millimeter per day'
MILLIVOLT = 'Millivolt'
MILLIWATT_PER_M2 = 'Milliwatt per m2'
HOURS = 'Hours'
OCTAS = 'Octas'
PERCENT = 'Percent'
DEGREE = 'Degree'
VOLT = 'Volt'
WATTS_PER_M2 = 'Watts per m2'
CENTIMETERS = 'Centimeters'

UNITS = (
    (QUANTITY, QUANTITY),
    (BOOLEAN, BOOLEAN),
    (KG, KG),
    (G, G),
    (CELSIUS, CELSIUS),
    (KELVIN, KELVIN),
    (KMH, KMH),
    (MS, MS),
    (HPA, HPA),
    (KNOTS, KNOTS),
    (LUX, LUX),
    (MILLIMETER, MILLIMETER),
    (MILLIMETER_PER_DAY, MILLIMETER_PER_DAY),
    (AMPERE, AMPERE),
    (VOLT, VOLT),
    (JOULE, JOULE),
    (MILLIVOLT, MILLIVOLT),
    (MILLIWATT_PER_M2, MILLIWATT_PER_M2),
    (HOURS, HOURS),
    (OCTAS, OCTAS),
    (PERCENT, PERCENT),
    (DEGREE, DEGREE),
    (VOLT, VOLT),
    (WATTS_PER_M2, WATTS_PER_M2),
    (CENTIMETERS, CENTIMETERS),
)

#########################################################
#Types of datasets
#########################################################

SYNTHETIC = 'Synthetic'
REAL_WORLD = 'Real World'

DATASET_TYPE = (
    (SYNTHETIC, SYNTHETIC),
    (REAL_WORLD, REAL_WORLD),
)

NON_SPATIAL = 'Non Spatial'
SPATIAL = 'Spatial'

DATASET_SPATIAL_DATA  = (
    (NON_SPATIAL, NON_SPATIAL),
    (SPATIAL, SPATIAL),
)

SAME_UNITS = 'Same units'
DIFFERENT_UNITS = 'Different units'

DATASET_TYPE_OF_DATA = (
    (SAME_UNITS, SAME_UNITS),
    (DIFFERENT_UNITS, DIFFERENT_UNITS),
)

#########################################################
# Correlation Algorithms
#########################################################

PEARSON = 'Pearson'
DTW = 'DTW with Pearson'
GEO = 'Geographical'

CORRELATION_ALGORITHMS = (
    (PEARSON, PEARSON),
    (DTW, DTW),
    (GEO, GEO),
)

CORRELATION_ALGORITHMS_NON_SPATIAL = (
    (PEARSON, PEARSON),
    (DTW, DTW),
)

SELECTION = 'as selected in chart'
FULL = 'full series'

TIME_RANGE = (
    (FULL, FULL),
    (SELECTION, SELECTION),
)

WINDOW_SIZE_ABSOLUTE = 'absolute'
WINDOW_SIZE_PERCENT = 'percent'

WINDOW_SIZES = (
    (WINDOW_SIZE_ABSOLUTE, WINDOW_SIZE_ABSOLUTE),
    (WINDOW_SIZE_PERCENT, WINDOW_SIZE_PERCENT),
)

EUCLIDEAN = "euclidean"
BRAYCURTIS = "braycurtis"
CANBERRA = "canberra"
CHEBYSHEV = "chebyshev"
CITYBLOCK = "cityblock"
CORRELATION = "correlation"
COSINE = "cosine"
DICE = "dice"
HAMMING = "hamming"
JACCARD = "jaccard"
KULSINSKI = "kulsinski"
MAHALANOBIS = "mahalanobis"
MATCHING = "matching"
MINKOWSKI = "minkowski"
ROGERSTANIMOTO = "rogerstanimoto"
RUSSELLRAO = "russellrao"
SEUCLIDEAN = "seuclidean"
SOKALMICHENER = "sokalmichener"
SOKALSNEATH = "sokalsneath"
SQEUCLIDEAN = "sqeuclidean"
WMINKOWSKI = "wminkowski"
YULE = "yule"

DTW_DISTANCE_FUNCTION = (
    (EUCLIDEAN, EUCLIDEAN),
    (BRAYCURTIS, BRAYCURTIS),
    (CANBERRA, CANBERRA),
    (CHEBYSHEV, CHEBYSHEV),
    (CITYBLOCK, CITYBLOCK),
    (CORRELATION, CORRELATION),
    (COSINE, COSINE),
    (DICE, DICE),
    (HAMMING, HAMMING),
    (JACCARD, JACCARD),
    (KULSINSKI, KULSINSKI),
    (MAHALANOBIS, MAHALANOBIS),
    (MATCHING, MATCHING),
    (MINKOWSKI, MINKOWSKI),
    (ROGERSTANIMOTO, ROGERSTANIMOTO),
    (RUSSELLRAO, RUSSELLRAO),
    (SEUCLIDEAN, SEUCLIDEAN),
    (SOKALMICHENER, SOKALMICHENER),
    (SOKALSNEATH, SOKALSNEATH),
    (SQEUCLIDEAN, SQEUCLIDEAN),
    (WMINKOWSKI, WMINKOWSKI),
    (YULE, YULE),
)

CH1903 = "Linear distance (CH1903)"
CH1903_ALT = "Linear distance with altitude (CH1903)"
HAVERSINE = "Haversine (Lat/Lon)"

GEO_DISTANCE = (
    (CH1903, CH1903),
    (CH1903_ALT, CH1903_ALT),
    (HAVERSINE, HAVERSINE),
)

#########################################################
# Defaults for application settings
#########################################################

DEFAULT_HIGHCHARTS_HEIGHT = 500
DEFAULT_LEGEND_HEIGHT = 100
DEFAULT_COLOR_OUTLIERS = '#FF0000'
DEFAULT_COLOR_CLUSTERS = '#0000FF'
DEFAULT_COLOR_TRUE_POSITIVES = '#008800'
DEFAULT_COLOR_FALSE_POSITIVES = '#FF0000'
DEFAULT_COLOR_FALSE_NEGATIVES = '#0000FF'
DEFAULT_ROUND_DIGITS = 3

DEFAULT_SETTINGS = (
    ('highcharts_height', DEFAULT_HIGHCHARTS_HEIGHT),
    ('legend_height', DEFAULT_LEGEND_HEIGHT),
    ('color_outliers', DEFAULT_COLOR_OUTLIERS),
    ('color_clusters', DEFAULT_COLOR_CLUSTERS),
    ('color_true_positive', DEFAULT_COLOR_TRUE_POSITIVES),
    ('color_false_positive', DEFAULT_COLOR_FALSE_POSITIVES),
    ('color_false_negative', DEFAULT_COLOR_FALSE_NEGATIVES),
    ('round_digits', DEFAULT_ROUND_DIGITS),
)