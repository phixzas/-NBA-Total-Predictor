# 🏀 NBA Total Predictor
live link: **https://rberemcqqkvtw3tnxfhcee.streamlit.app/**


Machine Learning model that predicts **Total Points (Over / Under)** for NBA games.

You enter the Bet main line, the model tells you its own predicted total, the edge, and whether to play OVER, UNDER, or SKIP.

Built for 24-hour NBA slate - shows all games as `HOME v AWAY` like Bet9ja.

## 🎯 How It Works

1. **Live Schedule** - Fetches next 24h NBA games from ESPN Scoreboard API
2. **Team Form** - Last 5 games PTS, Opp PTS, Pace, FG%, Season PTS, Rest / Back-to-Back
3. **Live Injuries** - Fetches ESPN injuries, adjusts prediction:
   - Star player OUT = -4.0 points
   - Rotation player OUT = -0.5 points
   - Max adjustment = -8.0 points
4. **Model Prediction** - Trained on 5 years NBA history
5. **Edge Calculation** - `Edge = Model Prediction - Bet9ja Line`

### Pick Logic
| Edge | Verdict |
| :--- | :--- |
| Edge >= +4 or <= -4 | ✅ STRONG BET |
| Edge >= +2 or <= -2 | ⚠️ SMALL EDGE |
| Edge < 2 | ❌ NO BET - SKIP |

Example:
> Model: 217.2 | Sportbet Line: 225.5 | Edge: -8.3 | Pick: UNDER ✅ STRONG BET

## 🚀 Live App

Try it live here: **https://rberemcqqkvtw3tnxfhcee.streamlit.app/**

## 📱 How To Use

1. Open the app
2. You go see all games for next 24h as `PHX v SAS`, `DAL v IND` etc
3. Open Bet9ja, copy MAIN LINE (1.90 / 1.90) for each game
4. Type the line for each game box
5. Click **PREDICT ALL GAMES**
6. See Model Total, Edge, Pick, and Injuries

## 🛠️ Run Locally

```bash
# Clone repo
git clone https://github.com/your-username/nba-total-predictor.git
cd nba-total-predictor

# Install
pip install -r requirements.txt

# Run
python -m streamlit run app.py
