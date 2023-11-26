# Importing libraries
import pandas as pd
import numpy as np
from datetime import datetime
import os
import warnings
import time
from openpyxl.styles import Alignment 
warnings.filterwarnings('ignore')

# Defining stuff
season_end_dates = pd.read_excel("C:/Mantovani/Careers/Football Manager 2023/0. Misc/_Data/FM Quick Data.xlsx", sheet_name='Countries')
folder_export = "C:/Mantovani/Careers/Football Manager 2023/PythonFM/Exports/"

# Manual inputs
print("Import folder path")
print("Example: 'D:/Documents/Sports Interactive/Football Manager 2023/exports/Portugal/Jun 24'")
folder_import = input("Enter import folder path without / at the end: ")
folder_import = folder_import.replace("\\", "/")

print("\nIn-game date of the export files")
print("Example: 30/05/2024")
date = input("Enter date: ")

print("\nName of your club")
print("Example: Newcastle")
club = input("Enter your club name: ")

print("\nName of the CSV file to be exported")
print("Example: JUN24")
csv_file = input("Enter CSV file name: ")
xlsx_file = csv_file

# Loading files
print("\n\n\nLoading the export of the Player Search screen - Stats view...")
fm_data = pd.read_html(os.path.join(folder_import, 'stats.html'), encoding="UTF-8", thousands=".", decimal=",")[0]
fm_data['Date'] = datetime.strptime(date, '%d/%m/%Y')

print("\nLoading the export of the Player Search screen - Attributes view...")
att_data = pd.read_html(os.path.join(folder_import, "atts.html"), encoding="UTF-8", thousands=".", decimal=",")[0]

print("\nLoading the Genie Scout file containing the same players from before...")
genie_data = pd.read_csv(os.path.join(folder_import, "genie.csv"), encoding="latin1", sep=';')

print("\nLoading the UID of players interested in joining...")
interest_data = pd.read_html(os.path.join(folder_import, "int.html"), encoding="UTF-8", thousands=".", decimal=",")[0]

# Printing the shape of each import
print("\n\n\nDATAFRAMES ROWS AND COLUMNS")
print("\nStats:", fm_data.shape)
print("Attributes:", att_data.shape)
print("Genie Scout:", genie_data.shape)
print("Interested:\n", interest_data.shape)

# Ask for user confirmation
confirmation = input("If any of the above values are wrong, type 'N' to abort the script: ")

# Check user input
if confirmation.upper() == 'N':
    print("At least one file is wrong. Exporting large amounts of data from FM does that sometimes.")
    print("Try creating the wrong files again until you see the expected number of rows and columns.")
    print("Aborting script.")
    time.sleep(5)
    exit()

# Beginning the transformation of data
print("Everything is set. Let's start processing the data.")
### GENIE SCOUT
genie = genie_data

# Renaming and removing columns
genie_renames = {
    'Unique ID': 'UID',
    'GK Rating': 'GK',
    'DR Rating': 'RB',
    'DC Rating': 'CB',
    'DL Rating': 'LB',
    'DM Rating': 'DM',
    'MC Rating': 'CM',
    'AMR Rating': 'RW',
    'AMC Rating': 'AM',
    'AML Rating': 'LW',
    'FS Rating': 'ST',
    'TS Rating': 'ST2',
    'GK Pot Rating': 'pGK',
    'DR Pot Rating': 'pRB',
    'DC Pot Rating': 'pCB',
    'DL Pot Rating': 'pLB',
    'DM Pot Rating': 'pDM',
    'MC Pot Rating': 'pCM',
    'AMR Pot Rating': 'pRW',
    'AMC Pot Rating': 'pAM',
    'AML Pot Rating': 'pLW',
    'FS Pot Rating': 'pST',
    'TS Pot Rating': 'pST2',}
genie.rename(columns=genie_renames, inplace=True)
genie_remove = ['EU Member', 'Best Rating', 'PoD', 'Value', 'Wage']
genie = genie.drop(columns=genie_remove)

# Remove percentage signs (%) from the rating columns
genie_positions = [
    'GK', 'RB', 'CB', 'LB', 'DM', 'CM', 'RW', 'AM', 'LW', 'ST', 'ST2']

genie_positions_pot = [
    'pGK', 'pRB', 'pCB', 'pLB', 'pDM', 'pCM', 'pRW', 'pAM', 'pLW', 'pST', 'pST2']

for column in genie_positions:
    genie[column] = genie[column].str.replace(',', '.')
    genie[column] = genie[column].str.replace('%', '')
    genie[column] = genie[column].astype(float)

for column in genie_positions_pot:
    genie[column] = genie[column].str.replace(',', '.')
    genie[column] = genie[column].str.replace('%', '')
    genie[column] = genie[column].astype(float)

# Getting the highest value between TS and FS and removing the other
genie['ST'] = genie[['ST', 'ST2']].max(axis=1)
genie['pST'] = genie[['pST', 'pST2']].max(axis=1)
genie.drop(columns=['ST2'], inplace=True)
genie.drop(columns=['pST2'], inplace=True)
genie_positions.remove('ST2')
genie_positions_pot.remove('pST2')

# Creating rating columns
genie['Rt1'] = genie[genie_positions].max(axis=1)
genie['Rt2'] = genie[genie_positions].apply(lambda row: sorted(row)[-2], axis=1)
genie['P1'] = genie[genie_positions].idxmax(axis=1)
genie['P2'] = genie[genie_positions].apply(lambda row: row.drop(row.idxmax()).idxmax(), axis=1)

# Creating potential columns
genie['Pt1'] = genie[genie_positions_pot].max(axis=1)
genie['Pt2'] = genie[genie_positions_pot].apply(lambda row: sorted(row)[-2], axis=1)
genie['PP1'] = genie[genie_positions_pot].idxmax(axis=1)
genie['PP2'] = genie[genie_positions_pot].apply(lambda row: row.drop(row.idxmax()).idxmax(), axis=1)

# Rounding the ratings
ratings_to_round = ['GK', 'RB', 'CB', 'LB', 'DM', 'CM', 'RW', 'AM', 'LW', 'ST', 'Rt1', 'Rt2']
potentials_to_round = ['pGK', 'pRB', 'pCB', 'pLB', 'pDM', 'pCM', 'pRW', 'pAM', 'pLW', 'pST', 'Pt1', 'Pt2']
genie[ratings_to_round] = genie[ratings_to_round].round(1)
genie[potentials_to_round] = genie[potentials_to_round].round(1)

#############################################

### FOOTBALL MANAGER DATA TRANSFORMATION
fm = fm_data.copy()
fm.dropna(subset=['Name'], inplace=True)

for col in ['AP', 'Prof', 'Amb']:
    if col not in fm.columns:
        fm.loc[:, col] = 0

fm.columns = fm.columns.str.replace(' ', '_')
fm = fm.drop(fm.columns[1:3], axis=1)
fm = fm.applymap(lambda x: 0 if x == "-" else x)

# Change column names
columns_to_rename = {
    'EU_National': 'EU',
    'AP': 'Value',
    'ShT': 'Sht_T',
    'Ps_C': 'Pas_C',
    'FA': 'Fls_Ag',
    'Hdrs': 'Hdrs_W',
    'Yel': 'Yellow',
    'Itc': 'Intcp',
    'Blk': 'Blocks',
    'Conc': 'Gls_Conc',
    'Pres_C': 'Press_C',
    'Shots': 'Sht',
    'Clean_sheets': 'CS',
    'Pr_Passes': 'Pr_Pas',
}

