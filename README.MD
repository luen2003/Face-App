## Install
On Python 3.10, run terminal
```
pip install -r requirements.txt
```

## Build executable file
```
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" --add-data "cv2/data;cv2/data" app.py
```
## Run
Method 1:

```
python app.py
```
Method 2:

After build executable file

Run open terminal and run 
```
./dist/app.exe
```

Or open dist folder and open file app.exe

App run on http://127.0.0.1:5000/
