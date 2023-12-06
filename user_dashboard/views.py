from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from django.db.models import Q , Prefetch , F
from admin_dashboard.models import MoviesDetails
from rest_framework import status
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from collections import defaultdict
from utils.mapping_variables import to_third_day,today, RELEASED, Available_dates
from rest_framework.permissions import (
    AllowAny,
)
from admin_dashboard.models import (
    Languages,
    MoviesDetails
    )
from theatre_dashboard.models import (
    ShowDates,
    ShowTime,
    TheatreDetails,
    ScreenDetails,
    ScreenSeatArrangement,
    Shows
)
from .serializers import (
    TicketBookingCreateUpdateSerializer,
)
from admin_dashboard.serializers import (
    MovieDetailListSerializer,
)
from theatre_dashboard.serializers import (
    ScreenSeatArrangementChoiceSerailizer,
    ShowDatesChoiceSerializer
    
)
from .models import (
    TicketBooking,
    BookingDetails,
    )
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

    

def screen_seat_details(Q_Base):
    return ScreenSeatArrangement.objects.filter(Q_Base).annotate(
        theatre_name=F('screen__theatre__theatre_name'),
        screen_number=F('screen__screen_number'),
        show_time=F('screen__shows__show_time__time'),
        show_dates=F('screen__shows__show_dates__dates'),
        movie_name=F('screen__shows__movies__movie_name'),
        language=F('screen__shows__language__name')).values(
            'seating',
            'screen_number',
            'show_time',
            'show_dates',
            'movie_name',
            'language',
            'theatre_name'
            ).first()  
        
        
    
    
def date_formatting(date):
    try:
        parsed_date = datetime.strptime(date, "%b %d %a")
        current_year = datetime.now().year
        parsed_date = parsed_date.replace(year=current_year)
        date = str(parsed_date)[:10]
        return date
    except:
        return date


@permission_classes([AllowAny])
class MovieSearching(APIView):
    name = openapi.Parameter('q',in_=openapi.IN_QUERY, description="movie name or director name",type=openapi.TYPE_STRING,)
    @swagger_auto_schema(
        operation_description="return list of movies by searching movie name or director name",
        manual_parameters=[name],
        responses={
            200:MovieDetailListSerializer,
            404:"Not Found",
            500:"errors"
        }
    )
    def get(self, reqeust):
        q = reqeust.GET.get("q")
        queryset = MoviesDetails.objects.filter(Q(movie_name__icontains=q) | Q(director__icontains=q)).values('id','movie_name','poster','director')
        if queryset:
            return Response(queryset, status=status.HTTP_200_OK)
        return Response({"data":"Not Found"}, status=status.HTTP_404_NOT_FOUND)




