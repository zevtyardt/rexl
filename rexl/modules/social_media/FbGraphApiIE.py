import argparse
import json
import copy
from lib.decorators import use_for, with_argparser, validate_facebook_access_token
from typing import Union
import textwrap
import requests

FACEBOOK = [("SocialMedia", "FbGraphApi")]
GRAPH_API = "https://graph.facebook.com"
GRAPH_API_VERSION = "v6.0"


class External(object):
    def make_request(self, *args, **kwargs):
        return requests.get(*args, **kwargs)

    def _fbgraph_api(
            self, *args, msgfmt="done: %(message)s", prettify=False,
            report=True, **kwargs) -> str:
        """convert node and params to valid url"""
        kwargs["access_token"] = self.facebook_user_access_token
        params = "?" + "&".join("{0}={1}".format(*i) for i in kwargs.items())

        if args[0] == "me" and len(args) > 1:
            self.perror("endpoint 'me' is not implemented!")
            return
        vals = (GRAPH_API, GRAPH_API_VERSION, *args)

        self.poutput(
            "%s %r %r" % (
                kwargs.get("method", "GET"), "/".join(args),
                params.replace(kwargs["access_token"], "[PRIVATE]")
            )
        )
        data_dict = self.make_request("/".join(vals) + params).json()
        error_message = data_dict.get("error", {}).get("message")
        if error_message:
            self.poutput(
                "error: " + self.style(error_message, fg=self.fg.bright_red)
            )
        else:
            if prettify:
                data_dict = "\n" + json.dumps(data_dict, indent=2)
            self.poutput(msgfmt % {"message": data_dict})

    AccessTokenParser = argparse.ArgumentParser()
    AccessTokenParser.add_argument("access_token", help="User access token.")

    @use_for(FACEBOOK)
    @with_argparser(AccessTokenParser)
    def do_set_access_token(self, param):
        """set new access token"""
        self.do_set("facebook_user_access_token %s" % param.access_token)

    @validate_facebook_access_token
    @use_for(FACEBOOK)
    def do_show_access_token(self, param):
        """show current access token"""
        self.do_set("facebook_user_access_token")

    @use_for(FACEBOOK)
    def do_reset_access_token(self, param):
        """reset current access token"""
        self.do_set("facebook_user_access_token None")

    def get_datalist(self, *args, **params) -> Union[iter, str, None]:
        """return datalist or print error message"""
        data_dict = self._fbgraph_api(*args, **params, report=False)

        error_message = data_dict.get("error", {}).get("message")
        if error_message:
            self.poutput(
                "error_message: " + self.style(error_message, fg=self.fg.red))
        else:

            def find(key, value):
                for k, v in (
                    value.items() if isinstance(value, dict) else
                    enumerate(value) if isinstance(value, list) else []
                ):
                    if k == key:
                        yield v
                    elif isinstance(v, (dict, list)):
                        for result in find(key, v):
                            yield result

            return next(find("data", data_dict))

    def get_home(self, limit: int = 50) -> iter:
        """get user newsfeed"""
        return self.get_datalist("me", "home", limit=limit)

    def get_feed(self, user_id: str = "me", limit: int = 500) -> iter:
        """get latest user feeds"""
        return self.get_datalist(user_id, "feed", limit=limit)

    def get_friends(self, user_id: str = "me", limit: int = 500) -> iter:
        """get friendlist metadata from user_id"""
        return self.get_datalist(user_id, "friends", limit=limit)

    def get_friendrequests(self, limit: int) -> iter:
        """get friendrequests"""
        return self.get_datalist("me", "friendrequests", limit=limit)

    def get_subscribedto(self, limit: int) -> iter:
        """get following user"""
        return self.get_datalist("me", "subscribedto", limit=limit)

    def get_albums(self, limit: int) -> iter:
        """get albums"""
        return self.get_datalist("me", "albums", limit=limit)

    def get_user(self, user_id: str = "me") -> dict:
        """get user metadata"""
        data_dict = self._fbgraph_api(user_id)
        return data_dict


