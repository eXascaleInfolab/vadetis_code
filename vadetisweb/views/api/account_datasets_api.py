from rest_framework import status
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.parsers import MultiPartParser
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import redirect
from celery.utils import uuid

from vadetisweb.models import DataSet, UserTasks
from vadetisweb.serializers import DatasetSerializer, TrainingDatasetSerializer
from vadetisweb.utils import datatable_dataset_rows, write_to_tempfile
from vadetisweb.tasks import TaskImportData, TaskImportTrainingData
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
    parser_classes = [MultiPartParser]
    template_name = 'vadetisweb/account/account_datasets_upload.html'

    def get(self, request):
        serializer = DatasetSerializer(context={"request": self.request,})
        return Response({'serializer': serializer}, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        serializer = DatasetSerializer(data=request.data, context={"request": self.request,})
        if serializer.is_valid():

            # handle dataset file
            dataset_file_raw = serializer.validated_data['csv_file']
            print("Dataset file received: ", dataset_file_raw.name)
            dataset_file = write_to_tempfile(dataset_file_raw)

            # handle spatial file
            spatial_data = serializer.validated_data['spatial_data']
            if spatial_data == SPATIAL:
                spatial_file_raw = serializer.validated_data['csv_spatial_file']
                print("Spatial file received: ", spatial_file_raw.name)
                spatial_file = write_to_tempfile(spatial_file_raw)
            else:
                spatial_file = None

            title = serializer.validated_data['title']
            type = serializer.validated_data['type']  # real world or synthetic

            # start import task
            user_tasks, _ = UserTasks.objects.get_or_create(user=user)
            task_uuid = uuid()
            if spatial_data == SPATIAL:
                user_tasks.apply_async(TaskImportData, args=[user.username, dataset_file.name, title,
                                                             type, spatial_data],
                                       kwargs={'spatial_file_name': spatial_file.name}, task_id=task_uuid)
            else:
                user_tasks.apply_async(TaskImportData, args=[user.username, dataset_file.name, title,
                                                             type, spatial_data], task_id=task_uuid)

        else:
            print(serializer.errors)
            # return redirect('vadetisweb:account_datasets_upload')
            emessage = serializer.errors
            return Response({
                'status': 'Bad request',
                'message': emessage,
            }, status=status.HTTP_400_BAD_REQUEST)


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
        serializer = TrainingDatasetSerializer(context={"request": self.request,})
        return Response({'serializer': serializer}, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        serializer = TrainingDatasetSerializer(data=request.data, context={"request": self.request, })

        if serializer.is_valid():
            title = serializer.validated_data['title']
            owner = serializer.validated_data['original_dataset'].user
            original_dataset = serializer.validated_data['original_dataset']
            training_dataset_file_raw = serializer.validated_data['csv_file']

            # check if somebody tries to insert for another user
            if owner != request.user or original_dataset.owner != request.user:
                return redirect('vadetisweb:account_training_datasets_upload')

            else: # user is ok
                print("Training dataset file received: ", training_dataset_file_raw.name)
                training_dataset_file = write_to_tempfile(training_dataset_file_raw)

                user_tasks, _ = UserTasks.objects.get_or_create(user=user)

                # start import task
                task_uuid = uuid()
                user_tasks.apply_async(TaskImportTrainingData,
                                       args=[user.username, original_dataset.id, training_dataset_file.name,
                                             title], task_id=task_uuid)

        else:
            print(serializer.errors)
            # return redirect('vadetisweb:account_datasets_upload')
            emessage = serializer.errors
            return Response({
                'status': 'Bad request',
                'message': emessage,
            }, status=status.HTTP_400_BAD_REQUEST)
