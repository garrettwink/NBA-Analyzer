from nba_api.stats.endpoints import leagueleaders
results = leagueleaders.LeagueLeaders()
print(results.get_data_frames()[0].columns.tolist())