from time import sleep, time

import cv2

from .certificate import InvalidCertificateError, NationalCertificate


WEBCAM_FPS = 10

qr_detector = cv2.QRCodeDetector()


def normalise_bounding_box(bounding_box):
    return [
        (int(x), int(y))
        for x, y in bounding_box[0]
    ]


def draw_box(image, bounding_box, line_colour):
    for i in range(0, 4):
        image = cv2.line(image, bounding_box[i], bounding_box[(i+1) % 4], line_colour, 2)

    return image


def draw_text(image, text, bounding_box, text_colour):
    image = cv2.putText(image, text, bounding_box[3], cv2.FONT_HERSHEY_DUPLEX, 0.8, text_colour, 2, cv2.LINE_AA)

    return image


def decode_image(image):
    qr_decoded = False

    try:
        data, bounding_box, _ = qr_detector.detectAndDecode(image)

        if data:
            qr_decoded = True
            bounding_box = normalise_bounding_box(bounding_box)

            try:
                certificate = NationalCertificate(data)
                image = draw_box(image, bounding_box, (0, 255, 0))
                image = draw_text(image, str(certificate).splitlines()[0], bounding_box, (0, 255, 0))

                return image, qr_decoded, certificate
            except InvalidCertificateError as e:
                image = draw_box(image, bounding_box, (0, 0, 255))
                image = draw_text(image, e.message, bounding_box, (0, 0, 255))
    except cv2.error:
        pass

    return image, qr_decoded, None


def decode_from_webcam():
    webcam = cv2.VideoCapture(0)
    webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        time_start = time()
        _, image = webcam.read()
        image, qr_decoded, certificate = decode_image(image)

        cv2.imshow('webcam', image)

        if cv2.waitKey(1) > 0:
            break

        time_end = time()

        if qr_decoded:
            sleep(5)
        else:
            delay = 1 / WEBCAM_FPS - (time_end - time_start)
            delay = delay if delay > 0 else 0
            sleep(delay)
