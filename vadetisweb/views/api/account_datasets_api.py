from rest_framework import status
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import redirect
from celery.utils import uuid

from vadetisweb.models import DataSet, UserTasks
from vadetisweb.serializers import DatasetSerializer, TrainingDatasetSerializer, DatasetTitleSerializer
from vadetisweb.utils import datatable_dataset_rows, write_to_tempfile
from vadetisweb.parameters import SPATIAL


class AccountDatasets(APIView):
    """
    Request information about datasets of current user
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        user = request.user
        data = []

        datasets = DataSet.objects.filter(owner=user, is_training_data=False)
        data = datatable_dataset_rows(data, datasets)

        return Response(data)


class AccountUploadDataset(APIView):
    """
    Upload a new dataset
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'vadetisweb/account/account_datasets_upload.html'

    def get(self, request):
        serializer = DatasetSerializer()
        return Response({'serializer': serializer}, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        serializer = DatasetSerializer(data=request.data)
        if serializer.is_valid():

            # handle dataset file
            dataset_file_raw = serializer.csv_file
            print("Dataset file received: ", dataset_file_raw.name)
            dataset_file = write_to_tempfile(dataset_file_raw)

            # handle spatial file
            if serializer.spatial_data == SPATIAL:
                spatial_file_raw = serializer.csv_spatial_file
                print("Spatial file received: ", spatial_file_raw.name)
                spatial_file = write_to_tempfile(spatial_file_raw)
            else:
                spatial_file = None

            type = serializer.type  # real world or synthetic
            type_of_data = serializer.type_of_data # same or different units

            # start import task
            user_tasks = UserTasks.objects.create(user=user)
            task_uuid = uuid()
            if serializer.spatial_data == SPATIAL:
                user_tasks.apply_async(TaskImportData, args=[user.username, dataset_file.name, title,
                                                             type, spatial_data],
                                       kwargs={'spatial_file_name': spatial_file.name}, task_id=task_uuid)
            else:
                user_tasks.apply_async(TaskImportData, args=[user.username, dataset_file.name, title,
                                                             type, spatial_data], task_id=task_uuid)

        else:
            return redirect('vadetisweb:account_datasets_upload')


class AccountTrainingDatasets(APIView):
    """
    Request information about datasets of current user
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [JSONRenderer]

    def get(self, request):
        user = request.user
        data = []

        datasets = DataSet.objects.filter(owner=user, is_training_data=True)
        data = datatable_dataset_rows(data, datasets)

        return Response(data)


class AccountUploadTrainingDataset(APIView):
    """
    Upload a new dataset
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'vadetisweb/account/account_training_datasets_upload.html'

    def get(self, request):
        serializer = TrainingDatasetSerializer()
        return Response({'serializer': serializer}, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user

        return redirect('vadetisweb:account_trainig_datasets_upload')