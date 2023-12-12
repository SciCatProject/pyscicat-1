# Ingest Dataset
Ingesting Datasets is one of the primary user cases for PySciCat. Here we're describing, step by step, what's going on in the provided file in `examples/ingest_dataset.py`

## Create a ScicatClient
To begin with:
```python
from datetime import datetime
from pathlib import Path

from pyscicat.client import encode_thumbnail, ScicatClient,CreateDatasetOrigDatablockDto
from pyscicat.model import (
    Attachment,
    Datablock,
    DataFile,
    RawDataset,
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
dataset = RawDataset(
    path="/foo/bar",
    size=42,
    owner="slartibartfast",
    contactEmail="slartibartfast@magrathea.org",
    creationLocation="magrathea",
    creationTime=str(datetime.now().isoformat()),
    type="raw",
    instrumentId="earth",
    proposalId="deepthought",
    dataFormat="planet",
    principalInvestigator="A. Mouse",
    sourceFolder="/foo/bar",
    scientificMetadata={"a": "field"},
    sampleId="gargleblaster",
    **ownable.model_dump())

# Required arguments: `contactEmail`, `creationTime`, `owner`, `sourceFolder`, and `type` (raw or derived)

dataset_id = scicat.datasets_create(dataset)

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
    **ownable.model_dump()
)
sample_id = scicat.samples_create(sample)  # sample_id == "gargleblaster"

# Required arguments: `isPublished`

```

## Upload a Datablock

```python
# Create Datablock with DataFiles
data_file = DataFile(path="file.h5", size=42, time = datetime.now().isoformat())

# Required arguments: `path`, `size`, `time`

data_block = CreateDatasetOrigDatablockDto(size=42,
                                           dataFileList=[data_file])

scicat.datasets_origdatablock_create(dataset_id, data_block)
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
    **ownable.model_dump()
)
scicat.upload_attachment(attachment)

# If your image is larger than 760kB you may get an error that the request entity is too large. You can resize the image before calling the encode thumbnail function. 

```
Now we upload an `Attachment`. This is often used in SciCat to display thumbnails for a `Dataset`. Here, we are loading the actual content of a file (stored in SciCat's database). 

So, to put it all together:

```python
from datetime import datetime
from pathlib import Path

from pyscicat.client import encode_thumbnail, ScicatClient,CreateDatasetOrigDatablockDto
from pyscicat.model import (
    Attachment,
    Datablock,
    DataFile,
    RawDataset,
    Sample,
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
dataset = RawDataset(
    path="/foo/bar",
    size=42,
    owner="slartibartfast",
    contactEmail="slartibartfast@magrathea.org",
    creationLocation="magrathea",
    creationTime=str(datetime.now().isoformat()),
    type="raw",
    instrumentId="earth",
    proposalId="deepthought",
    dataFormat="planet",
    principalInvestigator="A. Mouse",
    sourceFolder="/foo/bar",
    scientificMetadata={"a": "field"},
    sampleId="gargleblaster",
    **ownable.model_dump())

dataset_id = scicat.datasets_create(dataset)


# Create Datablock with DataFiles
data_file = DataFile(path="file.h5", size=42, time = datetime.now().isoformat())
data_block = CreateDatasetOrigDatablockDto(size=42,
                                           dataFileList=[data_file])

scicat.datasets_origdatablock_create(dataset_id, data_block)

# Create Attachment
attachment = Attachment(
    datasetId=dataset_id,
    thumbnail=encode_thumbnail(thumb_path),
    caption="scattering image",
    **ownable.model_dump()
)
scicat.upload_attachment(attachment)

```