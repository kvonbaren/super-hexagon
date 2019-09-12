## Vorschau

Durch das Klicken auf das unterliegene Bild gelangen Sie zu einem Video wo Sie das Programm mit dem Neuronalen Netzwerk als Spieler in 
Aktion sehen können.

[![](http://img.youtube.com/vi/CUSgHiqdhpE/0.jpg)](http://www.youtube.com/watch?v=CUSgHiqdhpE "")

## Erläuterung des Programmablaufes
#### Aufnahme des Bildes
Zuerst wird das Ausgangsbild beötigt, hierzu wird ein Bild in einem Bereich des Monitors aufgenommen.

<img src="Tutorial/1.png" width=1080> 

Zunächst wird es zu einem Graustufenbild transformiert, dies findet hier nach dem CCIR601 statt und nicht durch das arithmetische Mittel.

<img src="Tutorial/2.png" width=1080> 

#### Binarisierung 
Mittels des Graustufenbildes wird nun ein Histogramm als Hilfsmittel erzeugt, um einen Schwellenwert zu bilden.
Somit kann eine Schwarz-Weiß-Segmentierung vorgenommen werden.
Hierzu wird meistens der Farbwert des Bildpunktes in der Mitte gewählt, ist dieser zu hoch wird nach einem anderen gesucht.

<img src="Tutorial/3.png" width=1080> 




<img src="Tutorial/4.png" width=1080> 

<img src="Tutorial/5.png" width=1080> 

<img src="Tutorial/6.png" width=1080> 

<img src="Tutorial/7.png" width=1080> 

<img src="Tutorial/8.png" width=1080> 
