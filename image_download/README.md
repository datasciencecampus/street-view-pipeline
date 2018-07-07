# Street view image downloader

This **consumes** from the `image_download_jobs` queue. downloads images from street
view, saves the image to disk and **pushes** jobs to the `image_processing_jobs`
queue.

This stage can be:
* **long lived** - Blocking on `image_download_jobs` forever.
* **concurrent** - Image download workers can consume/produce in parallel.
* **distributed** - Image download workers can access job queues over a network.

## Dependencies

```bash
sudo pip3 install requests
```
