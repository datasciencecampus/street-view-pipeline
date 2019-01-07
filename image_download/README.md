# Image downloader

This **consumes** from the `image_download_jobs` queue.

`downloader.py` is a template: Modify accordingly to download images from a
remote source.

For each downloaded image, the image is saved to disk and then **pushed** to
the `image_processing_jobs` queue.

This stage can be:
* **long lived** - Blocking on `image_download_jobs` forever.
* **concurrent** - Image download workers can consume/produce in parallel.
* **distributed** - Image download workers can access job queues over a network.