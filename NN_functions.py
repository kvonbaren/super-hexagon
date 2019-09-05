import numpy as np
from tensorflow.keras.models import Model,load_model
from directKeys import PressKey,ReleaseKey,LEFT,RIGHT,R,SPACE
from functions import get_data
import time
import cv2


"""
Geben passende Tastendrücke an das Spiel bzw aktuell ausgewählte
Fenster weiter um Spieler zu simulieren
"""
def right():
    PressKey(RIGHT)
    ReleaseKey(LEFT)

def left():
    PressKey(LEFT)
    ReleaseKey(RIGHT)

def wait():
    ReleaseKey(LEFT)
    ReleaseKey(RIGHT)

"""
kleine verzögerungen eingebaut um problemen
oder ähnlichem vorzubeugen
"""
def restart():
    wait()
    time.sleep(1)
    PressKey(SPACE)
    time.sleep(0.05)
    ReleaseKey(SPACE)
    time.sleep(0.2)


"""
Lasse AI spielen
für <iter> viele Spieler mit <eps> random moves
"""
def AI_play(model, iter,eps):
    total_score=0
    useful_mem = []
    useful_act = []
    scores = np.zeros(iter)
    lost_in_row=0
    loops=0
    begin=time.time()
    # Pfeil-Bild
    l = cv2.imread("./Images/left.png",cv2.IMREAD_GRAYSCALE)
    r = cv2.imread("./Images/right.png",cv2.IMREAD_GRAYSCALE)
    w = cv2.imread("./Images/wait.png",cv2.IMREAD_GRAYSCALE)
    for t in range(iter):
        print("restarting")
        restart()
        start =time.time()
        game_memory = []
        game_memory_new = []
        action_memory = []
        observation = []
        alive=True
        while(alive):
            loops+=1
            observation, alive = get_data(True)
            score=time.time()-start

            if bool(alive)==True:
                if 1 <eps:
                    action = random.randint(0,2)

                else:
                    """
                    Vorhersage des Neuronalennetzes welche Aktion
                    ausgeführt werden soll
                    """
                    pred = model.predict((np.asarray(observation)).reshape(1,21))
                    action = np.argmax(pred)

                if action==0:
                    output = [1,0,0]
                    left()
                    cv2.imshow("predict",l)
                elif action==1:
                    output = [0,1,0]
                    wait()
                    cv2.imshow("predict",w)
                elif action==2:
                    output = [0,0,1]
                    right()
                    cv2.imshow("predict",r)
                prev_action = action
                prev_observation=observation
                #start recording game
                if len(game_memory)==0:
                    game_memory = observation
                else:
                    game_memory = np.vstack((game_memory,observation))
                if len(action_memory)==0:
                    action_memory = output
                else:
                    action_memory = np.vstack((action_memory,output))
            #Speichere den Spielverlauf, wenn Spiel zu Ende
            else:

                scores[t]=score
                if len(useful_mem)==0:
                    useful_mem = game_memory[0:len(action_memory)-7]
                else:
                    useful_mem = np.vstack((useful_mem,game_memory[0:len(action_memory)-7]))
                if len(useful_act)==0:
                    useful_act = action_memory[0:len(action_memory)-7]
                else:
                    useful_act = np.vstack((useful_act,action_memory[0:len(action_memory)-7]))
                #Option, dass man die letzten entscheidungen Flipped
                #useful_act[len(useful_act)-4:]*= (-1)

    return np.mean((np.sort(scores))[int(iter/2):iter]),useful_mem,useful_act





"""
Baue Model auf
Falls keine daten
Input X   Output y mitgegeben werden lade sie
<path> prefix zum namen
"""
def model_keras(epoches,input_size,path,X=False,y=False):

    inputs = Input(shape=[input_size])
    x = Dense(256, activation='relu')(inputs)
    #Um overfitting vorzubeugen
    #passt sich jedoch somit auch eher neuen daten an
    #x = Dropout(0.1)(x)
    x = Dense(128, activation='relu')(x)
    x = Dense(32, activation='relu')(x)
    predictions = Dense(3, activation='softmax')(x)
    model = Model(inputs=inputs, outputs=predictions)
    model.compile(loss='mse', optimizer='adam', metrics=['accuracy'])
    if not X:
        X=np.load(path+'saved_game_mem.npy')
        y=np.load(path+'saved_action_memory.npy')

    model.fit(X, y,epochs=epoches,steps_per_epoch=128,shuffle=True,verbose=2)

    return model
