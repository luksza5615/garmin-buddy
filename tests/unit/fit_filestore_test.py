import io
import zipfile
from unittest.mock import Mock

import pytest

from garmin_buddy.ingestion.fit_filestore import FitFileStore, MAX_ZIP_BYTES
from garmin_buddy.settings.config import Config


def _build_zip_bytes(file_content: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_STORED) as zip_ref:
        zip_ref.writestr("activity.fit", file_content)
    return buffer.getvalue()


@pytest.fixture
def fit_filestore(tmp_path) -> FitFileStore:
    config = Config(
        fit_dir_path=tmp_path,
        garmin_email="email",
        garmin_password="password",
        db_connection_string="connection",
        llm_api_key="api-key",
    )
    return FitFileStore(config)


@pytest.fixture
def garmin_client_mock() -> Mock:
    client = Mock()
    client.get_activity_signature.return_value = (1, "running", "2026-02-04")
    return client


def test_create_fit_file_from_zip_happy_path(
    fit_filestore: FitFileStore, garmin_client_mock: Mock, tmp_path
) -> None:
    fit_zip_file = _build_zip_bytes(b"fit-data")
    fit_filepath = tmp_path / "downloaded.fit"

    fit_filestore.create_fit_file_from_zip(
        fit_zip_file=fit_zip_file,
        garmin_activity={},
        fit_filepath=str(fit_filepath),
        garmin_client=garmin_client_mock,
    )

    assert fit_filepath.exists()
    assert fit_filepath.read_bytes() == b"fit-data"


def test_create_fit_file_from_zip_rejects_oversized_zip(
    fit_filestore: FitFileStore, garmin_client_mock: Mock, tmp_path
) -> None:
    fit_zip_file = _build_zip_bytes(b"a" * (MAX_ZIP_BYTES + 1))
    fit_filepath = tmp_path / "should_not_exist.fit"

    with pytest.raises(ValueError, match="exceeds the maximum allowed size"):
        fit_filestore.create_fit_file_from_zip(
            fit_zip_file=fit_zip_file,
            garmin_activity={},
            fit_filepath=str(fit_filepath),
            garmin_client=garmin_client_mock,
        )

    assert not fit_filepath.exists()
