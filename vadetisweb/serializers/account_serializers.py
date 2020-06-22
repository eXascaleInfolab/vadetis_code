import numpy as np
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from allauth.account import app_settings
from allauth.account.forms import get_adapter as get_account_adapter, filter_users_by_email
from allauth.socialaccount.models import SocialAccount

from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.core.validators import MaxLengthValidator, MaxValueValidator, MinValueValidator, RegexValidator, \
    FileExtensionValidator
from django.urls import reverse

from vadetisweb.models import UserSetting, DataSet, User
from vadetisweb.parameters import REAL_WORLD, DATASET_TYPE, BOOLEAN_SELECTION
from vadetisweb.fields import UserOriginalDatasetField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)


class DatasetImportSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, max_length=128, help_text='Human readable title of the dataset',
                                  style={'template': 'vadetisweb/parts/input/text_input.html'})

    csv_file = serializers.FileField(required=True, label='CSV File', help_text='The csv file of the dataset',
                                     validators=[FileExtensionValidator(allowed_extensions=['csv'])],
                                     style={'template': 'vadetisweb/parts/input/file_input.html'})

    owner = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())

    type = serializers.ChoiceField(choices=DATASET_TYPE, default=REAL_WORLD,
                                   help_text='Determines whether this dataset is real world or synthetic data.',
                                   style={'template': 'vadetisweb/parts/input/select_input.html'})

    public = serializers.BooleanField(default=True,
                                      help_text='Determines if this dataset is available to other users',
                                      style={'template': 'vadetisweb/parts/input/checkbox_input.html'})

    csv_spatial_file = serializers.FileField(label='Spatial CSV File',
                                             required=False,
                                             allow_empty_file=True,
                                             help_text='The csv file of spatial information. If geographic information about the time series of this dataset is available, you can provide this information here.',
                                             validators=[FileExtensionValidator(allowed_extensions=['csv'])],
                                             style={'template': 'vadetisweb/parts/input/file_input.html'})

    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=DataSet.objects.all(),
                fields=['title', 'owner'],
                message='You already have a dataset with this title. Title and owner of a dataset must be distinct.'
            )
        ]


class TrainingDatasetImportSerializer(serializers.Serializer):
    title = serializers.CharField(required=True, max_length=128,
                                  help_text='Human readable title of the training dataset',
                                  style={'template': 'vadetisweb/parts/input/text_input.html'})

    owner = UserSerializer(read_only=True, default=serializers.CurrentUserDefault())

    original_dataset = UserOriginalDatasetField(label="Associated dataset", required=True,
                                                style={'template': 'vadetisweb/parts/input/select_input.html'})

    public = serializers.BooleanField(default=True,
                                      help_text='Determines if this dataset is available to other users',
                                      style={'template': 'vadetisweb/parts/input/checkbox_input.html'})

    csv_file = serializers.FileField(required=True, label='CSV File', help_text='The csv file of the dataset',
                                     validators=[FileExtensionValidator(allowed_extensions=['csv'])],
                                     style={'template': 'vadetisweb/parts/input/file_input.html'})

    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=DataSet.objects.all(),
                fields=['title', 'owner'],
                message='You already have a dataset with this title. Title and owner of a dataset must be distinct.'
            )
        ]


