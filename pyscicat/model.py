import enum

# from re import L
from typing import List, Dict, Optional

from pydantic import BaseModel


class DatasetType(str, enum.Enum):
    """type of Dataset"""

    raw = "raw"
    derived = "derived"


class MongoQueryable(BaseModel):
    """Many objects in SciCat are mongo queryable
    None of these properties should be included. When they are included at all
    v4.x of the backend will throw an error saying that they should not exist.  
    """
    createdBy: Optional[str] = None
    updatedBy: Optional[str] = None
    updatedAt: Optional[str] = None
    createdAt: Optional[str] = None


class Ownable(MongoQueryable):
    """Many objects in SciCat are ownable"""

    ownerGroup: str
    accessGroups: Optional[List[str]]
    instrumentGroup: Optional[str] = None


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
    creationTime: Optional[str]  #Needed needs to be validated in use client side code because Typing module does not support typing for this type  # not sure yet which ones are optional or not.
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
    uniqueName: str
    name: str
    customMetadata: Optional[dict]


class Dataset(Ownable):
    """
    A dataset in SciCat, base class for derived and raw datasets
    """
    pid: Optional[str] = None # This should no longer be included. The v4.x backend will not accept this.
    classification: Optional[str] = None # Optional
    contactEmail: str # Needed
    creationTime: Optional[str]# Needed datetime
    datasetName: Optional[str] = None # Optional
    description: Optional[str] = None # Optional
    history: Optional[List[dict]] = None # Optional list of foreigh key ids to the Messages table
    instrumentId: Optional[str] = None # Optional
    isPublished: Optional[bool] = False # Optional
    keywords: Optional[List[str]] = None #optional
    license: Optional[str] = None # Optional
    numberOfFiles: Optional[int] = None #Optional
    numberOfFilesArchived: Optional[int] = None #Optional
    orcidOfOwner: Optional[str] = None # Optional
    packedSize: Optional[int] = None # Optional
    owner: str # Needed
    ownerEmail: Optional[str] =  None # Optional
    sharedWith: Optional[List[str]] = None # Optional
    size: Optional[int] = None # Otional
    sourceFolder: str # Needed
    sourceFolderHost: Optional[str] = None # Optional
    techniques: Optional[List[dict]] = None # Optional  # with {'pid':pid, 'name': name} as entries
    type: DatasetType  # Needed
    validationStatus: Optional[str] = None # Optional
    version: Optional[str] = None # Optional
    scientificMetadata: Optional[Dict] = None # Optional
    principalInvestigator: Optional[str] # Needed
    creationLocation: Optional[str] # Needed

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
    instrumentGroup: Optional[str] = None
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
