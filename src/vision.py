#
# Entry point for the actual display of cards
#

import face_recognition
import cv2
import os

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# The filesystem is a directory hehe
db_location = '../db/'

encodings = []
names = []
cards = []


def reloadFaces():
  # If you guys have time, try to make this only add the new names. 
  # I'm too bad at python to do it

  # Look, ideally, you'd just simply make a data structure of a user
  # That user would have a name, some pictures, and a card
  # Then when searching through opencv/face_recognition, you'd map any matches back onto the struct loc
  # BUT.
  # this is literally my first python script ever, and I'm writing this at 12:35am
  # fuelled by a redbull cocaine addiction, with massive depression
  # So I'm doing it the shit way
  # if y'all wanna fix this shit feel free to

  known_encodings = []
  known_names = []
  cards = []

  names = [f for f in os.listdir(db_location) if os.path.isdir(os.path.join(db_location, f))]

  for name in names:
    # Go through the folder
    # Find each id
    loc = db_location + name + '/'
    # I'm pretty bad at python so this is gonna be hacky

    id_locs = [loc + 'id_1.jpg', loc +'id_2.jpg', loc + 'id_3.jpg']
    card_loc = loc + 'card.jpg'

    for loc in id_locs:
      if os.path.isfile(loc):
        known_names.append(name)
        img = face_recognition.load_image_file(loc)
        known_encodings.append(face_recognition.face_encodings(img)[0])
        card = cv2.imread(card_loc)
        cards.append(card)
        print(card.shape)
  return known_encodings,known_names,cards
    
encodings,names,cards = reloadFaces()

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
face_cards = []
process_this_frame = True
frames_until_reload = 100000

# Using the tutorial code, process images 
while True:
  # Grab a single frame of video
  ret, frame = video_capture.read()

  frames_until_reload -= 1
  if(frames_until_reload is 0):
    encodings,names,cards = reloadFaces()
    frames_until_reload = 100000

  # Resize frame of video to 1/4 size for faster face recognition processing
  small_frame = cv2.resize(frame, (0, 0), fx=.25, fy=.25)

  # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
  rgb_small_frame = small_frame[:, :, ::-1]

  # Only process every other frame of video to save time
  if process_this_frame:
    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    face_names = []
    for face_encoding in face_encodings:
      # See if the face is a match for the known face(s)
      matches = face_recognition.compare_faces(encodings, face_encoding)
      name = "Unknown"

      # If a match was found in the known encodings, just use the first one.
      if True in matches:
        first_match_index = matches.index(True)
        face_names.append(names[first_match_index])
        face_cards.append(cards[first_match_index])

  process_this_frame = not process_this_frame


  # Display the results
  for (top, right, bottom, left), name, card in zip(face_locations, face_names, face_cards):
    # # Scale back up face locations since the frame we detected in was scaled to 1/4 size
    top *= 4
    right *= 4
    bottom *= 4
    left *= 4
  
    # The card should theoretically display on the side that is best suited, but I am so bad at python
    # But
    # my python knowledge is yikes sooooo

    right += 50

    free_y = frame.shape[0] - top
    free_x = frame.shape[1] - right

    max_y = card.shape[0]
    max_x = card.shape[1]

    if(max_y > free_y):
      max_y = free_y - 1
    if(max_x > free_x):
      max_x = free_x - 1

    frame[top: top+max_y, right: right+ max_x] = card[0:max_y, 0:max_x]
    #right+=100
    # frame[top:max_bottom, right:max_right] = card


  # Display the resulting image
  cv2.imshow('Video', frame)

  # Hit 'q' on the keyboard to quit!
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()

