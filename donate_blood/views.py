from django.shortcuts import render,redirect
from rest_framework import viewsets
from rest_framework import permissions
from . import models
from . import serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from django.http import JsonResponse, HttpResponse , HttpResponseRedirect
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view
# token 
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
# for sending email
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.shortcuts import redirect

from sslcommerz_lib import SSLCOMMERZ 
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import random
import string

# Create your views here.

class DonationRequestViewset(viewsets.ModelViewSet):
    
    queryset = models.DonationRequest.objects.all()
    # queryset = models.DonationRequest.objects.exclude(status='Completed')
    serializer_class = serializers.DonationRequestSerializer  
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user= self.request.user) 


    def get_queryset(self):
        queryset = super().get_queryset()
        blood_group = self.request.query_params.get('blood_group', None)
        if blood_group is not None:
            queryset = queryset.filter(blood_group=blood_group)
        return queryset

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_requests(self, request): 
        user = request.user
        blood_group = request.query_params.get('blood_group', None)
        queryset = models.DonationRequest.objects.filter(user=user)
        if blood_group is not None:
            queryset = queryset.filter(blood_group=blood_group)
        serializer = serializers.DonationRequestSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def request_accepted_by_me(self, request): 
        user = request.user
        blood_group = request.query_params.get('blood_group', None)
        queryset = models.DonationRequest.objects.filter(accepted_by=user)
        serializer = serializers.DonationRequestSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def blood_group_filter(self, request):
        blood_group = request.query_params.get('blood_group', None)
        queryset = models.DonationRequest.objects.filter( is_completed=False, is_accepted = False)
        if blood_group is not None:
            queryset = queryset.filter(blood_group=blood_group)
        serializer = serializers.DonationRequestSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





class DonationHistoryViewSet(viewsets.ModelViewSet):
    queryset = models.DonatioHistory.objects.all()
    serializer_class = serializers.DonationHistorySerializer  
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return models.DonatioHistory.objects.filter(user=self.request.user)

class DonationAcceptedViewSet(viewsets.ModelViewSet):
    queryset = models.DonationAccepted.objects.all()
    serializer_class = serializers.DonationAcceptedSerializer  
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return models.DonationAccepted.objects.filter(user=self.request.user)
        
        # return models.DonatioHistory.objects.all()

class UserAccountDetailView(generics.RetrieveAPIView):
    queryset = models.UserAccount.objects.all()
    serializer_class = serializers.UserAccountSerializer

    def get(self, request, user_id):
        try:
            # Get the UserAccount linked to the specified User ID
            user_account = models.UserAccount.objects.get(user__id=user_id)
            serializer = self.get_serializer(user_account)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.UserAccount.DoesNotExist:
            return Response({"detail": "UserAccount not found"}, status=status.HTTP_404_NOT_FOUND)


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.UserAccount.objects.all()

    serializer_class = serializers.UserAccountSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        # return super().get_queryset().filter(is_available_for_donation=True)
        return super().get_queryset()

    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Update using the UserAccountSerializer
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

        
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def blood_group_filter(self, request):
        blood_group = request.query_params.get('blood_group', None)
        queryset = self.get_queryset() 
        if blood_group is not None:
            queryset = queryset.filter(blood_group=blood_group)
        serializer = serializers.UserAccountSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRegistrationApiView(APIView):
    serializer_class = serializers.RegistrationSerializer
    permission_classes = [AllowAny] 

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                print("uid ", uid)
                confirm_link = f"https://lifelink-five.vercel.app/donate_blood/active/{uid}/{token}"
                email_subject = "Confirm Your Email"
                email_body = render_to_string('confirm_email.html', {'confirm_link': confirm_link})

                email = EmailMultiAlternatives(email_subject, '', to=[user.email])
                email.attach_alternative(email_body, "text/html")
                email.send()
                return Response("Check your mail for confirmation")
            except ValidationError as e:
                return Response(e.detail, status=400)
        return Response(serializer.errors, status=400)


def activate(request, uid64, token):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    try:
        uid = urlsafe_base64_decode(uid64).decode()
        user = User._default_manager.get(pk=uid)
    except(User.DoesNotExist):
        user = None 
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('https://fabulous-trifle-8657b5.netlify.app/login')
    else:
        return redirect('register')

