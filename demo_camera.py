import cv2 as cv

from src.DDPDevice import DDPDevice
from src.utils import load_config


config = load_config()
device = DDPDevice(dest_ip=config["dest_ip"])

cap = cv.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # if frame is read correctly ret is True
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    # Our operations on the frame come here
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    small = cv.resize(gray, (16, 16))

    blur = cv.GaussianBlur(small, (9, 9), sigmaX=0, sigmaY=0)

    edges = cv.Canny(image=blur, threshold1=50, threshold2=100)

    # data = cv.resize(edges, (16, 16))

    device.display_array(edges)

    edges_big = cv.resize(edges, (512, 512), interpolation=cv.INTER_NEAREST)

    # Display the resulting frame
    cv.imshow("edges", edges)
    cv.imshow("edges_big", edges_big)

    if cv.waitKey(1) == ord("q"):
        break

# When everything done, release the capture
cap.release()
cv.destroyAllWindows()
