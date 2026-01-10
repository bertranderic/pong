# Auteur: Eric Bertrand
# Version corrigée et optimisée

import pandas as pd
import pygame
from random import randint
from pygame.locals import *
from sklearn.ensemble import RandomForestRegressor
import os

# --- INITIALISATION ---
pygame.init()
pygame.mixer.init()

# Couleurs
COULEUR_NOIR = (0, 0, 0)
COULEUR_BLANC = (255, 255, 255)

# Dimensions
TAILLE_FENETRE_LARGEUR = 1000  # Attention: dans ton code original Hauteur/Largeur étaient inversés dans les noms variables
TAILLE_FENETRE_HAUTEUR = 600

# Fenêtre
fenetre = pygame.display.set_mode((TAILLE_FENETRE_LARGEUR, TAILLE_FENETRE_HAUTEUR))
pygame.display.set_caption("Pong IA - Eric Bertrand")
clock = pygame.time.Clock()

# --- CHARGEMENT DES ASSETS ---
# On utilise try/except pour éviter que le jeu plante si un son manque
def charger_son(chemin):
    try:
        return pygame.mixer.Sound(chemin)
    except:
        return None # Retourne rien si pas de son, mais ne plante pas

audio_terrain = charger_son('assets/pong_sound.mp3')
audio_game_over = charger_son('assets/game_over_sound.mp3')
audio_raquette = charger_son('assets/ping_sound.mp3')
audio_point = charger_son('assets/sou_sound.mp3')

# Images
try:
    loading_image = pygame.image.load("assets/background.jpg")
    image_plateau_jeu = pygame.image.load("assets/jeu.png")
except:
    # Fallback si pas d'image: on remplit de noir
    loading_image = pygame.Surface((TAILLE_FENETRE_LARGEUR, TAILLE_FENETRE_HAUTEUR))
    image_plateau_jeu = pygame.Surface((TAILLE_FENETRE_LARGEUR, TAILLE_FENETRE_HAUTEUR))

