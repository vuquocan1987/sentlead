from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory
import os 
import pysftp

app = Flask(__name__)
#CONFIG
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.csv', '.xlsx']
app.config['UPLOAD_PATH'] = 'uploads'
app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['HOST'] = "sftp-b2bgateway.sys.cigna.com"
app.config['USERNAME'] = "cig_hellosehat_idn"
app.config['PASSWORD'] = ""
app.config['OUTPUT_PATH'] = "/Outbox"



@app.route('/', methods=['GET'])
def index():
    files = os.listdir(app.config['UPLOAD_PATH'])

    return render_template('index.html', files=files)

@app.route('/400/<error>', methods=['GET'])
def bad_request(error):
    return render_template('400.html', error=error)

@app.route('/', methods=['POST'])
def upload_file():
    try:
        print('[INFO] Upload file...')
        upload_file = request.files['file']
        filename = upload_file.filename
        if filename:
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config['UPLOAD_EXTENSIONS']:
                abort(400)
            upload_file.save(os.path.join(app.config['UPLOAD_PATH'],filename))
        print("[INFO] Done!!!")
        return redirect(url_for('index'))

    except Exception as err:
        print('[ERROR] Something happend', err)
        return redirect(url_for('bad_request', error=err))

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

@app.route('/delete', methods=['POST'])
def delete_file():
    try:
        print('[INFO] Delete File...')
        files = os.listdir(app.config['UPLOAD_PATH'])
        for file in files:
            file_path = os.path.join(app.config['UPLOAD_PATH'], file)
            os.remove(file_path)
        print("[INFO] Done!!!")
        return redirect(url_for('index'))
    
    except Exception as err:
        print('[ERROR] Something happend', err)
        return redirect(url_for('bad_request', error=err))

@app.route('/sendFile', methods=['POST'])
def send_file():
    try:
        print('[INFO] Sending file...')
        files = os.listdir(app.config['UPLOAD_PATH'])
        with pysftp.Connection(app.config['HOST'], username=app.config['USERNAME'], password=app.config['PASSWORD']) as sftp:
            for file in files:
                file_path = os.path.join(app.config['UPLOAD_PATH'], file)
                sftp.put(file_path, app.config['OUTPUT_PATH'])
        print('[INFO] Done!!!')
        return redirect(url_for('index'))

    except Exception as err:
        print('[ERROR] Something happend', err)
        return redirect(url_for('bad_request', error=err))
