from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from django.db.models import Q
from admin_dashboard.models import MoviesDetails
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    AllowAny,
)
from .serializers import (
    MovieDetailsViewSerializer,
    TheatreViewByLocationSerializer,
    ScreenDetailsSerializer,
    ScreenSeatingSerializer,
)
from theatre_dashboard.models import (
    TheatreDetails,
    ScreenDetails,
    ScreenSeatArrangement,
)


@permission_classes([AllowAny])
class MovieSearching(APIView):
    def get(self, reqeust):
        q = reqeust.GET.get("q")
        Q_base = Q(movie_name__icontains=q) | Q(director__icontains=q)
        if not q:
            pass
        movies = MoviesDetails.objects.filter(Q_base)
        serializer = MovieDetailsViewSerializer(movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes([AllowAny])
class MovieSelectionView(APIView):
    def get(self, request):
        q = request.GET.get("q")
        location = request.GET.get("search")
        movie = request.GET.get("movie")
        cinemas = request.GET.get("cinemas")
        screen = request.GET.get("screen")
        Q_Base = ~Q(status="RELAESED") & (Q(screendetails__theatre__location__place=location) | Q(screendetails__theatre__location__district=location))
        q_query = Q()
        if q:
            q_query = Q(languages__name=q)
            Q_Base &= q_query
            if movie and cinemas and screen:
                response = self.get_screen_details(location, cinemas, screen)
                return Response(response, status=status.HTTP_200_OK)
            elif movie:
                Q_Base = ( Q(movies__movie_name=movie) & ( Q(theatre__location__place=location) | Q(theatre__location__district=location) ) & Q(movies__languages__name=q) )
                theatres = ScreenDetails.objects.filter(Q_Base).only("screen_number", "shows", "theatre", "movies").select_related("theatre", "movies").prefetch_related("shows")
                serializer = ScreenDetailsSerializer(theatres, many=True)
                return Response({"movies": serializer.data}, status=status.HTTP_200_OK)
        movies = MoviesDetails.objects.filter(Q_Base).distinct()
        serializer = MovieDetailsViewSerializer(movies, many=True)
        return Response({"movies": serializer.data}, status=status.HTTP_200_OK)

    def get_screen_details(self, location, cinemas, screen):
        Q_Base =  Q(screen__theatre__theatre_name=cinemas) & ( Q(screen__theatre__location__place=location) | Q(screen__theatre__location__district=location)) & Q(screen__screen_number=screen)
        screen_details = ScreenSeatArrangement.objects.filter(Q_Base).only("seating").select_related("screen", "screen__movies").first()
        serializer = ScreenSeatingSerializer(screen_details)
        return {"screen_details": serializer.data}


@permission_classes([AllowAny])
class TheatreSelectionView(APIView):
    def get(self, request):
        location = request.GET.get("search")
        cinemas = request.GET.get("cinemas")
        screen = request.GET.get("screen")
        if not cinemas and screen:
            theatres = TheatreDetails.objects.filter( Q(location__place=location) | Q(location__district=location)).only("theatre_name", "address")
            serializer = TheatreViewByLocationSerializer(theatres, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if not screen:
            Q_Base = Q(theatre__theatre_name=cinemas) & (Q(theatre__location__place=location) | Q(theatre__location__district=location))
            screens = ScreenDetails.objects.filter(Q_Base).only("movies", "shows").select_related("movies").prefetch_related("shows")
            serializer = ScreenDetailsSerializer(screens, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        Q_Base = Q(screen__theatre__theatre_name=cinemas) & ( Q(screen__theatre__location__place=location) | Q(screen__theatre__location__district=location)) & Q(screen__screen_number=screen)
        screen_detials = ScreenSeatArrangement.objects.filter(Q_Base).only("seating").select_related("screen", "screen__movies").first()
        serializer = ScreenSeatingSerializer(screen_detials)
        return Response(serializer.data, status=status.HTTP_200_OK)



