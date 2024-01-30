for %%I in (.) do set CurrDirName=%%~nxI
azcopy make https://redactpoc1storage.blob.core.windows.net/%CurrDirName%
azcopy copy * https://redactpoc1storage.blob.core.windows.net/%CurrDirName% --recursive
