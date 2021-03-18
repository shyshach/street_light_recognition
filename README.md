# Street Light Luminance Detection
A Flask Web-App detect object in image and calculate Luminosity for the street lights detected


## Project Structure

__app.py__ : To deploy the Flask service

__inference.py__ : Script to load the object detection yolo model and infer the image

__cal_lum.py__ : Script to calculate the luminosity of the given image

### Local Environment Instructions

1. Download and extract the given folder

2. Install a few required pip packages, which are specified in the requirements text file (including OpenCV).
    ```
    pip install -r requirements.txt
    ```
3. Darknet needs to be setup (https://github.com/AlexeyAB/darknet.git)

4. Run the app.py
    ```
    python app.py
    ```

    wait to a few seconds the darknet yolo model will load and it will display an IP address (http://127.0.0.1:5000/)

5. Open the URL in browser and its good to go