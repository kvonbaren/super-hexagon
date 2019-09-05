import numpy as np
import mss
import cv2
import math



"""
Konvertiere Graustufen bild zu schwarz/weiß bild
"""
def conv2bw(orginal, game_coords):

    mid=((int((game_coords[3]-game_coords[1])/2),int((game_coords[2]-game_coords[0])/2)))
    cv2.rectangle(orginal, (0, 0), (344,47), (0), cv2.FILLED)
    cv2.rectangle(orginal, (600, 0), (1151,65), (0), cv2.FILLED)
    """ Bestimme Wallcolor und färbe wall/player weiß rest schwarz"""

    larea=np.copy(orginal[270:370,400:575])
    mid_col=orginal[mid[0]][mid[1]]
    if mid_col<240:
        #wcol=np.max(orginal)
        sort=np.bincount(larea.ravel())
        sort[mid_col] = 0
        wc1=np.argmax(sort)
        sort[wc1]=0
        wc2=np.argmax(sort)
        sort[wc2]=0
        wc3=np.argmax(sort)
        wcol=np.max(((wc1,wc2,wc3)))
        img_bin= cv2.threshold(orginal, wcol-5, 255, cv2.THRESH_BINARY)[1]
    else:
        #Background ist weiß
        #Flippe alles und wieder richten
        wcol=np.min(orginal[100:,:])
        img_bin= cv2.threshold(orginal, wcol+1, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
        img_bin= cv2.bitwise_not(img_bin)
        cv2.rectangle(img_bin, (0, 0), (344,47), (0), cv2.FILLED)
        cv2.rectangle(img_bin, (600, 0), (1151,65), (0), cv2.FILLED)
        cv2.rectangle(img_bin, (990, 65), (1151,82), (0), cv2.FILLED)


    return img_bin


"""
Erstellt Screenshot vom Bereich game_coords des Bildschirmes
wobei <[0],[1]> die oben linke ecke beschreiben und <[2],[3]>
Länge und Breite des Bildes
"""
def getimage(game_coords):
    with mss.mss() as sct:
        mon = {"top": game_coords[1], "left": game_coords[0], "width": game_coords[2]-game_coords[0], "height": game_coords[3]-game_coords[1]}
        img_np =  np.asarray(sct.grab(mon))

        gray=cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

        return gray

"""
Findet den Spielwinkel bzgl des Mittleren Hexagons/Shapes
Hierzu wird das Bild mittels des GaussianBlur leicht verwaschen
um präzisere Kanten zu finden
Von den Gefundenen Hexagonen wird jenes mit dem geringsten Flächeninhalt
ausgewählt, welches außerdem Zentriert sein muss
Anschließend wird der vom mittelpunkt am weitest entfernteste
Punkt auf dem Hexagon ermittelt und als referenzpunkt benutzt
"""
def find_gang(img_bin,colored):

    game_angle=100
    max_dist=0
    sides=0
    max_coords=((0,0))
    center = np.copy(img_bin[200:500,400:750])
    thresh = cv2.dilate(center,(4,4),1)
    thresh= cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, (5,5))
    color=cv2.cvtColor(img_bin, cv2.COLOR_GRAY2RGB)
    center_mid=((158,174))
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)

    """
    Versuche Zentriertes Hexagon zu finden, welches nicht zu groß ist
    """
    min_area=100000
    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, False), True)
        posc=((int(np.mean(cnt[:,0,1] - center_mid[0])),int(np.mean(cnt[:,0,0]-center_mid[1]))))
        dist= np.sqrt(posc[0]**2 + posc[1]**2)
        if dist<10:
            if len(approx)==6:
                sides=6
                area = cv2.contourArea(cnt)
                if area<min_area:
                    min_area=area
    """
    Falls keines gefunden wurde versuche ein 7-Eck zu finden,
    falls die approximation zu ungenau war
    """
    if min_area==100000:

        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, False), True)
            posc=((int(np.mean(cnt[:,0,1] - center_mid[0])),int(np.mean(cnt[:,0,0]-center_mid[1]))))
            dist= np.sqrt(posc[0]**2 + posc[1]**2)
            if dist<10:
                if len(approx)==7:
                    sides=6
                    area = cv2.contourArea(cnt)
                    if area<min_area:
                        min_area=area
    """
    Falls dennoch kein passendes gefunden wurde gebe einen Fehlerwert aus,
    sodass später eine Annäherung gefunden werden kann

    Speichtert vorherige Werte ab um im Fall des Nicht-Findens eine
    vernünftige Schätzung geben zu können
    <dir> beschreibt die drehrichtung und prev_gang den vorherigen winkel
    """
    global dir
    global prev_gang
    if min_area==100000:


        try:
            game_angle = (prev_gang+60+dir) %60

        except:
            """
            Es wird mit einem falschen Wert weiter gearbeitet,wobei dieser Fall
            nahezu gar nicht auftritt und durch die anzahl der
            Durchläufe pro Sekunde zu vernachlässigen ist
            """
            game_angle = 0
    try:
        dir=game_angle-prev_gang
        if dir >30:
            dir=60-dir
        elif dir<-30:
            dir=60+dir
    except:
        dir=0
    prev_gang =game_angle

    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, False), True)
        posc=((int(np.mean(cnt[:,0,1] - center_mid[0])),int(np.mean(cnt[:,0,0]-center_mid[1]))))
        dist= np.sqrt(posc[0]**2 + posc[1]**2)
        if dist<10:
            #if len(approx)==6:
            sides=6
            area = cv2.contourArea(cnt)
            if area==min_area:
                #Es wurde das passende Hexagon gefunden
                for j in range(len(cnt)):
                    x=cnt[j][0][1]-center_mid[0]
                    y=cnt[j][0][0]-center_mid[1]
                    dist= np.sqrt(x**2 + y**2)
                    #Suche aus den Eckpunkten des zentrierten kleinsten polygons,
                    #Den am weitest entferntesten
                    if dist > max_dist:
                        game_angle = (np.arctan2(y, x)*57.29 +180)%(int(360/6))
                        max_dist=dist
                return game_angle

    return game_angle


