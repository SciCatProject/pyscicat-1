# these need to be loaded at the beginning to avoid errors related to relative imports (ImportWarning in h5py)
# might be related to the change of import style for Python 3.7+. Tested on Python 3.9 at 20220114
from pathlib import Path

# these packages are failing to import in McHat if they are not loaded here:
from pyscicat.hdf5.scientific_metadata import scientific_metadata
from pyscicat.hdf5.h5tools import h5Get, h5GetDict


def test_readValue():
    # more intelligent path finding:
    p = sorted(Path("").glob("**/cylinderHex_r5_s12_T50_large_ranW_0p5.nxs"))[0]
    v = h5Get(p, "/sasentry1/sasdata1/I")
    assert v != "none", "Did not extract value"


def test_readAttribute():
    p = sorted(Path("").glob("**/cylinderHex_r5_s12_T50_large_ranW_0p5.nxs"))[0]
    v = h5Get(p, "/sasentry1/sasdata1@timestamp")
    assert v != "none", "Did not extract attribute"


def test_readMixedDict():
    p = sorted(Path("").glob("**/cylinderHex_r5_s12_T50_large_ranW_0p5.nxs"))[0]
    v = h5GetDict(
        p,
        {
            "/sasentry1/sasdata1@timestamp": 123,
            "/sasentry1/sasdata1/I": 0,
            "/sasentry1/sasdata1/I@units": "inverse amps",
        },
    )
    assert (
        v["/sasentry1/sasdata1/I@units"] != "inverse amps"
    ), "Did not extract unit attribute"

    assert v["/sasentry1/sasdata1/I"] != 0, "Did not extract intensity value(s)"


def test_readMetadata_withroot():
    p = sorted(Path("").glob("**/cylinderHex_r5_s12_T50_large_ranW_0p5.nxs"))[0]
    assert p.exists(), f"HDF5/NeXus test file: {p.as_posix()} cannot be found"
    resultDict = scientific_metadata(p, excludeRootEntry=True, skipKeyList=["sasdata1"])
    assert resultDict is not None, "scientific_metadata has not returned anything"

    # make sure the root entry has been skipped
    assert "sasentry1" not in resultDict.keys(), "Root entry was not excluded"

    # make sure the skipKeyList item has been skipped
    assert "sasdata1" not in resultDict.keys(), "skipKey was not skipped"