@api_view(['GET', 'POST'])
def accept(request, donation_request_id):
    print(donation_request_id)
    try:

        donation_request = models.DonationRequest.objects.get(pk= donation_request_id)
        print(request.user)
        user_account = models.UserAccount.objects.get(user=request.user)
        

        if request.user == donation_request.user:
            return JsonResponse({'message': 'You cannot accept your own donation request.'}, status=400)

        
        else:
            if user_account.blood_group == donation_request.blood_group:
                donation_request.is_accepted = True
                donation_request.accepted_by = request.user
                donation_request.status = 'Accepted'
                donation_request.save() 
                # models.DonationAccepted.objects.create(user=request.user, donation_request=donation_request) 
                models.DonatioHistory.objects.create(user=request.user, donation_request=donation_request, status='Accepted')
                return JsonResponse({'message': 'Donation Request Accepted'}, status=200)
            else:
                return JsonResponse({'message': 'Blood Group Not Matched'}, status=404)
              
    except(donation_request.DoesNotExist):
        return JsonResponse({'message': 'Donation Request not found'}, status=404)

@api_view(['GET', 'POST'])
def cancel(request, donation_request_id):
    try:
        donation_request = models.DonationRequest.objects.get(pk= donation_request_id)
        donation_request.is_accepted = False
        donation_request.status = 'Canceled'
        donation_request.accepted_by = None
        donation_request.save()
        models.DonatioHistory.objects.create(user=request.user, donation_request=donation_request, status='Canceled')

        # donation_request_accept = models.DonationAccepted.objects.get(donation_request = donation_request_id)
        # donation_request_accept.delete()

        return JsonResponse({'message': 'Donation Request Canceled'}, status=200)
       
    except(donation_request.DoesNotExist):
        return JsonResponse({'message': 'Donation Request not found'}, status=404)
        
    
@api_view(['GET', 'POST'])
def complete(request, donation_request_id):
    try:
        donation_request = models.DonationRequest.objects.get(pk= donation_request_id)
        donation_request.is_completed = True
        donation_request.status = 'Completed'
        donation_request.save()

        user_account = models.UserAccount.objects.get(user=request.user)
        user_account.last_donation_date = timezone.now()
        user_account.save()

        models.DonatioHistory.objects.create(user=request.user, donation_request=donation_request, status='Completed')

        donation_request_accept = models.DonationAccepted.objects.get(donation_request = donation_request_id)
        donation_request_accept.delete()

        return JsonResponse({'message': 'Donation Request Completed'}, status=200)
       
    except(donation_request.DoesNotExist):
        return JsonResponse({'message': 'Donation Request not found'}, status=404)
        
    

def blood_group_filter(request, blood_group):
    try:
        donation_requests = models.DonationRequest.objects.filter(blood_group=blood_group)
        
        if not donation_requests.exists():
            return JsonResponse({'message': 'Donation Request not found'}, status=404)
        
        # Format the queryset into a list of dictionaries (or another suitable format)
        donation_requests_data = list(donation_requests.values())

        return JsonResponse(donation_requests_data, safe=False, status=200)
       
    except models.DonationRequest.DoesNotExist:
        return JsonResponse({'message': 'Donation Request not found'}, status=404)

def unique_transaction_id_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


@api_view(['GET', 'POST'])
def donateMoney(request):

    settings = { 'store_id': 'abv671fb22291c1a', 'store_pass': 'abv671fb22291c1a@ssl', 'issandbox': True }
    sslcz = SSLCOMMERZ(settings)
    post_body = {}
    post_body['total_amount'] = request.data.get('amount')
    post_body['currency'] = "BDT"
    post_body['tran_id'] = unique_transaction_id_generator()
    post_body['success_url'] = f"https://lifelink-five.vercel.app/donate_blood/payment-success-url/{request.user.username}/{post_body['tran_id']}/success?redirect=true"
    post_body['fail_url'] = "https://fabulous-trifle-8657b5.netlify.app/dashboard.html?success=false"
    post_body['cancel_url'] = "https://fabulous-trifle-8657b5.netlify.app/dashboard.html?success=cancel"
    post_body['emi_option'] = 0
    post_body['cus_name'] = request.user.username
    post_body['cus_email'] = request.user.email
    post_body['cus_phone'] = "01401277707"
    post_body['cus_add1'] = "customer address"
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['multi_card_name'] = ""
    post_body['num_of_item'] = 1
    post_body['product_name'] = "Test"
    post_body['product_category'] = "Test Category"
    post_body['product_profile'] = "general"


    response = sslcz.createSession(post_body) # API response
    # print(response)
    # Need to redirect user to response['GatewayPageURL']
    # return redirect(response['GatewayPageURL'])
    return JsonResponse({'url': response['GatewayPageURL']})

