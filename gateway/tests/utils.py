import typing
import asyncio
import json
from unittest.mock import Mock

from aiohttp import ClientSession, StreamReader, ContentTypeError, RequestInfo


class AiohttpResponseMock:
    def __init__(self, method, url, status, body, headers=None):
        self.method = method
        self.url = url
        self.status = status
        self.body = body
        self._headers = headers or {}

    def match_request(self, method, url):
        # URLs should exactly match (incl. order of query params), TODO: make more intelligent URL matching
        if method.lower() == self.method.lower() and url.lower() == self.url.lower():
            return True
        return False

    @property
    def headers(self):
        return self._headers

    @property
    def content(self):
        protocol = Mock(_reading_paused=False)
        stream = StreamReader(protocol)
        stream.feed_data(self.body)
        stream.feed_eof()
        return stream

    @asyncio.coroutine
    def read(self):
        return self.content.read()

    @asyncio.coroutine
    def text(self, encoding='utf-8'):
        return self.body.decode(encoding)

    @asyncio.coroutine
    def json(self, encoding='utf-8'):
        if not getattr(self.body, "decode", False):
            raise ContentTypeError(
                request_info=RequestInfo(self.url, self.method, self.headers),
                history=[self],
            )
        return json.loads(self.body.decode(encoding))

    @asyncio.coroutine
    def release(self):
        pass


def create_aiohttp_session_mock(
    response_mocks: typing.Iterable[AiohttpResponseMock],
    loop: asyncio.AbstractEventLoop = None,
) -> ClientSession:
    async def _request(method, url, *args, **kwargs):
        for response in response_mocks:
            if response.match_request(method, url):
                return response
        assert False, f'No response mock for {method} {url}'

    session = ClientSession(loop=loop)
    session._request = _request
    return session
