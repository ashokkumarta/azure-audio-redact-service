for %%I in (.) do set CurrDirName=%%~nxI
azcopy rm https://redactpoc1storage.blob.core.windows.net/%CurrDirName% --recursive
