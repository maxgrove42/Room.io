import configparser


class Config:
    # only read in one config, don't re-read it.
    # essentially make config prop's static
    _config = None

    default_path = 'src/resources/config.properties'
    def __init__(self, filepath = default_path):
        if Config._config is None:
            Config._config = configparser.ConfigParser()
            Config._config.read(filepath)
        self.load_properties()

    def load_properties(self):
        # Flask settings
        self.secret_key = Config._config.get('Flask', 'flask_secret_key', fallback='default_secret_key')
        self.debug = Config._config.getboolean('Flask', 'debug', fallback=False)
        self.flask_host = Config._config.get('Flask', 'flask_host', fallback='127.0.0.1')
        self.flask_port = Config._config.get('Flask', 'flask_port', fallback=5000)

        # Database settings
        self.db_host = Config._config.get('Database', 'db_host', fallback='localhost')
        self.db_port = Config._config.get('Database', 'db_port', fallback=3306)
        self.db_user = Config._config.get('Database', 'db_username', fallback='root')
        self.db_password = Config._config.get('Database', 'db_password', fallback='')
        self.db_name = Config._config.get('Database', 'db_name', fallback='mydatabase')
        self.db_charset = Config._config.get('Database', 'db_charset', fallback='utf8mb4')

if __name__ == "__main__":
    config = Config()
    print(f"Loaded secret_key: {config.secret_key}")
    print(f"Loaded debug: {config.debug}")
    print(f"Loaded flask_host: {config.flask_host}")
    print(f"Loaded flask_port: {config.flask_port}")
    print(f"Loaded db_host: {config.db_host}")
    print(f"Loaded db_port: {config.db_port}")
    print(f"Loaded db_user: {config.db_user}")
    print(f"Loaded db_password: {config.db_password}")
    print(f"Loaded db_name: {config.db_name}")
    print(f"Loaded db_charset: {config.db_charset}")

