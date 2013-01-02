# Create your views here.
from django.http import Http404, HttpResponse,HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import Context,RequestContext
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from reg.models import Person
import json
import hmac
import base64
import hashlib
import logging
from django.views.decorators.csrf import csrf_exempt
FACEBOOK_CONNECT_SECRET='YOUR_SECRET_KEY'

def registration(request):
    return render_to_response('sample.html')
from random import choice
import hashlib
import urllib2
import json
import base64
import hmac

def parse_signed_request(signed_request, app_secret):
    """Return dictionary with signed request data.
    Code taken from https://github.com/facebook/python-sdk"""
    try:
        l = signed_request.split('.', 2)
        encoded_sig = str(l[0])
        payload = str(l[1])
    except IndexError:
        raise ValueError("'signed_request' malformed")

    sig = base64.urlsafe_b64decode(encoded_sig + "=" * ((4 - len(encoded_sig) % 4) % 4))
    data = base64.urlsafe_b64decode(payload + "=" * ((4 - len(payload) % 4) % 4))

    data = json.loads(data)

    if data.get('algorithm').upper() != 'HMAC-SHA256':
        raise ValueError("'signed_request' is using an unknown algorithm")
    else:
        expected_sig = hmac.new(app_secret, msg=payload, digestmod=hashlib.sha256).digest()

    if sig != expected_sig:
        raise ValueError("'signed_request' signature mismatch")
    else:
        return data
@csrf_exempt
def fb_registration(request):
    """
     Register a user from Facebook-aided registration form
     """
    if request.POST:
        if 'signed_request' in request.POST:
            # parse and check data
            data = parse_signed_request(request.POST['signed_request'], FACEBOOK_CONNECT_SECRET)

            # lets try to check if user exists based on username or email
            try:
                check_user = User.objects.get(username=data['registration']['name'])
            except:
                pass
            else:
                return HttpResponseRedirect('/user/login/')

            try:
                check_user = User.objects.get(email=data['registration']['email'])
            except:
                pass
            else:
                return HttpResponseRedirect('/user/login/')

            # user does not exist. We create an account
            # in this example I assume that he will login via Facebook button or RPXnow
            # so no password is needed for him - using random password
            randompass = ''.join([choice('1234567890qwertyuiopasdfghjklzxcvbnm') for i in range(7)])
            user = User.objects.create_user(data['registration']['name'], data['registration']['email'], randompass)
            user.save()
            user = authenticate(username=data['registration']['name'], password=randompass)
            if user is not None:
                # save in user profile his facebook id. In this case for RPXNow login widget
                fbid = data['user_id']
                fbid=int(fbid)
                r = Person(user=user, identifier=fbid)
                r.save()
                login(request, user)
            return render_to_response('register.html', {}, context_instance=RequestContext(request))

    return render_to_response('register.html', {}, context_instance=RequestContext(request))
