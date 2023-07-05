# Ingest Dataset
Ingesting Datasets is one of the primary user cases for PySciCat. Here we're describing, step by step, what's going on in the provided file in `examples/ingest_dataset.py`

## Create a ScicatClient
To begin with:
```python
from datetime import datetime
from pathlib import Path

from pyscicat.client import encode_thumbnail, ScicatClient
from pyscicat.model import (
    Attachment,
    Datablock,
    DataFile,
    Dataset,
    Sample,
    Ownable
)

# Create a client object. The account used should have the ingestor role in SciCat
scicat = ScicatClient(base_url="http://localhost:3000/api/v3",
                        username="Zaphod",
                        password="heartofgold")
```
Here we simply import the python code. Then, we setup a `ScicatClient` instance with the username/password that you were given by your SciCat administrator.

## Setup an Ownable

```python
# Create an Ownable that will get reused for several other Model objects
ownable = Ownable(ownerGroup="magrathea", accessGroups=["deep_though"])
thumb_path = Path(__file__).parent.parent / "test/data/SciCatLogo.png"
```
Now we setup an `Ownable` instance. This is a model class that several other model classes inherit from. We do not have to create it explicitly (we could have simply added `ownerGroup` and `accessGroups` each object that takes it, but here we can be DRY (Don't Repeat Yourself).

## Upload a Dataset

```python
# Create a RawDataset object with settings for your choosing. Notice how
# we pass the `ownable` instance.
dataset = Dataset(
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
    **ownable.dict())
dataset_id = scicat.upload_raw_dataset(dataset)
```
Now we can create a Dataset instance and upload it! Notice how we passed the fields of the `ownable` instance there at the end.

Note that we store the provided dataset_id in a variable for later use.

Also note the `sourceFolder`. This is a folder on the file system that SciCat has access to, and will contain the files for this `Dataset`.

Proposals and instruments have to be created by an administrator. A sample with `sampleId="gargleblaster"` can be created like this:
```python
sample = Sample(
    sampleId="gargleblaster",
    owner="Chamber of Commerce",
    description="A legendary drink.",
    sampleCharacteristics={"Flavour": "Unknown, but potent"},
    isPublished=False,
    **ownable.dict()
)
sample_id = client.upload_sample(sample)  # sample_id == "gargleblaster"
```

## Upload a Datablock

```python
# Create Datablock with DataFiles
data_file = DataFile(path="file.h5", size=42)
data_block = Datablock(size=42,
                       version=1,
                       datasetId=dataset_id,
                       dataFileList=[data_file],
                       **ownable.dict())
scicat.upload_datablock(data_block)
```
The `Datablock` is a container for `DataFile` instances. We are not loading the files, rather we are creating references that are used (and displayed) in SciCat. 

In this example, there is only one `DataFile` instance. It has a path ("file.h5"). In the real world this would be a file that is in the folder identified in the `sourceFolder` of the `Dataset`.

## Upload Attachment
```python 

#Create Attachment
attachment = Attachment(
    datasetId=dataset_id,
    thumbnail=encode_thumbnail(thumb_path),
    caption="scattering image",
    **ownable.dict()
)
scicat.upload_attachment(attachment)
```
Now we upload an `Attachment`. This is often used in SciCat to display thumbnails for a `Dataset`. Here, we are loading the actual content of a file (stored in SciCat's database). 

So, to put it all together:
```python
from datetime import datetime
from pathlib import Path

from pyscicat.client import encode_thumbnail, ScicatClient
from pyscicat.model import (
    Attachment,
    Datablock,
    DataFile,
    Dataset,
    Ownable
)

# Create a client object. The account used should have the ingestor role in SciCat
scicat = ScicatClient(base_url="http://localhost:3000/api/v3",
                        username="Zaphod",
                        password="heartofgold")

# Create an Ownable that will get reused for several other Model objects
ownable = Ownable(ownerGroup="magrathea", accessGroups=["deep_though"])
thumb_path = Path(__file__).parent.parent / "test/data/SciCatLogo.png"


# Create a RawDataset object with settings for your choosing. Notice how
# we pass the `ownable` instance.
dataset = Dataset(
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
    **ownable.dict())
dataset_id = scicat.upload_raw_dataset(dataset)

# Create Datablock with DataFiles
data_file = DataFile(path="file.h5", size=42)
data_block = Datablock(size=42,
                       version=1,
                       datasetId=dataset_id,
                       dataFileList=[data_file],
                       **ownable.dict())
scicat.upload_datablock(data_block)

#Create Attachment
attachment = Attachment(
    datasetId=dataset_id,
    thumbnail=encode_thumbnail(thumb_path),
    caption="scattering image",
    **ownable.dict()
)
scicat.upload_attachment(attachment)

```