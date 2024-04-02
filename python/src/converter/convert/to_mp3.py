import pika, json, tempfile, os
from bson.objectid import ObjectId
import moviepy.editor


def start(body, fs_videos, fs_mp3s, channel):
    pass
    message = json.loads(body)

    # empty temp file
    tf = tempfile.NamedTemporaryFile()
    # video contents
    # video_fid is saved as a string inside message. So to use it is is necessary to convert it to object. That is why 'ObjectId' is used
    out = fs_videos.get(ObjectId(message["video_fid"]))
    # write the contents to the temp file by reading the bytes from 'out'.
    tf.write(out.read())
    # create audio from temp video file
    audio = moviepy.editor.VideoFileClip(tf.name).audio
    tf.close()

    # write audio to the file

    tf_file = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_file)

    # save audio to mongodb

    f = open(tf_file, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    os.remove(tf_file)

    message["mp3_fid"] = str(fid)
    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            propertie=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as e:
        fs_mp3s.delete(fid)
        return "Error publishing message"