loading_rect = loading_image.get_rect()
loading_rect.center = (TAILLE_FENETRE_LARGEUR // 2, TAILLE_FENETRE_HAUTEUR // 2)

# --- IA & DATA SCIENCE ---
print("Entraînement de l'IA en cours... Veuillez patienter.")

# Chargement des données
try:
    df = pd.read_csv('data/pong.csv')
    x_train = df.drop(columns="objet_raquette_2")
    y_train = df["objet_raquette_2"]

    # Création et entrainement du modèle
    rfr = RandomForestRegressor(n_estimators=10) # n_estimators réduit pour charger plus vite
    rfr.fit(x_train, y_train)
    print("IA Entraînée avec succès !")
    ia_active = True
except Exception as e:
    print(f"Erreur lors du chargement de l'IA : {e}")
    ia_active = False

# --- OBJETS DU JEU ---

# Limites
limite_haut = pygame.Rect(0, 0, 1000, 100)
limite_bas = pygame.Rect(0, 500, 1000, 100) # 600 - 100
limite_droite = pygame.Rect(1000, 0, 20, 600)
limite_gauche = pygame.Rect(-20, 0, 20, 600)

# Raquettes et Balle
objet_balle = pygame.Rect(487, 287, 32, 32)
objet_raquette_1 = pygame.Rect(40, 250, 15, 100)
objet_raquette_2 = pygame.Rect(940, 250, 15, 100)

vitesse_raquette = 10
vitesse_balle = [5, 5]
score = [0, 0]

# --- GESTION DES PIECES (OBSTACLES) ---
# Au lieu de 10 variables, on utilise une liste de dictionnaires
pieces = []
for _ in range(10):
    pieces.append({
        "rect": pygame.Rect(randint(100, 900), randint(100, 450), 20, 20),
        "touche_count": 0, # Compteur de touches pour cette pièce
        "actif": True
    })

ma_police = pygame.font.SysFont('Comic Sans MS', 30)

# --- FONCTIONS ---

def affiche_titre():
    titre = ma_police.render('Pong', False, COULEUR_BLANC)
    fenetre.blit(titre, (465, 40))

def affiche_score(j1, j2):
    txt_j1 = ma_police.render(f'score: {j1}.', False, COULEUR_BLANC)
    fenetre.blit(txt_j1, (110, 40))
    txt_j2 = ma_police.render(f'score: {j2}.', False, COULEUR_BLANC)
    fenetre.blit(txt_j2, (740, 540))

def check_collision(ball, j1, j2):
    # Collisions basiques
    if ball.colliderect(limite_bas) or ball.colliderect(limite_haut):
        return 1 # Mur haut/bas
    elif ball.colliderect(limite_gauche):
        return 2 # Point pour J2 (IA)
    elif ball.colliderect(limite_droite):
        return 3 # Point pour J1 (Joueur)
    elif ball.colliderect(j1):
        return 4 # Touche raquette joueur
    elif ball.colliderect(j2):
        return 5 # Touche raquette IA
    return 0

def reset_balle():
    objet_balle.x = 487
    objet_balle.y = 287
    # On inverse la direction pour varier le service
    vitesse_balle[0] = -vitesse_balle[0]
    # Reset simple des pièces si besoin (optionnel)
    # for p in pieces: p["touche_count"] = 0

def ecran_game_over():
    msg = ma_police.render("Game Over", True, COULEUR_NOIR)
    msg_rect = msg.get_rect(center=(TAILLE_FENETRE_LARGEUR/2, TAILLE_FENETRE_HAUTEUR/2))
    fenetre.fill(COULEUR_BLANC)
    fenetre.blit(msg, msg_rect)
    pygame.display.flip()
    if audio_game_over: audio_game_over.play()
    pygame.time.delay(3000)

# --- BOUCLE PRINCIPALE ---

continuer = True
move_up = False
move_down = False
players_tour = True # True = Tour du joueur (gauche), False = Tour IA

while continuer:
    clock.tick(70) # 70 FPS
     
    for event in pygame.event.get():
        if event.type == QUIT:
            continuer = False
        
        # Gestion clavier
        elif event.type == KEYDOWN:
            if event.key == pygame.K_DOWN:
                move_down = True
            elif event.key == pygame.K_UP:
                move_up = True
        elif event.type == KEYUP:
            if event.key == pygame.K_DOWN:
                move_down = False
            elif event.key == pygame.K_UP:
                move_up = False

    # --- LOGIQUE IA ---
    if ia_active:
        # On prépare les données pour la prédiction (format liste 2D)
        donnees_entree = [[objet_balle.x, objet_balle.y, vitesse_balle[0], vitesse_balle[1]]]
        try:
            prediction_y = rfr.predict(donnees_entree)[0]
            
            # Mouvement fluide vers la prédiction
            # L'IA essaie d'aligner le centre de sa raquette avec la prédiction
            centre_raquette = objet_raquette_2.centery
            
            if centre_raquette < prediction_y - 10:
                if objet_raquette_2.bottom < 500: # Limite basse
                    objet_raquette_2.y += 6 # Vitesse de l'IA (un peu plus lente que la balle pour être battable)
            elif centre_raquette > prediction_y + 10:
                if objet_raquette_2.top > 100: # Limite haute
                    objet_raquette_2.y -= 6
        except:
            pass # Si erreur prediction, l'IA ne bouge pas

    # --- MOUVEMENT JOUEUR ---
    if move_up and objet_raquette_1.top > 100:
        objet_raquette_1.y -= vitesse_raquette
    if move_down and objet_raquette_1.bottom < 500:
        objet_raquette_1.y += vitesse_raquette

    # --- MOUVEMENT BALLE ---
    objet_balle.x += vitesse_balle[0]
    objet_balle.y += vitesse_balle[1]

    # --- COLLISIONS PRINCIPALES ---
    collision = check_collision(objet_balle, objet_raquette_1, objet_raquette_2)
    
    if collision == 1: # Mur haut/bas
        if audio_terrain: audio_terrain.play()
        vitesse_balle[1] = -vitesse_balle[1]
    
    elif collision == 2: # IA marque
        score[1] += 1
        reset_balle()
        ecran_game_over() # Tu avais mis game over à chaque point ?
        
    elif collision == 3: # Joueur marque
        score[0] += 1
        reset_balle()
        ecran_game_over()

    elif collision == 4: # Raquette Joueur
        if audio_raquette: audio_raquette.play()
        vitesse_balle[0] = -vitesse_balle[0]
        # Petite accélération pour le fun ?
        # vitesse_balle[0] *= 1.05 
        players_tour = True

    elif collision == 5: # Raquette IA
        if audio_raquette: audio_raquette.play()
        vitesse_balle[0] = -vitesse_balle[0]
        players_tour = False

    # --- GESTION DES PIECES (OPTIMISÉE) ---
    # On détermine qui joue pour savoir qui gagne les points des carrés
    # (Note: ta logique originale donne le point au joueur actif si la balle touche un carré)
    
    for piece in pieces:
        if objet_balle.colliderect(piece["rect"]) and piece["touche_count"] >= 0:
            # Si c'est la première touche (touche_count == 0)
            if piece["touche_count"] == 0:
                vitesse_balle[1] = -vitesse_balle[1] # Rebond
                if audio_point: audio_point.play()
                
                # Attribution des points selon le tour
                if players_tour:
                    score[0] += 10
                else:
                    score[1] += 10
            
            piece["touche_count"] += 1

    # --- DESSIN ---
    fenetre.blit(image_plateau_jeu, (0, 0))
    
    affiche_titre()
    affiche_score(score[0], score[1])

    pygame.draw.rect(fenetre, COULEUR_BLANC, objet_raquette_1)
    pygame.draw.rect(fenetre, COULEUR_BLANC, objet_raquette_2)
    pygame.draw.rect(fenetre, COULEUR_BLANC, objet_balle)

    # Dessin des pièces
    for piece in pieces:
        if piece["touche_count"] > 0:
            # Touché -> Noir
            pygame.draw.rect(fenetre, COULEUR_NOIR, piece["rect"])
        else:
            # Pas touché -> Blanc
            pygame.draw.rect(fenetre, COULEUR_BLANC, piece["rect"])

    pygame.display.flip()

pygame.quit()
quit()