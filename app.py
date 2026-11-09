import streamlit as st
import pandas as pd
import pickle
import requests
from datetime import datetime, timedelta
import pytz

st.set_page_config(page_title="NBA Total Predictor", layout="centered")
st.title("🏀 NBA Total Predictor")
st.caption("Model asks for Bet MAIN LINE - Type it, Model will predict")

# ===== LOAD MODEL =====
@st.cache_resource
def load_stuff():
    model = pickle.load(open('nba_total_model.pkl','rb'))
    feature_cols = pickle.load(open('feature_cols.pkl','rb'))
    history = pd.read_csv('nba_5years_history.csv', parse_dates=['GAME_DATE'])
    return model, feature_cols, history

model, feature_cols, history = load_stuff()

# ===== YOUR FUNCTIONS - SAME AS COLAB =====
def get_team_live_features(team_abbr, history_df):
    team_games = history_df[history_df['TEAM_ABBREVIATION'] == team_abbr].sort_values('GAME_DATE')
    if len(team_games) == 0:
        return {'PTS_LAST5':112.0,'OPP_PTS_LAST5':112.0,'PACE_LAST5':100.0,'FG_PCT_LAST5':0.46,'PTS_SEASON':112.0,'REST':2,'B2B':0}
    last5 = team_games.tail(5)
    season = team_games.tail(20)
    last_game_date = pd.to_datetime(team_games.iloc[-1]['GAME_DATE'])
    us_today = datetime.now(pytz.timezone('US/Eastern')).date()
    rest = (pd.to_datetime(us_today) - last_game_date).days
    rest = int(max(1, min(rest, 3)))
    return {'PTS_LAST5': last5['PTS'].mean(),'OPP_PTS_LAST5': last5['OPP_PTS'].mean(),'PACE_LAST5': last5['PACE'].mean(),'FG_PCT_LAST5': last5['FG_PCT'].mean(),'PTS_SEASON': season['PTS'].mean(),'REST': rest,'B2B': 1 if rest==1 else 0}

# Paste your get_injuries_live here - use your own version
# If you no get am for this file, use dummy so app no crash
# ===== YOUR INJURY CELL - FROM nba.ipynb - DO NOT CHANGE =====
import time
INJURY_CACHE = {}
INJURY_CACHE_TIME = 0
CACHE_TTL = 3600

TEAM_NAME_TO_ABBR = {
    'Atlanta Hawks':'ATL','Boston Celtics':'BOS','Brooklyn Nets':'BKN','Charlotte Hornets':'CHA',
    'Chicago Bulls':'CHI','Cleveland Cavaliers':'CLE','Dallas Mavericks':'DAL','Denver Nuggets':'DEN',
    'Detroit Pistons':'DET','Golden State Warriors':'GSW','Houston Rockets':'HOU','Indiana Pacers':'IND',
    'LA Clippers':'LAC','Los Angeles Lakers':'LAL','Memphis Grizzlies':'MEM','Miami Heat':'MIA',
    'Milwaukee Bucks':'MIL','Minnesota Timberwolves':'MIN','New Orleans Pelicans':'NOP','New York Knicks':'NYK',
    'Oklahoma City Thunder':'OKC','Orlando Magic':'ORL','Philadelphia 76ers':'PHI','Phoenix Suns':'PHX',
    'Portland Trail Blazers':'POR','Sacramento Kings':'SAC','San Antonio Spurs':'SAS','Toronto Raptors':'TOR',
    'Utah Jazz':'UTA','Washington Wizards':'WAS'
}
STARS = {'Anthony Edwards','Paolo Banchero','Jimmy Butler','Jalen Suggs','Trae Young','Joel Embiid','Tyrese Maxey','Luka Doncic','LeBron James','Stephen Curry','Kevin Durant','Jayson Tatum','Jaylen Brown','Nikola Jokic','Giannis Antetokounmpo','Shai Gilgeous-Alexander','Anthony Davis','Ja Morant','Damian Lillard','Devin Booker','Kyrie Irving','Jalen Johnson','Jalen Brunson','Tyrese Haliburton','Donovan Mitchell','Zion Williamson','Chet Holmgren','Desmond Bane','Jalen Williams'}

def load_injuries_real(force_refresh=False):
    global INJURY_CACHE, INJURY_CACHE_TIME
    if INJURY_CACHE and not force_refresh and (time.time() - INJURY_CACHE_TIME) < CACHE_TTL:
        return INJURY_CACHE
    INJURY_CACHE = {}
    try:
        data = requests.get("https://site.api.espn.com/apis/site/v2/sports/basketball/nba/injuries", timeout=10).json()
        for team_entry in data.get('injuries', []):
            abbr = TEAM_NAME_TO_ABBR.get(team_entry.get('displayName',''))
            if not abbr: continue
            outs = []; out_count = 0
            for inj in team_entry.get('injuries', []):
                player = inj.get('athlete', {}).get('displayName','?')
                status = inj.get('status','')
                if status in ['Out','Out for Season','Out Indefinitely','Out For Season']:
                    outs.append(f"{player} (Out)"); out_count += 1
                elif status in ['Doubtful','Questionable','Day-To-Day']:
                    outs.append(f"{player} ({status})")
            INJURY_CACHE[abbr] = (outs, out_count)
        INJURY_CACHE_TIME = time.time()
        print(f"Injuries loaded for {len(INJURY_CACHE)} teams ✅")
    except Exception as e:
        print(f"Injury fetch fail: {e}")
    return INJURY_CACHE