class UserSettingSerializer(serializers.ModelSerializer):
    """
    The form for the settings of the user
    """

    highcharts_height = serializers.IntegerField(default=500,
                                                 help_text='Value in pixels, Default: 500',
                                                 validators=[MinValueValidator(250)],
                                                 style={'template': 'vadetisweb/parts/input/text_input.html'})

    legend_height = serializers.IntegerField(default=100,
                                             help_text='Value in pixels, Default: 100',
                                             validators=[MinValueValidator(50)],
                                             style={'template': 'vadetisweb/parts/input/text_input.html'})

    color_outliers = serializers.CharField(max_length=7, default="#FF0000",
                                           help_text='Default: #FF0000, the RGB color used to mark outliers',
                                           validators=[RegexValidator(regex='^#(?:[0-9a-fA-F]{3}){1,2}$')],
                                           style={'template': 'vadetisweb/parts/input/text_input.html',
                                                  'input_type': 'color'})

    color_clusters = serializers.CharField(max_length=7, default="#0000FF",
                                           help_text='Default: #0000FF, the RGB color used to mark LISA clusters of high or low values',
                                           validators=[RegexValidator(regex='^#(?:[0-9a-fA-F]{3}){1,2}$')],
                                           style={'template': 'vadetisweb/parts/input/text_input.html',
                                                  'input_type': 'color'})

    color_true_positive = serializers.CharField(max_length=7, default="#008800",
                                                help_text='Default: #008800, the RGB color used to mark true positives',
                                                validators=[RegexValidator(regex='^#(?:[0-9a-fA-F]{3}){1,2}$')],
                                                style={'template': 'vadetisweb/parts/input/text_input.html',
                                                       'input_type': 'color'})

    color_false_positive = serializers.CharField(max_length=7, default="#FF0000",
                                                 help_text='Default: #FF0000, the RGB color used to mark false positives',
                                                 validators=[RegexValidator(regex='^#(?:[0-9a-fA-F]{3}){1,2}$')],
                                                 style={'template': 'vadetisweb/parts/input/text_input.html',
                                                        'input_type': 'color'})

    color_false_negative = serializers.CharField(max_length=7, default="#0000FF",
                                                 help_text='Default: #0000FF, the RGB color used to mark false negatives',
                                                 validators=[RegexValidator(regex='^#(?:[0-9a-fA-F]{3}){1,2}$')],
                                                 style={'template': 'vadetisweb/parts/input/text_input.html',
                                                        'input_type': 'color'})

    round_digits = serializers.IntegerField(default=3,
                                            help_text='Must be a number between 1 and 6',
                                            validators=[MinValueValidator(1), MaxValueValidator(6)],
                                            style={'template': 'vadetisweb/parts/input/text_input.html',
                                                   'class': 'form-group-last'})

    class Meta:
        model = UserSetting
        fields = ('highcharts_height', 'legend_height', 'color_outliers', 'color_clusters',
                  'color_true_positive', 'color_false_positive', 'color_false_negative', 'round_digits')


class AccountDatasetDataTablesSerializer(serializers.ModelSerializer):
    title = serializers.CharField(read_only=True)
    timeseries = serializers.SerializerMethodField()
    values = serializers.SerializerMethodField()
    frequency = serializers.CharField(read_only=True)
    spatial = serializers.SerializerMethodField()
    public = serializers.BooleanField(read_only=True)
    training_datasets = serializers.SerializerMethodField()
    actions = serializers.SerializerMethodField()

    def get_timeseries(self, obj):
        return obj.timeseries_set.count()

    def get_values(self, obj):
        np_num_values = obj.dataframe.count().sum()
        return int(np_num_values) if isinstance(np_num_values, np.integer) else np_num_values

    def get_spatial(self, obj):
        return all(ts.location is not None for ts in obj.timeseries_set.all())

    def get_training_datasets(self, obj):
        return obj.training_dataset.count()

    def get_actions(self, obj):
        if obj.type == REAL_WORLD:
            view_link = reverse('vadetisweb:display_real_world_dataset', args=[obj.id])
            detection_link = reverse('vadetisweb:detection_real_world_dataset', args=[obj.id])
        else:
            view_link = reverse('vadetisweb:display_synthetic_dataset', args=[obj.id])
            detection_link = reverse('vadetisweb:detection_synthetic_dataset', args=[obj.id])
        return '<a href="%s">View</a> <a href="%s">Detection</a>' % (view_link, detection_link)

    class Meta:
        model = DataSet
        fields = (
            'title', 'timeseries', 'values', 'frequency', 'spatial', 'public', 'training_datasets', 'actions'
        )


