from libs.applib import App
from toml import loads

CONFIG_FILE: str = "config.toml"


def loadConfig(configFile: str) -> dict:
    with open(configFile) as file:
        configData = loads(file.read())
    return configData


def main():
    config = loadConfig(CONFIG_FILE)
    app = App(config)

    app.run(True)


if __name__ == "__main__":
    main()
