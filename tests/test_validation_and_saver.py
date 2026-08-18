import numpy as np
import pandas as pd
import pytest

from back.saver import Saver
from back.validation.validation import Validator


def test_validator_accepts_numpy_numeric_types():
    assert Validator.check_integer(np.int64(3))
    assert Validator.check_integer(np.int16(3))
    assert Validator.check_float(np.float64(3.5))
    assert Validator.check_float(np.float32(3.5))


@pytest.mark.parametrize("name", ["analysis_1", "A", "123"])
def test_validate_name_accepts_safe_names(name):
    assert Validator.validate_name(name)


@pytest.mark.parametrize("name", ["", None, "../escape", "name/part", "space name", "name!"])
def test_validate_name_rejects_empty_or_path_like_names(name):
    assert not Validator.validate_name(name)


def test_saver_writes_csv_xlsx_and_text(tmp_path):
    frame = pd.DataFrame({"a": [1, 2], "b": ["x", "y"]})
    csv_path = tmp_path / "DATA.CSV"
    xlsx_path = tmp_path / "DATA.XLSX"
    text_path = tmp_path / "REPORT.TXT"

    Saver(csv_path, frame).save()
    Saver(xlsx_path, frame).save()
    Saver(text_path, "report").save()

    pd.testing.assert_frame_equal(pd.read_csv(csv_path), frame)
    pd.testing.assert_frame_equal(pd.read_excel(xlsx_path), frame)
    assert text_path.read_text(encoding="utf-8") == "report"


def test_saver_rejects_unknown_extension_and_wrong_content(tmp_path):
    with pytest.raises(ValueError, match="Invalid file type"):
        Saver(tmp_path / "data.json", {})
    with pytest.raises(ValueError, match="pandas dataframe"):
        Saver(tmp_path / "data.csv", "not a dataframe").save()
