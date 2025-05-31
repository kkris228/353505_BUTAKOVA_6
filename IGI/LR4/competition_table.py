import csv
import pickle


class SerializationMixin:
    """Mixin providing interface for serialization methods."""
    def save(self, filename):
        raise NotImplementedError("Save method not implemented.")

    def load(self, filename):
        raise NotImplementedError("Load method not implemented.")


class CompetitionTable(SerializationMixin):
    _instances_count = 0  # class attribute

    def __init__(self, data=None):
        self._data = data or {}
        CompetitionTable._instances_count += 1

    @classmethod
    def instances_count(cls):
        return cls._instances_count

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        if isinstance(value, dict):
            self._data = value
        else:
            raise ValueError("Data must be a dictionary.")

    def add_team(self, team_name, points):
        self._data[team_name] = points

    def get_team_points(self, team_name):
        return self._data.get(team_name, None)

    def sort_by_points_desc(self):
        return sorted(self._data.items(), key=lambda item: item[1], reverse=True)

    def get_winner(self):
        sorted_list = self.sort_by_points_desc()
        return sorted_list[0] if sorted_list else (None, 0)

    def __str__(self):
        sorted_teams = self.sort_by_points_desc()
        return "\n".join(f"{idx + 1}. {team}: {points} pts" for idx, (team, points) in enumerate(sorted_teams))

    def __len__(self):
        return len(self._data)

    def __contains__(self, team_name):
        return team_name in self._data


class CompetitionTableCSV(CompetitionTable):
    def __init__(self, data=None):
        super().__init__(data)

    def save(self, filename):
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Team', 'Points'])
                for team, points in self._data.items():
                    writer.writerow([team, points])
        except Exception as e:
            print(f"Error saving to CSV: {e}")

    def load(self, filename):
        try:
            with open(filename, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self._data = {row['Team']: int(row['Points']) for row in reader}
        except Exception as e:
            print(f"Error loading from CSV: {e}")


class CompetitionTablePickle(CompetitionTable):
    def __init__(self, data=None):
        super().__init__(data)

    def save(self, filename):
        try:
            with open(filename, 'wb') as f:
                pickle.dump(self._data, f)
        except Exception as e:
            print(f"Error saving to pickle: {e}")

    def load(self, filename):
        try:
            with open(filename, 'rb') as f:
                self._data = pickle.load(f)
        except Exception as e:
            print(f"Error loading from pickle: {e}")

def safe_input(prompt, valid_func=None, error_msg="Invalid input. Please try again."):
    while True:
        value = input(prompt).strip()
        if valid_func is None or valid_func(value):
            return value
        print(error_msg)


def demo_task(table, filename, format_name):
    """
    Runs the demo task with printing output:
    - saves and loads data
    - prints standings
    - prints winner
    - asks for team name and prints info
    """
    table.save(filename)
    table.load(filename)

    print(f"\n--- Competition Table: {format_name} Variant ---")
    print("\nCurrent standings:")
    print(table)

    winner = table.get_winner()
    print(f"\nWinner is {winner[0]} with {winner[1]} points.\n")

    while True:
        team_name = input("Enter team name to search: ").strip()
        if team_name:
            break
        print("Please enter a non-empty team name.")

    points = table.get_team_points(team_name)
    if points is not None:
        print(f"Team '{team_name}' has {points} points.")
    else:
        print(f"Team '{team_name}' not found.")

