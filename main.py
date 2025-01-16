import tkinter as tk
import random


class Navire:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.positions = []
        self.hits = 0

    def is_hit(self, position):
        """   Vérifie si une position touche le navire """
        if position in self.positions:
            self.hits += 1
            return True
        return False

    def is_sunk(self):
        return self.hits == self.size

    @classmethod
    def create_default_ships(cls):
        """Méthode de classe pour créer les navires par défaut d'un joueur"""
        return [
            cls("Porte-avions", 5),
            cls("Croiseur", 4),
            cls("Destroyer 1", 3),
            cls("Destroyer 2", 3),
            cls("Sous-marin 1", 2),
            cls("Sous-marin 2", 2)
        ]


class Plateau:
    """Gère une grille de jeu et les interactions"""
    def __init__(self):
        self.grid = [[None for _ in range(10)] for _ in range(10)]
        self.ships = []

    def place_ship(self, ship, positions):
        """Place un navire sur le plateau aux positions spécifiées"""
        for x, y in positions:
            self.grid[x][y] = ship
        ship.positions = positions
        self.ships.append(ship)

    def is_valid_position(self, positions):
        """Vérifie si les positions sont valides, dans la grille et sans chevauchement"""
        for x, y in positions:
            if not (0 <= x < 10 and 0 <= y < 10):
                return False
            if self.grid[x][y] is not None:
                return False
        return True

    def place_ship_randomly(self, ship):
        """  Place un navire aléatoirement sur le plateau """
        while True:
            orientation = random.choice(["horizontal", "vertical"])
            if orientation == "horizontal":
                x = random.randint(0, 9)
                y = random.randint(0, 9 - ship.size)
                positions = [(x, y + i) for i in range(ship.size)]
            else:
                x = random.randint(0, 9 - ship.size)
                y = random.randint(0, 9)
                positions = [(x + i, y) for i in range(ship.size)]

            if self.is_valid_position(positions):
                self.place_ship(ship, positions)
                break

    def all_ships_sunk(self):
        return all(ship.is_sunk() for ship in self.ships)

    def receive_attack(self, x, y):
        target = self.grid[x][y]

        if target and isinstance(target, Navire):
            self.grid[x][y] = "hit"
            hit_result = target.is_hit((x, y))

            if target.is_sunk():
                for px, py in target.positions:
                    self.grid[px][py] = "sunk"
                return f"{target.name} coulé"
            return "hit"
        elif target == "hit":
            return "hit"
        elif target == "miss":
            return "miss"
        else:
            self.grid[x][y] = "miss"
            return "miss"


class Joueur:
    def __init__(self, name):
        self.name = name
        self.plateau = Plateau()
        self.ships_to_place = Navire.create_default_ships()
        self.placed_ships = []

    def place_all_ships_randomly(self):
        """Place tous les navires de manière aléatoire sur le plateau."""
        for ship in self.ships_to_place:
            self.plateau.place_ship_randomly(ship)


