from django.http import HttpResponse,HttpResponseServerError,HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.cache import cache

import json
import re
from datetime import datetime
from hashlib import md5

from embedly import Embedly
from embeds.models import SavedEmbed

from embeds.templatetags.embed_filters import make_cache_key

USER_AGENT = 'Mozilla/5.0 (compatible; django-embedly/0.2; ' \
        '+http://github.com/BayCitizen/)'
        
def cache_embed(request):
    if not request.POST:
        return HttpResponseBadRequest("cache_embed requires POST")
    url = request.POST.get('url')
    if not url:
        return HttpResponseBadRequest("POST a url, and I'll happily cache it")
    maxwidth = request.POST.get('maxwidth')
    
    #try memcache first
    key = make_cache_key(url, maxwidth)
    cached_response = cache.get(key)
    if cached_response and type(cached_response) == type(dict()):    
        cached_response['cache'] = 'memcache'
        return HttpResponse(json.dumps(cached_response), mimetype="application/json")

    #then the database
    try:
        saved = SavedEmbed.objects.get(url=url, maxwidth=maxwidth)
        response = saved.response
        response['html'] = saved.html
        response['cache'] = 'database'
        cache.set(key, response) #and save it to memcache
        return HttpResponse(json.dumps(response), mimetype="application/json")
    except SavedEmbed.DoesNotExist:
        pass

    #if we've never seen it before, call the embedly API
    client = Embedly(key=settings.EMBEDLY_KEY, user_agent=USER_AGENT)
    if maxwidth:
       oembed = client.oembed(url, maxwidth=maxwidth)
    else:
       oembed = client.oembed(url)
    if oembed.error:
        return HttpResponseServerError('Error embedding %s.\n %s' % (url,oembed.error))

    #save result to database
    row, created = SavedEmbed.objects.get_or_create(url=url, maxwidth=maxwidth,
                    defaults={'type': oembed.type})
    row.provider_name = oembed.provider_name
    row.response = json.dumps(oembed.data)

    if oembed.type == 'photo':
        html = '<img src="%s" width="%s" height="%s" />' % (oembed.url,
               oembed.width, oembed.height)
    else:
        html = oembed.html

    if html:
        row.html = html
        row.last_updated = datetime.now()
        row.save()

    #and to memcache
    cache.set(key, row.response, 86400)
    response = row.response
    response['html'] = row.html #overwrite for custom oembed types
    response['cache'] = "none"
    return HttpResponse(json.dumps(response), mimetype="application/json")