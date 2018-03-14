from __future__ import unicode_literals

from urllib.parse import unquote

import youtube_dl
from flask import Flask, jsonify, request
from youtube_dl import downloader
from youtube_dl.downloader import http

app = Flask(__name__)


@app.route('/parse', methods=["GET"])
def parse():
    url = request.args.get('page')
    page = unquote(url)

    print("parse: " + page)
    # realUrl = base64.urlsafe_b64decode(url).decode('utf-8')
    ydl_opts = {
        "nocheckcertificate": True,
        "format": 'best[ext=mp4]',
        "simulate": True
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(page)
        if 'entries' in result:
            for entry in result['entries']:
                entry['filename'] = ydl.prepare_filename(entry)

                fd = downloader.get_suitable_downloader(entry, ydl_opts)
                if fd is http.HttpFD:
                    entry['is_http'] = True
                else:
                    entry['is_http'] = False
        else:
            result['filename'] = ydl.prepare_filename(result)

            fd = downloader.get_suitable_downloader(result, ydl_opts)
            if fd is http.HttpFD:
                result['is_http'] = True
            else:
                result['is_http'] = False

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
                videoInfo['filename'] = video['filename']
                videoInfo['is_http'] = video['is_http']
                videoInfo['http_headers'] = video['http_headers']

                if result.__contains__('is_live'):
                    videoInfo['is_live'] = video['is_live']
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
            info['filename'] = result['filename']
            info['is_http'] = result['is_http']
            info['http_headers'] = result['http_headers']

            if result.__contains__('is_live'):
                info['is_live'] = result['is_live']
            if result.__contains__('description'):
                info['description'] = result['description']
            if result.__contains__('thumbnail'):
                info['thumbnail'] = result['thumbnail']

        return jsonify(info)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
