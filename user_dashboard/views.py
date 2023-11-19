from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from django.db.models import Q,Prefetch,Subquery
from admin_dashboard.models import MoviesDetails
from rest_framework import status
from datetime import datetime,timedelta
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
    Shows,
    ShowDates
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
        date = request.GET.get('dt')
        Q_Base = ~Q(status="RELAESED") & ( Q(shows__screen__theatre__location__place=location) | Q(shows__screen__theatre__location__district=location))
        q_query = Q()
        if q:
            q_query = Q(shows__language__name=q)
            Q_Base &= q_query
            if movie and cinemas and screen:
                if date :
                    response = self.get_screen_details(location, cinemas, screen,q,movie,date)
                else:
                    response = self.get_screen_details(location, cinemas, screen,q,movie)
                return Response(response, status=status.HTTP_200_OK)
            elif movie:
                today = datetime.today().date()
                three_days = today + timedelta(days=3)  
                Q_Base = (
                    Q(shows__movies__movie_name=movie) & ( 
                    Q(theatre__location__place=location)| 
                    Q(theatre__location__district=location)) &
                    Q(shows__language__name=q)&
                    Q(shows__show_dates__dates__range=(today,three_days))
                    )
                theatres = ScreenDetails.objects.filter(Q_Base).select_related("theatre").prefetch_related(
                Prefetch("shows_set",Shows.objects.select_related("movies", "language")
                .prefetch_related("show_time", Prefetch("show_dates",ShowDates.objects.filter(dates__range=(today,three_days)))))
               ).distinct()
                serializer = ScreenDetailsSerializer(theatres, many=True)
                return Response({"movies": serializer.data}, status=status.HTTP_200_OK)
        movies = MoviesDetails.objects.filter(Q_Base).distinct()
        serializer = MovieDetailsViewSerializer(movies, many=True)
        return Response({"movies": serializer.data}, status=status.HTTP_200_OK)

    def get_screen_details(self, location, cinemas, screen,q,movie,date=None):
        if date is None:
            date = datetime.today().date()
        
        Q_Base = (
            Q(screen__theatre__theatre_name=cinemas) &
            (Q(screen__theatre__location__place=location) |
            Q(screen__theatre__location__district=location)) &
            Q(screen__screen_number=screen) &
            Q(screen__shows__language__name=q) &
            Q(screen__shows__movies__movie_name=movie) &
            Q(screen__shows__show_dates__dates=date) 
        )
        screen_details = ScreenSeatArrangement.objects.filter(Q_Base).select_related("screen", "screen__theatre").prefetch_related(
            Prefetch("screen__shows_set",Shows.objects.select_related("movies","language").prefetch_related(
                "show_time","show_dates"
                ))).first()
        if screen_details is None:
            return {"data": "No data"}    
        serializer = ScreenSeatingSerializer(screen_details)
        return {"screen_details": serializer.data}


@permission_classes([AllowAny])
class TheatreSelectionView(APIView):
    def get(self, request):
        location = request.GET.get("search")
        cinemas = request.GET.get("cinemas")
        screen = request.GET.get("screen")
        if not cinemas and not screen:
            theatres = TheatreDetails.objects.filter(Q(location__place=location) | Q(location__district=location)).only("theatre_name", "address")
            serializer = TheatreViewByLocationSerializer(theatres, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if not screen:
            Q_Base = Q(theatre__theatre_name=cinemas) & ( Q(theatre__location__place=location) | Q(theatre__location__district=location))
            screens = ScreenDetails.objects.filter(Q_Base).select_related("theatre").prefetch_related("shows_set","shows_set__movies","shows_set__language","shows_set__show_time")
            serializer = ScreenDetailsSerializer(screens, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        Q_Base = Q(screen__theatre__theatre_name=cinemas) & (Q(screen__theatre__location__place=location)| Q(screen__theatre__location__district=location))& Q(screen__screen_number=screen)
        screen_details = ScreenSeatArrangement.objects.filter(Q_Base).select_related("screen", "screen__theatre").prefetch_related(
        Prefetch("screen__shows_set",Shows.objects.select_related("movies","language").prefetch_related(
            "show_time","show_dates"
            ))).first()       
        serializer = ScreenSeatingSerializer(screen_details)
        return Response(serializer.data, status=status.HTTP_200_OK)

 