class BatailleNavale:
    def __init__(self, root):
        self.root = root
        self.root.title("Bataille Navale")
        self.main_menu()
        self.last_hit_position = None
        self.last_hit_sunk = False
        self.attack_directions = []


    def main_menu(self):
        self.main_menu_frame = tk.Frame(self.root)
        self.main_menu_frame.pack(expand=True)

        title_label = tk.Label(self.main_menu_frame, text="Bataille Navale", font=("Helvetica", 24, "bold"))
        title_label.pack(pady=50)

        play_button = tk.Button(self.main_menu_frame, text="Jouer", font=("Helvetica", 16), command=self.start_game)
        play_button.pack(pady=20)

    def start_game(self):
        self.main_menu_frame.destroy()
        self.joueur1 = Joueur("Joueur 1")
        self.ordinateur = Joueur("Ordinateur")
        self.current_ship_index = 0
        self.orientation = "horizontal"
        self.ordinateur.place_all_ships_randomly()
        self.setup_ui()

    def setup_ui(self):
        self.instructions_label = tk.Label(self.root, text="Placez vos navires", font=("Helvetica", 14))
        self.instructions_label.pack(pady=10)

        self.player_grid_frame = tk.Frame(self.root)
        self.player_grid_frame.pack()

        self.player_buttons = []
        for i in range(10):
            row = []
            for j in range(10):
                btn = tk.Button(
                    self.player_grid_frame,
                    text=" ",
                    width=3,
                    height=1,
                    command=lambda x=i, y=j: self.place_ship(x, y)
                )
                btn.grid(row=i, column=j)
                row.append(btn)
            self.player_buttons.append(row)

        # Orientation toggle
        self.orientation_button = tk.Button(self.root, text=f"Orientation : {self.orientation.capitalize()}", command=self.toggle_orientation)
        self.orientation_button.pack(pady=5)

    def toggle_orientation(self):
        self.orientation = "vertical" if self.orientation == "horizontal" else "horizontal"
        self.orientation_button.config(text=f"Orientation : {self.orientation.capitalize()}")

    def place_ship(self, x, y):
        """Gère le placement d'un navire sur la grille du joueur."""
        if self.current_ship_index >= len(self.joueur1.ships_to_place):
            return

        current_ship = self.joueur1.ships_to_place[self.current_ship_index]
        ship_positions = []

        if self.orientation == "horizontal":
            ship_positions = [(x, y + i) for i in range(current_ship.size)]
        elif self.orientation == "vertical":
            ship_positions = [(x + i, y) for i in range(current_ship.size)]

        if not self.joueur1.plateau.is_valid_position(ship_positions):
            self.instructions_label.config(text="Placement invalide, essayez encore.")
            return

        self.joueur1.plateau.place_ship(current_ship, ship_positions)
        for px, py in ship_positions:
            self.player_buttons[px][py].config(bg="gray")

        self.current_ship_index += 1
        if self.current_ship_index < len(self.joueur1.ships_to_place):
            next_ship = self.joueur1.ships_to_place[self.current_ship_index]
            self.instructions_label.config(text=f"Placez votre {next_ship.name} ({next_ship.size} cases).")
        else:
            self.start_game_phase()

    def start_game_phase(self):
        self.instructions_label.config(text="La phase de tir commence !")
        self.orientation_button.destroy()

        self.enemy_grid_frame = tk.Frame(self.root)
        self.enemy_grid_frame.pack(pady=20)

        self.enemy_buttons = []
        for i in range(10):
            row = []
            for j in range(10):
                btn = tk.Button(self.enemy_grid_frame, text=" ", width=3, height=1, command=lambda x=i, y=j: self.attack_enemy(x, y))
                btn.grid(row=i, column=j)
                row.append(btn)
            self.enemy_buttons.append(row)

    def attack_enemy(self, x, y):
        """Gère une attaque sur la grille de l'ordinateur."""
        target = self.ordinateur.plateau.grid[x][y]

        if target in ["hit", "miss"]:
            return

        result = self.ordinateur.plateau.receive_attack(x, y)
        if result == "hit":
            self.enemy_buttons[x][y].config(bg="red")
        elif result == "miss":
            self.enemy_buttons[x][y].config(bg="blue")
        elif "coulé" in result:

            ship = [ship for ship in self.ordinateur.plateau.ships if ship.name in result][0]
            for px, py in ship.positions:
                self.enemy_buttons[px][py].config(bg="black")

        if self.ordinateur.plateau.all_ships_sunk():
            self.show_game_over("Vous avez gagné !", "Bien joué")
            return

        self.computer_turn()

    def computer_turn(self):
        """Tour de l'ordinateur pour attaquer le joueur."""
        if self.last_hit_position and not self.last_hit_sunk:
            x, y = self.last_hit_position

            if not self.attack_directions:
                self.attack_directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

            while self.attack_directions:
                dx, dy = self.attack_directions[0]
                nx, ny = x + dx, y + dy

                if 0 <= nx < 10 and 0 <= ny < 10 and self.joueur1.plateau.grid[nx][ny] not in ("hit", "miss", "sunk"):
                    break
                else:
                    self.attack_directions.pop(0)

            if self.attack_directions:
                dx, dy = self.attack_directions[0]
                nx, ny = x + dx, y + dy
            else:
                # Si aucune direction valide n'est trouvée, revenir au tir aléatoire
                nx, ny = self.random_target()
                self.last_hit_position = None  # Réinitialiser si aucune direction n'est trouvée
        else:
            # Si le dernier tir a raté ou le navire a été coulé, tirer au hasard
            nx, ny = self.random_target()

        # Résultat de l'attaque
        result = self.joueur1.plateau.receive_attack(nx, ny)

        # Mettre à jour la couleur de la case du joueur
        if result == "hit":
            self.player_buttons[nx][ny].config(bg="red")
            self.last_hit_position = (nx, ny)
            self.last_hit_sunk = False
        elif result == "miss":
            self.player_buttons[nx][ny].config(bg="blue")
            if self.last_hit_position:
                # Si le dernier tir a raté, changer de direction
                if self.attack_directions:  # Vérifier si la liste n'est pas vide avant d'appeler pop
                    self.attack_directions.pop(0)
        elif "coulé" in result:  # Si un navire est coulé
            ship = [ship for ship in self.joueur1.plateau.ships if ship.name in result][0]
            for px, py in ship.positions:
                self.player_buttons[px][py].config(bg="black")
            self.last_hit_position = None
            self.last_hit_sunk = True
            self.attack_directions = []

        # Vérifier si tous les navires du joueur sont coulés
        if self.joueur1.plateau.all_ships_sunk():
            self.show_game_over("L'ordinateur a gagné !", "Dommage, essaye encore")

    def show_game_over(self, message, result):
        """Affiche la fenêtre de fin de jeu avec le message de résultat."""
        self.root.destroy()  # Ferme la fenêtre du jeu actuel

        # Crée une nouvelle fenêtre de résultat
        result_window = tk.Tk()
        result_window.title("Résultat")

        result_label = tk.Label(result_window, text=message, font=("Helvetica", 16))
        result_label.pack(pady=20)

        result_message = tk.Label(result_window, text=result, font=("Helvetica", 14))
        result_message.pack(pady=10)

        play_again_button = tk.Button(result_window, text="Jouer à nouveau", font=("Helvetica", 14), command=lambda: self.restart_game(result_window))
        play_again_button.pack(pady=20)

        result_window.mainloop()

    def restart_game(self, result_window):
        """Redémarre une nouvelle partie."""
        result_window.destroy()  # Ferme la fenêtre de résultat
        self.root = tk.Tk()
        self.game = BatailleNavale(self.root)
        self.root.mainloop()

    def random_target(self):
        """Génère une cible aléatoire pour l'ordinateur."""
        while True:
            x, y = random.randint(0, 9), random.randint(0, 9)
            if self.joueur1.plateau.grid[x][y] not in ("hit", "miss"):
                return x, y

if __name__ == "__main__":
    root = tk.Tk()
    game = BatailleNavale(root)
    root.mainloop()
