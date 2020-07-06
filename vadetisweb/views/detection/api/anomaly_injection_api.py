from rest_framework import status
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.settings import api_settings
from drf_yasg.utils import swagger_auto_schema

from django.contrib import messages
from django.shortcuts import reverse
from django.db.models import Q

from vadetisweb.models import DataSet
from vadetisweb.serializers import InjectionSerializer, MessageSerializer
from vadetisweb.anomaly_algorithms import anomaly_injection
from vadetisweb.utils import dataset_to_json, get_settings, q_public_or_user_is_owner, get_type_from_dataset_json
from vadetisweb.factory import *


class InjectionView(APIView):
    """
    Request anomaly injection
    """
    renderer_classes = [JSONRenderer]

    @swagger_auto_schema(request_body=InjectionSerializer)
    def post(self, request, dataset_id):

        dataset = DataSet.objects.filter(Q(id=dataset_id),
                                         q_public_or_user_is_owner(request)).first()
        if dataset is None:
            messages.error(request, dataset_not_found_msg(dataset_id))
            response = Response({}, status=status.HTTP_404_NOT_FOUND)
            response['Location'] = reverse('vadetisweb:index')
            return response

        serializer = InjectionSerializer(context={'dataset_selected': dataset_id, 'request' : request}, data=request.data)

        if serializer.is_valid():
            data = {}
            settings = get_settings(request)
            df_inject, df_inject_class = anomaly_injection(serializer.validated_data)
            type = get_type_from_dataset_json(serializer.validated_data['dataset_series_json'])
            data['series'] = dataset_to_json(dataset, df_inject, df_inject_class, settings, type)
            return Response(data, status=status.HTTP_200_OK)

        else:
            json_messages = []
            json_message_utils.error(json_messages, 'Form was invalid')
            return response_invalid_form(serializer, json_messages)
