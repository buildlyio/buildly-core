import json


class BuildlyError(Exception):
    def __init__(self, msg, status: int = None):
        content = {'detail': msg}
        self.content = json.dumps(content)
        self.status = status
        self.content_type = 'application/json'


class SocialAuthFailed(BuildlyError):
    def __init__(self, msg):
        super(SocialAuthFailed, self).__init__(msg, 400)


class SocialAuthNotConfigured(BuildlyError):
    def __init__(self, msg):
        super(SocialAuthNotConfigured, self).__init__(msg, 500)
