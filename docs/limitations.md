# Limitations

- Paperlane is synthetic. There is no customer extract and no production warehouse.
- The Databricks CLI was not installed. `resources/databricks.yml` was not deployed.
- `pipelines/paperlane_medallion.py` is Lakeflow source. The Lakeflow service was not started, and this workstation's PySpark 3.5 build does not provide `pyspark.pipelines`. The decorators were not executed. The functions they call were executed through `spark_job` when Java was present.
- `resources/unity_catalog.sql` was not applied. Grants are enforced by `lakehouse_poc.catalog` inside the process. Fixture tokens authorize nothing outside the process.
- Databricks SQL, Photon, and a SQL warehouse were not used. The SQL text ran on local Spark 3.5.6. On 40,000 synthetic rows and 40 repeats, the partitioned p50 was 0.4407844999950612 seconds and the unpartitioned p50 was 0.397024899997632 seconds. The partitioned layout was not faster. That is a local file result, not a warehouse or Photon result.
- Kafka is an ordered JSON capture. No broker was started.
- Object storage is a local directory. `s3://`, `abfss://`, and `gs://` are blocked unless `LAKEHOUSE_ALLOW_REMOTE=1`, which this reference does not set.
- The refund model is a single logistic regression with `C=1.0`, no class weight, and threshold 0.5. Those choices were frozen before the measurement. The holdout is the last 60 orders. It is not a time-shifted production backtest beyond that split. The recorded scores are majority F1 0.0, logistic F1 0.0, and logistic false-positive rate 0.0, so the recommendation is `majority`. The threshold was not lowered after that result.
- scikit-learn 1.5.2 prints `OptimizeWarning: Unknown solver options: iprint` during the fit. The fit still returns coefficients. The estimator and the SciPy pin were not changed after the score.
- On this Windows host, `SparkSession.createDataFrame` crashes the Python worker. The job writes JSON lines and Spark reads that file in the JVM. `winutils.exe` and `hadoop.dll` from a Hadoop 3.3.5 Windows build must sit in `.hadoop/bin`. They are not committed. Ubuntu runners do not need those binaries.
- `resources/unity_catalog.sql` names privileges by role. The local enforcer also refuses a principal whose tenant is not Paperlane, so Prue is denied even though her role is analyst. That SQL file was not applied.
- MLflow writes a local file store. On Windows the tracking URI is a `file:` URI. The model registry was not used.
- Deployment decision: NO-GO.
