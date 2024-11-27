from flask import render_template, Flask, Response
import cv2 as cv


app = Flask(__name__)


camera = cv.VideoCapture(0)

def gen_frames():
   while True:
       success, frame = camera.read()
       if not success:
           break
       else:
           #フレームデータをjpgに圧縮
           ret, buffer = cv.imencode('.jpg',frame)
           # bytesデータ化
           frame = buffer.tobytes()
           yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
   #imgタグに埋め込まれるResponseオブジェクトを返す
   return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
@app.route('/index')
def index():
   
   user = {'username': 'FZ50'}
   return render_template('index.html', title='home', user=user)