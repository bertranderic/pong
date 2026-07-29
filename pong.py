# Auteur: Eric Bertrand

import os
import sys
import pygame
from random import randint
from pygame.locals import *



def get_asset_path(relative_path):
    """Retourne un chemin d’asset compatible avec Python et PyInstaller onefile."""
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)

pygame.init()

audio_terrain = pygame.mixer.Sound(get_asset_path('assets/pong_sound.mp3'))
audio_game_over = pygame.mixer.Sound(get_asset_path('assets/game_over_sound.mp3'))
audio_raquette = pygame.mixer.Sound(get_asset_path('assets/ping_sound.mp3'))
audio_niveau = pygame.mixer.Sound(get_asset_path('assets/level_sound.mp3'))
audio_point = pygame.mixer.Sound(get_asset_path('assets/sou_sound.mp3'))

image_plateau_jeu = pygame.image.load(get_asset_path("assets/jeu.png"))

pygame.joystick.init()

COULEUR_NOIR = (0, 0, 0)
COULEUR_BLANC = (255, 255, 255)
TAILLE_FENETRE_HAUTEUR = 1000
TAILLE_FENETRE_LARGEUR = 600

vitesse_raquette = [1, 1]
vitesse_balle = [5, 5]

players_tour = True
score = [0, 0]
niveau = 1

move_up= False
move_down = False

fenetre = pygame.display.set_mode((TAILLE_FENETRE_HAUTEUR, TAILLE_FENETRE_LARGEUR))

loading_image = pygame.image.load(get_asset_path("assets/background.jpg"))

loading_rect = loading_image.get_rect()
loading_rect.center = (500, 300)
background_color = (255, 255, 255)

touche_raquette = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

debut = pygame.time.get_ticks()

while pygame.time.get_ticks() - debut < 3000:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    fenetre.fill(COULEUR_BLANC)
    fenetre.blit(loading_image, loading_rect)
    pygame.display.flip()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            
                        
    fenetre.fill(background_color)

    # Afficher la fenêtre
    pygame.display.flip()
	

    limite_haut = pygame.Rect(0, 0, 1000, 100)
    limite_bas = pygame.Rect(0, 600 - 100, 1000, 100)
    limite_droite = pygame.Rect(1032, 0, 1, 600)
    limite_gauche = pygame.Rect(-32, 0, 1, 600)

    pieces = [
        pygame.Rect(randint(100, 900), randint(100, 500), 20, 20)
        for _ in range(10)
    ]

    touche_raquette = [0] * 10

    objet_balle = pygame.Rect(487, 287, 32, 32)
    objet_raquette_1 = pygame.Rect(40, 250, 15, 100)
    objet_raquette_2 = pygame.Rect(940, 250, 15, 100)
    
    ma_police = pygame.font.SysFont('Comic Sans MS', 30)

    break

def affiche_titre():
    """Affiche le titre du jeu"""
    titre_jeu_objet = ma_police.render('Pong', False, COULEUR_BLANC)
    fenetre.blit(titre_jeu_objet, (465, 40))
    


def affiche_score(joueur_1, joueur_2):
    """affiche le nombre de coups et le niveau atteinds pendant le jeu"""
    # joueur 1
    point_texte_joueur_1 = ma_police.render('score: {}.'.format(joueur_1), False, COULEUR_BLANC)
    fenetre.blit(point_texte_joueur_1, (110, 40))
    # joueur 2 'ia'
    point_texte_joueur_2 = ma_police.render('score: {}.'.format(joueur_2), False, COULEUR_BLANC)
    fenetre.blit(point_texte_joueur_2, (740, 540))



def check_collision(ball, bas, haut, cote_gauche, cote_droit, joueur_1, joueur_2):
    """verifie les collisions et renvoie un nombre selon l'endroit toucher"""
    if ball.colliderect(bas) or ball.colliderect(haut):
        return 1
    elif ball.colliderect(cote_gauche):
        return 2
    elif ball.colliderect(cote_droit):
        return 3
    elif ball.colliderect(joueur_1):
        return 4
    elif ball.colliderect(joueur_2):
        return 5