fm.rename(columns=columns_to_rename, inplace=True)

# Transform into int values
fm['Clear'] = fm['Clear'].astype(float).astype(int)
convert_to_int = ['Pas_A', 'Pas_C', 'Drb', 'Fls_Ag', 'Intcp', 'Press_C', 'Starts',
                  'Mins', 'Gls', 'Ast', 'Sht', 'OP-KP', 'CCC', 'Pr_Pas', 'Sht_T',
                  'Cr_A', 'Cr_C', 'Hdrs_W', 'Hdrs_A', 'Blocks', 'Gls_Conc', 'CS']
for col in convert_to_int:
    fm[col] = fm[col].astype(int)

# Transform into float values
convert_to_float = ['Av_Rat', 'xG', 'xA', 'NP-xG', 'xGP', 'Sprints/90']
for col in convert_to_float:
    fm[col] = fm[col].astype(float)

# Removing the division name from Based column
fm['Division'] = fm['Based'].str.extract(r'\((.*?)\)')
fm['Based'] = fm['Based'].str.extract(r'^([^(]+)')
fm['Based'] = fm['Based'].str.strip()

# Converting 'Expires' to datetime
fm['Expires'] = fm['Expires'].replace(0, np.nan)
fm['Expires'] = pd.to_datetime(fm['Expires'], format='%d/%m/%Y')
fm['Expires'] = fm['Expires'].dt.strftime('%d/%m/%Y')

# Height and Distance into numeric values
fm['Height'] = fm['Height'].astype(str).str.replace(' cm', '').astype(int)
#fm['Distance'] = fm['Distance'].str.replace('km', '').str.replace(',', '.').astype(float)

# Removing sub appearances from parenthesis and summing with starting
fm['Apps'] = fm['Apps'].str.extract(r'\((\d+)\)').fillna(0).astype(int)
fm['Apps'] = fm['Apps'] + fm['Starts']

# Fixing average rating
fm['Av_Rat'] = (fm['Av_Rat'] / 100).round(2)
fm['Av_Rat_Total'] = (fm['Av_Rat'] * fm['Apps']).round(2)

# Turning Wage column into numeric value
fm['Wage_Aux'] = fm['Wage'].str.replace('.', '').str[2:-4]
fm['Wage'] = fm['Wage_Aux'].fillna(0).astype(int)

# Turning Value column into numeric value and deleting Aux columns
if not (fm['Value'] == 0).all():
    fm['Aux1'] = fm['Value'].str[-1]
    possible_values_aux = [(fm['Aux1'] == '0'), (fm['Aux1'] == 'K'), (fm['Aux1'] == 'M')]
    replacements_aux = [0, 1000, 1000000]
    fm['Aux2'] = np.select(possible_values_aux, replacements_aux, default=0)
    fm['Aux3'] = fm['Value'].str[2:]
    fm['Aux4'] = fm['Aux3'].apply(lambda x: 0 if x == '0' else x[:-1])
    fm['Aux4'] = fm['Aux4'].str.replace(',', '.').fillna(0).astype(float)
    fm['Value'] = fm['Aux4'] * fm['Aux2']
    fm['Value'] = fm['Value'].astype(int)
    fm = fm.drop(columns=['Aux1', 'Aux2', 'Aux3', 'Aux4'], axis=1)

fm['Date'] = pd.to_datetime(fm['Date'])
fm = fm.merge(season_end_dates[['Based', 'Rgn']], on='Based', how='left')
fm.dropna(subset=['Rgn'], inplace=True)

def calculate_period(row):
    if row['Rgn'] == "EU":
        if row['Date'].month in [4, 5, 6, 7, 8, 9]:
            return "End"
        elif row['Date'].month in [1, 2, 3, 10, 11, 12]:
            return "Mid"
    elif row['Rgn'] == "RW":
        if row['Date'].month in [4, 5, 6, 7, 8, 9]:
            return "Mid"
        elif row['Date'].month in [1, 2, 3, 10, 11, 12]:
            return "End"
    return np.nan  # Return NaN for other cases

fm['Half'] = fm.apply(calculate_period, axis=1)

#############################################

# AGGREGATING GENIE AND FM DATA INTO TWO SEPARATE DATAFRAMES

# De-fragmenting
fm = fm.copy()

### Creating per 90 stats and metrics
stats = ['Gls', 'Mins', 'xG', 'NP-xG', 'Sht', 'Sht_T', 'OP-KP', 'CCC',
         'Pr_Pas', 'Ast', 'xA', 'Pas_A', 'Pas_C', 'Cr_A', 'Cr_C',
         'Drb', 'Fls_Ag', 'Hdrs_A', 'Hdrs_W', 'Blocks',
         'Intcp', 'Clear', 'Press_C', 'Gls_Conc', 'CS', 'xGP']

for i in stats:
    new_col = f'{i}/90'
    fm[new_col] = (fm[i] / fm['Mins'] * 90).round(2)

# Creating percentage stats
fm['Min/Gl'] = np.where(fm['Gls'] != 0, (fm['Mins'] / fm['Gls']).round(2), 0)
fm['Starts_%'] = np.where(fm['Apps'] != 0, (fm['Starts'] / fm['Apps'] * 100).round(1), 0)
fm['Shots_%'] = np.where(fm['Sht'] != 0, (fm['Sht_T'] / fm['Sht'] * 100).round(1), 0)
fm['Shots_Gls%'] = np.where(fm['Sht'] != 0, (fm['Gls'] / fm['Sht'] * 100).round(1), 0)
fm['NP-xG/Shot'] = np.where(fm['Sht'] != 0, (fm['NP-xG'] / fm['Sht']).round(3), 0)
fm['Hdrs_%'] = np.where(fm['Hdrs_A'] != 0, (fm['Hdrs_W'] / fm['Hdrs_A'] * 100).round(1), 0)
fm['Pas_%'] = np.where(fm['Pas_A'] != 0, (fm['Pas_C'] / fm['Pas_A'] * 100).round(1), 0)
fm['Cr_%'] = np.where(fm['Cr_A'] != 0, (fm['Cr_C'] / fm['Cr_A'] * 100).round(1), 0)

# Creating metrics based on stats
fm['GK%'] = (fm['xGP/90'] + fm['CS/90'] - fm['Gls_Conc/90'] + (fm['Av_Rat'] / 10)).round(5)
fm['DFg%'] = (fm['Blocks/90'] + fm['Intcp/90'] + fm['Clear/90'] + fm['Press_C/90']).round(5)
fm['DFa%'] = (fm['Blocks/90'] + fm['Intcp/90'] + fm['Clear/90'] + fm['Press_C/90'] + fm['Hdrs_W/90'] + (fm['Hdrs_%'] / 100)).round(5)
fm['PAS%'] = (fm['OP-KP/90'] + fm['CCC/90'] + fm['Pr_Pas/90'] + fm['xA/90'] + (fm['Pas_%']) / 100).round(5)
fm['DRB%'] = (fm['Drb/90'] + fm['Cr_C/90'] + (fm['Cr_%'] / 100) + fm['Fls_Ag/90'] + (fm['Sprints/90'] / 9)).round(5)
fm['ST%'] = (fm['NP-xG/90'] + fm['Gls/90'] + fm['Sht_T/90'] + (fm['Shots_Gls%'] / 100) + fm['NP-xG/Shot']).round(5)

