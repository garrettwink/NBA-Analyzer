from dataset import X_test, y_test, id_test
from train import model
from sklearn.metrics import mean_absolute_error, mean_squared_error

predicted_vote_share = model.predict(X_test)

results = id_test.copy()
results["actual_vote_share"] = y_test.to_numpy()
results["predicted_vote_share"] = predicted_vote_share

results["prediction_rank"] = (
    results.groupby("season")["predicted_vote_share"]
    .rank(method="first", ascending=False)
    .astype(int)
)

for season, season_results in results.groupby("season"):
    print(f"\nSeason: {season}")
    print(
        season_results
        .sort_values("prediction_rank")
        .head(10)
        [["prediction_rank", "player_name", "predicted_vote_share", "actual_vote_share"]]
        .to_string(index=False)
    )

print("\nMAE:", mean_absolute_error(y_test, predicted_vote_share))
print("RMSE:", mean_squared_error(y_test, predicted_vote_share) ** 0.5)