@permission_classes([AllowAny])
class MovieSelectionView(APIView):
    location = openapi.Parameter( 'search', in_=openapi.IN_QUERY, description='location', type=openapi.TYPE_STRING, )
    language = openapi.Parameter( 'q', in_=openapi.IN_QUERY, description='language', type=openapi.TYPE_STRING, )
    movie = openapi.Parameter( 'movie', in_=openapi.IN_QUERY, description='movies', type=openapi.TYPE_STRING, )
    cinemas = openapi.Parameter( 'cinemas', in_=openapi.IN_QUERY, description='theatre', type=openapi.TYPE_STRING, )
    screen = openapi.Parameter( 'screen', in_=openapi.IN_QUERY, description='screen number', type=openapi.TYPE_STRING, )
    date = openapi.Parameter( 'dt', in_=openapi.IN_QUERY, description='date', type=openapi.TYPE_STRING, )
    @swagger_auto_schema(
    manual_parameters=( location, language, movie, cinemas, screen,date),
    operation_description = f"return list of all recordes of theatre and details by location of user",
    responses = {
        200:ScreenSeatArrangementChoiceSerailizer,
        400:'bad syntax',
        500:'error'
        })
    def get(self, request):
        q = request.GET.get("q")
        location = request.GET.get("search")
        movie = request.GET.get("movie")
        cinemas = request.GET.get("cinemas")
        screen = request.GET.get("screen")
        date = request.GET.get('dt')
        times = request.GET.get('tm')
        
        if location:
            Q_Base = (
                ~Q(status=RELEASED) &
                (Q(shows__screen__theatre__location__place=location) |
                Q(shows__screen__theatre__location__district=location)) &
                Q(shows__show_dates__dates__range=(today,to_third_day))&
                Q(shows__screen__is_approved=True)
                )
        if movie and cinemas and screen:
            if q != 'all' and q is not None :
                response = self.get_screen_details(location ,cinemas,date,screen,movie,times,q)
            else:
                response = self.get_screen_details(location ,cinemas,date,screen,movie,times)
            return Response(response, status=status.HTTP_200_OK)
        elif movie: 
            Q_Base = (
                Q(shows__movies__movie_name=movie) & ( 
                Q(theatre__location__place=location)| 
                Q(theatre__location__district=location)) &
                Q(is_approved=True)&
                Q(shows__show_dates__dates__range=(today,to_third_day))
                )
            if q != 'all' and q is not None :  
                Q_Base &= Q(shows__language__name=q)
            response = self.get_theatre_screen_details(Q_Base,date) 
            return Response(response, status=status.HTTP_200_OK)       
        queryset = MoviesDetails.objects.filter(Q_Base).distinct().values('id', 'movie_name', 'poster', 'director', 'shows__language__name')
        print(queryset)
        languages = list(set(data['shows__language__name'] for data in queryset))
        unique_movies = set() 

        movie_data = []
        for data in queryset:
            movie_name = data.get('movie_name')
            director = data.get('director')
            movie_director_combination = (movie_name, director)

            if q == 'all' or data.get('shows__language__name') == q:
                if movie_director_combination not in unique_movies:
                    unique_movies.add(movie_director_combination)
                    movie_data.append(data)
           
        return Response({"movies": movie_data, 'languages': languages}, status=status.HTTP_200_OK)

    
    def get_theatre_screen_details(self,Q_Base,date):
        date = date_formatting(date)
        queryset = ScreenDetails.objects.filter(Q_Base).annotate(
            theatre_name=F('theatre__theatre_name'),
            show_time=F('shows__show_time__time'),
            language = F('shows__language__name'),
            show_dates = F('shows__show_dates__dates')
            ).values('screen_number',
                     'theatre_name',
                     'show_time',
                     'language',
                     'show_dates'             
                     ).distinct()

        current_screen_data = []
        grouped_data = defaultdict(list)
        date_data = []
        for screen_details in queryset:
            key = (screen_details['theatre_name'],screen_details['screen_number'],screen_details['language'])
            if str(screen_details.get('show_dates')) == date:
                grouped_data[key].append({
                    'show_time':screen_details['show_time']
                })
            formatted_date = datetime.strptime(str(screen_details.get('show_dates')), "%Y-%m-%d").strftime("%b %d %a")
            
            if formatted_date not in date_data:
                date_data.append(formatted_date)
        for key, items in grouped_data.items():
            current_screen_data.append({
                'theatre_name': key[0],
                'screen_number': key[1],
                'show_times': items,
            })
            
        response_data = {
            "data" : current_screen_data,
            "dates":date_data  
        }
        return response_data
    
   


    def get_screen_details(self,location ,cinemas,date,screen,movie,times,q=None):
        date = date_formatting(date)
        Q_Base = (
            Q(screen__theatre__theatre_name=cinemas) &
            (Q(screen__theatre__location__place=location) |
            Q(screen__theatre__location__district=location)) &
            Q(screen__screen_number=screen) &
            Q(screen__shows__movies__movie_name=movie) &
            Q(screen__shows__show_dates__dates=date) &
            Q(screen__shows__show_time__time=times) 
            )
        if q :
            Q_Base &= Q(screen__shows__language__name=q) 
        screen_details = screen_seat_details(Q_Base)   
        if screen_details is None:
            return {"data": "No data"}    
        return  screen_details



