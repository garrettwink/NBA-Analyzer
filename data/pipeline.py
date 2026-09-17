from fetch import build_historical_dataset, save_historical_dataset


def main():
    seasons = [f"{year}-{str(year + 1)[-2:]}" for year in range(2010, 2026)]
    stats_historical = build_historical_dataset(seasons)
    save_historical_dataset(stats_historical)

if __name__ == "__main__":
    main()