# azure-audio-redact-service
Service to redact PII information from audio files

Tools to install
----------------
```
python3
azcopy
ffmpeg
```

Python modules
--------------
```
pip install azure-cognitiveservices-speech
pip install azure-ai-language-conversations==1.1.0b2
```

Azure services used
-------------------
```
Storage account
Speech service
Language
```

Azure Permissions required
--------------------------
```
Cognitive Services Contributor
Cognitive Services Speech Contributor
Storage Account Contributor 
Storage Blob Data Contributor
```

Scripts to copy/delete folder to/from Azure storage
---------------------------------------------------
```
copy_to_az.bat
del_from_az.bat
```

Environment variables to set
----------------------------
```
set AZURE_CONVERSATIONS_ENDPOINT=<language service url>
set AZURE_CONVERSATIONS_KEY=<language service key>
set SPEECH_KEY=<speech service key>
set SPEECH_REGION=<speech service region>
set STORAGE_ACCOUNT=<storage account>
set INPUT_AUDIO_FOLDER=input-audio
set TRANSCRIBED_FOLDER=transcribed
set REDACTION_INFO_FOLDER=redaction-info
set REDACTED_AUDIO_FOLDER=redacted-audio
set REDACTION_STATUS_FOLDER=status
set INPUT_AZURE_STORAGE_CONTAINER=batch1
set RUN_ID=batch1
```
