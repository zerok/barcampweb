import logging


LOG = logging.getLogger(__name__)

class PlatformMiddleware(object):
    def process_request(self, request):
        platform = 'default'
        if 'iphone' in request.get_host():
            platform = 'iphone'
        LOG.debug("Detected platform: %s" % platform)
        setattr(request, 'platform', platform)