"""
Betrachtet mitteleren ausschnitt des Bildes um hier den Spieler
bzw das Dreieck zufinden
Hierzu werden einige Referenzbilder benutzt um mittels
cv2.matchTemplate den Spieler zu zufinden
Und übermalt diesen
Return ist <int>angle_clockwise mit 0°<=> 12Uhr   180°<=> 18Uhr
"""
def findp(orginal):

    center=orginal[200:500,400:750]
    triag=cv2.imread("./Images/1.png",cv2.IMREAD_GRAYSCALE)
    color=cv2.cvtColor(center,cv2.COLOR_GRAY2RGB)
    center_mid=((158,174))

    # Vergleicht
    for i in range(11):
        triag=cv2.imread("./Images/"+str(i+1)+".png",cv2.IMREAD_GRAYSCALE)
        w, h = triag.shape[::-1]
        res = cv2.matchTemplate(center,triag,cv2.TM_CCOEFF_NORMED)
        threshold=0.6
        loc = np.where( res >= threshold)
        coords=((0,0))
        """
        Falls Dreieck gefunden, wird es überdeckt, damit später die
        Distanzen vernünftig bestimmt werden können und nicht durch
        dieses gestört werden
        """
        for pt in zip(*loc[::-1]):
            orginal=cv2.rectangle(orginal, (pt[0]+400, pt[1]+200), (pt[0] + w+400, pt[1] + h+200), 0, cv2.FILLED)
            coords = ((int(pt[0]+w/2), int(pt[1]+h/2)))
            break;
        if not len(loc[0])==0:
            break;
        elif i==10:
            coords=((0,0))


    pangle = 360 - (np.arctan2((coords[0]-center_mid[1]),(coords[1]-center_mid[0]))*57.2958 +180)
    pangle=int(pangle)
    """
    Falls kein Spieler gefunden,was jedoch
    nahezu nie vorkommt, nur in uninteressanten Randfällen
    """
    if coords == ((0,0)):
        pangle=370


    return pangle


"""
Schaut ob "LEVEL" an passener Stelle steht
"""
def lost(bin):

    temp= cv2.imread("./Images/11.png",cv2.IMREAD_GRAYSCALE)
    res = cv2.matchTemplate(bin[245:305,20:300],temp,cv2.TM_CCOEFF_NORMED)
    return not (abs(res)>0.8)


"""
Rechnet Polarkoordinaten zu karthesischen Koordinaten um
"""
def pol2cart(angle, dist):
    x = dist * np.cos(angle)
    y = dist * np.sin(angle)
    return(x, y)