class FbGraphApi(External):
    # ARGUMENT PARSER
    # ~~~~~~~~~~~~~~~

    SingleObjectParser = argparse.ArgumentParser()
    SingleObjectParser.add_argument(
        "object_id", help="String that contains a object ID.")

    SingleReactPostParser = copy.deepcopy(SingleObjectParser)
    SingleReactPostParser.add_argument(
        "--type", default="LIKE", type=str, help="Reaction type.",
        choices={"LIKE", "LOVE", "WOW", "HAHA", "SAD", "ANGRY", "PRIDE",
                 "CARE"})

    CommentPostParser = argparse.ArgumentParser()
    CommentPostParser.add_argument(
        "post_id", help="String that contains a post ID.")
    CommentPostParser.add_argument("message", help="The comment text.")

    UserParser = argparse.ArgumentParser()
    UserParser.add_argument("uid", help="String that contains a (user) ID.")

    @validate_facebook_access_token
    @with_argparser(SingleObjectParser)
    def do_like__SocialMedia__FbGraphApi(self, param):
        """like post, albums or :object:"""
        self._fbgraph_api(param.object_id, "likes", method="POST")

    @validate_facebook_access_token
    @with_argparser(SingleReactPostParser)
    def do_reaction__SocialMedia__FbGraphApi(self, param):
        """send reaction to :object:"""
        self._fbgraph_api(
            param.object_id, "reactions", method="POST", type=param.type
        )

    @validate_facebook_access_token
    @with_argparser(CommentPostParser)
    def do_comment__SocialMedia__FbGraphApi(self, param):
        """send comment to someone post"""
        self._fbgraph_api(
            param.post_id, "comments", method="POST", message=param.message
        )

    @validate_facebook_access_token
    @with_argparser(UserParser)
    def do_poke__SocialMedia__FbGraphApi(self, param):
        """send poke to user"""
        self._fbgraph_api(param.uid, "pokes", method="POST")

    @validate_facebook_access_token
    @with_argparser(UserParser)
    def do_block__SocialMedia__FbGraphApi(self, param):
        """block person, page or :object:"""
        self._fbgraph_api("me", "blocked", uid=param.uid)

    @validate_facebook_access_token
    @with_argparser(UserParser)
    def do_unfollow__SocialMedia__FbGraphApi(self, param):
        """unfollow person, page or :object:"""
        self._fbgraph_api(param.uid, "subscribers", method="DELETE")

    @validate_facebook_access_token
    @with_argparser(UserParser)
    def do_follow__SocialMedia__FbGraphApi(self, param):
        """follow person, page or :object:"""
        self._fbgraph_api(param.uid, "subscribers", method="POST")

    @validate_facebook_access_token
    @with_argparser(UserParser)
    def do_confirm__SocialMedia__FbGraphApi(self, param):
        """add user to the friendlist"""
        self._fbgraph_api("me", "friends", param.uid, method="POST")

    @validate_facebook_access_token
    @with_argparser(UserParser)
    def do_unfriend__SocialMedia__FbGraphApi(self, param):
        """remove user from friendlist"""
        self._fbgraph_api("me", "friends", method="DELETE", uid=param.uid)

    @validate_facebook_access_token
    @with_argparser(SingleObjectParser)
    def do_obj__SocialMedia__FbGraphApi(self, param):
        """view object"""
        self._fbgraph_api(param.object_id, prettify=True)

    @validate_facebook_access_token
    @with_argparser(SingleObjectParser)
    def do_delete__SocialMedia__FbGraphApi(self, param):
        """remove :object:"""
        self._fbgraph_api(param.object_id, method="DELETE")


    BooleanParser = argparse.ArgumentParser()
    BooleanParser.add_argument("-s", dest="status", metavar="boolean", help="active or deactive shield, choice from {true, false}", default=True, choices={"true", "false"})

    @validate_facebook_access_token
    @with_argparser(BooleanParser)
    def do_shield__SocialMedia__FbGraphApi(self, param):
        """activate or delete profile guard"""
        token = self.facebook_user_access_token
        headers = {'Authorization': 'OAuth ' + token}
        id = self.get_user("me")

        if id:
            data = {'variables': '{"0":{"is_shielded":%s,"session_id":"9b78191c-84fd-4ab6-b0aa-19b39f04a6bc","actor_id":"%s","client_mutation_id":"b0316dd6-3fd6-4beb-aed4-bb29c5dc64b0"}}' % (param.status, id.get("id")),
                'method': 'post',
                'doc_id': '1477043292367183',
                'query_name': 'IsShieldedSetMutation',
                'strip_defaults': True,
                'strip_nulls': True,
                'locale': 'en_US',
                'client_country_code': 'US',
                'fb_api_req_friendly_name': 'IsShieldedSetMutation',
                'fb_api_caller_class': 'IsShieldedSetMutation'}
            r = requests.post("https://graph.facebook.com/graphql", data=data, headers=headers)
            self.poutput(r.text)

