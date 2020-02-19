from rest_framework import status
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response

from vadetisweb.models import DataSet
from vadetisweb.serializers import AlgorithmSerializer

class SyntheticDatasets(APIView):
    """
    View for synthetic datasets
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'vadetisweb/datasets/synthetic/datasets.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class RealWorldDatasets(APIView):
    """
    View for real world datasets
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'vadetisweb/datasets/real-world/datasets.html'

    def get(self, request):
        return Response(status=status.HTTP_200_OK)


class SyntheticDataset(APIView):
    """
    View for a single synthetic dataset
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'vadetisweb/datasets/synthetic/dataset.html'

    def get(self, request, dataset_id):
        dataset = DataSet.objects.get(id=dataset_id)

        #algorithm = AlgorithmAnomalyDetection(dataset.id, 'Histogram')
        #serializer = AlgorithmSerializer(algorithm, many=False)
        #print(JSONRenderer().render(serializer.data))

        serializer = AlgorithmSerializer()

        return Response({
            'dataset' : dataset,
            'serializer' : serializer,
            }, status=status.HTTP_200_OK)


class RealWorldDataset(APIView):
    """
    View for a single real world dataset
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'vadetisweb/datasets/real-world/dataset.html'

    def get(self, request, dataset_id):
        dataset = DataSet.objects.get(id=dataset_id)

        return Response({
            'dataset' : dataset,
            }, status=status.HTTP_200_OK)
