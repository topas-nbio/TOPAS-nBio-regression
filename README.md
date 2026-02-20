### A regression system for TOPAS-nBio                              ###
### Jose Ramos-Mendez, Naoki D. Kondo, and Thongchai A. M. Masilela   #
### Department of Radiation Oncology                                  #
### University of California San Francisco.                           #
### Jose.RamosMendez@ucsf.edu                                         #
### February 2026                                                     #
### ############################################################### ###

### Overview
This repository allows you to perform regression tests for TOPAS-nBio based on examples with existing published reference data.

Each directory has TOPAS parameters with the follow pattern:
- `mainABCD.txt`, where ABCD is Topas, Opt2, Opt4 or Opt6 that refer to the physics list to be used.
- `depFileN.txt`, with N=1,... dependence file used by the main file.
- `inputfiles.txt`. Lists the main file (s) to be submitted as a job.
- `tcsh script files`. Each directory has three tcsh files to submit the example to e.g. a cluster system or locally. These files are `submitLocally.sh`, `submitBSUB.sh`, and `submitQSUB.sh`.

### Batch runs
You can run multiple regression tests in one go using the batch script (run_batch.sh) and a JSON config file (batch_config.json), both located at the repository root. For the moment doing batch runs only works when using `submitLocally.sh`.

1. **Config:** Edit `batch_config.json` to set:
   - **run_folder_name** – Name used for the run directory (e.g. `"nBio-v4.1.0"`). Results will go under `run/<run_folder_name>_<date>/`.
   - **topas_executable** – TOPAS binary name (e.g. the command that you use to run TOPAS. If following the quickStart guides this should just be `"topas"`).
   - **python_cmd** – Python interpreter for tests that use scripts (e.g. `"python3"`).
   - **default_runs** – Default number of runs (iterations) per test. These runs are performed sequentially for each test.
   - **tests** – List of test directory names to run (e.g. `["DBSCAN", "FrickeIRT", "Gvalue_LET-IRT"]`).
   - **runs_per_test** (optional) – Override runs for specific tests (e.g. change the empty key-value pair to something like `{ "DBSCAN": 7, "FrickeIRT": 3 }` if you want 7 runs of DBSCAN and 3 runs of FrickeIRT).
   - **max_parallel_jobs** (optional) - Max tests in one batch. Tests run in batches of this size, then the next batch starts when the current batch has all finished (defaults to 1). 
   - Note: This current implementation doesn't avoid the problem of large differences in execution times between tests. If one test finishes fast, those cores are idle until the longest test in that batch finishes, then the remaining batches are run. More robust solutions exist to more efficiently allocate resources but for simplicity sake this is how things work.

2. **Run:** From the repository root:
   ```bash
   ./run_batch.sh
   ```
   The script temporarily patches each test's `submitLocally.sh` (and, for Gvalue_LET-IRT and Gvalue_LET-SBS, `ParameterFiles/runMain.py`) with the config values, runs `tcsh submitLocally.sh <runs>`, then restores the original files. No permanent changes are made to the test scripts. Please note that any significant modifications that you yourself make to `submitLocally.sh` may cause `run_batch.sh` to fail.

3. **Dry run:** To list which tests would run and with how many runs, without patching or executing:
   ```bash
   ./run_batch.sh --dry-run
   ```

**Requirements:** `jq` (for reading the JSON config) and `tcsh` must be installed.

### Single runs
Instead of performing batch runs you have the option to go into any of the test folders and perform a single run of that test should you so wish. This is done by:

1. Go into the directory of the test you want to run, then modify the name of the TOPAS command that should be used in `submitLocally.sh`, `submitBSUB.sh`, or `submitQSUB.sh`. For the tests Gvalue_LET-IRT and Gvalue_LET-SBS this TOPAS command should be changed in `ParameterFiles/runMain.py` and the bash scripts should instead be modified with the command you use to run Python, i.e. `"python3"`.

"Gvalue_LET-IRT" || "$test_name" == "Gvalue_LET-SBS"

