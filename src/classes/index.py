import json

class Index:
    def __init__(self, config_path: str):
        with open(config_path, "r") as file:
            config_data = json.load(file)

        self.org                = config_data["info"]["org"]
        self.main_polished_name = config_data["info"]["main_polished_name"]
        self.main_name          = config_data["info"]["main_name"]
        self.nb_sub_indexes     = int(config_data["info"]["nb_sub_indexes"])
        self.sub_indexes        = config_data["info"]["sub_indexes"]
        self.config             = config_data["info"]["config"]
        self.version            = int(config_data["info"]["version"])

    def __str__(self):
        return f"{self.main_name} by {self.org} with {self.nb_sub_indexes} sub-indexes."

    def is_comprehensive(self) -> bool:
        """Determine if the index is comprehensive based on the number of sub-indexes."""
        return self.nb_sub_indexes > 10

    def display_info(self):
        """Display detailed information about the index."""
        print(f"Organization: {self.org}")
        print(f"Main Polished Index Name: {self.main_polished_name}")
        print(f"Main Index Name: {self.main_name}")
        print(f"Number of Sub-Indexes: {self.nb_sub_indexes}")
        print(f"Sub-Indexes: {', '.join(self.sub_indexes)}")
        print(f"Version: {self.version}")
        print(f"Is Comprehensive: {'Yes' if self.is_comprehensive() else 'No'}")

    def get_patternizable_indexes(self) -> list:
        """Return a list of patternizable indexes, starting with the main index followed by sub-indexes."""
        return [self.main_polished_name] + self.sub_indexes

    def add_sub_index(self, sub_index_name: str):
        """Add a new sub-index."""
        if sub_index_name not in self.sub_indexes:
            self.sub_indexes.append(sub_index_name)
            self.nb_sub_indexes += 1
            print(f"Added '{sub_index_name}'. Total sub-indexes: {self.nb_sub_indexes}")
        else:
            print(f"'{sub_index_name}' already exists.")

    def remove_sub_index(self, sub_index_name: str):
        """Remove a sub-index."""
        if sub_index_name in self.sub_indexes:
            self.sub_indexes.remove(sub_index_name)
            self.nb_sub_indexes -= 1
            print(f"Removed '{sub_index_name}'. Total sub-indexes: {self.nb_sub_indexes}")
        else:
            print(f"'{sub_index_name}' not found.")

    def load_config(self) -> dict:
        """Load configuration from the provided JSON file."""
        with open(self.config, "r") as file:
            config_data = json.load(file)
        return config_data

    def save_config(self, data: dict):
        """Save configuration to the provided JSON file."""
        with open(self.config, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Configuration saved to {self.config}")


# Example usage:
# index_instance = Index(r"\path\to\config.json")
# print(index_instance)
# index_instance.display_info()
# index_instance.add_sub_index("sub_index_4")
# index_instance.remove_sub_index("sub_index_1")
