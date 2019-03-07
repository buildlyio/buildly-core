import json


class BifrostError(Exception):
    def __init__(self, msg, status: int = None):
        content = {'detail': msg}
        self.content = json.dumps(content)
        self.status = status
        self.content_type = 'application/json'


class SocialAuthFailed(BifrostError):
    def __init__(self, msg):
        super(SocialAuthFailed, self).__init__(msg, 400)


class SocialAuthNotConfigured(BifrostError):
    def __init__(self, msg):
        super(SocialAuthNotConfigured, self).__init__(msg, 500)