2. Choose how many runs you want to do of that test, then:
   ```bash
   tcsh submitLocally.sh 5
   ```
   Similar to the batch runs, a `run` subdirectory is created which contains the output of all runs.

### Analysis
To make comparisons between different run directories, use the python script `analysis/analysis.py`. The following is an example for comparing the results of the GvalueIRT regression test of nBio-v4.0 and nBio-v3.0.

```bash
python3 analysis/analysis.py run/nBio-v4.0_2025Jul3/mainTopas run/nBio-v3.0_2025Jul3/mainTopas --sut_label nBio-v4.0 --ref_label nBio-v3.0
```
Look for the images in the directory `results/`. A table which contains averaged execution time per CPU is also available.

### Test details
1. DBSCAN. Quantifies the ratio between SSB to DSB for protons using the clustering algorithm DBSCAN. Reference data from previous Geant4-DNA version (Francis et al., 2017) and digitized data from PARTRAC and measured is provided.

2. GvalueStepByStep. Quantifies the G-value as a function of the time for fast electrons of 1 MeV. Reference data from Wang et al., 2018 at the shortest times (7 ps) is provided.

3. LET. Quantifies restricted LET. Reference data from PARTRAC is provided.

4. NanodosimetryI. Quantifies the conditional ionization cluster size distribution (nu > 0) from carbon ions of 88 MeV incident in a single cylinder. Measured data obtained in gas from Hilgers et al., 2017 is provided.

5. NanodosimetryII. Quantifies F2 vs M1, where F2 is the cumulative probability of having ionization clusters of size 2 or bigger, and M1 is the fist moment of the unconditional ionization cluster size distribution. Measured data obtained from Conte et al. 2017 is provided.

6. NanodosimetryIII. Quantifies ionization cluster size distribution produced in randomly oriented cylinders for ions from proton to oxygen ions. Calculated reference data from Ramos-Mendez et al., 2017 is provided.

7. GValueIRT. Quantifies the G-value as a function of the time for fast electrons of 1 MeV. 

8. FrickeIRT. Quantifies the G-value of Fe^3+ which comes from the oxidation of Fe^2+.
This example must give a value of around 15.5 +- 0.1 reported by the ICRU.

9. GValue_LET-IRT. LET-dependent G values for e-, p and alpha at selected energies.

10. GValue_LET-SBS. LET-dependent G values for e-, p and alpha at selected energies.

11. GvalueIRT-Temperature. Temperature-dependent G values for fast electrons at T < 200C.

12. GvalueIRT_H2O2. OH-scavenger-dependent G value for H2O2 within microsecond time range.

13. GvalueIRT_H. H-scavenger-dependent G value for H within microsecond time range.

### Optional
If you have modified the names of the image files resulting from `analysis.py`, open the python script `copy_and_paste.py` in the directory Summary/tex_openTOPAS and change the names of the appropriate files such that they match. Then run the script. This will copy and paste all the regression test images into a new directory called Summary/openTOPAS. Run the .tex file in order to generate a PDF summarising all the results.

### For future maintainers
Recommendations for future maintainers of this repository are as follows:

1. Download the repository and do batch or single runs with the new version of TOPAS-nBio to be released. This will add a new subdirectory in `/run/` for the new TOPAS-nBio version under test. 

2. Delete the oldest version of TOPAS-nBio in `/run/` such that it only contains two directories - the previous version of TOPAS-nBio and the new version to be released. This is to avoid accumulating old runs since past regression results can be downloaded in the Releases tab on the right of the GitHub page.

3. Run the analyses scripts, generate the summary pdf, then move this pdf to root of the repository, replacing the old pdf.

4. To keep things as simple as possible I recommend the following workflow when preparing to push to github:
```bash
git add .
git commit -m "TOPAS-nBio v<new version number> baseline"
git push origin main
```
Then on the GitHub webpage Releases → "Draft a new release" → "Create new tag" → Enter the new version number → Enter a release title/release notes → Publish release.

5. For the moment this approach is fine, but as new releases accumulate we may reach GitHub's recommended limit for repository size (< 5 GB).