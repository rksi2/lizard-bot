from rest_framework.views import APIView
from rest_framework.response import Response
from .disk import get_filenames


class FileListView(APIView):
    def get(self, request):
        files = get_filenames()
        return Response(files)
