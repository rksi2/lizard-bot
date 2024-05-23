from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ScheduleRequestSerializer, ScheduleTeacherSeriaizer
from .disk import get_filenames, service, search_schedule_by_teacher


class ServiceView(APIView):
    def post(self, request):
        serializer = ScheduleRequestSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data["date"]
            group = serializer.validated_data["group"]
            try:
                result = service(name, group)
                if result is None:
                    return Response(
                        {"error": "No data returned from service."},
                        status=status.HTTP_204_NO_CONTENT,
                    )
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                # Логирование ошибки (можно использовать logging)
                print(f"Ошибка в функции service: {e}")
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScheduleTeacherView(APIView):
    def post(self, request):
        serializer = ScheduleTeacherSeriaizer(data=request.data)
        if serializer.is_valid():
            date = serializer.validated_data["date"]
            teachers_name = serializer.validated_data["group"]
            try:
                result = search_schedule_by_teacher(date, teachers_name)
                if result is None:
                    return Response(
                        {"error": "No data returned from service."},
                        status=status.HTTP_204_NO_CONTENT,
                    )
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                # Логирование ошибки (можно использовать logging)
                print(f"Ошибка в функции service: {e}")
                return Response(
                    {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FileListView(APIView):
    def get(self, request):
        files = get_filenames()
        return Response(files)
