import numpy as np
from NN_functions import AI_play,model_keras
from tensorflow.keras.models import Model,load_model


"""
Speichert Spielverlauf in s+saved_game_mem.npy ab
Falls data=[] wird ein Backup erzeugt
"""
def save_game_memory(game_memory, s):
    save=[]
    #Leere Daten -> Back-Up
    if len(game_memory)==0:
        cur=np.load(s+'saved_game_mem.npy')
        np.save(s+'backup_game_mem.npy',cur)
        return

    #
    for data in game_memory:
        if len(save)==0:
            save = data
        else:
            #Packe alle daten aufeinander
            save= np.vstack((save, data))
    try:
        #Versuche vorhandene Daten abzufragen
        prev=np.load(s+'saved_game_mem.npy')
    except:
        #Falls Error existieren sie nicht
        np.save(s+'saved_game_mem.npy',save)
        return
    if len(prev)==0:
        #Falls Leer ignoriere ebenfalls
        np.save(s+'saved_game_mem.npy',save)
    else:
        #Packe neue daten auf alte und save
        np.save(s+'saved_game_mem.npy',np.vstack((prev,save)))

"""
Speichert Actions in saved.npy ab
Falls data=[] wird ein Backup erzeugt
Erklärung wie oben
"""
def save_action_memory(action_memory, s):

    if len(action_memory)==0:
        cur=np.load(s+'saved_action_memory.npy')
        np.save(s+'backup_action_memory.npy',cur)
        return
    save=[]
    for data in action_memory:
        if len(save)==0:
            save = data
        else:
            save= np.vstack((save, data))
    try:
        prev=np.load(s+'saved_action_memory.npy')
    except:
        np.save(s+'saved_action_memory.npy',save)
        return
    if len(prev)==0:
        np.save(s+'saved_action_memory.npy',save)
    else:
        np.save(s+'saved_action_memory.npy',np.vstack((prev,save)))


"""
"""
if __name__=="__main__":
    model=load_model("./Networks/Best.h5")
    while True:
        base ,useful_mem,useful_act =AI_play(model,5,0)
        save_game_memory(useful_mem ,"./Networks/AI_")
        save_action_memory(useful_act,"./Networks/AI_")
        model.fit(useful_mem, useful_act,epochs=10,steps_per_epoch=30,shuffle=True,verbose=2)
