from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.viewsets import ModelViewSet
from vadetisweb.models import DataSet
from vadetisweb.parameters import *


class DatasetTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSet
        fields = ('title',)


class DatasetChoicesViewSet(ModelViewSet):
    """
    A viewset for viewing and editing dataset instances.
    """
    queryset = DataSet.objects.filter(is_training_data=False)
    serializer = DatasetTitleSerializer(queryset, many=False)


class DatasetSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, max_length=128, help_text='Human readable title of the dataset',
                                  style={'template': 'vadetisweb/parts/input/text_input.html'})

    csv_file = serializers.FileField(required=True, label='CSV File', help_text='The csv file of the dataset',
                                     validators=[FileExtensionValidator(allowed_extensions=['csv'])],
                                     style={'template': 'vadetisweb/parts/input/text_input.html'})

    type = serializers.ChoiceField(choices=DATASET_TYPE, default=REAL_WORLD,
                                   help_text='Determines whether this dataset is real world or synthetic data.',
                                   style={'template': 'vadetisweb/parts/input/select_input.html'})

    spatial_data = serializers.ChoiceField(choices=DATASET_SPATIAL_DATA, default=NON_SPATIAL,
                                           help_text='Determines whether this dataset is spatial or not. Spatial data requires geographic information about the time series recording location.',
                                           style={'template': 'vadetisweb/parts/input/select_input.html'})

    csv_spatial_file = serializers.FileField(label='Spatial CSV File',
                                             help_text='The csv file of spatial information. It\'s only required if dataset is spatial.',
                                             validators=[FileExtensionValidator(allowed_extensions=['csv'])],
                                             style={'template': 'vadetisweb/parts/input/text_input.html'})

    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=DataSet.objects.all(),
                fields=['title', 'owner'],
                message='You already have a dataset with this title. Title and owner of a dataset must be distinct.'
            )
        ]

    def validate(self, data):
        """
        Object level validation
        """
        if data['spatial_data'] == SPATIAL and data['csv_spatial_file'] is None:
            raise serializers.ValidationError("A spatial dataset requires a CSV file about location information.")
        return data


class TrainingDatasetSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, max_length=128,
                                  help_text='Human readable title of the training dataset',
                                  style={'template': 'vadetisweb/parts/input/text_input.html'})

    original_dataset = DatasetChoicesViewSet()

    csv_file = serializers.FileField(required=True, label='CSV File', help_text='The csv file of the dataset',
                                     style={'template': 'vadetisweb/parts/input/text_input.html'})

    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=DataSet.objects.all(),
                fields=['title', 'owner'],
                message='You already have a dataset with this title. Title and owner of a dataset must be distinct.'
            )
        ]
