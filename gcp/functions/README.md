# Google Cloud Functions

I tried to use Google Cloud Functions to deploy serverless LIP_JPPNET+CP-VTON.

BUT FAILED!!!!

Because there are a few [restrictions for GCF](https://cloud.google.com/functions/quotas):

- Currently the **Max deployment size** is: 100MB (compressed) for sources. 500MB (uncompressed) for sources plus modules.
- Currently the **max memory** is 2GB.

This should be enough if used for RAM only, BUT!!! read on...

Because the pre-trained models is way larger than 100MB, so we can't deploy with the function,
and will need to be downloaded everytime when the function is invoked (slow, but who cares about UX right?).
I stored the models in Google Cloud Storage and let the function download the models. However...

- the filesystem for Cloud Functions is READ-ONLY! that's okay, lets write to `/tmp`, that's write-able!
- the /tmp filesystem is in-memory filesystem and is stored in RAM together uses the 2GB quota...

So after downlaoding the pre-trained model, the RAM is not enough anymore...


MISSION FAILED...


Moving on to use Cloud Run. Let's bundle the pre-trained models with docker image!