# Cutting to specific columns
main_columns = [
    'Rgn', 'Half', 'Date', 'UID', 'EU', 'NoB', 'Nat', 'Position', 'Age', 'Name', 'Av_Rat',
    'Club', 'Division', 'Based', 'Apps', 'Starts', 'Gls', 'Ast', 'PoM', 'Mins', 'GK%', 'DFg%',
    'DFa%', 'PAS%', 'DRB%', 'ST%', 'Value', 'Wage', 'Expires', 'Det', 'Prof', 'Amb',
    'Acc', 'Pac', 'Agi', 'Sta', 'Wor', 'Personality', 'Height']

fm_main = fm[main_columns]
fm_main = fm_main.copy()

stats_columns = [
    'UID', 'xGP/90', 'CS/90', 'Gls_Conc/90', 'Blocks/90', 'Intcp/90', 'Clear/90',
    'Press_C/90', 'Hdrs_W/90', 'OP-KP/90', 'CCC/90', 'Pr_Pas/90', 'xA/90', 'Pas_C/90', 'Drb/90',
    'Sprints/90', 'Fls_Ag/90', 'Cr_C/90', 'NP-xG/90', 'Gls/90', 'Sht_T/90',
    'NP-xG/Shot', 'xGP', 'CS', 'Gls_Conc', 'Blocks', 'Intcp', 'Clear', 'Press_C',
    'Hdrs_A', 'Hdrs_W', 'OP-KP', 'CCC', 'Pr_Pas', 'xA', 'Pas_A', 'Pas_C', 'Cr_A',
    'Cr_C', 'Drb', 'Fls_Ag', 'xG', 'NP-xG', 'Sht', 'Sht_T']

fm_stats = fm_main.merge(fm[stats_columns], on='UID', how='left')
fm_stats = fm_stats.copy()

### Merging ratings and potentials
fm_main_genie = fm_main.merge(genie[['UID', 'Rt1', 'P1', 'P2', 'Pt1', 'PP1', 'PP2']], on='UID', how='left')
fm_main_genie['RtG'] = fm_main_genie['Rt1']
fm_main_genie['PtG'] = fm_main_genie['Pt1']

new_col_order = [
    'Rgn', 'Half', 'Date', 'UID', 'EU', 'NoB', 'Nat', 'P1', 'P2', 'Rt1', 'Pt1', 'RtG', 'PtG',
    'Position', 'Age', 'Name', 'Av_Rat', 'Club', 'Division', 'Based', 'Apps', 'Starts',
    'Gls', 'Ast', 'PoM', 'Mins', 'GK%', 'DFg%', 'DFa%', 'PAS%', 'DRB%', 'ST%', 'Value',
    'Wage', 'Expires', 'Det', 'Prof', 'Amb', 'Acc', 'Pac', 'Personality', 'Height']

fm_main_genie = fm_main_genie[new_col_order]
fm_main_genie = fm_main_genie.sort_values('Rt1', ascending=False)

fm_stats_genie = fm_main_genie.merge(fm[stats_columns], on='UID', how='left')
fm_stats_genie = fm_stats_genie.sort_values('Rt1', ascending=False)
fm_stats_genie['Ps%'] = ((fm_stats_genie['Pas_C'] / fm_stats_genie['Pas_A'] * 100).round(0)).fillna(0).astype(int)
fm_stats_genie['Hd%'] = ((fm_stats_genie['Hdrs_W'] / fm_stats_genie['Hdrs_A'] * 100).round(0)).fillna(0).astype(int)
fm_stats_genie['Cr%'] = ((fm_stats_genie['Cr_C'] / fm_stats_genie['Cr_A'] * 100).round(0)).fillna(0).astype(int)

#############################################

# FILTERING KNOWN PLAYERS
# FOR PLAYERS WE KNOW ALL ATTRIBUTES, WE USE THE GENIE RATING
# FOR THE OTHERS WE CALCULATE THE RATINGS ON OUR OWN USING THE WORST POSSIBLE SCENARIO
# FOR EXAMPLE, IF AN ATTRIBUTE IS 5-10 WE CONSIDER IT TO BE 5

known_att = att_data
interested = interest_data['UID'].unique().tolist()

def count_hyphens(row, position):
    columns_to_count = []
    if position != "GK":
        columns_to_count = ['Det', 'Prof', 'Amb', 'Acc', 'Pac', 'Agi', 'Bal',
    'Sta', 'Ant', 'Cnt', 'Wor', 'Cro', 'Dri', 'Fin', 'Fir',
    'Jum', 'Mar', 'Pas', 'Str', 'Tck', 'Tec', 'Vis', 'Agg',
    'Bra', 'Cmp', 'Cor', 'Dec', 'Fla', 'Fre', 'Hea', 'Ldr',
    'Lon', 'L Th', 'Nat', 'OtB', 'Pen', 'Pos', 'Tea']
    else:
        columns_to_count = ['Det', 'Prof', 'Amb', 'Acc', 'Pac', 'Agi', 'Bal',
    'Sta', 'Ant', 'Cnt', 'Wor', 'Cro', 'Dri', 'Fin', 'Fir',
    'Jum', 'Mar', 'Pas', 'Str', 'Tck', 'Tec', 'Vis', 'Aer',
    'Ref', 'Han', '1v1', 'Agg', 'Bra', 'Cmd', 'Com', 'Cmp',
    'Cor', 'Dec', 'Ecc', 'Fla', 'Fre', 'Hea', 'Kic', 'Ldr',
    'Lon', 'L Th', 'Nat', 'OtB', 'Pen', 'Pos', 'Pun',
    'TRO', 'Tea', 'Thr']

    count = sum([1 for col in columns_to_count if "-" in str(row[col])])
    return count

gk_attributes = ['Aer', 'Ref', 'Han', '1v1', 'Ecc', 'Kic', 'Cmd', 'Com', 'Pun', 'TRO', 'Thr']

known_att_gk = known_att[known_att['Position'] == 'GK']
known_att_gk['Count'] = known_att_gk.apply(lambda row: count_hyphens(row, row['Position']), axis=1)
known_att_gk = known_att_gk[['UID', 'Position', 'Name', 'Count']]

known_att_all = known_att[known_att['Position'] != 'GK']
known_att_all.drop(columns=gk_attributes, inplace=True)
known_att_all['Count'] = known_att_all.apply(lambda row: count_hyphens(row, row['Position']), axis=1)
known_att_all = known_att_all[['UID', 'Position', 'Name', 'Count']]

known_att = pd.concat([known_att_all, known_att_gk], ignore_index=True)
known = known_att[known_att['Count'] == 0]
unknown = known_att[known_att['Count'] != 0]

my_club_ids = fm_stats_genie[['UID', 'Club']][fm_stats_genie['Club'] == club]['UID'].to_list()
known_ids = known['UID'].to_list()
known_ids.append(my_club_ids)
unknown_ids = fm_main_genie[fm_main_genie['Rt1'] == 0]['UID'].to_list()

fm_main_genie.loc[~fm_main_genie['UID'].isin(known_ids), 'Rt1'] = 0
fm_main_genie.loc[~fm_main_genie['UID'].isin(known_ids), 'Pt1'] = 0
fm_main_genie['Interested'] = fm_main_genie['UID'].apply(lambda x: 1 if x in interested else 0)

