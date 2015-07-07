# UBCSailBot-VideoTrainingData

## Overview
UBCSailBot-VideoTrainingData is a tool intended to ease the creation of training data for machine learning from human input. This tool converts the human input to generate a file with .label extension that is used as training data for obstacle detection algorithm. The standard format for this file can be found at demo_metainfo_label.

## Usage
Install the requirements and opencv

```sudo pip install -r requirements.txt```

Run the script and pass in a video file as the first argument

```python main.py boat.avi```


The control scheme is the following:

| Button | Action              |
| :-----------: |:------------:|
| d | next                     |
| a | previous                 |
| w | skip 24 frames back      |
| s | skip 24 frames ahead     |
| n | mark frame as empty      |
| z | mark frame as uncertain  |
| esc | quit                   |
