from pyscicat.client import ScicatClient
from pyscicat.model import RawDataset, Ownable
from datetime import datetime
import os


"""
These test_pyscicat do not use mocks and are designed to connect
 to a v4 service for Scicat backend. You can run this easily
in docker-compose following the repo
https://github.com/SciCatProject/scicatlive.
You will also need to use one of the default user accounts or add
your own.

You will need to set environmental variables for
BASE_URL - the url of your scicat service e.g. http://localhost:3000/api/v3
SCICAT_USER - the name of your scicat user.
SCICAT_PASSWORD - the password for your scicat user.
"""

sci_clie = ScicatClient(base_url=os.environ["BASE_URL"],
                        token=None,
                        username=os.environ["SCICAT_USER"],
                        password=os.environ["SCICAT_PASSWORD"])


def test_client():

    assert type(sci_clie) == ScicatClient


def test_upload_dataset():
    ownable = Ownable(ownerGroup="ingestor", accessGroups=[])
    payload = RawDataset(
        datasetName="a new guide book",
        path="/foo/bar",
        size=42,
        packedSize=0,
        owner=os.environ["SCICAT_USER"],
        contactEmail="slartibartfast@magrathea.org",
        creationLocation="Magrathea",
        creationTime=datetime.isoformat(datetime.now()),
        instrumentId="earth",
        proposalId="deepthought",
        dataFormat="planet",
        principalInvestigator="A. Mouse",
        sourceFolder="/foo/bar",
        scientificMetadata={"type": "string", "value": {"a": "field"}},
        sampleId="gargleblaster",
        type="raw",
        ownerEmail="scicatingestor@your.site",
        sourceFolderHost="s3.heartofgold.org",
        endTime=datetime.isoformat(datetime.now()),
        techniques=[],
        numberOfFiles=0,
        numberOfFilesArchived=0,
        **ownable.dict()
    )

    sci_clie.upload_new_dataset(payload)


def test_get_dataset():

    datasets = sci_clie.get_datasets({"ownerGroup": "ingestor"})

    for dataset in datasets:
        assert dataset["ownerGroup"] == "ingestor"


def test_update_dataset():
    sci_clie = ScicatClient(base_url=os.environ["BASE_URL"],
                            token=None,
                            username=os.environ["SCICAT_USER"],
                            password=os.environ["SCICAT_PASSWORD"])

    datasets = sci_clie.get_datasets({})
    pid = datasets[0]["pid"]
    payload = RawDataset(
        size=142,
        owner="slartibartfast",
        ownerGroup="Magrateheans",
        contactEmail="slartibartfast@magrathea.org",
        creationLocation="magrathea",
        creationTime=datetime.isoformat(datetime.now()),
        instrumentId="earth",
        proposalId="deepthought",
        dataFormat="planet",
        principalInvestigator="A. Mouse",
        sourceFolder="/foo/bar",
        scientificMetadata={"a": "field"},
        sampleId="gargleblaster",
        accessGroups=["Vogons"]
    )
    sci_clie.update_dataset(payload, pid)
