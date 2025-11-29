"""
Script to regenerate 29 defender CSV files with incorrect schema.

This script re-generates defender CSV files that have 135 columns (with deprecated
FPL columns) instead of the correct 112 columns. It extracts functions from
GeneralScrape.ipynb and reruns data compilation for the affected players.

Author: Claude Code
Date: 2025-11-26
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import time
import sys
from datetime import datetime


# ============================================================================
# HELPER FUNCTIONS (from GeneralScrape.ipynb)
# ============================================================================

def get_url_final(code, year_range, category, player):
    """Get HTML from FBref for a specific player, season, and category."""
    base_url = 'https://fbref.com/en/players/{}/matchlogs/{}/c9/{}/{}-Match-Logs'
    url = base_url.format(code, year_range, category, player)
    html = requests.get(url).text
    soup = BeautifulSoup(html, 'lxml')
    html_filtered = soup.find('tbody')
    return(html_filtered)


def get_dat(dat, col):
    """Extract column data from table rows."""
    coldat = []
    for row in dat.find_all('tr'):
        if not row.attrs:
            coldat.append(row.find('td', {'data-stat': col}).text)
    return (coldat)


def get_date(dat, col):
    """Extract date column from table headers."""
    coldat = []
    for row in dat.find_all('tr'):
        if not row.attrs:
            coldat.append(row.find('th', {'data-stat': col}).text)
    return (coldat)


def get_matchweek(dat, col):
    """Extract and clean matchweek column."""
    coldat = []
    for row in dat.find_all('tr'):
        if not row.attrs:
            coldat.append(row.find('td', {'data-stat': col}).text)
    coldat = [coldat.replace('Matchweek ', '') for coldat in coldat]
    return(coldat)


def get_premgames(code, player):
    """Get total Premier League games played by a player."""
    base_url = f'https://fbref.com/en/players/{code}/{player}'
    html = requests.get(base_url).text
    soup = BeautifulSoup(html, 'lxml')
    summary = soup.find('table', class_='stats_table sortable min_width')
    table = summary.find('tbody')

    comp = table.find_all('td', attrs={'data-stat': 'comp_level'})
    comp_text = [cell.get_text() for cell in comp]
    games = table.find_all('td', attrs={'data-stat': 'games'})
    games_text = [cell.get_text() for cell in games]
    season = table.find_all('th', attrs={'data-stat': 'year_id'})
    season_text  = [cell.get_text() for cell in season]

    country = table.find_all('td', attrs={'data-stat': 'country'})
    country_text = [cell.get_text() for cell in country]

    df = pd.DataFrame({
        'Season': season_text,
        'Competition': comp_text,
        'Games Played': games_text,
        'Country': country_text
    })

    season_list = ('2023-2024', '2022-2023', '2021-2022', '2020-2021', '2019-2020', '2018-2019', '2017-2018')
    total_games = df[(df['Competition'] == '1. Premier League') & (df['Season'].isin(season_list)) & (df['Country'] == 'eng ENG')]['Games Played']
    total_games = pd.to_numeric(total_games)
    prem_games = total_games.sum()
    return(prem_games)


# Initialize column names for empty dataframes
test = pd.DataFrame()  # This will be populated after first successful scrape
column_names = None


def get_data_final(code, year_range, player, fpl_name):
    """
    Scrape and compile all match data for a player in a given season.
    Returns dataframe with 112 columns (correct schema).
    """
    global column_names

    data_summary = get_url_final(code, year_range, '', player)

    # If no data exists for this year, return empty dataframe
    if not data_summary:
        if column_names is not None:
            empty = pd.DataFrame(columns = column_names)
            return(empty)
        else:
            # First call and no data - return truly empty df
            return pd.DataFrame()

    data_passing = get_url_final(code, year_range, 'passing', player)
    data_passingtype = get_url_final(code, year_range, 'passing_types', player)
    data_gca = get_url_final(code, year_range, 'gca', player)
    data_defense = get_url_final(code, year_range, 'defense', player)
    data_possession = get_url_final(code, year_range, 'possession', player)

    # Extract all data columns
    # Summary data
    date = get_date(data_summary, 'date')
    day = get_dat(data_summary,'dayofweek')
    matchweek = get_matchweek(data_summary, 'round')
    venue = get_dat(data_summary, 'venue')
    result = get_dat(data_summary, 'result')
    team = get_dat(data_summary, 'team')
    opponent = get_dat(data_summary, 'opponent')
    start = get_dat(data_summary, 'game_started')
    position = get_dat(data_summary, 'position')
    mins = get_dat(data_summary, 'minutes')
    goals = get_dat(data_summary, 'goals')
    assist = get_dat(data_summary, 'assists')
    pen_goals = get_dat(data_summary, 'pens_made')
    pen_attempted = get_dat(data_summary, 'pens_att')
    shots = get_dat(data_summary, 'shots')
    sot = get_dat(data_summary, 'shots_on_target')
    yellow = get_dat(data_summary, 'cards_yellow')
    red = get_dat(data_summary, 'cards_red')
    touches = get_dat(data_summary, 'touches')
    tackles = get_dat(data_summary, 'tackles')
    interceptions = get_dat(data_summary, 'interceptions')
    blocks = get_dat(data_summary, 'blocks')
    xg = get_dat(data_summary, 'xg')
    npxg = get_dat(data_summary, 'npxg')
    xag = get_dat(data_summary, 'xg_assist')
    sca = get_dat(data_summary, 'sca')
    gca = get_dat(data_summary, 'gca')
    passes_completed = get_dat(data_summary, 'passes_completed')
    passes_attempted = get_dat(data_summary, 'passes')
    prg_passes = get_dat(data_summary, 'progressive_passes')
    carries = get_dat(data_summary, 'carries')
    prg_carries = get_dat(data_summary, 'progressive_carries')
    takeon_att = get_dat(data_summary, 'take_ons')
    takeon_suc = get_dat(data_summary, 'take_ons_won')

    # Passing data
    pass_distance = get_dat(data_passing, 'passes_total_distance')
    prg_pass_distance = get_dat(data_passing, 'passes_progressive_distance')
    short_pass_completed = get_dat(data_passing, 'passes_completed_short')
    short_pass_attempted = get_dat(data_passing, 'passes_short')
    med_pass_completed = get_dat(data_passing, 'passes_completed_medium')
    med_pass_attempted = get_dat(data_passing, 'passes_medium')
    long_pass_completed = get_dat(data_passing, 'passes_completed_long')
    long_pass_attempted = get_dat(data_passing, 'passes_long')
    xa = get_dat(data_passing, 'pass_xa')
    keypass = get_dat(data_passing, 'assisted_shots')
    finalthird_pass = get_dat(data_passing, 'passes_into_final_third')
    penaltyarea_pass = get_dat(data_passing, 'passes_into_penalty_area')
    penaltyarea_cross = get_dat(data_passing, 'crosses_into_penalty_area')

    # Passing types data
    live_pass = get_dat(data_passingtype, 'passes_live')
    dead_pass = get_dat(data_passingtype, 'passes_dead')
    freekick_pass = get_dat(data_passingtype, 'passes_free_kicks')
    through_balls = get_dat(data_passingtype, 'through_balls')
    switches = get_dat(data_passingtype, 'passes_switches')
    crosses = get_dat(data_passingtype, 'crosses')
    throwin = get_dat(data_passingtype, 'throw_ins')
    corners = get_dat(data_passingtype, 'corner_kicks')
    offside_pass = get_dat(data_passingtype, 'passes_offsides')

    # GCA data
    live_sca = get_dat(data_gca, 'sca_passes_live')
    deadball_sca = get_dat(data_gca, 'sca_passes_dead')
    takeons_sca = get_dat(data_gca, 'sca_take_ons')
    shots_sca = get_dat(data_gca, 'sca_shots')
    fouls_sca = get_dat(data_gca, 'sca_fouled')
    defense_sca = get_dat(data_gca, 'sca_defense')
    live_gca = get_dat(data_gca, 'gca_passes_live')
    deadball_gca = get_dat(data_gca, 'gca_passes_dead')
    takeons_gca = get_dat(data_gca, 'gca_take_ons')
    shots_gca = get_dat(data_gca, 'gca_shots')
    fouls_gca = get_dat(data_gca, 'gca_fouled')
    defense_gca = get_dat(data_gca, 'gca_defense')

    # Defensive data
    tackles_won = get_dat(data_defense,'tackles_won')
    tackles_def = get_dat(data_defense, 'tackles_def_3rd')
    tackles_mid = get_dat(data_defense, 'tackles_mid_3rd')
    tackles_att = get_dat(data_defense, 'tackles_att_3rd')
    dribblers_tackled = get_dat(data_defense, 'challenge_tackles')
    dribbles_challenged = get_dat(data_defense, 'challenges')
    challenges_lost = get_dat(data_defense, 'challenges_lost')
    shots_blocked = get_dat(data_defense, 'blocked_shots')
    pass_blocked = get_dat(data_defense, 'blocked_passes')
    clearances = get_dat(data_defense, 'clearances')
    def_errors = get_dat(data_defense, 'errors')

    # Possession data
    def_penarea_touches = get_dat(data_possession, 'touches_def_pen_area')
    def_third_touches = get_dat(data_possession, 'touches_def_3rd')
    mid_third_touches = get_dat(data_possession, 'touches_mid_3rd')
    att_third_touches = get_dat(data_possession, 'touches_att_3rd')
    pen_area_touches = get_dat(data_possession, 'touches_att_pen_area')
    carry_distance = get_dat(data_possession, 'carries_distance')
    prg_carry_distance = get_dat(data_possession, 'carries_progressive_distance')
    final_third_carries = get_dat(data_possession, 'carries_into_final_third')
    pen_area_carries = get_dat(data_possession, 'carries_into_penalty_area')
    miscontrols = get_dat(data_possession, 'miscontrols')
    dispossesed = get_dat(data_possession, 'dispossessed')
    pass_received = get_dat(data_possession, 'passes_received')
    prg_pass_received = get_dat(data_possession, 'progressive_passes_received')

    # Create dataframe
    df = pd.DataFrame({
        'Date': date,
        'Day': day,
        'Matchweek': matchweek,
        'Venue': venue,
        'Result': result,
        'Team': team,
        'Opponent': opponent,
        'Start': start,
        'Position': position,
        'Minutes Played': mins,
        'Goals': goals,
        'Assists': assist,
        'Penalties Scored': pen_goals,
        'Penalties Attempted': pen_attempted,
        'Shots': shots,
        'Shots on Target': sot,
        'Yellow Cards': yellow,
        'Red Cards': red,
        'Touches': touches,
        'Tackles': tackles,
        'Interceptions': interceptions,
        'Blocks': blocks,
        'xG': xg,
        'npxG': npxg,
        'xAG': xag,
        'Shot Creating Actions': sca,
        'Goal Creating Actions': gca,
        'Passes Completed': passes_completed,
        'Passes Attempted': passes_attempted,
        'Progressive Passes': prg_passes,
        'Carries': carries,
        'Progressive Carries': prg_carries,
        'Take-ons Attempted': takeon_att,
        'Successful Take-ons': takeon_suc,

        'Passing Distance': pass_distance,
        'Progressive Passing Distance': prg_pass_distance,
        'Short Passes Completed' : short_pass_completed,
        'Short Passes Attempted': short_pass_attempted,
        'Medium Passes Completed': med_pass_completed,
        'Medium Passes Attempted': med_pass_attempted,
        'Long Passes Completed': long_pass_completed,
        'Long Passes Attempted': long_pass_attempted,
        'Expected Assists': xa,
        'Key Passes': keypass,
        'Passes into Final Third': finalthird_pass,
        'Passes into Penalty Area': penaltyarea_pass,
        'Crosses into Penalty Area': penaltyarea_cross,

        'Live Pass': live_pass,
        'Dead Pass': dead_pass,
        'Free Kick Pass': freekick_pass,
        'Through Balls': through_balls,
        'Switches': switches,
        'Crosses': crosses,
        'Throw Ins Taken': throwin,
        'Corners Taken': corners,
        'Passes Offside': offside_pass,

        'Live SCA': live_sca,
        'Deadball SCA': deadball_sca,
        'Take-on SCA': takeons_sca,
        'Shot SCA': shots_sca,
        'Foul SCA': fouls_sca,
        'Defense SCA': defense_sca,

        'Live GCA': live_gca,
        'Deadball GCA': deadball_gca,
        'Take-on GCA': takeons_gca,
        'Shot GCA': shots_gca,
        'Foul GCA': fouls_gca,
        'Defense GCA': defense_gca,

        'Tackles Won': tackles_won,
        'Defensive Third Tackles': tackles_def,
        'Middle Third Tackles': tackles_mid,
        'Attacking Third Tackles': tackles_att,
        'Dribblers Tackled': dribblers_tackled,
        'Dribblers Tackled Attempts': dribbles_challenged,
        'Challenges Lost': challenges_lost,
        'Shots Blocked': shots_blocked,
        'Passes Blocked': pass_blocked,
        'Clearances': clearances,
        'Defensive Errors': def_errors,

        'Defensive Penalty Area Touches': def_penarea_touches,
        'Defensive Third Touches': def_third_touches,
        'Middle Third Touches': mid_third_touches,
        'Attacking Third Touches': att_third_touches,
        'Penalty Area Touches': pen_area_touches,
        'Carry Distance': carry_distance,
        'Progressive Carry Distance': prg_carry_distance,
        'Final Third Carries': final_third_carries,
        'Carries into Penalty Area': pen_area_carries,
        'Miscontrols': miscontrols,
        'Dispossessed': dispossesed,
        'Passes Received': pass_received,
        'Progressive Passes Received': prg_pass_received
    })

    # Replace empty strings with zero
    for column in df.columns:
        df[column] = df[column].replace('',0)

    # Set data types
    df = df.astype({
        'Date': 'datetime64[ns]',
        'Day': 'object',
        'Matchweek': 'int64',
        'Venue': 'object',
        'Result': 'object',
        'Team': 'object',
        'Opponent': 'object',
        'Start': 'object',
        'Position': 'object',
        'Minutes Played': 'int64',
        'Goals': 'int64',
        'Assists': 'int64',
        'Penalties Scored': 'int64',
        'Penalties Attempted': 'int64',
        'Shots': 'int64',
        'Shots on Target': 'int64',
        'Yellow Cards': 'int64',
        'Red Cards': 'int64',
        'Touches': 'int64',
        'Tackles': 'int64',
        'Interceptions': 'int64',
        'Blocks': 'int64',
        'xG': 'float64',
        'npxG': 'float64',
        'xAG': 'float64',
        'Shot Creating Actions': 'int64',
        'Goal Creating Actions': 'int64',
        'Passes Completed': 'int64',
        'Passes Attempted': 'int64',
        'Progressive Passes': 'int64',
        'Carries': 'int64',
        'Progressive Carries': 'int64',
        'Take-ons Attempted': 'int64',
        'Successful Take-ons': 'int64',

        'Short Passes Completed' : 'int64',
        'Short Passes Attempted': 'int64',
        'Medium Passes Completed': 'int64',
        'Medium Passes Attempted': 'int64',
        'Long Passes Completed': 'int64',
        'Long Passes Attempted': 'int64',
        'Expected Assists': 'float64',
        'Key Passes': 'int64',
        'Passes into Final Third': 'int64',
        'Passes into Penalty Area': 'int64',
        'Crosses into Penalty Area': 'int64',

        'Live Pass': 'int64',
        'Dead Pass': 'int64',
        'Free Kick Pass': 'int64',
        'Through Balls': 'int64',
        'Switches': 'int64',
        'Crosses': 'int64',
        'Throw Ins Taken': 'int64',
        'Corners Taken': 'int64',
        'Passes Offside': 'int64',

        'Live SCA': 'int64',
        'Deadball SCA': 'int64',
        'Take-on SCA': 'int64',
        'Shot SCA': 'int64',
        'Foul SCA': 'int64',
        'Defense SCA': 'int64',

        'Live GCA': 'int64',
        'Deadball GCA': 'int64',
        'Take-on GCA': 'int64',
        'Shot GCA': 'int64',
        'Foul GCA': 'int64',
        'Defense GCA': 'int64',

        'Tackles Won': 'int64',
        'Defensive Third Tackles': 'int64',
        'Middle Third Tackles': 'int64',
        'Attacking Third Tackles': 'int64',
        'Dribblers Tackled': 'int64',
        'Dribblers Tackled Attempts': 'int64',
        'Challenges Lost': 'int64',
        'Shots Blocked': 'int64',
        'Passes Blocked': 'int64',
        'Clearances': 'int64',
        'Defensive Errors': 'int64',

        'Defensive Penalty Area Touches': 'int64',
        'Defensive Third Touches': 'int64',
        'Middle Third Touches': 'int64',
        'Attacking Third Touches': 'int64',
        'Penalty Area Touches': 'int64',
        'Carry Distance': 'float64',
        'Progressive Carry Distance': 'float64',
        'Final Third Carries': 'int64',
        'Carries into Penalty Area': 'int64',
        'Miscontrols': 'int64',
        'Dispossessed': 'int64',
        'Passes Received': 'int64',
        'Progressive Passes Received': 'int64'
    })

    # Convert date column
    df['Date'] = df['Date'].dt.date

    # Merge with FPL data
    start_year = year_range[:4]
    end_year = year_range[-2:]
    format_year = f'{start_year}-{end_year}'
    directory = f'Fantasy-Premier-League/data/{format_year}/players'
    files = os.listdir(directory)
    csv_file = [f for f in files if fpl_name in f]
    fpldf = pd.read_csv(os.path.join(directory, csv_file[0]) + '/gw.csv')

    # Drop duplicate columns
    fpldf = fpldf.drop(['assists', 'expected_assists', 'expected_goal_involvements', 'expected_goals', 'fixture',
                        'goals_conceded', 'goals_scored', 'penalties_missed', 'penalties_saved', 'red_cards',
                        'team_a_score', 'team_h_score', 'was_home', 'yellow_cards', 'element', 'opponent_team', 'starts',
                        'expected_goals_conceded'], axis=1, errors='ignore')

    # Convert kickoff time
    fpldf['kickoff_time'] = pd.to_datetime(fpldf['kickoff_time'])
    fpldf['kickoff_date'] = fpldf['kickoff_time'].dt.date

    # Merge dataframes
    finaldf = pd.merge(df, fpldf, left_on='Date', right_on='kickoff_date', how='inner')

    # Store column names for future empty dataframes
    if column_names is None:
        column_names = finaldf.columns

    return finaldf


def compile_dat(code, player, fpl_name, checkgames):
    """
    Compile all seasons of data for a given player.
    Returns dataframe with 112 columns (correct schema).
    """
    year_list = ('2023-24', '2022-23', '2021-22', '2020-21', '2019-20', '2018-19', '2017-18')

    # Find seasons where player was active
    active_years = []
    for year in year_list:
        directory = f'Fantasy-Premier-League/data/{year}/players'
        files = os.listdir(directory)
        csv_file = [f for f in files if fpl_name in f]
        if csv_file:
            update_year = year[:5] + '20' + year[5:]
            active_years.append(update_year)

    # Scrape data for each active season
    dataframes = {}
    for year in active_years:
        dataframes[year] = get_data_final(code, year, player, fpl_name)
        time.sleep(60)  # 1 minute pause between API calls

    # Concatenate all seasons
    finaldf = pd.concat(dataframes.values(), join = "inner", ignore_index = True)

    # Optionally verify game count
    if checkgames:
        games_played = get_premgames(code, player)
        if games_played == finaldf.shape[0]:
            return finaldf
        else:
            print(f'Warning: {player} - Expected {games_played} games, got {finaldf.shape[0]} rows')
            return finaldf
    else:
        return finaldf


# ============================================================================
# PLAYER DATA - 29 defenders to regenerate
# ============================================================================

DEFENDERS_TO_REGENERATE = [
    {'name': 'Bruno Saltor', 'code': '78803d03', 'fpl_name': 'Saltor', 'checkgames': True, 'filename': 'saltor_finaldat.csv'},
    {'name': 'S Ward', 'code': '42f52db9', 'fpl_name': 'Sward', 'checkgames': True, 'filename': 'sward_finaldat.csv'},
    {'name': 'Schindler', 'code': '5d1ed4a7', 'fpl_name': 'Schindler', 'checkgames': True, 'filename': 'schindler_finaldat.csv'},
    {'name': 'Chris Lowe', 'code': 'c6896eab', 'fpl_name': 'Chris_L', 'checkgames': True, 'filename': 'clowe_finaldat.csv'},
    {'name': 'T Smith', 'code': '00c6c896', 'fpl_name': 'Tsmith', 'checkgames': True, 'filename': 'tsmith_finaldat.csv'},
    {'name': 'Florent Hadergjonaj', 'code': '9aa186b2', 'fpl_name': 'Hadergjonaj', 'checkgames': True, 'filename': 'hadergjonaj_finaldat.csv'},
    {'name': 'Danny Simpson', 'code': '3201b03d', 'fpl_name': 'Danny_Simpson', 'checkgames': True, 'filename': 'dsimpson_finaldat.csv'},
    {'name': 'Aleksandar Dragovic', 'code': '6fd8a334', 'fpl_name': 'Aleksandar_Dragovic', 'checkgames': False, 'filename': 'adragovic_finaldat.csv'},
    {'name': 'Moreno', 'code': '4fa80a7b', 'fpl_name': 'Moreno', 'checkgames': True, 'filename': 'moreno_finaldat.csv'},
    {'name': 'Vincent Kompany', 'code': '92f6f9f7', 'fpl_name': 'Kompany', 'checkgames': True, 'filename': 'kompany_finaldat.csv'},
    {'name': 'Valencia', 'code': '74d6e0d2', 'fpl_name': 'Valencia', 'checkgames': True, 'filename': 'valencia_finaldat.csv'},
    {'name': 'Ryan Shawcross', 'code': 'ec23a1a6', 'fpl_name': 'Shawcross', 'checkgames': True, 'filename': 'shawcross_finaldat.csv'},
    {'name': 'Geoff Cameron', 'code': '1a160ea3', 'fpl_name': 'Geoff_Cameron', 'checkgames': True, 'filename': 'gcameron_finaldat.csv'},
    {'name': 'Wimmer', 'code': '8d3e4b6f', 'fpl_name': 'Wimmer', 'checkgames': True, 'filename': 'wimmer_finaldat.csv'},
    {'name': 'Martins Indi', 'code': '53d3a2d1', 'fpl_name': 'Martins Indi', 'checkgames': False, 'filename': 'martinsindi_finaldat.csv'},
    {'name': 'M Bauer', 'code': '35f84da5', 'fpl_name': 'Bauer', 'checkgames': True, 'filename': 'mbauer_finaldat.csv'},
    {'name': 'Naughton', 'code': '5a4a2cf0', 'fpl_name': 'Naughton', 'checkgames': True, 'filename': 'naughton_finaldat.csv'},
    {'name': 'Vanderhoorn', 'code': 'ea95e4c8', 'fpl_name': 'Vanderhoorn', 'checkgames': True, 'filename': 'vanderhoorn_finaldat.csv'},
    {'name': 'Molsson', 'code': '02ce4c60', 'fpl_name': 'Molsson', 'checkgames': True, 'filename': 'molsson_finaldat.csv'},
    {'name': 'Miguel Britos', 'code': '356a9a62', 'fpl_name': 'Britos', 'checkgames': True, 'filename': 'britos_finaldat.csv'},
    {'name': 'Nyom', 'code': 'ef9b5c08', 'fpl_name': 'Nyom', 'checkgames': True, 'filename': 'nyom_finaldat.csv'},
    {'name': 'James Collins', 'code': 'c61f1719', 'fpl_name': 'James_Collins', 'checkgames': True, 'filename': 'jcollins_finaldat.csv'},
    {'name': 'Lichtsteiner', 'code': '4c7ba847', 'fpl_name': 'Lichtsteiner', 'checkgames': True, 'filename': 'lichtsteiner_finaldat.csv'},
    {'name': 'Morrison', 'code': '79d8d887', 'fpl_name': 'Morrison', 'checkgames': True, 'filename': 'morrison_finaldat.csv'},
    {'name': 'S Bamba', 'code': 'e49f27e2', 'fpl_name': 'Bamba', 'checkgames': True, 'filename': 'sbamba_finaldat.csv'},
    {'name': 'Manga', 'code': 'dde0ba4d', 'fpl_name': 'Manga', 'checkgames': True, 'filename': 'manga_finaldat.csv'},
    {'name': 'Erik Durm', 'code': 'cf623c78', 'fpl_name': 'Erik_Durm', 'checkgames': True, 'filename': 'durm_finaldat.csv'},
    {'name': 'Jon Gorenc Stankovic', 'code': '9c74fa25', 'fpl_name': 'Jon Gorenc', 'checkgames': True, 'filename': 'jgstankovic_finaldat.csv'},
    {'name': 'Joe Bennett', 'code': 'dc936144', 'fpl_name': 'Joe_Bennett', 'checkgames': True, 'filename': 'bennett_finaldat.csv'},
]


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    print("=" * 70, flush=True)
    print("DEFENDER CSV REGENERATION SCRIPT", flush=True)
    print("=" * 70, flush=True)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"Total defenders to regenerate: {len(DEFENDERS_TO_REGENERATE)}", flush=True)
    print(f"Estimated runtime: ~50-60 minutes (60 sec API delays)", flush=True)
    print("=" * 70, flush=True)
    print(flush=True)

    # Setup output directory
    nest_folder_def = os.path.join("Player_Data", "Defenders")
    if not os.path.exists(nest_folder_def):
        print(f"Error: Directory {nest_folder_def} does not exist!")
        sys.exit(1)

    # Track results
    successful = []
    failed = []

    # Process each defender
    for idx, player in enumerate(DEFENDERS_TO_REGENERATE, 1):
        print(f"\n[{idx}/{len(DEFENDERS_TO_REGENERATE)}] Processing: {player['name']}", flush=True)
        print(f"  FBref ID: {player['code']}", flush=True)
        print(f"  FPL Name: {player['fpl_name']}", flush=True)
        print(f"  Filename: {player['filename']}", flush=True)

        try:
            # Compile player data
            df = compile_dat(
                player['code'],
                player['name'].replace(' ', '-'),
                player['fpl_name'],
                player['checkgames']
            )

            # Verify it's a dataframe (not None or error message)
            if isinstance(df, pd.DataFrame) and not df.empty:
                # Save to CSV
                output_path = os.path.join(nest_folder_def, player['filename'])
                df.to_csv(output_path, index=False)

                # Verify column count
                col_count = len(df.columns)
                row_count = len(df)
                status = "OK" if col_count == 112 else f"ERROR ({col_count} cols)"

                print(f"  Status: {status}", flush=True)
                print(f"  Rows: {row_count}", flush=True)
                print(f"  Columns: {col_count}", flush=True)
                print(f"  Saved: {output_path}", flush=True)

                if col_count == 112:
                    successful.append(player['name'])
                else:
                    failed.append(f"{player['name']} ({col_count} cols)")
            else:
                print(f"  Status: FAILED - No dataframe returned", flush=True)
                failed.append(f"{player['name']} (no data)")

        except Exception as e:
            print(f"  Status: FAILED - {str(e)}", flush=True)
            failed.append(f"{player['name']} ({str(e)[:50]})")

    # Print summary
    print("\n" + "=" * 70)
    print("REGENERATION COMPLETE")
    print("=" * 70)
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Successful: {len(successful)}/{len(DEFENDERS_TO_REGENERATE)}")
    print(f"Failed: {len(failed)}/{len(DEFENDERS_TO_REGENERATE)}")

    if failed:
        print("\nFailed files:")
        for f in failed:
            print(f"  - {f}")

    print("\nNext steps:")
    print("  1. Verify all files have 112 columns")
    print("  2. Run: python compile_defender_data.py")
    print("  3. Test: pd.read_csv('def_finaldat.csv')")
    print("=" * 70)


if __name__ == "__main__":
    main()
