import logging
from urllib.parse import quote

from flask import Blueprint, Flask, jsonify, make_response, redirect, request

from connectai.lark.sdk import *
from connectai.lark.sdk.mixin import BotMessageDecorateMixin


class Server(BotMessageDecorateMixin):
    def __init__(
        self, *bot, bots=list(), prefix="/oauth/feishu", host="0.0.0.0", port=8888
    ):
        self.bots = list(bot) + bots
        self.bots_map = {b.app_id: b for b in self.bots}
        self.prefix = prefix
        self.host = host
        self.port = port

    def get_blueprint(self):
        bp = Blueprint("lark-oauth", __name__)

        def oauth_handler():
            app_id = request.args.get("app_id", default="", type=str)
            code = request.args.get("code", default="", type=str)
            state = request.args.get("state", default="", type=str)
            if not app_id and not state:
                raise Exception("param error")

            def oauth_redirect():
                redirect_uri = request.base_url
                # scope = "contact:contact.base:readonly"
                scope = ""
                oauth_url = f"https://open.feishu.cn/open-apis/authen/v1/authorize?app_id={app_id or state}&redirect_uri={quote(redirect_uri)}&scope={scope}&state={app_id or state}"
                return redirect(oauth_url, code=302)

            if code:
                result = None
                bot = self.get_bot(state)  # state=app_id
                if bot:
                    access = bot.post(
                        f"{bot.host}/open-apis/authen/v1/oidc/access_token",
                        json=dict(
                            grant_type="authorization_code",
                            code=code,
                        ),
                        headers={
                            "Authorization": f"Bearer {bot.app_access_token}",
                        },
                    ).json()
                    if "data" not in access:
                        return oauth_redirect()
                    user_info = bot.get(
                        f"{bot.host}/open-apis/authen/v1/user_info",
                        headers={
                            "Authorization": f"Bearer {access['data']['access_token']}",
                        },
                    ).json()
                    try:
                        user_contact = bot.get(
                            f"{bot.host}/open-apis/contact/v3/users/{user_info['data']['open_id']}?user_id_type=open_id",
                        ).json()
                    except Exception as e:
                        logging.error(e)
                        user_contact = {}

                    if "user" in user_contact.get("data", {}) and user_info.get("data"):
                        user_info["data"].update(user_contact["data"]["user"])
                    if "open_id" in user_info.get("data", {}):
                        result = bot.process_message(
                            {
                                "headers": {
                                    key.lower(): value
                                    for key, value in request.headers.items()
                                },
                                "body": dict(
                                    header=dict(
                                        event_type="oauth:user_info",
                                        event_id="placeholder",
                                    ),
                                    event=user_info.get("data", {}),
                                ),
                            }
                        )
                return make_response(
                    """
<script>
try {
  window.opener.postMessage("""
                    + json.dumps(dict(event="oauth", data=result))
                    + """, '*')
} catch(e) {
  console.error(e)
  setTimeout(() => window.close(), 3000)
  // location.replace('/')
}
</script>
                                     """,
                    {"Content-Type": "text/html"},
                )
                return jsonify()
            return oauth_redirect()

        bp.add_url_rule(
            self.prefix,
            "oauth_handler",
            oauth_handler,
            methods=["GET"],
        )
        return bp

    def get_app(self):
        app = Flask(__name__)
        app.register_blueprint(self.get_blueprint())
        return app

    def start(self, host=None, port=None):
        app = self.get_app()
        app.run(host=host or self.host, port=port or self.port)
