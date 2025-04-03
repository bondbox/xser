# coding:utf-8

from flask import Flask
from flask import Request
from flask import Response
from flask import request  # noqa:H306
from flask import stream_with_context
from requests import ConnectionError

from xserver.http.proxy import MethodNotAllowed
from xserver.http.proxy import RequestProxy
from xserver.http.proxy import ResponseProxy


class FlaskProxy(RequestProxy):

    def __init__(self, target: str) -> None:
        super().__init__(target)

    @classmethod
    def forward(cls, rp: ResponseProxy) -> Response:
        response = Response(stream_with_context(rp.generator), rp.status_code, rp.headers)  # noqa:E501
        for cookie in rp.cookies:
            response.set_cookie(
                key=cookie.name,
                value=cookie.value or "",
                expires=cookie.expires,
                path=cookie.path,
                domain=cookie.domain,
                secure=cookie.secure
            )
        return response

    def request(self, request: Request) -> Response:
        try:
            headers = self.filter_headers({k: v for k, v in request.headers.items()})  # noqa:E501
            print(f"request headers:\n{headers}")
            response = super().request(path=request.path,
                                       method=request.method,
                                       data=request.data,
                                       headers=headers)
            return self.forward(response)
        except MethodNotAllowed:
            return Response("Method Not Allowed", status=405)
        except ConnectionError:
            return Response("Bad Gateway", status=502)


flask_proxy: FlaskProxy = FlaskProxy("https://example.com/")
app: Flask = Flask(__name__)


@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def proxy(path: str) -> Response:  # pylint: disable=unused-argument
    print(f"request.headers:\n{request.headers}")
    response: Response = flask_proxy.request(request)
    print(f"response.headers:\n{response.headers}")
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