class AccountDatasetSearchSerializer(serializers.Serializer):
    """
        Order is important and must refer to the order in the datatables serializer
    """
    title = serializers.CharField(write_only=True,
                                  style={'template': 'vadetisweb/parts/input/text_input.html',
                                         'class': 'col-lg-3 kt-margin-b-10-tablet-and-mobile',
                                         'input_class' : 'search-input',
                                         'col_index' : '0' })

    timeseries = serializers.IntegerField(write_only=True,
                                          style={'template': 'vadetisweb/parts/input/text_input.html',
                                                 'input_type': 'number',
                                                 'class': 'col-lg-3 kt-margin-b-10-tablet-and-mobile',
                                                 'input_class' : 'search-input',
                                                 'col_index': '1',
                                                 'step': 'any'})

    values = serializers.IntegerField(write_only=True,
                                      style={'template': 'vadetisweb/parts/input/text_input.html',
                                             'input_type' : 'number',
                                             'class': 'col-lg-3 kt-margin-b-10-tablet-and-mobile',
                                             'input_class': 'search-input',
                                             'col_index': '2',
                                             'step': 'any'})

    frequency = serializers.CharField(write_only=True,
                                      style={'template': 'vadetisweb/parts/input/text_input.html',
                                             'class': 'col-lg-3 kt-margin-b-10-tablet-and-mobile',
                                             'input_class' : 'search-input',
                                             'col_index' : '3' })

    spatial = serializers.ChoiceField(write_only=True, choices=BOOLEAN_SELECTION,
                                      style={'template': 'vadetisweb/parts/input/select_input.html',
                                             'class': 'col-lg-3 kt-margin-b-10-tablet-and-mobile',
                                             'input_class' : 'search-input',
                                             'col_index' : '4' })

    public = serializers.ChoiceField(write_only=True, choices=BOOLEAN_SELECTION,
                                     style={'template': 'vadetisweb/parts/input/select_input.html',
                                            'class': 'col-lg-3 kt-margin-b-10-tablet-and-mobile',
                                            'input_class' : 'search-input',
                                            'col_index' : '5' })

    training_datasets = serializers.IntegerField(write_only=True,
                                                 style={'template': 'vadetisweb/parts/input/text_input.html',
                                                        'input_type': 'number',
                                                        'class': 'col-lg-3 kt-margin-b-10-tablet-and-mobile',
                                                        'input_class' : 'search-input',
                                                        'col_index' : '6'})

    def __init__(self, *args, **kwargs):
        super(AccountDatasetSearchSerializer, self).__init__(*args, **kwargs)


class AccountTrainingDatasetDataTablesSerializer(serializers.ModelSerializer):
    title = serializers.CharField(read_only=True)
    timeseries = serializers.SerializerMethodField()
    values = serializers.SerializerMethodField()
    frequency = serializers.CharField(read_only=True)
    public = serializers.BooleanField(read_only=True)
    spatial = serializers.SerializerMethodField()

    def get_timeseries(self, obj):
        return obj.timeseries_set.count()

    def get_values(self, obj):
        np_num_values = obj.dataframe.count().sum()
        return int(np_num_values) if isinstance(np_num_values, np.integer) else np_num_values

    def get_spatial(self, obj):
        return all(ts.location is not None for ts in obj.timeseries_set.all())

    class Meta:
        model = DataSet
        fields = (
            'title', 'timeseries', 'values', 'frequency', 'public', 'spatial',
        )


class AccountTrainingDatasetSearchSerializer(serializers.Serializer):
    """
        Order is important and must refer to the order in the datatables serializer
    """
    title = serializers.CharField(write_only=True,
                                  style={'template': 'vadetisweb/parts/input/text_input.html',
                                         'class': 'col-lg-3 kt-margin-b-10-tablet-and-mobile',
                                         'input_class' : 'search-input',
                                         'col_index' : '0' })

    timeseries = serializers.IntegerField(write_only=True,
                                          style={'template': 'vadetisweb/parts/input/text_input.html',
                                                 'input_type': 'number',
                                                 'class': 'col-lg-3 kt-margin-b-10-tablet-and-mobile',
                                                 'input_class' : 'search-input',
                                                 'col_index': '1',
                                                 'step': 'any'})

    values = serializers.IntegerField(write_only=True,
                                      style={'template': 'vadetisweb/parts/input/text_input.html',
                                             'input_type' : 'number',
                                             'class': 'col-lg-3 kt-margin-b-10-tablet-and-mobile',
                                             'input_class': 'search-input',
                                             'col_index': '2',
                                             'step': 'any'})

    frequency = serializers.CharField(write_only=True,
                                      style={'template': 'vadetisweb/parts/input/text_input.html',
                                             'class': 'col-lg-3 kt-margin-b-10-tablet-and-mobile',
                                             'input_class' : 'search-input',
                                             'col_index' : '3' })

    spatial = serializers.ChoiceField(write_only=True, choices=BOOLEAN_SELECTION,
                                      style={'template': 'vadetisweb/parts/input/select_input.html',
                                             'class': 'col-lg-3 kt-margin-b-10-tablet-and-mobile',
                                             'input_class' : 'search-input',
                                             'col_index' : '4' })

    public = serializers.ChoiceField(write_only=True, choices=BOOLEAN_SELECTION,
                                     style={'template': 'vadetisweb/parts/input/select_input.html',
                                            'class': 'col-lg-3 kt-margin-b-10-tablet-and-mobile',
                                            'input_class' : 'search-input',
                                            'col_index' : '5' })


    def __init__(self, *args, **kwargs):
        super(AccountTrainingDatasetSearchSerializer, self).__init__(*args, **kwargs)


class AccountUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(label='Username', required=True,
                                     help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.',
                                     style={'template': 'vadetisweb/parts/input/text_input.html'})

    first_name = serializers.CharField(label='First Name', required=False,
                                       style={'template': 'vadetisweb/parts/input/text_input.html'})

    last_name = serializers.CharField(label='Last Name', required=False,
                                      style={'template': 'vadetisweb/parts/input/text_input.html'})

    email = serializers.EmailField(label='E-Mail Address', required=True,
                                   style={'template': 'vadetisweb/parts/input/text_input.html'})

    def validate_email(self, value):
        value = get_account_adapter().clean_email(value)
        errors = {
            "different_account": "This e-mail address is already associated with another account.",
        }
        users = filter_users_by_email(value)
        on_diff_account = [u for u in users if u.pk != self.instance.pk]

        if on_diff_account and app_settings.app_settings.UNIQUE_EMAIL:
            raise serializers.ValidationError(errors["different_account"])
        return value

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email',)


class AccountPasswordSerializer(serializers.Serializer):
    oldpassword = serializers.CharField(label='Current Password', write_only=True, required=True,
                                        allow_null=False, allow_blank=False,
                                        style={'input_type': 'password',
                                               'template': 'vadetisweb/parts/input/text_input.html'})

    password1 = serializers.CharField(label='New Password', write_only=True, required=True,
                                      allow_null=False, allow_blank=False,
                                      style={'input_type': 'password',
                                             'template': 'vadetisweb/parts/input/text_input.html'})

    password2 = serializers.CharField(label='New Password (again)', write_only=True, required=True,
                                      allow_null=False, allow_blank=False,
                                      style={'input_type': 'password',
                                             'template': 'vadetisweb/parts/input/text_input.html'})

    def validate_oldpassword(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Please type your current password.')
        return value

    def validate(self, data):

        # validate password match
        password1 = data['password1']
        password2 = data['password2']
        if (password1 and password2) and password1 != password2:
            raise serializers.ValidationError({'password2': "You must type the same password each time."})

        # validate password
        try:
            # If the password is valid, returns ``None``
            password_validation.validate_password(password1)
        except ValidationError as error:
            raise serializers.ValidationError({'password2': error.messages})

        return data

    def save(self):
        user = self.context['request'].user
        get_account_adapter().set_password(user, self.validated_data["password1"])

    def __init__(self, *args, **kwargs):
        super(AccountPasswordSerializer, self).__init__(*args, **kwargs)


class AccountSocialDisconnectSerializer(serializers.Serializer):
    account = serializers.PrimaryKeyRelatedField(queryset=SocialAccount.objects.none(),
                                                 required=True,
                                                 style={'template': 'vadetisweb/parts/input/select_input.html'})

    def __init__(self, *args, **kwargs):
        super(AccountSocialDisconnectSerializer, self).__init__(*args, **kwargs)


class AccountDeleteSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(initial=True, label='Account is active',
                                         help_text='Uncheck this box and save if you are sure you want to delete your account.',
                                         style={'template': 'vadetisweb/parts/input/checkbox_input.html'})

    class Meta:
        model = User
        fields = ('is_active',)

    def __init__(self, *args, **kwargs):
        super(AccountDeleteSerializer, self).__init__(*args, **kwargs)
