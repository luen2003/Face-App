## Install
On Python 3.10, run terminal
```
pip install -r requirements.txt
```
## Run
```
python app.py
```

Or open terminal and run 
```
./dist/app.exe
```

Or open dist folder and open file app.exe

App run on http://127.0.0.1:5000/

## Build executable file
```
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" --add-data "cv2/data;cv2/data" app.py
```