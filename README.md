# hsadownload

Python package for downloading data from the Herschel Science Archive

hsadownload.access contains functions generic to all Herschel products

hsadownload.getpacs contains functions specific to data products from the PACS instrument

## Usage

```
from hsadownload import access, getpacs
```

The main function for downloading PACS maps is `getpacs.storePacsPhoto`. It is
designed to download the highest-level PACS map for a given observation id. By
default for Level 2.5 and Level 3 it checks whether the obsid matches
'obsid001' in the observation metadata. If not, it skips the download.
Specify `checkBlue=False` to download the blue map regardless.

Note that these functions have been tested for downloading SPG v12.1.0 and
SPG v13.0.0 data from the Herschel Science Archive. For 14.0 version the
metadata will change and this will require a new means of checking whether
to download a map.