def get_injuries_live(team_abbr):
    cache = load_injuries_real()
    if team_abbr not in cache: return "Healthy", 0, 0.0
    outs, out_count = cache[team_abbr]
    if not outs: return "Healthy", 0, 0.0
    adj = 0.0
    for o in outs:
        name = o.split(' (')[0]
        if '(Out)' in o:
            adj += -4.0 if name in STARS else -0.5
    adj = max(adj, -8.0)
    return "OUT: " + ", ".join(outs[:4]), out_count, adj

# ===== GET GAMES FOR NEXT 24H =====
ESPN_TO_NBA = {'GS':'GSW','WSH':'WAS','NO':'NOP','NY':'NYK','SA':'SAS','UTAH':'UTA','PHX':'PHX'}
us_now = datetime.now(pytz.timezone('US/Eastern'))
today_us = us_now.strftime('%Y-%m-%d')
tomorrow_us = (us_now + timedelta(days=1)).strftime('%Y-%m-%d')

st.info(f"USA Now: {us_now.strftime('%Y-%m-%d %H:%M')} | Lagos: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

games_today = []
for game_date in [today_us, tomorrow_us]:
    try:
        data = requests.get(f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard?dates={game_date.replace('-','')}", timeout=20).json()
    except:
        continue
    for ev in data.get('events', []):
        status = ev.get('status', {}).get('type', {})
        if status.get('state') == 'post': continue
        if 'Final' in status.get('description',''): continue
        comps = ev.get('competitions', [{}])[0].get('competitors', [])
        home = next((c for c in comps if c.get('homeAway')=='home'), {})
        away = next((c for c in comps if c.get('homeAway')=='away'), {})
        h = ESPN_TO_NBA.get(home.get('team',{}).get('abbreviation','???'), home.get('team',{}).get('abbreviation','???'))
        a = ESPN_TO_NBA.get(away.get('team',{}).get('abbreviation','???'), away.get('team',{}).get('abbreviation','???'))
        games_today.append({'home':h,'away':a,'status':status.get('description','Scheduled')})

st.subheader(f"Next 24h: {len(games_today)} games")

# ===== STEP 1: SHOW ALL GAMES + ASK LINE =====
# We use session_state so lines no go disappear when you press button
if len(games_today) == 0:
    st.warning("No games for next 24h. Check later.")
    st.stop()

lines = {}
for i, g in enumerate(games_today):
    display = f"{g['home']} v {g['away']}"  # HOME v AWAY - PHX v PHI
    st.markdown(f"### {i+1}. {display}")
    st.caption(f"Status: {g['status']}")
    # Box to type line - THIS NA THE MODEL ASKING YOU
    line = st.number_input(
        f"Bet MAIN LINE for {display}",
        min_value=180.0, max_value=260.0, value=226.5, step=0.5,
        key=f"line_{i}_{display}"
    )
    lines[display] = line
    st.divider()

# ===== STEP 2: PREDICT BUTTON =====
if st.button("🔮 PREDICT ALL GAMES", type="primary", use_container_width=True):
    st.subheader("Results")
    for g in games_today:
        home_abbr, away_abbr = g['home'], g['away']
        display = f"{home_abbr} v {away_abbr}"
        line = lines[display]

        home_inj, home_out, home_adj = get_injuries_live(home_abbr)
        away_inj, away_out, away_adj = get_injuries_live(away_abbr)
        hf = get_team_live_features(home_abbr, history)
        af = get_team_live_features(away_abbr, history)

        feat = {'HOME_PTS_LAST5': hf['PTS_LAST5'],'AWAY_PTS_LAST5': af['PTS_LAST5'],'HOME_OPP_PTS_LAST5': hf['OPP_PTS_LAST5'],'AWAY_OPP_PTS_LAST5': af['OPP_PTS_LAST5'],'HOME_PACE_LAST5': hf['PACE_LAST5'],'AWAY_PACE_LAST5': af['PACE_LAST5'],'HOME_FG_PCT_LAST5': hf['FG_PCT_LAST5'],'AWAY_FG_PCT_LAST5': af['FG_PCT_LAST5'],'HOME_PTS_SEASON': hf['PTS_SEASON'],'AWAY_PTS_SEASON': af['PTS_SEASON'],'EXPECTED_TOTAL': hf['PTS_LAST5']+af['PTS_LAST5'],'PACE_AVG': (hf['PACE_LAST5']+af['PACE_LAST5'])/2,'DEF_AVG': (hf['OPP_PTS_LAST5']+af['OPP_PTS_LAST5'])/2,'HOME_REST': hf['REST'],'AWAY_REST': af['REST'],'HOME_B2B': hf['B2B'],'AWAY_B2B': af['B2B']}
        base_pred = float(model.predict(pd.DataFrame([feat])[feature_cols])[0])
        pred_total = base_pred + home_adj + away_adj
        if pred_total < 180 or pred_total > 260:
            pred_total = feat['EXPECTED_TOTAL'] + home_adj + away_adj

        edge = pred_total - line
        pick = "OVER" if edge > 0 else "UNDER"

        if abs(edge) >= 4:
            badge = "✅ STRONG BET"
            color = "green"
        elif abs(edge) >= 2:
            badge = "⚠️ SMALL EDGE"
            color = "orange"
        else:
            badge = "❌ NO BET"
            color = "red"

        with st.container():
            st.markdown(f"**{display}**")
            st.write(f"Model: **{pred_total:.1f}** | Bet9ja Line: **{line}** | Edge: **{edge:+.1f}** | Pick: **{pick}**")
            st.write(f"Injuries: HOME {home_inj} (OUT {home_out}) | AWAY {away_inj} (OUT {away_out})")
            st.markdown(f":{color}[{badge}]")
            st.divider()