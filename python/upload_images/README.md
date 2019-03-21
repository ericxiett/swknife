# Upload images

## Intro
Need to bulk upload images to Glance.

## Proposal
1. Fill in the image to be uploaded according to the template.
2. Parse the template and call glanceclient to upload images

## Work items
* Generate excel template
* Parse excel contents
* Call glanceclient to upload

## Note
* template format: excel
* Check if the uploaded image is already in the environment.
* Specify image's properties