fm_stats_genie.loc[~fm_stats_genie['UID'].isin(known_ids), 'Rt1'] = 0
fm_stats_genie.loc[~fm_stats_genie['UID'].isin(known_ids), 'Pt1'] = 0
fm_stats_genie['Interested'] = fm_stats_genie['UID'].apply(lambda x: 1 if x in interested else 0)

threshold = 17.5
threshold_gk = 16.5
threshold_w = 18

attributes_columns = [
    'Cor', 'Cro', 'Dri', 'Fin', 'Fir', 'Fre', 'Hea', 'Lon', 'L Th', 'Mar',
    'Pas', 'Pen', 'Tck', 'Tec', 'Agg', 'Ant', 'Bra', 'Cmp', 'Cnt', 'Vis',
    'Dec', 'Det', 'Fla', 'Ldr', 'OtB', 'Pos', 'Tea', 'Wor', 'Acc', 'Agi',
    'Bal', 'Jum', 'Nat', 'Pac', 'Sta', 'Str', 'Aer', 'Cmd', 'Com', 'Ecc',
    'Han', 'Kic', '1v1', 'Ref', 'TRO', 'Pun', 'Thr'
]

df = att_data.copy()
att = df.drop(columns=['Rec', 'Inf', 'Based', 'AP', 'Wage'])
att[attributes_columns] = att[attributes_columns].applymap(lambda x: str(x).split("-")[0] if isinstance(x, str) else x)
att = att.replace('', 0)

for col in attributes_columns:
    att[col] = att[col].astype(int)

att['GK_x'] = (
    0 * att['Cor'] + 0 * att['Cro'] + 0 * att['Dri'] + 0 * att['Fin'] + 0.08 * att['Fir'] + 0 * att['Fre'] +
    0 * att['Hea'] + 0 * att['Lon'] + 0 * att['L Th'] + 0 * att['Mar'] + 0 * att['Pas'] + 0 * att['Pen'] +
    0 * att['Tck'] + 0.08 * att['Tec'] + 0 * att['Agg'] + 0.66 * att['Ant'] + 6.26 * att['Bra'] + 0.44 * att['Cmp'] +
    6.26 * att['Cnt'] + 10.43 * att['Dec'] + 0 * att['Det'] + 0 * att['Fla'] + 0.44 * att['Ldr'] +
    0 * att['OtB'] + 5.21 * att['Pos'] + 0.44 * att['Tea'] + 0.08 * att['Vis'] + 0.08 * att['Wor'] +
    3.49 * att['Acc'] + 8.34 * att['Agi'] + 0.44 * att['Bal'] + 0.08 * att['Jum'] + 0 * att['Nat'] +
    0.66 * att['Pac'] + 0.08 * att['Sta'] + 2.33 * att['Str'] + 6.26 * att['Aer'] + 6.26 * att['Cmd'] +
    5.21 * att['Com'] + 0 * att['Ecc'] + 12.64 * att['Han'] + 5.21 * att['Kic'] + 4.17 * att['1v1'] +
    0 * att['Ref'] + 0 * att['TRO'] + 0 * att['Pun'] + 1.74 * att['Thr']
) / threshold_gk

att['LB_x'] = (
    0.11 * att['Cor'] + 0.92 * att['Cro'] + 0.11 * att['Dri'] + 0.11 * att['Fin'] + 1.38 * att['Fir'] + 0.11 * att['Fre'] +
    0.92 * att['Hea'] + 0.11 * att['Lon'] + 0.11 * att['L Th'] + 3.13 * att['Mar'] + 0.92 * att['Pas'] + 0.11 * att['Pen'] +
    7.47 * att['Tck'] + 0.92 * att['Tec'] + 0 * att['Agg'] + 3.13 * att['Ant'] + 0.92 * att['Bra'] + 0.92 * att['Cmp'] +
    7.47 * att['Cnt'] + 13.08 * att['Dec'] + 0 * att['Det'] + 0 * att['Fla'] + 0.22 * att['Ldr'] +
    0.11 * att['OtB'] + 14.94 * att['Pos'] + 0.46 * att['Tea'] + 0.46 * att['Vis'] + 0.92 * att['Wor'] +
    13.08 * att['Acc'] + 6.26 * att['Agi'] + 0.92 * att['Bal'] + 0.92 * att['Jum'] + 0 * att['Nat'] +
    9.34 * att['Pac'] + 6.26 * att['Sta'] + 4.17 * att['Str'] + 0 * att['Aer'] + 0 * att['Cmd'] +
    0 * att['Com'] + 0 * att['Ecc'] + 0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] +
    0 * att['Pun'] + 0 * att['Ref'] + 0 * att['TRO'] + 0 * att['Thr']
) / threshold

att['RB_x'] = att['LB_x']

att['CB_x'] = (
    0.09 * att['Cor'] + 0.09 * att['Cro'] + 0.09 * att['Dri'] + 0.09 * att['Fin'] + 0.59 * att['Fir'] + 0.09 * att['Fre'] +
    6.70 * att['Hea'] + 0.09 * att['Lon'] + 0.09 * att['L Th'] + 10.72 * att['Mar'] + 0.59 * att['Pas'] + 0.09 * att['Pen'] +
    6.70 * att['Tck'] + 0.09 * att['Tec'] + 0 * att['Agg'] + 3.70 * att['Ant'] + 0.59 * att['Bra'] + 0.59 * att['Cmp'] +
    5.36 * att['Cnt'] + 13.40 * att['Dec'] + 0 * att['Det'] + 0 * att['Fla'] + 0.59 * att['Ldr'] +
    0.09 * att['OtB'] + 10.72 * att['Pos'] + 0.09 * att['Tea'] + 0.09 * att['Vis'] + 0.59 * att['Wor'] +
    8.04 * att['Acc'] + 4.44 * att['Agi'] + 0.59 * att['Bal'] + 8.04 * att['Jum'] + 0 * att['Nat'] +
    6.70 * att['Pac'] + 2.22 * att['Sta'] + 8.04 * att['Str'] + 0 * att['Aer'] + 0 * att['Cmd'] +
    0 * att['Com'] + 0 * att['Ecc'] + 0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] +
    0 * att['Pun'] + 0 * att['Ref'] + 0 * att['TRO'] + 0 * att['Thr']
) / threshold

att['LWB_x'] = (
    0.13 * att['Cor'] + 2.86 * att['Cro'] + 1.37 * att['Dri'] + 0.22 * att['Fin'] + 2.11 * att['Fir'] + 0.13 * att['Fre'] +
    0.40 * att['Hea'] + 0.22 * att['Lon'] + 0.13 * att['L Th'] + 1.69 * att['Mar'] + 1.48 * att['Pas'] + 0.13 * att['Pen'] +
    4.73 * att['Tck'] + 2.11 * att['Tec'] + 0 * att['Agg'] + 3.45 * att['Ant'] + 0.40 * att['Bra'] + 1.41 * att['Cmp'] +
    4.73 * att['Cnt'] + 7.88 * att['Dec'] + 0 * att['Det'] + 0 * att['Fla'] + 0.13 * att['Ldr'] +
    0.45 * att['OtB'] + 4.43 * att['Pos'] + 0.99 * att['Tea'] + 1.41 * att['Vis'] + 1.41 * att['Wor'] +
    20.96 * att['Acc'] + 5.76 * att['Agi'] + 0.99 * att['Bal'] + 0.40 * att['Jum'] + 0 * att['Nat'] +
    15.72 * att['Pac'] + 8.06 * att['Sta'] + 3.76 * att['Str'] + 0 * att['Aer'] + 0 * att['Cmd'] +
    0 * att['Com'] + 0 * att['Ecc'] + 0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] +
    0 * att['Pun'] + 0 * att['Ref'] + 0 * att['TRO'] + 0 * att['Thr']
) / threshold

