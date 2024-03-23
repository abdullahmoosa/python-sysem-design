import pika, json

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
    except Exception as err:
        return "internal server error", 500
    
    message = {
        "video_fid" : str(fid),
        "mp3_fid" : None,
        "username" : access["username"]
    }

    try: 
        channel.basic_publish(
            exchange = "",
            routing_key = "video",
            body = json.dumps(message),
            properties = pika.BasicProperties(
                delivery_mode= pika.spec.PERSISTENT_DELIVERY_MODE  
                # If the pod is reset and then it spins back up, "PERSISTENT_DELIVERY_MODE" ensures that the messages are still there.
            ), 
            )
    except:
        fs.delete(fid)
        # If the publish to queue is failed, it means the file will not get processed. So it is important to delete the file because it will take up unnecessary space 
        return "internal server error", 500
