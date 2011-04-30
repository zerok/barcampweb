import logging


LOG = logging.getLogger(__name__)

class PlatformMiddleware(object):
    def process_request(self, request):
        platform = 'default'
        if request.get_host().startswith('m.'):
            platform = 'iphone'
        LOG.debug("Detected platform: %s" % platform)
        setattr(request, 'platform', platform)