att['RWB_x'] = att['LWB_x']

att['DM_x'] = (
    0.12 * att['Cor'] + 0.12 * att['Cro'] + 0.56 * att['Dri'] + 0.56 * att['Fin'] + 2.95 * att['Fir'] + 0.12 * att['Fre'] +
    0.95 * att['Hea'] + 1.80 * att['Lon'] + 0.12 * att['L Th'] + 3.34 * att['Mar'] + 4.55 * att['Pas'] + 0.12 * att['Pen'] +
    10.03 * att['Tck'] + 1.80 * att['Tec'] + 0 * att['Agg'] + 5.17 * att['Ant'] + 0.26 * att['Bra'] + 1.47 * att['Cmp'] +
    3.34 * att['Cnt'] + 11.46 * att['Dec'] + 0 * att['Det'] + 0 * att['Fla'] + 0.26 * att['Ldr'] + 0.28 * att['OtB'] +
    5.57 * att['Pos'] + 0.56 * att['Tea'] + 3.99 * att['Vis'] + 2.95 * att['Wor'] + 10.99 * att['Acc'] + 6.20 * att['Agi'] +
    0.84 * att['Bal'] + 0.95 * att['Jum'] + 0 * att['Nat'] + 7.33 * att['Pac'] + 4.13 * att['Sta'] + 7.16 * att['Str'] +
    0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] + 0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] +
    0 * att['Pun'] + 0 * att['Ref'] + 0 * att['TRO'] + 0 * att['Thr']
) / threshold

att['CM_x'] = (
    0.11 * att['Cor'] + 0.11 * att['Cro'] + 0.84 * att['Dri'] + 0.84 * att['Fin'] + 6.20 * att['Fir'] + 0.11 * att['Fre'] +
    0.11 * att['Hea'] + 3.10 * att['Lon'] + 0.11 * att['L Th'] + 1.27 * att['Mar'] + 10.79 * att['Pas'] + 0.11 * att['Pen'] +
    3.10 * att['Tck'] + 4.13 * att['Tec'] + 0 * att['Agg'] + 3.10 * att['Ant'] + 0.11 * att['Bra'] + 3.10 * att['Cmp'] +
    0.84 * att['Cnt'] + 7.24 * att['Dec'] + 0 * att['Det'] + 0 * att['Fla'] + 0.11 * att['Ldr'] + 1.27 * att['OtB'] +
    1.27 * att['Pos'] + 0.84 * att['Tea'] + 10.79 * att['Vis'] + 3.10 * att['Wor'] + 10.79 * att['Acc'] + 6.20 * att['Agi'] +
    0.84 * att['Bal'] + 0.11 * att['Jum'] + 0 * att['Nat'] + 8.99 * att['Pac'] + 6.20 * att['Sta'] + 4.13 * att['Str'] +
    0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] + 0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] +
    0 * att['Pun'] + 0 * att['Ref'] + 0 * att['TRO'] + 0 * att['Thr']
) / threshold

att['AM_x'] = (
    0.11 * att['Cor'] + 0.11 * att['Cro'] + 2.64 * att['Dri'] + 2.64 * att['Fin'] + 4.40 * att['Fir'] + 0.11 * att['Fre'] +
    0.11 * att['Hea'] + 2.64 * att['Lon'] + 0.11 * att['L Th'] + 0.11 * att['Mar'] + 6.33 * att['Pas'] + 0.11 * att['Pen'] +
    0.65 * att['Tck'] + 4.40 * att['Tec'] + 0 * att['Agg'] + 2.64 * att['Ant'] + 0.11 * att['Bra'] + 2.64 * att['Cmp'] +
    0.65 * att['Cnt'] + 5.27 * att['Dec'] + 0 * att['Det'] + 0 * att['Fla'] + 0.11 * att['Ldr'] + 2.64 * att['OtB'] +
    0.65 * att['Pos'] + 0.65 * att['Tea'] + 9.49 * att['Vis'] + 2.64 * att['Wor'] + 21.36 * att['Acc'] + 5.27 * att['Agi'] +
    0.65 * att['Bal'] + 0.11 * att['Jum'] + 0 * att['Nat'] + 11.87 * att['Pac'] + 6.15 * att['Sta'] + 2.64 * att['Str'] +
    0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] + 0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] +
    0 * att['Pun'] + 0 * att['Ref'] + 0 * att['TRO'] + 0 * att['Thr']
) / threshold

att['LW_x'] = (
    0.09 * att['Cor'] + 6.62 * att['Cro'] + 6.62 * att['Dri'] + 0.62 * att['Fin'] + 3.86 * att['Fir'] + 0.09 * att['Fre'] +
    0.09 * att['Hea'] + 0.62 * att['Lon'] + 0.09 * att['L Th'] + 0.09 * att['Mar'] + 0.62 * att['Pas'] + 0.09 * att['Pen'] +
    0.62 * att['Tck'] + 3.09 * att['Tec'] + 0 * att['Agg'] + 2.32 * att['Ant'] + 0.09 * att['Bra'] + 2.32 * att['Cmp'] +
    0.62 * att['Cnt'] + 1.54 * att['Dec'] + 0 * att['Det'] + 0 * att['Fla'] + 0.09 * att['Ldr'] + 0.62 * att['OtB'] +
    0.09 * att['Pos'] + 0.62 * att['Tea'] + 2.32 * att['Vis'] + 2.32 * att['Wor'] + 26.10 * att['Acc'] + 4.63 * att['Agi'] +
    0.62 * att['Bal'] + 0.09 * att['Jum'] + 0 * att['Nat'] + 26.10 * att['Pac'] + 5.40 * att['Sta'] + 0.93 * att['Str'] +
    0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] + 0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] +
    0 * att['Pun'] + 0 * att['Ref'] + 0 * att['TRO'] + 0 * att['Thr']
) / threshold_w

att['RW_x'] = att['LW_x']

att['FS_x'] = (
    0.08 * att['Cor'] + 0.43 * att['Cro'] + 2.88 * att['Dri'] + 8.39 * att['Fin'] + 6.29 * att['Fir'] + 0.08 * att['Fre'] +
    6.29 * att['Hea'] + 0.43 * att['Lon'] + 0.08 * att['L Th'] + 0.08 * att['Mar'] + 0.43 * att['Pas'] + 0.08 * att['Pen'] +
    0.08 * att['Tck'] + 2.30 * att['Tec'] + 0 * att['Agg'] + 2.88 * att['Ant'] + 0.08 * att['Bra'] + 6.29 * att['Cmp'] +
    0.43 * att['Cnt'] + 1.08 * att['Dec'] + 0 * att['Det'] + 0 * att['Fla'] + 0.08 * att['Ldr'] + 6.29 * att['OtB'] +
    0.43 * att['Pos'] + 0.08 * att['Tea'] + 0.43 * att['Vis'] + 0.43 * att['Wor'] + 21.65 * att['Acc'] + 3.45 * att['Agi'] +
    0.43 * att['Bal'] + 5.24 * att['Jum'] + 0 * att['Nat'] + 15.15 * att['Pac'] + 1.30 * att['Sta'] + 6.29 * att['Str'] +
    0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] + 0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] +
    0 * att['Pun'] + 0 * att['Ref'] + 0 * att['TRO'] + 0 * att['Thr']
) / threshold

