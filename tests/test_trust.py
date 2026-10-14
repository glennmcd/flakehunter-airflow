from pathlib import Path

from flakehunter_ingest.github import get_list_of_runs
from flakehunter_ingest.trust import is_run_trusted


def test_trust_logic():
    fixture_path = Path(__file__).parent / "fixtures" / "github_list_runs.json"
    strData = fixture_path.read_text(encoding="utf-8")
    list_of_runs = get_list_of_runs(strData)
    assert isinstance(list_of_runs, list)
    assert len(list_of_runs) == 10
    num_trusted_runs = 0
    for run in list_of_runs:
        if is_run_trusted(run):
            num_trusted_runs += 1
    assert num_trusted_runs > 0
