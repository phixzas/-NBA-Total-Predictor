# 🏀 NBA Total Predictor

An XGBoost machine-learning app that estimates total points for upcoming NBA games. Enter a bookmaker's points line to see the model's predicted total, the difference from that line, and a suggested over/under pick.

**Live app:** [NBA Total Predictor](https://rberemcqqkvtw3tnxfhcee.streamlit.app/)

## How It Works

1. **Upcoming games:** Retrieves NBA game listings from the ESPN Scoreboard API.
2. **Team form:** Builds features from recent team scoring, points allowed, pace, field-goal percentage, recent scoring averages, and rest.
3. **Injuries:** Retrieves player injury statuses from ESPN. Out players affect the prediction; uncertain statuses such as Questionable and Doubtful are shown without an adjustment.
4. **Prediction:** Adds the home and away injury adjustments to the model's prediction.
5. **Edge:** Calculates `Predicted Total - Bookmaker Points Line`.

### Pick thresholds

| Absolute edge | App label |
| --- | --- |
| 4 points or more | ✅ Strong bet |
| 2 points or more, but less than 4 | ⚠️ Small edge |
| Less than 2 points | ❌ No bet |

**Example:** A predicted total of 217.2 against a points line of 225.5 gives an edge of -8.3, which the app labels as a strong UNDER.

## Data and Model

- **Training data:** NBA seasons 2021–22 through 2025–26, collected with `nba_api` and the NBA Stats `LeagueGameFinder`.
- **Live data:** ESPN Scoreboard and Injuries APIs.
- **Model:** XGBoost regressor with 800 estimators, maximum depth 5, learning rate 0.03, and subsample 0.8.
- **Evaluation split:** The notebook uses an 85/15 sequential train/test split.
- **Features:** Recent home and away scoring, points allowed, pace, field-goal percentage, 20-game scoring averages, expected total, average pace, average points allowed, rest days, and back-to-back indicators.

## How to Use

1. Open the live app.
2. Find an upcoming game and check your bookmaker's **total points line** (for example, `225.5`).
3. Enter that points line for the game. Decimal odds (such as `1.90`) are not the points line.
4. Click **PREDICT ALL GAMES**.
5. Review the predicted total, edge, pick, and injury report.

## Run Locally

Clone the repository and install its dependencies:

```powershell
git clone https://github.com/phixzas/-NBA-Total-Predictor.git nba-total-predictor
Set-Location nba-total-predictor
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py
```

On macOS or Linux, activate the virtual environment with:

```bash
source .venv/bin/activate
```

## Project Structure

```text
.
├── app.py
├── NBA.ipynb
├── nba_total_model.pkl
├── feature_cols.pkl
├── nba_5years_history.csv
├── requirements.txt
├── README.md
└── LICENSE
```

## Built With

- Python
- Streamlit
- pandas
- scikit-learn
- XGBoost
- NBA Stats API (`nba_api`)
- ESPN APIs

## Disclaimer

This project is for educational and research purposes. Predictions are estimates, not guarantees of outcomes. If you choose to bet, do so responsibly and never wager more than you can afford to lose.

## License

See [LICENSE](LICENSE).