@permission_classes([AllowAny])
class TheatreSelectionView(APIView):
    location = openapi.Parameter( 'search', in_=openapi.IN_QUERY, description='location', type=openapi.TYPE_STRING, )
    cinemas = openapi.Parameter( 'cinemas', in_=openapi.IN_QUERY, description='theatre', type=openapi.TYPE_STRING, )
    screen = openapi.Parameter( 'screen', in_=openapi.IN_QUERY, description='screen number', type=openapi.TYPE_STRING, )
    date = openapi.Parameter( 'dt', in_=openapi.IN_QUERY, description='date', type=openapi.TYPE_STRING, )
    @swagger_auto_schema(
        tags={
            'users' },
        manual_parameters=(location,cinemas,screen,date),
        operation_description="return Theatre detials , screens , movies by users location",
        responses={
            200:ScreenSeatArrangementChoiceSerailizer,
            404:"Not Found",
            500:"errors"
        }
    )
    def get(self, request):
        location = request.GET.get("search")
        cinemas = request.GET.get("cinemas")
        screen = request.GET.get("screen")
        date = request.GET.get("dt")
        if not cinemas and not screen :
            queryset = TheatreDetails.objects.filter(
                Q(location__place=location) | 
                Q(location__district=location) & 
                Q(is_verified=True)).values("theatre_name", "address")
            if queryset:
                return Response(queryset, status=status.HTTP_200_OK)
            return Response({"msg":"No theatre In your Location"}, status=status.HTTP_404_NOT_FOUND)
                
        date = date_formatting(date)
        if date not in Available_dates:
            print(Available_dates)
            return Response({"error":"page not found"},status=status.HTTP_404_NOT_FOUND)
        if not screen and date: 
            queryset = ScreenDetails.objects.filter((
                Q(theatre__theatre_name=cinemas) & (
                Q(theatre__location__place=location) | 
                Q(theatre__location__district=location) & 
                Q(shows__show_dates__dates__range=(today,to_third_day))&
                Q(is_approved=True))
                )).annotate(
                theatre_name=F('theatre__theatre_name'),
                show_time=F('shows__show_time__time'),
                movie_name=F('shows__movies__movie_name'),
                show_dates=F('shows__show_dates__dates'),
                language=F('shows__language__name')).values(
                    "screen_number",
                    'theatre_name',
                    'show_time',
                    'movie_name',
                    'language',
                    'show_dates'
                    )

            current_screen_data = []
            date_data = []
                        
            for screen_details in queryset:
                screen_number = screen_details['screen_number']
                show_time = screen_details['show_time']
                language = screen_details['language']
                movie_name = screen_details['movie_name']

                if str(screen_details.get('show_dates')) == date:
                    existing_screen = next((screen for screen in current_screen_data if screen['screen_number'] == screen_number), None)

                    if existing_screen:
                        existing_screen['details'].append({
                            'show_time': show_time,
                            'language': language,
                            'movie_name': movie_name
                        })
                    else:
                        new_screen = {
                            'screen_number': screen_number,
                            'details': [{
                                'show_time': show_time,
                                'language': language,
                                'movie_name': movie_name
                            }]
                        }
                        current_screen_data.append(new_screen)



                formatted_date = datetime.strptime(str(screen_details.get('show_dates')), "%Y-%m-%d").strftime("%b %d %a")
                
                if formatted_date not in date_data :
                    date_data.append(formatted_date)
            response_data = {
                "data" : current_screen_data,
                "dates":date_data  
            }
            print(date_data)
            return Response(response_data, status=status.HTTP_200_OK)
        
    
    

class SingleMovieDetailsView(APIView):
    def get (self,request,movie,id):
        queryset = MoviesDetails.objects.filter(Q(movie_name=movie) & Q(id=id)).first()
        serializer = MovieDetailListSerializer(queryset)
        return Response({'data':serializer.data},status=status.HTTP_200_OK)
        
        
@permission_classes([IsAuthenticated])
class TicketBookingApi(APIView):
    def post(self,request):
        print(request.data)
        time_ = request.data.get("time")
        date_ = request.data.get("date")
        date = ShowDates.objects.get(dates=date_)
        time = ShowTime.objects.get(time=time_)
        request.data["time"] = time.id
        request.data["date"] = date.id
        print(request.data)
        serializer = TicketBookingCreateUpdateSerializer(data=request.data,context={"request":request})
        if serializer.is_valid():
            serializer.save()
            return Response({"msg":"ticket added..."},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request,):

        quesryset = TicketBooking.objects.filter(user=request.user).order_by("booking_date").first()
        serializer = TicketBookingCreateUpdateSerializer(quesryset,data=request.data)
        
        