att['TS_x'] = (
    0.08 * att['Cor'] + 0.43 * att['Cro'] + 2.88 * att['Dri'] + 8.39 * att['Fin'] + 6.29 * att['Fir'] + 0.08 * att['Fre'] +
    13.29 * att['Hea'] + 0.43 * att['Lon'] + 0.08 * att['L Th'] + 0.08 * att['Mar'] + 0.43 * att['Pas'] + 0.08 * att['Pen'] +
    0.08 * att['Tck'] + 2.30 * att['Tec'] + 0 * att['Agg'] + 2.88 * att['Ant'] + 0.08 * att['Bra'] + 6.29 * att['Cmp'] +
    0.43 * att['Cnt'] + 1.08 * att['Dec'] + 0 * att['Det'] + 0 * att['Fla'] + 0.08 * att['Ldr'] + 6.29 * att['OtB'] +
    0.43 * att['Pos'] + 0.08 * att['Tea'] + 0.43 * att['Vis'] + 0.43 * att['Wor'] + 14.65 * att['Acc'] + 3.45 * att['Agi'] +
    0.43 * att['Bal'] + 12.24 * att['Jum'] + 0 * att['Nat'] + 8.15 * att['Pac'] + 1.30 * att['Sta'] + 6.29 * att['Str'] +
    0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] + 0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] +
    0 * att['Pun'] + 0 * att['Ref'] + 0 * att['TRO'] + 0 * att['Thr']
) / threshold

att['GK_y'] = ((0 * att['Cor'] + 0 * att['Cro'] + 0 * att['Dri'] + 0 * att['Fin'] + 30 * att['Fir'] + 0 * att['Fre'] +
            0 * att['Hea'] + 0 * att['Lon'] + 0 * att['L Th'] + 0 * att['Mar'] + 45 * att['Pas'] + 0 * att['Pen'] +
            0 * att['Tck'] + 0 * att['Tec'] + 40 * att['Agg'] + 40 * att['Ant'] + 30 * att['Bra'] + 40 * att['Cmp'] +
            65 * att['Cnt'] + 40 * att['Vis'] + 50 * att['Dec'] + 20 * att['Det'] + 20 * att['Fla'] + 10 * att['Ldr'] +
            0 * att['OtB'] + 40 * att['Pos'] + 20 * att['Tea'] + 10 * att['Wor'] + 70 * att['Acc'] + 100 * att['Agi'] +
            20 * att['Bal'] + 45 * att['Jum'] + 10 * att['Nat'] + 50 * att['Pac'] + 10 * att['Sta'] + 70 * att['Str'] +
            60 * att['Aer'] + 40 * att['Cmd'] + 30 * att['Com'] + 0 * att['Ecc'] + 50 * att['Han'] + 35 * att['Kic'] +
            45 * att['1v1'] + 80 * att['Ref'] + 40 * att['TRO'] + 0 * att['Pun'] + 30 * att['Thr']) / 1285) * (100/threshold_gk)

att['LB_y'] = ((30 * att['Cor'] + 25 * att['Cro'] + 50 * att['Dri'] + 10 * att['Fin'] + 30 * att['Fir'] +
             10 * att['Fre'] + 20 * att['Hea'] + 10 * att['Lon'] + 30 * att['L Th'] + 45 * att['Mar'] +
             45 * att['Pas'] + 10 * att['Pen'] + 50 * att['Tck'] + 45 * att['Tec'] + 45 * att['Agg'] +
             45 * att['Ant'] + 20 * att['Bra'] + 30 * att['Cmp'] + 45 * att['Cnt'] + 25 * att['Vis'] +
             45 * att['Dec'] + 20 * att['Det'] + 20 * att['Fla'] + 10 * att['Ldr'] + 70 * att['OtB'] +
             30 * att['Pos'] + 45 * att['Tea'] + 90 * att['Wor'] + 100 * att['Acc'] + 60 * att['Agi'] +
             25 * att['Bal'] + 40 * att['Jum'] + 10 * att['Nat'] + 90 * att['Pac'] + 100 * att['Sta'] +
             25 * att['Str'] + 0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] +
             0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] + 0 * att['Ref'] + 0 * att['TRO'] +
             0 * att['Pun'] + 0 * att['Thr']) / 1400) * (100/threshold)

att['RB_y'] = att['LB_y']

att['CB_y'] = ((5 * att['Cor'] + 1 * att['Cro'] + 40 * att['Dri'] + 10 * att['Fin'] + 35 * att['Fir'] + 10 * att['Fre'] +
            55 * att['Hea'] + 10 * att['Lon'] + 5 * att['L Th'] + 55 * att['Mar'] + 55 * att['Pas'] + 10 * att['Pen'] +
            40 * att['Tck'] + 35 * att['Tec'] + 40 * att['Agg'] + 50 * att['Ant'] + 30 * att['Bra'] + 80 * att['Cmp'] +
            50 * att['Cnt'] + 50 * att['Vis'] + 50 * att['Dec'] + 20 * att['Det'] + 10 * att['Fla'] + 10 * att['Ldr'] +
            10 * att['OtB'] + 55 * att['Pos'] + 20 * att['Tea'] + 55 * att['Wor'] + 90 * att['Acc'] + 60 * att['Agi'] +
            35 * att['Bal'] + 65 * att['Jum'] + 10 * att['Nat'] + 90 * att['Pac'] + 30 * att['Sta'] + 50 * att['Str'] +
            0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] + 0 * att['Han'] + 0 * att['Kic'] +
            0 * att['1v1'] + 0 * att['Ref'] + 0 * att['TRO'] + 0 * att['Pun'] + 0 * att['Thr']) / 1326) * (100/threshold)

att['LWB_y'] = ((30 * att['Cor'] + 40 * att['Cro'] + 50 * att['Dri'] + 0 * att['Fin'] + 30 * att['Fir'] +
              10 * att['Fre'] + 20 * att['Hea'] + 10 * att['Lon'] + 30 * att['L Th'] + 40 * att['Mar'] +
              45 * att['Pas'] + 10 * att['Pen'] + 35 * att['Tck'] + 45 * att['Tec'] + 40 * att['Agg'] +
              45 * att['Ant'] + 20 * att['Bra'] + 30 * att['Cmp'] + 40 * att['Cnt'] + 25 * att['Vis'] +
              40 * att['Dec'] + 20 * att['Det'] + 20 * att['Fla'] + 10 * att['Ldr'] + 50 * att['OtB'] +
              35 * att['Pos'] + 45 * att['Tea'] + 85 * att['Wor'] + 100 * att['Acc'] + 60 * att['Agi'] +
              20 * att['Bal'] + 35 * att['Jum'] + 10 * att['Nat'] + 95 * att['Pac'] + 90 * att['Sta'] +
              20 * att['Str'] + 0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] +
              0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] + 0 * att['Ref'] + 0 * att['TRO'] +
              0 * att['Pun'] + 0 * att['Thr']) / 1330) * (100/threshold)