def game_over():
    debut = pygame.time.get_ticks()

    while pygame.time.get_ticks() - debut < 3000:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        """Affiche un ecran de game over"""
        message = ma_police.render("Game Over", True, COULEUR_NOIR)
        message_rect = message.get_rect(center=(1000/2, 600/2))
        fenetre.fill(COULEUR_BLANC)
        fenetre.blit(message, message_rect)
        pygame.display.flip()
   

clock = pygame.time.Clock()

#pongData = open('data/pong.csv', 'a+')
#print("x,y,vx,vy,objet_raquette_2", file=pongData)

continuer = True
while continuer:
    clock.tick(50)
     
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit(0)

        elif event.type == KEYDOWN and event.key == pygame.K_DOWN:
            move_down = True
            move_up = False
        elif event.type == KEYDOWN and event.key == pygame.K_UP:
           move_up = True
           move_down=False
        elif event.type == KEYUP:
            move_down = False
            # print(event.key)
            move_up = False
        #elif event.type == KEYDOWN and event.key == pygame.K_DOWN and objet_raquette_2.y < 400:
            #objet_raquette_2.y += vitesse_raquette[1]
        #elif event.type == KEYDOWN and event.key == pygame.K_UP and objet_raquette_2.y > 100:
            #objet_raquette_2.y -= vitesse_raquette[1]

    # value_to_predict = pd.concat([to_predict, pd.DataFrame({'x' : [objet_balle.x],  'y': [objet_balle.y], 'vx' : [vitesse_balle[0]], 'vy' : [vitesse_balle[1]]})], ignore_index=True)
    # moveTo = rfr.predict(value_to_predict)

    objet_raquette_2.y = objet_balle.y - 34

    collision = check_collision(objet_balle, limite_bas, limite_haut, limite_gauche,
                                limite_droite, objet_raquette_1, objet_raquette_2)
    if move_up and objet_raquette_1.y > 100 :
        objet_raquette_1.y -= 10
    if move_down and objet_raquette_1.y < 400:
        objet_raquette_1.y += 10
    
        
    # Cas de figure: si la balle touche la raquette, le haut ou le bas etc.. voir fonction
    if collision == 1:
        audio_terrain.play()
        vitesse_balle[1] = -vitesse_balle[1]
    elif collision == 2:
        score[1] += 1
        objet_balle.x = 487
        objet_balle.y = 287
        audio_game_over.play()
        game_over()
    elif collision == 3:
        score[0] += 1
        objet_balle.x = 487
        objet_balle.y = 287
        audio_game_over.play()
        game_over()
    elif collision == 4:
        audio_raquette.play()
        vitesse_balle[0] = -vitesse_balle[0] * 1.05
    elif collision == 5:
        audio_raquette.play()
        vitesse_balle[0] = -vitesse_balle[0] * 1.05

    # la balle se deplace
    objet_balle.x += vitesse_balle[0]
    objet_balle.y += vitesse_balle[1]
    
    fenetre.blit(image_plateau_jeu, (0, 0))

    # on verifie quel joueur a frapper la balle
    if objet_balle.colliderect(objet_raquette_1):
        players_tour = True
    elif objet_balle.colliderect(objet_raquette_2):
        players_tour = False
            
    joueur = 0 if players_tour else 1

    for i, piece in enumerate(pieces):

        if objet_balle.colliderect(piece):

            if touche_raquette[i] == 0:
                vitesse_balle[1] *= -1
                score[joueur] += 10
                audio_point.play()

            touche_raquette[i] += 1

        if touche_raquette[i] == 0:
            pygame.draw.rect(fenetre, COULEUR_BLANC, piece)
        else:
            pygame.draw.rect(fenetre, COULEUR_NOIR, piece)
    
    affiche_titre()
    affiche_score(score[0], score[1])

    pygame.draw.rect(fenetre, COULEUR_BLANC, objet_raquette_1)
    pygame.draw.rect(fenetre, COULEUR_BLANC, objet_raquette_2)
    pygame.draw.rect(fenetre, COULEUR_BLANC, objet_balle)
   
    pygame.display.flip()

pygame.quit()
