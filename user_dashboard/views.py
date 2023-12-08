from django.core.cache import cache
import json
import hashlib
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from django.db.models import Q , Prefetch , F
from admin_dashboard.models import MoviesDetails
from rest_framework import status
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from collections import defaultdict
from utils.mapping_variables import (
    to_third_day,
    today,
    RELEASED,
    Available_dates,
    CACHE_PREFIX,
    row_alpha,
    CACHE_TIME,
    CACHED,
    BOOKED
    )
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
    
    def get(self, reqeust,hi=None):
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
        # print(times)
        Q_Base = Q()
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
            queryset = TicketBooking.objects.filter(
                Q(time__time=response['show_time']) &
                Q(date__dates = str(response['show_dates'])) &
                Q(show__screen__screen_number=response['screen_number']) &
                Q(show__screen__theatre__theatre_name=response['theatre_name'])
                  ) 
             
            booked_tickets = set()

            if queryset:
                for ticket in queryset:
                    booked_tickets = booked_tickets.union(set(ticket.tickets))  
            all_keys = cache.keys('*')
            all_data = {key: cache.get(key) for key in all_keys}
            for key, value in all_data.items():
                if key.startswith(CACHE_PREFIX) and \
                response['show_time'] == value.get('time') and \
                str(response['show_dates']) == str(value.get('date')) and \
                response['theatre_name'] == value.get('theatre_name') and \
                str(response['screen_number']) == str(value.get('screen_number')): 
                    print(value)
                    for ticket in set(value.get('tickets', [])):
                        index = row_alpha.index(ticket[0]) if ticket[0] in row_alpha else None
                        if index is not None:
                            response['seating'][index][int(ticket[1:])-1] = f'{ticket}{CACHED}' if value['cache_id'] == request.GET['cache_id'] else f'{ticket}{BOOKED}'
            for ticket in booked_tickets:
                index = row_alpha.index(ticket[0]) if ticket[0] in row_alpha else None
                response['seating'][index][int(ticket[1:])-1] = f'{ticket}{BOOKED}'

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
        languages = list(set(data['shows__language__name'] for data in queryset))
        unique_movies = set() 
        cache_key = "ticket_booking_api"

        # Check if the data is in the cache
        cached_data = cache.get(cache_key)
        print(cached_data)


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
        

class TicketCachingView(APIView):
   
    @staticmethod
    def hash_request_data(data):
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()

    @staticmethod
    def get_cache_key(request_data_hash):
        return f"{CACHE_PREFIX}_{request_data_hash}"
    
    
    
    def put(self, request):
            print(request.data)
            cache_id = request.data.get('cache_id')      
            if cache_id and request.data['tickets'][0][-1] != BOOKED:
                try:
                    key = cache.keys(f"{CACHE_PREFIX}_{cache_id}")[0]
                    value = cache.get(key)    
                    if value is not None:
                        if request.data['tickets'][0][-1] == CACHED:
                            value['tickets'].remove(request.data['tickets'][0][:-1])
                        else:
                            value['tickets'].extend(request.data['tickets'])
                            if len(value['tickets']) > 6:
                                value['tickets'].pop(0)
                        value['cache_id'] = cache_id
                        cache.set(key, value, CACHE_TIME)
                        return Response({'cache_id': cache_id}, status=200)
                except IndexError:
                    pass
            elif request.data['tickets'][0][-1] == BOOKED:
                return Response({"error":"Already Booked..."},status=status.HTTP_400_BAD_REQUEST)
            date = date_formatting(request.data.get('date'))
            request.data['date'] = date
            request_data_hash = TicketCachingView.hash_request_data(request.data)
            cache_key = TicketCachingView.get_cache_key(request_data_hash)
            cache.set(cache_key, request.data,CACHE_TIME)
            return Response({'cache_id': request_data_hash}, status=200)




import stripe
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeCheckoutView(APIView):
    
    def post(self,request):
        print(request.data,'lllllllllll')
        # data = stripe.Product.create(name=request.data['tickets'])
        # print(data)
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price': 'price_1OL0sHSCSC2S0RMY5gvcCfVL',
                        'quantity': 1,
                    },
                ],
                payment_method_types=['card'],
                mode='payment',
                success_url= settings.SITE_URL + 'payment/?success=true&session_id={CHECKOUT_SESSION_ID}',
                cancel_url= settings.SITE_URL + 'payment/?canceled=true',
            )
            print(checkout_session)
            return redirect(checkout_session.url)
        except Exception as e:
            print(e)
            return Response({"error":"something went Wrong"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