@method_decorator(csrf_exempt, name='dispatch')
class PaymentSuccessView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request, username, tran_id):
        user = User.objects.filter(username = username).first()
        if request.data.get('status') == 'VALID' and request.data.get('tran_id') == tran_id:
            models.Payment.objects.create(
                transaction_id = tran_id,
                amount = request.data.get('amount'),
                user = user,
            )

            if request.GET.get('redirect') == 'true':
                # return HttpResponseRedirect ("https://fabulous-trifle-8657b5.netlify.app/")
                return HttpResponseRedirect ("https://fabulous-trifle-8657b5.netlify.app/dashboard.html?success=true")
            return Response ({'message': 'Paymeny successfull'}, status = status.HTTP_200_OK)
        return Response ({'message': 'Payment Failed'}, status= status.HTTP_400_BAD_REQUEST)




class UserLoginApiView(APIView):
    permission_classes = [AllowAny] 
    def post(self, request):
        serializer = serializers.UserLoginSerializer(data = self.request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            try:
                user = models.User.objects.get(username=username)
                if not user.is_active:
                    return Response({'error': "Please check your email to activate your account."}, status=403)
            except models.User.DoesNotExist:
                return Response({'error': "Invalid credentials."}, status=400)

            user = authenticate(username= username, password=password)
            if user:
                userAccount = models.UserAccount.objects.get(user=user)
                token, _ = Token.objects.get_or_create(user=user)
                print(token)
                print(_)
                login(request, user)

                return Response({'token' : token.key, 'user' : user.username, 'user_id' : userAccount.id})
            
            else:
                return Response({'error' : "Invalid Credential"})

        return Response(serializer.errors)


class UserLogoutView(APIView):
    def get(self, request):
        request.user.auth_token.delete()
        logout(request)
        return redirect('login')


class ContactViewSet(viewsets.ModelViewSet):
    queryset = models.ContactForm.objects.all()
    serializer_class = serializers.ContactSerializer
    permission_classes = [AllowAny] 
    def get_queryset(self):
        # return super().get_queryset().filter(is_available_for_donation=True)
        return super().get_queryset()

    def perform_create(self, serializer):
        # Save the form data
        contact_form = serializer.save(user=self.request.user)

        # Send an email to the user
        send_mail(
            subject=f"Thank you for contacting us: {contact_form.subject}",
            message=f"Dear {contact_form.name},\n\n"
                    f"Thank you for reaching out to us. We have received your message:\n\n"
                    f"We will get back to you shortly.\n\n"
                    f"Best regards,\nLifeLink",
            from_email='lifelink@example.com',  # Replace with your sender email
            recipient_list=[contact_form.email],  # Email to the user
            fail_silently=False,
        )

class PaymentViewset(viewsets.ModelViewSet):
    
    # queryset = models.Payment.objects.filter(user= self.request.user)
    # queryset = models.DonationRequest.objects.exclude(status='Completed')
    serializer_class = serializers.PaaymentSerializer  
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return models.Payment.objects.filter(user=self.request.user)


@api_view(['GET', 'POST'])
def statistics(request):
    donation_request_count = models.DonationRequest.objects.filter(user=request.user).count()
    completed_request_count = models.DonationRequest.objects.filter(user=request.user, status='Completed').count()
    pending_request_count = models.DonationRequest.objects.filter(user=request.user, status='Pending').count()
    accepted_request_count = models.DonationRequest.objects.filter(user=request.user, status='Accepted').count()

    accepted_request_by_you_count = models.DonationRequest.objects.filter(accepted_by= request.user).count()

    return Response({
        "total_donation_request": donation_request_count,
        "total_completed_request": completed_request_count,
        "total_pending_request": pending_request_count,
        "total_accepted_request": accepted_request_count,
        "accepted_request_by_you_count": accepted_request_by_you_count,
    })