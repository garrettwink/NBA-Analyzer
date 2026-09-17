library(hoopR)
library(dplyr)
library(DBI)
library(RSQLite)
library(stringr)

# Seasons to collect
seasons <- c(seq(2010, 2025, by=1))

# Fetch all award rows for each season and attach the season column
all_awards <- list()

for (season in seasons) {
  temp <- hoopR::bref_awards(season = season)
  temp$season <- season
  all_awards[[length(all_awards) + 1]] <- temp
}

all_awards <- bind_rows(all_awards)

# Keep only MVP award rows if the table includes an award column
if ("award" %in% names(all_awards)) {
  all_awards <- all_awards %>%
    filter(grepl("MVP", award, ignore.case = TRUE))
}

# Pull player lookup from SQLite to map names to player_id
con <- dbConnect(RSQLite::SQLite(), "nba.db")
players_lookup <- dbGetQuery(con, "SELECT name, player_id FROM players") %>%
  select(player_id, name)

# Join the award data to player_id using matching names
mvp_table <- all_awards %>%
  left_join(players_lookup, by = c("player" = "name")) %>%
  select(
    player_id,
    player,
    season,
    rank,
    age,
    team,
    points_won,
    award_share
  ) %>%
  filter(!is.na(player_id)) %>%
  rename(
    'name' = 'player',
    'mvp_rank' = 'rank',
    'mvp_vote_share' = 'award_share'
  )

# Save final MVP table to SQLite so it can join with the stats table
if (nrow(mvp_table) > 0) {
  dbWriteTable(
    con,
    name = "mvp_awards",
    value = as.data.frame(mvp_table),
    overwrite = FALSE,
    append = TRUE
  )
}

dbDisconnect(con)

