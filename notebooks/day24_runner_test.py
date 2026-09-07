import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(PROJECT_ROOT)
)

from config import DEFAULT_CONFIG

from backtest.runner import BacktestRunner


runner = BacktestRunner(
    DEFAULT_CONFIG
)

result = runner.run()

print(
    "\nFinal Portfolio:",
    f"${result['final_value']:,.2f}"
)

print("\nTrades:")

print(
    result["engine"].get_trades()
)