from datetime import datetime
from pathlib import Path

import pytest
import requests_mock
from pyscicat.client import (
    from_credentials,
    from_token,
    encode_thumbnail,
    get_file_mod_time,
    get_file_size,
    ScicatCommError,
)

from pyscicat.model import (
    Attachment,
    Datablock,
    DataFile,
    Instrument,
    Proposal,
    RawDataset,
    Sample,
    Ownable,
)

local_url = "http://localhost:3000/api/v3/"


def add_mock_requests(mock_request):
    mock_request.post(
        local_url + "Users/login",
        json={"id": "a_token"},
    )

    mock_request.post(local_url + "Instruments", json={"pid": "earth"})
    mock_request.post(local_url + "Proposals", json={"proposalId": "deepthought"})
    mock_request.post(local_url + "Samples", json={"sampleId": "gargleblaster"})
    mock_request.patch(local_url + "Instruments/earth", json={"pid": "earth"})
    mock_request.patch(
        local_url + "Proposals/deepthought", json={"proposalId": "deepthought"}
    )
    mock_request.patch(
        local_url + "Samples/gargleblaster", json={"sampleId": "gargleblaster"}
    )

    mock_request.post(local_url + "RawDatasets/replaceOrCreate", json={"pid": "42"})
    mock_request.patch(
        local_url + "Datasets/42",
        json={"pid": "42"},
    )
    mock_request.post(
        local_url + "Datasets/42/origdatablocks",
        json={"response": "random"},
    )
    mock_request.post(
        local_url + "Datasets/42/attachments",
        json={"response": "random"},
    )

    mock_request.post(local_url + "Datasets", json={"pid": "42"})


def test_scicat_ingest():
    with requests_mock.Mocker() as mock_request:
        add_mock_requests(mock_request)
        scicat = from_credentials(
            base_url=local_url,
            username="Zaphod",
            password="heartofgold",
        )
        assert (
            scicat._token == "a_token"
        ), "scicat client set the token given by the server"

        ownable = Ownable(ownerGroup="magrathea", accessGroups=["deep_though"])
        thumb_path = Path(__file__).parent / "data/SciCatLogo.png"

        time = get_file_mod_time(thumb_path)
        assert time is not None
        size = get_file_size(thumb_path)
        assert size is not None

        # Instrument
        instrument = Instrument(
            pid="earth", name="Earth", customMetadata={"a": "field"}
        )
        assert scicat.upload_instrument(instrument) == "earth"
        assert scicat.instruments_create(instrument) == "earth"
        assert scicat.instruments_update(instrument) == "earth"

        # Proposal
        proposal = Proposal(
            proposalId="deepthought",
            title="Deepthought",
            email="deepthought@viltvodle.com",
            **ownable.dict()
        )
        assert scicat.upload_proposal(proposal) == "deepthought"
        assert scicat.proposals_create(proposal) == "deepthought"
        assert scicat.proposals_update(proposal) == "deepthought"

        # Sample
        sample = Sample(
            sampleId="gargleblaster",
            description="Gargleblaster",
            sampleCharacteristics={"a": "field"},
            **ownable.dict()
        )
        assert scicat.upload_sample(sample) == "gargleblaster"
        assert scicat.samples_create(sample) == "gargleblaster"
        assert scicat.samples_update(sample) == "gargleblaster"

        # RawDataset
        dataset = RawDataset(
            path="/foo/bar",
            size=42,
            owner="slartibartfast",
            contactEmail="slartibartfast@magrathea.org",
            creationLocation="magrathea",
            creationTime=str(datetime.now()),
            type="raw",
            instrumentId="earth",
            proposalId="deepthought",
            dataFormat="planet",
            principalInvestigator="A. Mouse",
            sourceFolder="/foo/bar",
            scientificMetadata={"a": "field"},
            sampleId="gargleblaster",
            **ownable.dict()
        )
        dataset_id = scicat.upload_new_dataset(dataset)
        assert dataset_id == "42"

        # Update record
        dataset.principalInvestigator = "B. Turtle"
        dataset_id_2 = scicat.update_dataset(dataset, dataset_id)
        assert dataset_id_2 == dataset_id

        # Datablock with DataFiles
        data_file = DataFile(path="/foo/bar", size=42)
        data_block = Datablock(
            size=42,
            version=1,
            datasetId=dataset_id,
            dataFileList=[data_file],
            **ownable.dict()
        )
        scicat.upload_dataset_origdatablock(data_block)

        # Attachment
        attachment = Attachment(
            datasetId=dataset_id,
            thumbnail=encode_thumbnail(thumb_path),
            caption="scattering image",
            **ownable.dict()
        )
        scicat.upload_attachment(attachment)


def test_get_dataset():
    with requests_mock.Mocker() as mock_request:
        dataset = RawDataset(
            size=42,
            owner="slartibartfast",
            contactEmail="slartibartfast@magrathea.org",
            creationLocation="magrathea",
            creationTime=str(datetime.now()),
            instrumentId="earth",
            proposalId="deepthought",
            dataFormat="planet",
            principalInvestigator="A. Mouse",
            sourceFolder="/foo/bar",
            scientificMetadata={"a": "field"},
            sampleId="gargleblaster",
            ownerGroup="magrathea",
            accessGroups=["deep_though"],
        )
        mock_request.get(
            local_url + "Datasets/123", json=dataset.dict(exclude_none=True)
        )

        client = from_token(base_url=local_url, token="a_token")
        retrieved = client.datasets_get_one("123")
        assert retrieved == dataset.dict(exclude_none=True)


def test_get_nonexistent_dataset():
    with requests_mock.Mocker() as mock_request:
        mock_request.get(
            local_url + "Datasets/74",
            status_code=404,
            reason="Not Found",
            json={
                "error": {
                    "statusCode": 404,
                    "name": "Error",
                    "message": 'Unknown "Dataset" id "74".',
                    "code": "MODEL_NOT_FOUND",
                }
            },
        )
        client = from_token(base_url=local_url, token="a_token")
        assert client.datasets_get_one("74") is None


def test_get_dataset_bad_url():
    with requests_mock.Mocker() as mock_request:
        mock_request.get(
            "http://localhost:3000/api/v100/Datasets/53",
            status_code=404,
            reason="Not Found",
            json={
                "error": {
                    "statusCode": 404,
                    "name": "Error",
                    "message": "Cannot GET /api/v100/Datasets/53",
                }
            },
        )
        client = from_token(base_url="http://localhost:3000/api/v100", token="a_token")
        with pytest.raises(ScicatCommError):
            client.datasets_get_one("53")


def test_initializers():
    with requests_mock.Mocker() as mock_request:
        add_mock_requests(mock_request)

        client = from_token(local_url, "let me in!")
        assert client._token == "let me in!"
