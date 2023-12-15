from django.core.cache import cache
import json
import hashlib
from django.utils.decorators import method_decorator
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework.views import APIView
from django.db.models import Q , F
from admin_dashboard.models import MoviesDetails
from rest_framework import status
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from collections import defaultdict

from authentications.models import MyUser
from .serializers import(
    TicketBookingCreateUpdateSerializer
    )
from utils.mapping_variables import (
    to_third_day,
    today,
    row_alpha,
    Available_dates,
    RELEASED,
    CACHE_PREFIX_TICKET_BOOKING,
    CACHE_TIME_TICKET_DETAILS,
    CACHE_TIME,
    CACHED,
    BOOKED,
    PROCESSING,
    CACHE_PREFIX_TICKET_DETAILS,
    )
from rest_framework.permissions import (
    AllowAny,
)
from admin_dashboard.models import (
    Languages,
    MoviesDetails
    )
from theatre_dashboard.models import (
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
    
)
from .models import (
    TicketBooking,
    )
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

#STRIPE
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY

#whatsapp_message_sending
from authentications.modules.utils import send_whatsapp_message

    

def screen_seat_details(Q_Base):
    print(Q_Base)
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
            print(request.query_params)
            if queryset:
                for ticket in queryset:
                    booked_tickets = booked_tickets.union(set(ticket.tickets))  
            all_keys = cache.keys('*')
            all_data = {key: cache.get(key) for key in all_keys}
            for key, value in all_data.items():
                if key.startswith(CACHE_PREFIX_TICKET_BOOKING) and \
                response['show_time'] == value.get('time') and \
                str(response['show_dates']) == str(value.get('date')) and \
                response['theatre_name'] == value.get('theatre_name') and \
                str(response['screen_number']) == str(value.get('screen_number')): 
                    print(value)
                    for ticket in set(value.get('tickets', [])):
                        index = row_alpha.index(ticket[0]) if ticket[0] in row_alpha else None
                        if index is not None:
                            response['seating'][index][int(ticket[1:])-1] = f'{ticket}{CACHED}' if request.GET.get('cache_id') is not None and value['cache_id'] == request.GET.get('cache_id') else f'{ticket}{BOOKED}'
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
        print(screen_details)
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
        return f"{CACHE_PREFIX_TICKET_BOOKING}_{request_data_hash}"
    
    
    
    def put(self, request):
        print(request.data)
        cache_id = request.data.get('cache_id')      
        if cache_id and request.data['tickets'][0][-1] != BOOKED:
            try:
                key = cache.keys(f"{CACHE_PREFIX_TICKET_BOOKING}_{cache_id}")[0]
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
    
    
    def delete(self,request):
        print(request.data,'request.data')
        cache.delete(f"{CACHE_PREFIX_TICKET_BOOKING}_{request.data.get('cache_id')}")
        return Response({"msg":"deleted"},status=status.HTTP_200_OK)
        