"""
Bestimmt die längen von mitte zu innerer wand
die stärke der Inneren wand
und die Länge vom Ende der inneren Wand zu nächsten wand
Und gibt diese //oder eine auswahl davon zusammen mit ihrem Winkel
zurück
"""
def get_dist(img_bin,color,colored,angle,sides,pangle,mid,game_coords):

    #((game_coords[3]-game_coords[1])/2-30)
    if bool(pangle)==True:
        angle=int(angle*57.2958)
    #my_ang=int(360-angle+180)%360
    my_ang= angle%360
    #fac=(1+(np.abs(np.sin(math.radians(my_ang))))**2/(1.5))
    fac=1
    length=((game_coords[3]-game_coords[1])/2-10)*fac
    outer_x,outer_y=pol2cart(math.radians(angle),length)
    outer_x = int(mid[0]+outer_x)
    outer_y = int(mid[1]+outer_y)
    dist=np.zeros((3))
    n=-1
    found_inner_wall=False
    found_inner_end =False
    finished        =False
    inner_wall=((0,0))
    end_inner_wall=((outer_y,outer_x))
    first_wall=((outer_y,outer_x))
    steps=125
    begin_inner=0
    end_inner=steps
    begin_wall=steps
    #print(end_inner_wall)
    while n<steps and not bool(finished):
        n+=1
        if not bool(found_inner_wall):
            coordsx=int(mid[0] - (mid[0]-outer_x)*n/steps)
            coordsy=int(mid[1]- (mid[1]-outer_y)*n/steps)
            if img_bin[coordsx][coordsy]==255:
                found_inner_wall=True
                inner_wall=((coordsy,coordsx))
                begin_inner=n
        elif not bool(found_inner_end):
            coordsx=int(mid[0] - (mid[0]-outer_x)*n/steps)
            coordsy=int(mid[1]- (mid[1]-outer_y)*n/steps)
            if img_bin[coordsx][coordsy]==0:
                found_inner_end=True
                end_inner=n
                end_inner_wall=((coordsy,coordsx))
        else:
            begin_wall=n
            coordsx=int(mid[0] - (mid[0]-outer_x)*n/steps)
            coordsy=int(mid[1]- (mid[1]-outer_y)*n/steps)
            if img_bin[coordsx][coordsy]==255:
                finished=True
                first_wall=((coordsy,coordsx))

    angle=int(360-angle+180)%360
    dist[0]=angle/360
    dist[1]=((end_inner-begin_inner)/fac)/steps
    dist[2]=((begin_wall-end_inner)/fac)/steps

    if bool(colored)==True:
        cv2.line(color,(mid[1],mid[0]),(int(outer_y),int(outer_x)),(255,0,0),5)
        cv2.line(color,inner_wall,end_inner_wall,(0,0,255),5)
        #cv2.line(color,(mid[1],mid[0]),inner_wall,(0,0,0),5)
        cv2.line(color,end_inner_wall,first_wall,(0,255,0),5)


    return dist

"""
Zentrale Funktion der Bildverarbeitung
Steuert und koodiniert die anderen Funktionen
Als Input kann bestimmt werden, ob ein Window erzeugt werden soll
in welchem man erkennen kann wie das Ergebnis aussieht
"""
def get_data(colored):

    game_coords=[1,35,1151,754]
    gray=getimage(game_coords)
    bin = conv2bw(gray, game_coords)
    color=cv2.cvtColor(bin,cv2.COLOR_GRAY2RGB)
    alive = lost(bin)
    game_angle=find_gang(bin,colored)
    pangle=findp(bin)/360
    mid=((int((game_coords[3]-game_coords[1])/2  +1),int((game_coords[2]-game_coords[0])/2 -1)))
    dists=np.zeros((7,3))
    i=0
    for ang in range(0,360,60):
        dists[i]=get_dist(bin,color,colored,game_angle+30+ang,6,0,mid,game_coords)
        dists[i][0] = dists[i][0] -pangle
        if  dists[i][0] >0.5:
            dists[i][0] = -(6/6) +dists[i][0]
        elif dists[i][0] < -0.5:
            dists[i][0]= (6/6)+dists[i][0]
        i+=1
    #print(pangle)
    dists[6]=get_dist(bin,color,colored, 360- pangle*360+180  ,6,0,mid,game_coords)
    dists[6][0]=0
    dists= dists[np.argsort(dists[:,0])]
    dist = np.abs(dists.ravel())

    if bool(colored)==True:
        cv2.imshow(" ",color)
        cv2.waitKey(1)

    return dist,alive
