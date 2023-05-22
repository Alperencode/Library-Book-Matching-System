from isbnlib import *
import cv2
import numpy as np
from classes.book import Book

# Global variables
result_dictionary = {}
last_book = ""

def ParseISBN(isbn):
    """
    Parsing the ISBN number
    If ISBN is valid, return the metadata
    Else return False
    """
    if not is_isbn10(isbn) and not is_isbn13(isbn):
        return False
    else:
        return meta(isbn)

def ParseMeta(isbn_meta):
    """
    Parsing the metadata from the ISBN
    If data is valid, update the result dictionary
    """
    global last_book
    for key, value in isbn_meta.items():
        result_dictionary[key] = value

    if isbn_meta["Title"] != last_book:
        for key, value in result_dictionary.items():
            print(f"{key}: {value}")
        last_book = isbn_meta["Title"]

def DetectBarcode(img):
    """
    Detect barcode in the frame
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    detector = cv2.barcode_BarcodeDetector()

    # Detecting the barcode
    # Respectively: validation, barcode data, decode type, points of the barcode
    valid, decoded_info, decoded_type, corners = detector.detectAndDecode(gray)

    # If barcode is valid
    if valid:
        # Drawing the polygon around the barcode
        int_corners = np.array(corners, dtype=np.int32)
        cv2.polylines(img, [int_corners], True, (0, 255, 0), 5)

        # Parsing ISBN data
        isbn_meta = ParseISBN(decoded_info[0])

        # If ISBN is valid
        if isbn_meta:
            # Parsing the metadata
            ParseMeta(isbn_meta)

            # Writing the title of the book
            cv2.putText(img, isbn_meta["Title"], (int(corners[0][0][0]), int(corners[0][0][1])-5), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color=(0, 255, 0), thickness=2)
        else:
            print("Invalid or Unknown ISBN")

def DetectFaces(img):
    """
    Detect faces in the frame
    """
    # Using the Haar Cascade Classifier
    face_cascade = cv2.CascadeClassifier('methods/haarcascade_frontalface_default.xml')

    # Applying grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detecting faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.5, minNeighbors=5)
    
    for (x,y,w,h) in faces:
            # These variables represents the coordinates of the rectangle
            # Respectively: x_start, y_start, x_end, y_end
            
            # The detected zones (Gray)
            roi_gray = gray[y:y+h, x:x+w]

            # Rectange BGR, thickness, width and height
            color = (0, 0, 255)
            border = 2
            width = x + w
            height = y + h

            # Drawing rectangle
            if faces.all():
                cv2.rectangle(img, (x, y), (width, height), color, border)
                cv2.putText(img, "Face Found", (x,y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color=color, thickness=2)

def OutputTXT():
    """
    Output the result dictionary to a txt file
    """
    if GetResult():
        # Create a txt file
        with open('output.txt', 'w', encoding='utf-8') as f:
            # Write the result dictionary to the txt file
            for key, value in result_dictionary.items():
                # If the value is a list, write the list items
                if type(result_dictionary[key]) == list:
                    f.write(f"{key}: ")
                    for item in result_dictionary[key]:
                        f.write(f"{item}, ") if item != result_dictionary[key][-1] else f.write(f"{item}")
                    f.write("\n")
                else:
                    f.write(f"{key}: {value}\n")

def ReadISBN(cap):
    """
    Read the ISBN from the barcode
    """
    while cv2.waitKey(1) == -1:
        # Read the frame
        success, img = cap.read()
        
        # Flip the image for mirror effect
        img_flip = cv2.flip(img,1)

        # Detect faces
        # DetectFaces(img_flip)

        # Detect barcode
        DetectBarcode(img_flip)

        # Show the frame
        cv2.imshow('User', img_flip)
        
        # If any result is found, break the loop
        if GetResult():
            break

        cv2.waitKey(1)

def GetResult():
    """ 
    Getter for the result dictionary 
    """
    return result_dictionary

def GatherBook():
    book = Book(
        result_dictionary["ISBN-13"],
        result_dictionary["Title"],
        result_dictionary["Authors"],
        result_dictionary["Publisher"],
        result_dictionary["Year"],
        result_dictionary["Language"])
    return book