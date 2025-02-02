import yaml


class Util:

    @staticmethod
    def load_yaml(file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
            return data
