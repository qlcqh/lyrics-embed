from flask import Flask, request, send_file
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, USLT
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

# 创建临时目录
TEMP_DIR = '/tmp'
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

@app.route('/api/embed', methods=['POST'])
def embed_lyrics():
    try:
        if 'mp3' not in request.files or 'lrc' not in request.files:
            return '请选择文件', 400

        mp3_file = request.files['mp3']
        lrc_file = request.files['lrc']

        # 保存上传的文件
        input_path = os.path.join(TEMP_DIR, 'input.mp3')
        output_path = os.path.join(TEMP_DIR, 'output.mp3')
        
        # 保存MP3文件
        mp3_file.save(input_path)
        
        # 读取歌词
        lyrics = lrc_file.read().decode('utf-8')

        try:
            # 复制原始文件到输出文件
            with open(input_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    f_out.write(f_in.read())

            # 处理MP3文件
            audio = MP3(output_path, ID3=ID3)
            
            # 添加或更新ID3标签
            if audio.tags is None:
                audio.add_tags()

            # 清除已存在的歌词标签
            if 'USLT' in audio.tags:
                del audio.tags['USLT']

            # 添加新歌词
            audio.tags.add(USLT(
                encoding=3,
                lang='eng',
                desc='',
                text=lyrics
            ))

            # 保存更改
            audio.save()

            # 发送文件
            response = send_file(
                output_path,
                mimetype='audio/mpeg',
                as_attachment=True,
                download_name=f"{mp3_file.filename.replace('.mp3', '')}_带歌词.mp3"
            )

            # 返回文件
            return response

        finally:
            # 清理临时文件
            try:
                if os.path.exists(input_path):
                    os.remove(input_path)
                if os.path.exists(output_path):
                    os.remove(output_path)
            except Exception as e:
                logging.error(f"清理临时文件失败: {e}")

    except Exception as e:
        logging.error(f"处理失败: {e}")
        return f"处理失败: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)