att['RWB_y'] = att['LWB_y']

att['DM_y'] = ((10 * att['Cor'] + 10 * att['Cro'] + 45 * att['Dri'] + 20 * att['Fin'] + 50 * att['Fir'] +
             30 * att['Fre'] + 10 * att['Hea'] + 40 * att['Lon'] + 5 * att['L Th'] + 20 * att['Mar'] +
             65 * att['Pas'] + 10 * att['Pen'] + 35 * att['Tck'] + 50 * att['Tec'] + 50 * att['Agg'] +
             55 * att['Ant'] + 30 * att['Bra'] + 60 * att['Cmp'] + 50 * att['Cnt'] + 55 * att['Vis'] +
             65 * att['Dec'] + 20 * att['Det'] + 50 * att['Fla'] + 10 * att['Ldr'] + 40 * att['OtB'] +
             65 * att['Pos'] + 65 * att['Tea'] + 90 * att['Wor'] + 65 * att['Acc'] + 45 * att['Agi'] +
             35 * att['Bal'] + 15 * att['Jum'] + 0 * att['Nat'] + 70 * att['Pac'] + 70 * att['Sta'] +
             35 * att['Str'] + 0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] +
             0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] + 0 * att['Ref'] + 0 * att['TRO'] +
             0 * att['Pun'] + 0 * att['Thr']) / 1440) * (100/threshold)

att['CM_y'] = ((5 * att['Cor'] + 5 * att['Cro'] + 55 * att['Dri'] + 40 * att['Fin'] + 50 * att['Fir'] +
             30 * att['Fre'] + 10 * att['Hea'] + 30 * att['Lon'] + 5 * att['L Th'] + 10 * att['Mar'] +
             65 * att['Pas'] + 15 * att['Pen'] + 20 * att['Tck'] + 50 * att['Tec'] + 50 * att['Agg'] +
             50 * att['Ant'] + 25 * att['Bra'] + 40 * att['Cmp'] + 35 * att['Cnt'] + 40 * att['Vis'] +
             50 * att['Dec'] + 20 * att['Det'] + 35 * att['Fla'] + 10 * att['Ldr'] + 40 * att['OtB'] +
             40 * att['Pos'] + 50 * att['Tea'] + 80 * att['Wor'] + 100 * att['Acc'] + 40 * att['Agi'] +
             40 * att['Bal'] + 10 * att['Jum'] + 0 * att['Nat'] + 75 * att['Pac'] + 75 * att['Sta'] +
             30 * att['Str'] + 0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] +
             0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] + 0 * att['Ref'] + 0 * att['TRO'] +
             0 * att['Pun'] + 0 * att['Thr']) / 1325) * (100/threshold)

att['AM_y'] = ((5 * att['Cor'] + 5 * att['Cro'] + 65 * att['Dri'] + 65 * att['Fin'] + 40 * att['Fir'] +
             30 * att['Fre'] + 10 * att['Hea'] + 20 * att['Lon'] + 1 * att['L Th'] + 5 * att['Mar'] +
             50 * att['Pas'] + 15 * att['Pen'] + 15 * att['Tck'] + 65 * att['Tec'] + 50 * att['Agg'] +
             70 * att['Ant'] + 20 * att['Bra'] + 35 * att['Cmp'] + 25 * att['Cnt'] + 30 * att['Vis'] +
             40 * att['Dec'] + 20 * att['Det'] + 20 * att['Fla'] + 10 * att['Ldr'] + 35 * att['OtB'] +
             10 * att['Pos'] + 35 * att['Tea'] + 80 * att['Wor'] + 100 * att['Acc'] + 30 * att['Agi'] +
             50 * att['Bal'] + 10 * att['Jum'] + 10 * att['Nat'] + 80 * att['Pac'] + 80 * att['Sta'] +
             30 * att['Str'] + 0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] +
             0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] + 0 * att['Ref'] + 0 * att['TRO'] +
             0 * att['Pun'] + 0 * att['Thr']) / 1261) * (100/threshold)

att['LW_y'] = ((30 * att['Cor'] + 65 * att['Cro'] + 55 * att['Dri'] + 15 * att['Fin'] + 30 * att['Fir'] +
             10 * att['Fre'] + 10 * att['Hea'] + 10 * att['Lon'] + 30 * att['L Th'] + 35 * att['Mar'] +
             50 * att['Pas'] + 15 * att['Pen'] + 35 * att['Tck'] + 50 * att['Tec'] + 35 * att['Agg'] +
             45 * att['Ant'] + 15 * att['Bra'] + 30 * att['Cmp'] + 35 * att['Cnt'] + 35 * att['Vis'] +
             35 * att['Dec'] + 20 * att['Det'] + 20 * att['Fla'] + 10 * att['Ldr'] + 40 * att['OtB'] +
             35 * att['Pos'] + 40 * att['Tea'] + 75 * att['Wor'] + 100 * att['Acc'] + 50 * att['Agi'] +
             15 * att['Bal'] + 10 * att['Jum'] + 10 * att['Nat'] + 100 * att['Pac'] + 75 * att['Sta'] +
             30 * att['Str'] + 0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] +
             0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] + 0 * att['Ref'] + 0 * att['TRO'] +
             0 * att['Pun'] + 0 * att['Thr']) / 1300) * (100/threshold_w)

att['RW_y'] = att['LW_y']

att['FS_y'] = ((5 * att['Cor'] + 5 * att['Cro'] + 75 * att['Dri'] + 80 * att['Fin'] + 50 * att['Fir'] +
             5 * att['Fre'] + 25 * att['Hea'] + 25 * att['Lon'] + 1 * att['L Th'] + 1 * att['Mar'] +
             40 * att['Pas'] + 20 * att['Pen'] + 5 * att['Tck'] + 65 * att['Tec'] + 50 * att['Agg'] +
             50 * att['Ant'] + 20 * att['Bra'] + 35 * att['Cmp'] + 5 * att['Cnt'] + 20 * att['Vis'] +
             45 * att['Dec'] + 20 * att['Det'] + 25 * att['Fla'] + 10 * att['Ldr'] + 45 * att['OtB'] +
             5 * att['Pos'] + 35 * att['Tea'] + 60 * att['Wor'] + 100 * att['Acc'] + 30 * att['Agi'] +
             50 * att['Bal'] + 20 * att['Jum'] + 10 * att['Nat'] + 70 * att['Pac'] + 65 * att['Sta'] +
             25 * att['Str'] + 0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] +
             0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] + 0 * att['Ref'] + 0 * att['TRO'] +
             0 * att['Pun'] + 0 * att['Thr']) / 1197) * (100/threshold)

