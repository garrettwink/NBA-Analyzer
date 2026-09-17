library(hoopR)
library(dplyr)
library(DBI)
library(RSQLite)
library(stringr)

# Seasons to collect
seasons <- c(2020, 2021, 2022, 2023, 2024, 2025)

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

# Normalized player names so they can match the database names
all_awards <- all_awards %>%
  mutate(
    player_name = if ("player" %in% names(.)) player else NA_character_,
    player_name_clean = tolower(str_trim(player_name)),
    player_name_clean = str_replace_all(player_name_clean, "\\s+", " ")
  )

# Pull player lookup from SQLite to map names to player_id
con <- dbConnect(RSQLite::SQLite(), "nba.db")
players_lookup <- dbGetQuery(con, "SELECT name, player_id FROM players") %>%
  mutate(
    name_clean = tolower(str_trim(name)),
    name_clean = str_replace_all(name_clean, "\\s+", " ")
  ) %>%
  select(player_id, name_clean)

# Join the award data to player_id using matching names
mvp_table <- all_awards %>%
  left_join(players_lookup, by = c("player_name_clean" = "name_clean")) %>%
  select(
    player_id,
    player_name,
    season,
    everything()
  ) %>%
  filter(!is.na(player_id))

# Save final MVP table to SQLite so it can join with the stats table
if (nrow(mvp_table) > 0) {
  dbWriteTable(
    con,
    name = "mvp_awards",
    value = mvp_table,
    overwrite = FALSE,
    append = TRUE
  )
}

dbDisconnect(con)

print(mvp_table)

