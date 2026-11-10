import cv2
CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
if CASCADE.empty():
    raise RuntimeError('No se pudo cargar el clasificador Haar Cascade')
def detect_faces(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    boxes = CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(35,35))
    return [{'x':int(x),'y':int(y),'width':int(w),'height':int(h)} for x,y,w,h in boxes]
