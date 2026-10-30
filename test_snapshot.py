from src.data.loader import RaceDataLoader
from src.race_engine.snapshot import DriverSnapshotEngine


def main():
    loader = RaceDataLoader()
    engine = DriverSnapshotEngine(loader)
    result = engine.snapshot(44, 28)

    print(result)


if __name__ == "__main__":
    main()
