from __future__ import unicode_literals

from urllib.parse import unquote

import youtube_dl
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/parse', methods=["GET"])
def parse():
    url = request.args.get('page')
    page = unquote(url)

    print("parse: " + page)
    # realUrl = base64.urlsafe_b64decode(url).decode('utf-8')
    ydl_opts = {
        "nocheckcertificate": True,
        "format": 'best[ext=mp4]'
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(
            page,
            download=False  # We just want to extract the info
        )

        info = {}
        if 'entries' in result:
            # Can be a playlist or a list of videos
            info['type'] = 'playlist'

            playlist = []
            for video in result['entries']:
                videoInfo = {}
                videoInfo['type'] = 'video'
                videoInfo['page'] = video['webpage_url']
                videoInfo['title'] = video['title']
                videoInfo['url'] = video['url']
                videoInfo['ext'] = video['ext']

                if result.__contains__('is_live'):
                    videoInfo['isLive'] = video['is_live']
                if result.__contains__('description'):
                    videoInfo['description'] = video['description']
                if result.__contains__('thumbnail'):
                    videoInfo['thumbnail'] = video['thumbnail']
                playlist.append(videoInfo)
            info['playlist'] = playlist
        else:
            # Just a video
            info['type'] = 'video'
            info['page'] = result['webpage_url']
            info['title'] = result['title']
            info['url'] = result['url']
            info['ext'] = result['ext']

            if result.__contains__('is_live'):
                info['isLive'] = result['is_live']
            if result.__contains__('description'):
                info['description'] = result['description']
            if result.__contains__('thumbnail'):
                info['thumbnail'] = result['thumbnail']

        return jsonify(info)

if __name__ == '__main__':
    app.run(debug=True)
