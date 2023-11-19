from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from django.db.models import Q , Prefetch
from admin_dashboard.models import MoviesDetails
from rest_framework import status
from datetime import timedelta
from utils.mapping_variables import to_third_day,today
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



    

def screen_seat_details(Q_Base,query):
    return ScreenSeatArrangement.objects.filter(Q_Base).select_related("screen", "screen__theatre").prefetch_related(
        Prefetch("screen__shows_set",Shows.objects.select_related("movies","language").prefetch_related(
        "show_time",Prefetch("show_dates",query)))
        ).first()  
    

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
                response = self.get_screen_details(location, cinemas, screen,q,movie,date)
                # response_data = ({
                #     "status":status.HTTP_200_OK ,
                #     "movie": response['screen_details']["screen"]["shows_set"][0]["movies"]["movie_name"] ,
                #     "language": response['screen_details']["screen"]["shows_set"][0]["language"]["name"] ,
                #     "screen_number": response['screen_details']["screen"]["screen_number"] ,
                #     "date": [i["dates"] for i in response['screen_details']["screen"]["shows_set"][0]["show_dates"]],
                #     "time": [i["time"] for i in response['screen_details']["screen"]["shows_set"][0]["show_time"]] ,
                #     "seating": response['screen_details']["seating"] 
                # })
                return Response(response, status=status.HTTP_200_OK)
            elif movie:  
                Q_Base = (
                    Q(shows__movies__movie_name=movie) & ( 
                    Q(theatre__location__place=location)| 
                    Q(theatre__location__district=location)) &
                    Q(shows__language__name=q)&
                    Q(shows__show_dates__dates__range=(today,to_third_day))&
                    Q(screenseatarrangement__is_approved=True)
                    )
                theatres = ScreenDetails.objects.filter(Q_Base).select_related("theatre").prefetch_related(
                Prefetch("shows_set",Shows.objects.select_related("movies", "language")
                .prefetch_related("show_time", Prefetch("show_dates",ShowDates.objects.filter(dates__range=(today,to_third_day)))))
               ).distinct()
                serializer = ScreenDetailsSerializer(theatres, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        movies = MoviesDetails.objects.filter(Q_Base).distinct()
        serializer = MovieDetailsViewSerializer(movies, many=True)
        return Response({"movies": serializer.data}, status=status.HTTP_200_OK)

    def get_screen_details(self, location, cinemas, screen,q,movie,date=None):
        Q_Base = (
            Q(screen__theatre__theatre_name=cinemas) &
            (Q(screen__theatre__location__place=location) |
            Q(screen__theatre__location__district=location)) &
            Q(screen__screen_number=screen) &
            Q(screen__shows__language__name=q) &
            Q(screen__shows__movies__movie_name=movie) &
            Q(is_approved=True)
            )
        if date:
            Q_Base &= Q(screen__shows__show_dates__dates=date) 
            screen_details = screen_seat_details(Q_Base,ShowDates.objects.filter(dates=date))            
        else:
            screen_details = screen_seat_details(Q_Base,ShowDates.objects.filter(dates__range=(today,to_third_day)))            
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
        date = request.GET.get("dt")
        if not cinemas and not screen:
            theatres = TheatreDetails.objects.filter(Q(location__place=location) | Q(location__district=location)).only("theatre_name", "address")
            serializer = TheatreViewByLocationSerializer(theatres, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if not screen:
            Q_Base = Q(theatre__theatre_name=cinemas) & ( Q(theatre__location__place=location) | Q(theatre__location__district=location))
            screens = ScreenDetails.objects.filter(Q_Base).select_related("theatre").prefetch_related(
            Prefetch("shows_set",Shows.objects.select_related("movies","language")
            .prefetch_related("show_time",Prefetch("show_dates",ShowDates.objects.filter(dates__range=(today,to_third_day))))))
            serializer = ScreenDetailsSerializer(screens, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        Q_Base = Q(screen__theatre__theatre_name=cinemas) & (Q(screen__theatre__location__place=location)| Q(screen__theatre__location__district=location))& Q(screen__screen_number=screen)
        if date:        
            if date not in (str(today),str(today+timedelta(days=1)),str(today+timedelta(days=2)),str(to_third_day)):
                return Response({"error":"page not found"},status=status.HTTP_404_NOT_FOUND)
            Q_Base &= Q(screen__shows__show_dates__dates=date)
            screen_details = screen_seat_details(Q_Base,ShowDates.objects.filter(dates=date))
        else:
            screen_details = screen_seat_details(Q_Base,ShowDates.objects.filter(dates__range=(today,to_third_day)))
        serializer = ScreenSeatingSerializer(screen_details)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    




