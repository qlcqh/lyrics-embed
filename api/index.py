from flask import Flask, request, send_file
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT
import io
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/api/embed', methods=['POST'])
def embed_lyrics():
    try:
        if 'mp3' not in request.files or 'lrc' not in request.files:
            return '请选择文件', 400

        mp3_file = request.files['mp3']
        lrc_file = request.files['lrc']

        # 读取文件内容
        mp3_data = mp3_file.read()
        lyrics = lrc_file.read().decode('utf-8')

        # 处理MP3
        mp3_io = io.BytesIO(mp3_data)
        audio = MP3(mp3_io, ID3=ID3)
        
        # 添加歌词
        if audio.tags is None:
            audio.add_tags()
            
        # 清除已存在的歌词标签
        if 'USLT' in audio.tags:
            del audio.tags['USLT']
            
        audio.tags.add(USLT(
            encoding=3,
            lang='eng',
            desc='',
            text=lyrics
        ))

        # 保存结果
        output = io.BytesIO()
        audio.save(output)
        output.seek(0)

        return send_file(
            output,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name=f"{mp3_file.filename.replace('.mp3', '')}_带歌词.mp3"
        )

    except Exception as e:
        logging.error(f"处理失败: {str(e)}")
        return f"处理失败: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