class StripeCheckoutView(APIView):   
    def post(self,request):
        print(request.user)
        cache_id  = request.GET.get('cache_id')
        print(cache_id)
        user_profile = None
        if request.user.is_authenticated:
            try:
                user_profile = request.user.userprofile
            except:
                pass
        
        if cache_id is not None:
            key = f"{CACHE_PREFIX_TICKET_BOOKING}_{cache_id}"
            cached_data = cache.get(key)
            cached_data["payment"] = PROCESSING
            cache.set(key, cached_data, None)
            show_price = Shows.objects.filter(
                Q(screen__theatre__theatre_name=cached_data['theatre_name']) &
                Q(screen__screen_number=cached_data['screen_number']) &
                Q(show_dates__dates=cached_data['date']) &
                Q(show_time__time=cached_data['time'])
                ).values('screen__ticket_rate','movies__movie_name').first()

            print(show_price)
            data = stripe.Product.create(
                name="Total Amount",
                default_price_data={
                    "unit_amount":show_price['screen__ticket_rate']*100,
                    "currency": "inr",
                },
                expand=["default_price"],
                )
            customer = None
            if request.user.is_authenticated:
                customer = stripe.Customer.create(
                    email = request.user.email,
                    phone = user_profile.phone
                )
        
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price': data['default_price']['id'],
                        'quantity': len(cached_data['tickets']),
                    },
                ],
                phone_number_collection={"enabled": True},
                payment_method_types=['card'], 
                mode='payment',
                metadata={'cache_id':key},
                customer=customer.id if customer is not None else None,
                success_url= settings.SITE_URL + '/payment/?success=true&session_id={CHECKOUT_SESSION_ID}',
                cancel_url= settings.SITE_URL + '/payment/?canceled=true',
            )
            print(checkout_session) 
            return Response(checkout_session.url,status=status.HTTP_200_OK)
        except Exception as e:
            cache.delete(f"{CACHE_PREFIX_TICKET_BOOKING}_{request.data.get('cache_id')}")
            print(e)
            return Response({"error":"something went Wrong"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TicketBookingApi(APIView):
    def get(self,request):
        session_id = request.GET.get('session_id')
        if session_id:
            data = stripe.checkout.Session.retrieve(session_id)
            cached_ticket_data = cache.get(f"{CACHE_PREFIX_TICKET_DETAILS}_{data['customer_details']['email']}")
            if cached_data is None and cached_ticket_data is not None:
                return Response(cached_ticket_data,status=status.HTTP_200_OK)
            elif cached_data is None and cached_ticket_data is None:
                return Response({"msg":"session cleared..."},status=status.HTTP_400_BAD_REQUEST)
            key = data['metadata']['cache_id']
            cached_data = cache.get(key)
            time = cached_data['time']
            date = cached_data['date']
            theatre_name = cached_data['theatre_name']
            screen_number = cached_data['screen_number']
            payment_data = Shows.objects.filter(
                Q(screen__theatre__theatre_name=theatre_name) &
                Q(screen__screen_number=screen_number) &
                Q(show_dates__dates=date) &
                Q(show_time__time=time)
                ).values('show_dates__dates','show_time__time',show=F('id'),time=F('show_time__id'),date=F('show_dates__id')).first()
            payment_data['user'] = request.user.id
            payment_data['tickets'] =cached_data['tickets']
            payment_data['amount_paid'] = str(data['amount_total']/100)
            payment_data['payment_id'] = data['payment_intent']
            serializer = TicketBookingCreateUpdateSerializer(data=payment_data)
            if serializer.is_valid():
                serializer.save()
                try:
                    send_whatsapp_message(data['customer_details']['phone'])
                except:
                    pass
                cache.delete(key)
                self.user_checking(data['customer_details']['email'])
                response_data = {
                    'tickets' : serializer.data['tickets'],
                    'date': payment_data['show_dates__dates'],
                    'time': payment_data['show_time__time'],
                    'amount': serializer.data['amount_paid'],
                    'theatre':theatre_name,
                    'screen':screen_number,
                    'booked_date':today
                }
                cache.set(f"{CACHE_PREFIX_TICKET_DETAILS}_{data['customer_details']['email']}", response_data,CACHE_TIME_TICKET_DETAILS)
                return Response(response_data,status=status.HTTP_200_OK)
            else:
                cache.delete(key)
                return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        else:
            cache_id = request.GET.get('cache_id')
            key = f"{CACHE_PREFIX_TICKET_BOOKING}_{cache_id}"
            cache.delete(key)
            return Response({'error':'Error while payment processing...'},status=status.HTTP_400_BAD_REQUEST)
  
    
    def user_checking(self,data):
        MyUser.objects.get_or_create(email=data)
        return

        

@permission_classes([IsAuthenticated])
class BookedView(APIView):
    def get(self,request):
        queryset = TicketBooking.objects.filter(user=request.user).order_by('-id').values(
            'booking_date',
            'tickets',
            'amount_paid',
            show_date=F('date__dates'),
            screen=F('show__screen__screen_number'),
            theatre=F('show__screen__theatre__theatre_name'),
            show_time=F('time__time'),
            movie=F('show__movies__movie_name'),
            language=F('show__language__name'),      
            )
        if queryset:
            return Response(queryset,status=status.HTTP_200_OK)
        return Response({"msg":"no bookings.."},status=status.HTTP_400_BAD_REQUEST)
        
    