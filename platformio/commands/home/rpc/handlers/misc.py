# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import re
import time

from bs4 import BeautifulSoup
from twisted.internet import defer, reactor

from platformio import app
from platformio.commands.home import helpers
from platformio.commands.home.rpc.handlers.os import OSRPC


class MiscRPC(object):

    def load_latest_tweets(self, username):
        cache_key = "piohome_latest_tweets_%s" % username
        cache_valid = "7d"
        with app.ContentCache() as cc:
            cache_data = cc.get(cache_key)
            if cache_data:
                cache_data = json.loads(cache_data)
                # automatically update cache in background every 12 hours
                if cache_data['time'] < (time.time() - (3600 * 12)):
                    reactor.callLater(5, self._preload_latest_tweets, username,
                                      cache_key, cache_valid)
                return cache_data['result']

        result = self._preload_latest_tweets(username, cache_key, cache_valid)
        return result

    @defer.inlineCallbacks
    def _preload_latest_tweets(self, username, cache_key, cache_valid):
        result = yield self._fetch_tweets(username)
        with app.ContentCache() as cc:
            cc.set(cache_key,
                   json.dumps({
                       "time": int(time.time()),
                       "result": result
                   }), cache_valid)
        defer.returnValue(result)

    @defer.inlineCallbacks
    def _fetch_tweets(self, username):
        api_url = ("https://twitter.com/i/profiles/show/%s/timeline/tweets?"
                   "include_available_features=1&include_entities=1&"
                   "include_new_items_bar=true") % username
        if helpers.is_twitter_blocked():
            api_url = self._get_proxed_uri(api_url)
        html_or_json = yield OSRPC.fetch_content(
            api_url, headers=self._get_twitter_headers(username))
        # issue with PIO Core < 3.5.3 and ContentCache
        if not isinstance(html_or_json, dict):
            html_or_json = json.loads(html_or_json)
        assert "items_html" in html_or_json
        soup = BeautifulSoup(html_or_json['items_html'], "html.parser")
        tweet_nodes = soup.find_all(
            "div", attrs={
                "class": "tweet",
                "data-tweet-id": True
            })
        result = yield defer.DeferredList(
            [self._parse_tweet_node(node, username) for node in tweet_nodes],
            consumeErrors=True)
        defer.returnValue([r[1] for r in result if r[0]])

    @defer.inlineCallbacks
    def _parse_tweet_node(self, tweet, username):
        # remove non-visible items
        for node in tweet.find_all(class_=["invisible", "u-hidden"]):
            node.decompose()
        twitter_url = "https://twitter.com"
        time_node = tweet.find("span", attrs={"data-time": True})
        text_node = tweet.find(class_="tweet-text")
        quote_text_node = tweet.find(class_="QuoteTweet-text")
        if quote_text_node and not text_node.get_text().strip():
            text_node = quote_text_node
        photos = [
            node.get("data-image-url") for node in (tweet.find_all(class_=[
                "AdaptiveMedia-photoContainer", "QuoteMedia-photoContainer"
            ]) or [])
        ]
        urls = [
            node.get("data-expanded-url")
            for node in (quote_text_node or text_node).find_all(
                class_="twitter-timeline-link",
                attrs={"data-expanded-url": True})
        ]

        # fetch data from iframe card
        if (not photos or not urls) and tweet.get("data-card2-type"):
            iframe_node = tweet.find(
                "div", attrs={"data-full-card-iframe-url": True})
            if iframe_node:
                iframe_card = yield self._fetch_iframe_card(
                    twitter_url + iframe_node.get("data-full-card-iframe-url"),
                    username)
                if not photos and iframe_card['photo']:
                    photos.append(iframe_card['photo'])
                if not urls and iframe_card['url']:
                    urls.append(iframe_card['url'])
                if iframe_card['text_node']:
                    text_node = iframe_card['text_node']

        if not photos:
            photos.append(tweet.find("img", class_="avatar").get("src"))

        def _fetch_text(text_node):
            text = text_node.decode_contents(formatter="html").strip()
            text = re.sub(r'href="/', 'href="%s/' % twitter_url, text)
            if "</p>" not in text and "<br" not in text:
                text = re.sub(r"\n+", "<br />", text)
            return text

        defer.returnValue({
            "tweetId":
            tweet.get("data-tweet-id"),
            "tweetUrl":
            twitter_url + tweet.get("data-permalink-path"),
            "author":
            tweet.get("data-name"),
            "time":
            int(time_node.get("data-time")),
            "timeFormatted":
            time_node.string,
            "text":
            _fetch_text(text_node),
            "entries": {
                "urls":
                urls,
                "photos": [
                    self._get_proxed_uri(uri)
                    if helpers.is_twitter_blocked() else uri for uri in photos
                ]
            },
            "isPinned":
            "user-pinned" in tweet.get("class")
        })

    @defer.inlineCallbacks
    def _fetch_iframe_card(self, url, username):
        if helpers.is_twitter_blocked():
            url = self._get_proxed_uri(url)
        html = yield OSRPC.fetch_content(
            url, headers=self._get_twitter_headers(username), cache_valid="7d")
        soup = BeautifulSoup(html, "html.parser")
        photo_node = soup.find("img", attrs={"data-src": True})
        url_node = soup.find("a", class_="TwitterCard-container")
        text_node = soup.find("div", class_="SummaryCard-content")
        if text_node:
            text_node.find(
                "span", class_="SummaryCard-destination").decompose()
        defer.returnValue({
            "photo":
            photo_node.get("data-src") if photo_node else None,
            "text_node":
            text_node,
            "url":
            url_node.get("href") if url_node else None
        })

    @staticmethod
    def _get_proxed_uri(uri):
        index = uri.index("://")
        return "https://dl.platformio.org/__prx__/" + uri[index + 3:]

    @staticmethod
    def _get_twitter_headers(username):
        return {
            "Accept":
            "application/json, text/javascript, */*; q=0.01",
            "Referer":
            "https://twitter.com/%s" % username,
            "User-Agent":
            ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit"
             "/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8"),
            "X-Twitter-Active-User":
            "yes",
            "X-Requested-With":
            "XMLHttpRequest"
        }
