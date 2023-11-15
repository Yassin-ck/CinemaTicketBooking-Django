from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly,AllowAny
from rest_framework.views import APIView
from django.db.models import Q
from admin_dashboard.models import MoviesDetails
from rest_framework import status
from .serializers import(
    MovieDetailsViewSerializer,
)


@permission_classes([AllowAny])
class MovieOrTheatreSearching(APIView):
    def get(self,reqeust):
        q = reqeust.GET.get('q')
        Q_base = Q(movie_name__icontains=q) | Q(director__icontains=q)
        if not q:
            pass   
        movies = MoviesDetails.objects.filter(Q_base)
        serializer = MovieDetailsViewSerializer(movies,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
        
            
