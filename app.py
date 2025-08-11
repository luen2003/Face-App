import sys
import os
import base64
import cv2
import numpy as np
from flask import Flask, render_template, request
from deepface import DeepFace
from werkzeug.utils import secure_filename

# Xác định base_path tùy môi trường (dev hoặc exe)
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.abspath(".")

# Đường dẫn haarcascade cho OpenCV
cv2.data.haarcascades = os.path.join(base_path, "cv2", "data") + os.sep

# Tạo thư mục uploads nằm trong static/
upload_folder = os.path.join(base_path, 'static', 'uploads')
os.makedirs(upload_folder, exist_ok=True)

# Cấu hình Flask
app = Flask(__name__,
            template_folder=os.path.join(base_path, 'templates'),
            static_folder=os.path.join(base_path, 'static'))

app.config['UPLOAD_FOLDER'] = upload_folder

# Hàm nhận diện người
def identify_user(img_array):
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        db_img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            db_img_array = cv2.imread(db_img_path)
            if db_img_array is None:
                print(f"❌ Không đọc được ảnh: {db_img_path}")
                continue
            result = DeepFace.verify(
                img1_path=img_array,
                img2_path=db_img_array,
                model_name='Facenet',
                enforce_detection=False
            )
            if result.get("verified"):
                return os.path.splitext(filename)[0], db_img_path
        except Exception as e:
            print(f"⚠️ Lỗi khi xác thực với {filename}: {e}")
    return "Không xác định", None

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    upload_type = request.form.get('upload_type')
    person_name = request.form.get('person_name', '').strip().replace(" ", "_")

    img_array = None
    matched_filename = None
    captured_image_base64 = None

    # 1. Ảnh chụp từ webcam (base64)
    if 'image_data' in request.form and request.form['image_data']:
        try:
            image_data = request.form['image_data']
            header, encoded = image_data.split(",", 1)
            binary_data = base64.b64decode(encoded)
            np_arr = np.frombuffer(binary_data, np.uint8)
            img_array = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            captured_image_base64 = image_data
        except Exception:
            return render_template("index.html", message="❌ Lỗi khi xử lý ảnh từ webcam.")

    # 2. Ảnh tải lên
    elif 'file' in request.files and request.files['file'].filename != '':
        try:
            file = request.files['file']
            np_arr = np.frombuffer(file.read(), np.uint8)
            img_array = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        except Exception:
            return render_template("index.html", message="❌ Lỗi khi đọc ảnh từ máy.")

    if img_array is None:
        return render_template("index.html", message="❌ Không có ảnh hợp lệ để xử lý.")

    # Nếu thêm ảnh vào thư viện
    if upload_type == 'add':
        if not person_name:
            return render_template("index.html", message="❌ Vui lòng nhập tên người khi thêm ảnh.")
        filename = secure_filename(f"{person_name}.jpg")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cv2.imwrite(filepath, img_array)
        return render_template("index.html", message=f"✅ Đã thêm ảnh vào thư viện: {filename}")

    # Nếu phân tích & nhận diện
    try:
        analysis = DeepFace.analyze(
            img_path=img_array,
            actions=['age', 'gender', 'emotion'],
            enforce_detection=False
        )[0]

        gender = max(analysis["gender"], key=analysis["gender"].get)
        emotion = max(analysis["emotion"], key=analysis["emotion"].get)

        name, matched_img_path = identify_user(img_array)
        if matched_img_path:
            matched_filename = os.path.relpath(matched_img_path, start=os.path.join(base_path, 'static')).replace("\\", "/")
            matched_filename = f"/static/{matched_filename}"

        return render_template("index.html",
                               result={
                                   "age": analysis["age"],
                                   "gender": gender,
                                   "emotion": emotion
                               },
                               name=name,
                               matched_filename=matched_filename,
                               captured_image=captured_image_base64)
    except Exception as e:
        return render_template("index.html", message=f"❌ Lỗi phân tích: {e}")

if __name__ == '__main__':
    app.run(debug=True)