att['TS_y'] = ((5 * att['Cor'] + 5 * att['Cro'] + 50 * att['Dri'] + 80 * att['Fin'] + 50 * att['Fir'] +
             5 * att['Fre'] + 40 * att['Hea'] + 25 * att['Lon'] + 1 * att['L Th'] + 1 * att['Mar'] +
             40 * att['Pas'] + 20 * att['Pen'] + 5 * att['Tck'] + 50 * att['Tec'] + 50 * att['Agg'] +
             50 * att['Ant'] + 20 * att['Bra'] + 35 * att['Cmp'] + 5 * att['Cnt'] + 20 * att['Vis'] +
             45 * att['Dec'] + 20 * att['Det'] + 25 * att['Fla'] + 10 * att['Ldr'] + 50 * att['OtB'] +
             5 * att['Pos'] + 35 * att['Tea'] + 50 * att['Wor'] + 100 * att['Acc'] + 30 * att['Agi'] +
             50 * att['Bal'] + 50 * att['Jum'] + 10 * att['Nat'] + 70 * att['Pac'] + 50 * att['Sta'] +
             50 * att['Str'] + 0 * att['Aer'] + 0 * att['Cmd'] + 0 * att['Com'] + 0 * att['Ecc'] +
             0 * att['Han'] + 0 * att['Kic'] + 0 * att['1v1'] + 0 * att['Ref'] + 0 * att['TRO'] +
             0 * att['Pun'] + 0 * att['Thr']) / 1207) * (100/threshold)

att['ST_x'] = att[['TS_x', 'FS_x']].max(axis=1)
att['ST_y'] = att[['TS_y', 'FS_y']].max(axis=1)

positions = ['GK', 'LB', 'RB', 'CB', 'LWB', 'RWB', 'DM', 'CM', 'AM', 'LW', 'RW', 'ST']

for position in positions:
    x_column = f'{position}_x'
    y_column = f'{position}_y'
    att[position] = att[[x_column, y_column]].max(axis=1)

att[positions] = att[positions].round(1)
att = att[['UID', 'GK', 'LB', 'RB', 'CB', 'LWB', 'RWB', 'DM', 'CM', 'AM', 'LW', 'RW', 'ST']]

# Define a function to replace 0 values in 'Rt1' with values from corresponding columns
def replace_zero(row):
    if row['Rt1'] == 0:
        primary_position = row['P1']
        secondary_position = row['P2']
        
        if pd.notnull(row[primary_position]) and pd.notnull(row[secondary_position]):
            return max(row[primary_position], row[secondary_position])
        elif pd.notnull(row[primary_position]):
            return row[primary_position]
        elif pd.notnull(row[secondary_position]):
            return row[secondary_position]
    
    return row['Rt1']


fm_main_genie = fm_main_genie.merge(att, on='UID', how='left')
fm_stats_genie = fm_stats_genie.merge(att, on='UID', how='left')

# Apply the function to update 'Rt1'
fm_main_genie['Rt1'] = fm_main_genie.apply(replace_zero, axis=1)
fm_stats_genie['Rt1'] = fm_stats_genie.apply(replace_zero, axis=1)

new_main_columns_order = [
    'Rgn', 'Half', 'Date', 'UID', 'EU', 'NoB', 'Nat', 'P1', 'P2', 'Rt1',
    'Pt1', 'RtG', 'PtG', 'Interested', 'Position', 'Age', 'Name', 'Av_Rat',
    'Club', 'Division', 'Based', 'Apps', 'Starts', 'Gls', 'Ast', 'PoM', 'Mins',
    'GK%', 'DFg%', 'DFa%', 'PAS%', 'DRB%', 'ST%', 'Value', 'Wage', 'Expires',
    'Det', 'Prof', 'Amb', 'Acc', 'Pac', 'Personality', 'Height'
]

new_stats_columns_order = [
    'Rgn', 'Half', 'Date', 'UID', 'EU', 'NoB', 'Nat', 'P1', 'P2', 'Rt1',
    'Pt1', 'RtG', 'PtG', 'Interested', 'Position', 'Age', 'Name', 'Av_Rat',
    'Club', 'Division', 'Based', 'Apps', 'Starts', 'Gls', 'Ast', 'PoM',
    'Mins', 'GK%', 'DFg%', 'DFa%', 'PAS%', 'DRB%', 'ST%', 'Value', 'Wage',
    'Expires', 'Det', 'Prof', 'Amb', 'Acc', 'Pac', 'Personality', 'Height',
    'xGP/90', 'CS/90', 'Gls_Conc/90', 'Blocks/90', 'Intcp/90', 'Clear/90',
    'Press_C/90', 'Hdrs_W/90', 'OP-KP/90', 'CCC/90', 'Pr_Pas/90', 'xA/90',
    'Pas_C/90', 'Drb/90', 'Sprints/90', 'Fls_Ag/90', 'Cr_C/90', 'NP-xG/90',
    'Gls/90', 'Sht_T/90', 'NP-xG/Shot', 'xGP', 'CS', 'Gls_Conc', 'Blocks',
    'Intcp', 'Clear', 'Press_C', 'Hdrs_A', 'Hdrs_W', 'OP-KP', 'CCC',
    'Pr_Pas', 'xA', 'Pas_A', 'Pas_C', 'Cr_A', 'Cr_C', 'Drb', 'Fls_Ag', 'xG',
    'NP-xG', 'Sht', 'Sht_T', 'Ps%', 'Hd%', 'Cr%'
]

# Create a new DataFrame with the desired column order
main = fm_main_genie[new_main_columns_order].copy()
stats = fm_stats_genie[new_stats_columns_order].copy()

# Exporting the resulting dataframe to a CSV file
csv_file_path = os.path.join(folder_export, csv_file + ".csv")

excel_column_order = [
    'Rgn', 'Half', 'Date', 'UID', 'EU', 'Nat', 'Interested', 'P1', 'P2',
    'Rt1', 'Pt1', 'RtG', 'PtG', 'Position', 'Age', 'Name', 'Av_Rat',
    'Club', 'Division', 'Based', 'Apps', 'Starts', 'Gls', 'Ast', 'PoM',
    'Mins', 'GK%', 'DFg%', 'DFa%', 'xGP/90', 'CS/90', 'Gls_Conc/90',
    'Hdrs_W/90', 'Hd%', 'Blocks/90', 'Intcp/90', 'Clear/90', 'Press_C/90',
    'PAS%', 'OP-KP/90', 'CCC/90', 'Pr_Pas/90', 'xA/90', 'Pas_C/90', 'Ps%',
    'DRB%', 'ST%', 'Drb/90', 'Cr_C/90', 'Cr%', 'NP-xG/90', 'Gls/90',
    'NP-xG/Shot', 'Sht_T/90', 'Sprints/90', 'Fls_Ag/90', 'Value', 'Wage',
    'Expires', 'Det', 'Prof', 'Amb', 'Acc', 'Pac', 'Height', 'Personality',
    'xGP', 'CS', 'Gls_Conc', 'Blocks', 'Intcp', 'Clear', 'Press_C', 'Hdrs_A',
    'Hdrs_W', 'OP-KP', 'CCC', 'Pr_Pas', 'xA', 'Pas_A', 'Pas_C', 'Cr_A',
    'Cr_C', 'Drb', 'Fls_Ag', 'xG', 'NP-xG', 'Sht', 'Sht_T']

excel_table = fm_stats_genie[excel_column_order]

columns_to_format_as_text  = ['Det', 'Prof', 'Amb', 'Acc', 'Pac']
for col in columns_to_format_as_text:
    excel_table[col] = excel_table[col].astype(str)
    excel_table[col] = excel_table[col].str.replace('-', '_')

excel_table.to_csv(csv_file_path, index=False, encoding='utf-8', sep=';', decimal=',')

print(f'Full list of players exported.')
print(f'File {csv_file}.csv created at "{folder_export}"')