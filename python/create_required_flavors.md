# CREATE DESIRED FLAVORS

## INTRODUCTION

* Setup parser as well as logging configurations
  * parser configurations
  * logger format
* Read flavors from a excel doc
  * check input values before creating flavors
* Create desired flavor one by one
  * naming convention: service_NCNGNG_spec1_spec2: service is in **LOWER** case
  * metadata: SERVICE=SERVICE, SPEC=SPEC; these two are all in **UPPER** case
  * ram unit input is in GB, so conversion is required
  * if there is already a flavor with same name, set its metadata no matter what
  * if it does not exists, create this flavor and attach a tag
* Exception handling

## RUN

```bash
./create_required_flavors -f ${PATH_TO_CONFIG}
```