import enum

# from re import L
from typing import List, Dict, Optional

from pydantic import BaseModel


class DatasetType(str, enum.Enum):
    """type of Dataset"""

    raw = "raw"
    derived = "derived"


class MongoQueryable(BaseModel):
    """Many objects in SciCat are mongo queryable"""

    createdBy: Optional[str]
    updatedBy: Optional[str]
    updatedAt: Optional[str]
    createdAt: Optional[str]


class Ownable(MongoQueryable):
    """Many objects in SciCat are ownable"""

    ownerGroup: str
    accessGroups: Optional[List[str]]
    instrumentGroup: Optional[str]


class User(BaseModel):
    """Base user."""

    # TODO: find out which of these are not optional and update
    realm: str
    username: str
    email: str
    emailVerified: bool = False
    id: str


class Proposal(Ownable):
    """
    Defines the purpose of an experiment and links an experiment to principal investigator and main proposer
    """

    proposalId: str
    pi_email: Optional[str]
    pi_firstname: Optional[str]
    pi_lastname: Optional[str]
    email: str
    firstname: Optional[str]
    lastname: Optional[str]
    title: Optional[str]  # required in next backend version
    abstract: Optional[str]
    startTime: Optional[str]
    endTime: Optional[str]
    MeasurementPeriodList: Optional[
        List[dict]
    ]  # may need updating with the measurement period model


class Sample(Ownable):
    """
    Models describing the characteristics of the samples to be investigated.
    Raw datasets should be linked to such sample definitions.
    """

    sampleId: Optional[str]
    owner: Optional[str]
    description: Optional[str]
    sampleCharacteristics: Optional[dict]
    isPublished: bool = False


class Job(MongoQueryable):
    """
    This collection keeps information about jobs to be excuted in external systems.
    In particular it keeps information about the jobs submitted for archiving or
    retrieving datasets stored inside an archive system. It can also be used to keep
    track of analysis jobs e.g. for automated analysis workflows
    """

    id: Optional[str]
    emailJobInitiator: str
    type: str
    creationTime: Optional[str]  # not sure yet which ones are optional or not.
    executionTime: Optional[str]
    jobParams: Optional[dict]
    jobStatusMessage: Optional[str]
    datasetList: Optional[dict]  # documentation says dict, but should maybe be list?
    jobResultObject: Optional[dict]  # ibid.


class Instrument(MongoQueryable):
    """
    Instrument class, most of this is flexibly definable in customMetadata
    """

    pid: Optional[str]
    name: str
    customMetadata: Optional[dict]


class Dataset(Ownable):
    """
    A dataset in SciCat, base class for derived and raw datasets
    """

    pid: Optional[str]
    classification: Optional[str]
    contactEmail: str
    creationTime: str  # datetime
    datasetName: Optional[str]
    description: Optional[str]
    history: Optional[List[dict]]  # list of foreigh key ids to the Messages table
    instrumentId: Optional[str]
    isPublished: Optional[bool] = False
    keywords: Optional[List[str]]
    license: Optional[str]
    numberOfFiles: Optional[int]
    numberOfFilesArchived: Optional[int]
    orcidOfOwner: Optional[str]
    packedSize: Optional[int]
    owner: str
    ownerEmail: Optional[str]
    sharedWith: Optional[List[str]]
    size: Optional[int]
    sourceFolder: str
    sourceFolderHost: Optional[str]
    techniques: Optional[List[dict]]  # with {'pid':pid, 'name': name} as entries
    type: DatasetType
    validationStatus: Optional[str]
    version: Optional[str]
    scientificMetadata: Optional[Dict]


class RawDataset(Dataset):
    """
    Raw datasets from which derived datasets are... derived.
    """

    principalInvestigator: Optional[str]
    creationLocation: Optional[str]
    type: DatasetType = DatasetType.raw
    dataFormat: Optional[str]
    endTime: Optional[str]  # datetime
    sampleId: Optional[str]
    proposalId: Optional[str]


class DerivedDataset(Dataset):
    """
    Derived datasets which have been generated based on one or more raw datasets
    """

    investigator: str
    inputDatasets: List[str]
    usedSoftware: List[str]
    jobParameters: Optional[dict]
    jobLogData: Optional[str]
    type: DatasetType = DatasetType.derived


class DataFile(MongoQueryable):
    """
    A reference to a file in SciCat. Path is relative
    to the Dataset's sourceFolder parameter

    """

    path: str
    size: int
    time: Optional[str]
    chk: Optional[str]
    uid: Optional[str] = None
    gid: Optional[str] = None
    perm: Optional[str] = None


class Datablock(Ownable):
    """
    A Datablock maps between a Dataset and contains DataFiles
    """

    id: Optional[str]
    # archiveId: str = None  listed in catamel model, but comes back invalid?
    size: int
    packedSize: Optional[int]
    chkAlg: Optional[int]
    version: str = None
    instrumentGroup: Optional[str]
    dataFileList: List[DataFile]
    datasetId: str


class OrigDatablock(Ownable):
    """
    An Original Datablock maps between a Dataset and contains DataFiles
    """

    id: Optional[str]
    # archiveId: str = None  listed in catamel model, but comes back invalid?
    size: int
    instrumentGroup: Optional[str]
    dataFileList: List[DataFile]
    datasetId: str


class Attachment(Ownable):
    """
    Attachments can be any base64 encoded string...thumbnails are attachments
    """

    id: Optional[str]
    thumbnail: str
    caption: Optional[str]
    datasetId: str


class PublishedData:
    """
    Published Data with registered DOI
    """

    doi: str
    affiliation: str
    creator: List[str]
    publisher: str
    publicationYear: int
    title: str
    url: Optional[str]
    abstract: str
    dataDescription: str
    resourceType: str
    numberOfFiles: Optional[int]
    sizeOfArchive: Optional[int]
    pidArray: List[str]
    authors: List[str]
    registeredTime: str
    status: str
    thumbnail: Optional[str]
    createdBy: str
    updatedBy: str
    createdAt: str
    updatedAt: str
