"""
Správce 12týdenních cyklů (Hybrid system)

Struktura:
- data/active/       - aktivní cyklus (běžná práce)
- data/archive/      - archivované cykly (historie)
- data/cycles_metadata.pkl - info o všech cyklech
"""

import os
import pickle
import pandas as pd
from datetime import datetime, timedelta


class CyclesManager:
    """
    Spravuje cykly - aktivní a archivované
    """
    
    def __init__(self):
        # Cesty
        self.data_dir = "data"
        self.active_dir = "data/active"
        self.archive_dir = "data/archive"
        self.metadata_file = "data/cycles_metadata.pkl"
        
        # Vytvoř složky pokud neexistují
        os.makedirs(self.active_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)
        
        # Načti metadata (info o všech cyklech)
        self.cycles = self.load_metadata()
    
    def load_metadata(self):
        """
        Načte metadata všech cyklů ze souboru
        
        Returns:
            list: [{"id": 1, "start_date": datetime, "status": "active"}, ...]
        """
        # Zkontroluj jestli soubor existuje
        if os.path.exists(self.metadata_file):
            # ANO - načti ho
            with open(self.metadata_file, 'rb') as f:
                cycles = pickle.load(f)
                print(f"✅ Načteno {len(cycles)} cyklů z metadata")
                return cycles
        else:
            # NE - první spuštění, žádné cykly
            print("⚠️ Žádná metadata - první spuštění")
            return []
    
    def save_metadata(self):
        """
        Uloží metadata všech cyklů do souboru
        """
        with open(self.metadata_file, 'wb') as f:
            pickle.dump(self.cycles, f)
        print(f"✅ Uloženo {len(self.cycles)} cyklů do metadata")
    
    def get_active_cycle(self):
        """
        Najde a vrátí aktivní cyklus
        
        Returns:
            dict nebo None: {"id": 2, "start_date": datetime, ...}
        """
        # Projdi všechny cykly a najdi ten s status="active"
        for cycle in self.cycles:
            if cycle.get("status") == "active":
                return cycle
        
        # Žádný aktivní cyklus
        return None
    
    def create_new_cycle(self, start_date=None):
        """
        Vytvoří nový aktivní cyklus
        
        Args:
            start_date: Kdy cyklus začíná (default: dnes)
        
        Returns:
            dict: Metadata nového cyklu
        """
        # Pokud není zadán start_date, použij dnes
        if start_date is None:
            start_date = datetime.now()
        
        # Vypočítej cycle_id (největší ID + 1)
        if self.cycles:
            # Máme nějaké cykly - vezmi max ID a přičti 1
            cycle_id = max(c["id"] for c in self.cycles) + 1
        else:
            # První cyklus
            cycle_id = 1
        
        # Spočítej end_date (za 12 týdnů)
        end_date = start_date + timedelta(days=84)  # 12 týdnů = 84 dní
        
        # Vytvoř metadata pro nový cyklus
        new_cycle = {
            "id": cycle_id,
            "start_date": start_date,
            "end_date": end_date,
            "status": "active",
            "created_at": datetime.now()
        }
        
        # Přidej do listu cyklů
        self.cycles.append(new_cycle)
        
        # Ulož metadata
        self.save_metadata()
        
        print(f"✅ Vytvořen cyklus #{cycle_id}: {start_date.date()} - {end_date.date()}")
        
        return new_cycle
        """
        Archivuje aktivní cyklus
        
        Proces:
        1. Najde aktivní cyklus
        2. Načte všechna data z data/active/
        3. Uloží do data/archive/cycle_XXX.pkl
        4. Označ cyklus jako "completed"
        5. Smaže data z data/active/
        """
        # Najdi aktivní cyklus
       
    
    def archive_current_cycle(self):

        active = self.get_active_cycle()
        
        if not active:
            print("Žádný aktivní cyklus k archivaci")
            return False
        
        cycle_id = active["id"]
        
        print(f"Archivuji cyklus #{cycle_id}...")
        
        # Název archive souboru
        archive_filename = f"cycle_{cycle_id:03d}.pkl"
        # :03d = "formátuj jako 3 cifry s nulami" → cycle_001.pkl
        
        archive_path = os.path.join(self.archive_dir, archive_filename)
        
        # Shromáždi všechna data z active/
        archive_data = {
            "metadata": active,
            "tasks": self._load_file_if_exists("data/active/tasks_dataframe.pkl"),
            "goals": self._load_file_if_exists("data/active/goals_dataframe.pkl"),
            "notes": self._load_file_if_exists("data/active/notes_file.pkl"),
            "rewards": self._load_file_if_exists("data/active/reward_dataframe.pkl")
        }
        
        # Ulož do archive souboru
        with open(archive_path, 'wb') as f:
            pickle.dump(archive_data, f)
        
        print(f"Data uložena do {archive_filename}")
        
        # Označ cyklus jako "completed"
        active["status"] = "completed"
        active["archived_at"] = datetime.now()
        active["archive_file"] = archive_filename
        
        # Ulož aktualizovaná metadata
        self.save_metadata()
        
        # Smaž soubory z active/
        self._clear_active_directory()
        
        print(f"Cyklus #{cycle_id} archivován")
        
        return True
    
        
    
    def _load_file_if_exists(self, filepath):
        """
        Pomocná funkce - načte pickle soubor pokud existuje
        
        Args:
            filepath: Cesta k souboru
        
        Returns:
            data nebo None
        """
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        return None
    
    def _clear_active_directory(self):
        """
        Smaže všechny .pkl soubory z data/active/ a vytvoří prázdné
        """
        
        
        files_to_delete = [
            "tasks_dataframe.pkl",
            "goals_dataframe.pkl",
            "notes_file.pkl",
            "reward_dataframe.pkl",
            "settings_dataframe.pkl"
        ]
        
        # Smaž staré soubory
        for filename in files_to_delete:
            filepath = os.path.join(self.active_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"Smazán {filename}")
        
        print("Active složka vyčištěna")
        
        # Vytvoř prázdné soubory pro nový cyklus
        print("Vytvářím prázdné soubory...")
        
        empty_tasks = pd.DataFrame(columns=["name", "subclass", "date", "hours", "score", "review"])
        empty_goals = pd.DataFrame(columns=["goal_name", "subclass", "timer", "average_score", "date_of_creation", "checked", "end_date", "completed"])
        empty_notes = pd.DataFrame(columns=["date", "subclass", "topic", "text"])
        empty_rewards = pd.DataFrame(columns=["date", "name", "time", "finished", "actual_time"])
        empty_settings = pd.DataFrame(columns=["goals_set"])
        
        empty_tasks.to_pickle(f"{self.active_dir}/tasks_dataframe.pkl")
        empty_goals.to_pickle(f"{self.active_dir}/goals_dataframe.pkl")
        empty_notes.to_pickle(f"{self.active_dir}/notes_file.pkl")
        empty_rewards.to_pickle(f"{self.active_dir}/reward_dataframe.pkl")
        empty_settings.to_pickle(f"{self.active_dir}/settings_dataframe.pkl")
        
        print("Prázdné soubory vytvořeny")
    
    def needs_new_cycle(self):
        """
        Zkontroluje jestli je potřeba začít nový cyklus
        
        Returns:
            bool: True pokud uplynulo 12 týdnů nebo žádný aktivní cyklus
        """
        active = self.get_active_cycle()
        
        # Žádný aktivní cyklus? Potřeba vytvořit
        if not active:
            return True
        
        # Kolik dní od startu?
        start_date = active["start_date"]
        today = datetime.now()
        days_since_start = (today - start_date).days
        
        # Uplynulo 12 týdnů? (84 dní)
        if days_since_start >= 84:
            return True
        
        return False
    
    def get_all_cycles_summary(self):
        """
        Vrátí přehled všech cyklů (pro statistiky)
        
        Returns:
            list: [{"id": 1, "start": datetime, "status": "completed"}, ...]
        """
        return self.cycles.copy()  # Kopie aby se neupravoval originál